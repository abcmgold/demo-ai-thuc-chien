"""Offline checks for request-aware search and catalog planning."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from nexus import travel
import travel_search


class TravelSearchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "samples.json"
        self.original = json.loads(travel.DATA_PATH.read_text(encoding="utf-8"))
        self.path.write_text(json.dumps(self.original, ensure_ascii=False), encoding="utf-8")
        self.sample = deepcopy(self.original["samples"][0])
        self.source = SimpleNamespace(text="Sourced travel facts", sources=[{"url": "https://example.org/travel"}])
        for target, name in ((travel_search, "SAMPLE_PATH"), (travel, "DATA_PATH")):
            setting = patch.object(target, name, self.path)
            setting.start()
            self.addCleanup(setting.stop)
        environment = patch.dict("os.environ", {
            "TRAVEL_SEARCH_MODEL": "gemini-3.5-flash-lite",
            "TRAVEL_EXTRACTION_MODEL": "gemini-3.1-flash-lite",
            "TRAVEL_FRESHNESS_DAYS": "30",
        })
        environment.start()
        self.addCleanup(environment.stop)

    def test_prompt_uses_relevant_preferences(self):
        prompt = travel_search.build_search_prompt({
            "people": 3, "days": 4, "nights": 2, "budget": 1000000,
            "budget_basis": "Mỗi người", "interests": ["Cà phê"],
            "start_area": "Đến từ nơi khác", "transport": "Taxi",
            "comfort": "Tiêu chuẩn", "pace": "Thư thả", "meals_per_day": 2,
        })
        for phrase in ("4 ngày", "3 người", "Cà phê", "Taxi", "Tiêu chuẩn",
                       "Thư thả", "3000000 VND", "Đến từ nơi khác", "2 bữa", "2 đêm"):
            self.assertIn(phrase, prompt)

    def test_zero_nights_omits_hotel_search(self):
        prompt = travel_search.build_search_prompt({"days": 1, "nights": 0})
        self.assertIn("không cần tìm khách sạn", prompt)
        self.assertNotIn("giá phòng/đêm", prompt)

    def test_complete_search_row_is_planner_eligible(self):
        with patch.object(travel_search, "web_search", return_value=self.source), \
             patch.object(travel_search, "chat_json", return_value=deepcopy(self.sample)):
            saved = travel_search.search_and_append({"people": 2, "days": 1, "nights": 1})
        catalog = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(catalog["sample_count"], self.original["sample_count"] + 1)
        self.assertEqual(saved["source_urls"], ["https://example.org/travel"])
        self.assertIn(saved["id"], {sample["id"] for sample in travel.load_catalog()})
        request = travel.normalize_request({"people": 2, "days": 1, "nights": 1})
        plan = travel.build_plan(request, {
            "days": [{"sample_id": saved["id"], "reason": "Sourced sample"}],
            "hotel_sample_id": saved["id"],
        })
        self.assertEqual(plan["days"][0]["sample_id"], saved["id"])
        self.assertEqual(plan["price_status"], "mixed_synthetic_and_web_unverified")

    def test_partial_search_row_is_saved_but_not_selected(self):
        partial = deepcopy(self.sample)
        partial["hotel"]["name"] = None
        partial["hotel"]["room_capacity_persons"] = None
        partial["hotel"]["cost_vnd_per_room_per_night"] = None
        with patch.object(travel_search, "web_search", return_value=self.source), \
             patch.object(travel_search, "chat_json", return_value=partial) as extraction:
            saved = travel_search.search_and_append({"people": 2, "days": 1, "nights": 0})
        self.assertIn("No overnight stay was requested", extraction.call_args.args[0])
        self.assertIsNone(saved["sample_total_vnd"])
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8"))["sample_count"],
                         self.original["sample_count"] + 1)
        self.assertNotIn(saved["id"], {sample["id"] for sample in travel.load_catalog()})

    def test_repeated_search_refreshes_instead_of_appending(self):
        sample = deepcopy(self.sample)
        sample["travel_location"]["name"] = "A unique sourced attraction"
        with patch.object(travel_search, "web_search", return_value=self.source), \
             patch.object(travel_search, "chat_json", side_effect=[deepcopy(sample), deepcopy(sample)]):
            first = travel_search.search_and_append({"people": 2, "days": 1, "nights": 1})
            second = travel_search.search_and_append({"people": 2, "days": 1, "nights": 1})
        catalog = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(catalog["sample_count"], self.original["sample_count"] + 1)


if __name__ == "__main__":
    unittest.main()
