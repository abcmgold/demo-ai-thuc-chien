"""Search for travel facts and append one sample to the travel dataset."""

import json
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone
import unicodedata

from nexus.text import chat_json, web_search
from nexus.travel import COMFORTS, TRANSPORTS, normalize_request


ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = ROOT / "data" / "synthetic_travel_samples.json"
PRICE_FIELDS = (
    ("travel_location", "entrance_cost_vnd_per_person"),
    ("hotel", "cost_vnd_per_room_per_night"),
    ("food", "cost_vnd_per_person_per_meal"),
    ("transport", "cost_vnd_per_group_round_trip"),
)


class SearchDataError(ValueError):
    """A web result lacked data required for a usable planner sample."""


def validate_sample(sample: dict, shape: dict) -> None:
    """Require the sample structure while allowing unknown prices as null."""
    for key, expected in shape.items():
        if key not in sample:
            raise ValueError(f"Missing sample field: {key}")
        value = sample[key]
        if isinstance(expected, dict):
            if not isinstance(value, dict):
                raise ValueError(f"Expected object: {key}")
            validate_sample(value, expected)
        elif isinstance(expected, list):
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise ValueError(f"Expected string array: {key}")
        elif isinstance(expected, int):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"Expected nonnegative integer or null: {key}")
        elif value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"Expected nonempty string or null: {key}")
    if "party_size" in shape:
        if sample["party_size"] is None or sample["stay_nights"] is None:
            raise ValueError("Party size and stay nights are required")
        if sample["party_size"] < 1 or sample["stay_nights"] < 1:
            raise ValueError("Party size and stay nights must be positive")
        capacity = sample["hotel"]["room_capacity_persons"]
        if capacity is not None and capacity < 1:
            raise ValueError("Room capacity must be positive")


def calculate_total(sample: dict) -> int | None:
    prices = [sample[section][field] for section, field in PRICE_FIELDS]
    if any(price is None for price in prices) or sample["hotel"]["room_capacity_persons"] is None:
        return None
    entrance, room, food, transport = prices
    rooms = math.ceil(sample["party_size"] / sample["hotel"]["room_capacity_persons"])
    return (entrance + food) * sample["party_size"] + room * rooms * sample["stay_nights"] + transport


def next_id(samples: list[dict]) -> str:
    numbers = [int(item["id"][3:]) for item in samples
               if isinstance(item.get("id"), str) and item["id"].startswith("DL-")
               and item["id"][3:].isdigit()]
    return f"DL-{max(numbers, default=0) + 1:03d}"


def _normalized(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").casefold().replace("đ", "d"))
    return " ".join("".join(char for char in text if not unicodedata.combining(char)).split())


def duplicate_key(sample: dict) -> tuple:
    return (
        _normalized(sample.get("profile")), sample.get("party_size"), sample.get("stay_nights"),
        _normalized(sample["travel_location"].get("name")),
        _normalized(sample["hotel"].get("name")),
        _normalized(sample["food"].get("item")),
        _normalized(sample["transport"].get("mode")),
        _normalized(sample["transport"].get("origin")),
        _normalized(sample["transport"].get("destination")),
    )


def save_web_sample(template: dict, sample: dict, sources: list[str]) -> dict:
    """Refresh a matching web sample or append a distinct one."""
    key = duplicate_key(sample)
    existing = next((item for item in template["samples"]
                     if item.get("source_urls") and duplicate_key(item) == key), None)
    sample["id"] = existing["id"] if existing else next_id(template["samples"])
    sample["source_urls"] = sources
    sample["price_status"] = "web_sourced_unverified"
    sample["collected_at"] = datetime.now(timezone.utc).isoformat()
    if existing:
        template["samples"][template["samples"].index(existing)] = sample
    else:
        template["samples"].append(sample)
    template["sample_count"] = len(template["samples"])
    template["is_synthetic"] = False
    template["price_status"] = "mixed_synthetic_and_web_unverified"
    note = f" {sample['id']} refreshed from web sources: " if existing else f" {sample['id']} added from web sources: "
    template["notes"] += note + ", ".join(sources) + "."
    serialized = json.dumps(template, ensure_ascii=False, indent=2) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=SAMPLE_PATH.parent, delete=False) as temporary:
        temporary.write(serialized)
        temporary_path = Path(temporary.name)
    temporary_path.replace(SAMPLE_PATH)
    return sample


def build_search_prompt(request: dict) -> str:
    """Create a fact-finding question from validated trip preferences."""
    request = normalize_request(request)
    lodging = (
        f"Cần khách sạn tại Buôn Ma Thuột cho {request['nights']} đêm, "
        "giá phòng/đêm và sức chứa phòng. "
        if request["nights"] else
        "Chuyến đi không lưu trú qua đêm; không cần tìm khách sạn. "
    )
    return (
        f"Tìm một điểm tham quan ở Đắk Lắk phù hợp chuyến đi {request['days']} ngày, "
        f"{request['people']} người, sở thích {', '.join(request['interests']) or 'linh hoạt'}, "
        f"phương tiện {request['transport']}, mức tiện nghi {request['comfort']}, "
        f"nhịp độ {request['pace']}, ngân sách cả nhóm {request['group_budget_vnd']} VND. "
        f"Điểm bắt đầu: {request['start_area']}; dự trù {request['meals_per_day']} bữa/người/ngày. "
        "Nếu điểm bắt đầu không xác định hoặc ngoài Đắk Lắk, không ước tính chi phí đến/rời tỉnh. "
        "Cần nguồn URL cho giá vé tham quan mỗi người và giá mỗi bữa ăn. "
        + lodging +
        "Cần chi phí di chuyển khứ hồi cho nhóm từ trung tâm Buôn Ma Thuột trong tỉnh. "
        "Chỉ nêu giá có nguồn xác nhận; nói rõ mục nào chưa tìm thấy."
    )


def search_and_append(raw_request: dict) -> dict:
    request = normalize_request(raw_request)
    search_model = os.environ["TRAVEL_SEARCH_MODEL"]
    extraction_model = os.environ["TRAVEL_EXTRACTION_MODEL"]
    result = web_search(build_search_prompt(request), model=search_model)
    sources = list(dict.fromkeys(source["url"] for source in result.sources if source.get("url")))
    if not sources:
        raise SearchDataError("Web search không trả URL nguồn. Hãy thử lại với tiêu chí khác.")
    template = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    shape = template["samples"][0]
    lodging_instruction = (
        "Choose a hotel in Buôn Ma Thuột for the requested nights. "
        if request["nights"] else
        "No overnight stay was requested; use null for unsupported hotel details. "
    )
    prompt = (
        "Extract ONE Đắk Lắk travel sample as JSON with exactly the example fields. "
        "Use the example only for shape, never its values. Use only facts supported by the "
        "search answer and URLs; set unsupported names and prices to null. "
        + lodging_instruction +
        "Use a group round trip from central Buôn Ma Thuột. "
        "Set sample_total_vnd to null and id to a placeholder.\n"
        f"Trip request: {json.dumps(request, ensure_ascii=False)}\n"
        f"Example shape: {json.dumps(shape, ensure_ascii=False)}\n"
        f"Search answer: {result.text}\nSources: {json.dumps(sources, ensure_ascii=False)}"
    )
    sample = chat_json(prompt, model=extraction_model)
    if not isinstance(sample, dict):
        raise SearchDataError("Không trích xuất được dữ liệu du lịch dạng JSON.")
    sample["party_size"] = request["people"]
    sample["stay_nights"] = max(1, request["nights"])
    try:
        validate_sample(sample, shape)
    except ValueError as error:
        raise SearchDataError(f"Dữ liệu tìm kiếm chưa đúng cấu trúc: {error}") from error
    sample["sample_total_vnd"] = calculate_total(sample)
    if sample["hotel"]["area"] not in (None, "Buôn Ma Thuột"):
        raise SearchDataError("Dữ liệu tìm kiếm chưa có khách sạn tại Buôn Ma Thuột.")
    if request["transport"] != "Linh hoạt" and sample["transport"]["mode"] not in (None, TRANSPORTS[request["transport"]]):
        raise SearchDataError("Phương tiện tìm được không khớp lựa chọn của bạn.")
    comfort = COMFORTS[request["comfort"]] or "tieu_chuan"
    sample["profile"] = f"web_{comfort}"
    sample["sample_total_vnd"] = calculate_total(sample)
    return save_web_sample(template, sample, sources)


def main() -> None:
    query = os.environ["TRAVEL_SEARCH_QUERY"]
    search_model = os.environ["TRAVEL_SEARCH_MODEL"]
    extraction_model = os.environ["TRAVEL_EXTRACTION_MODEL"]
    template = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    shape = template["samples"][0]

    result = web_search(query, model=search_model)
    sources = list(dict.fromkeys(source["url"] for source in result.sources))
    if not sources:
        raise ValueError("Web search did not provide source URLs")
    prompt = (
        "Extract ONE realistic travel sample from the following web search answer. "
        "Return a JSON object with exactly the fields shown in the example sample. "
        "Use the example ONLY for field names and types, never for its values. "
        "Use null for any price or name not explicitly supported by the search answer or sources; "
        "do not guess hotel names, prices, transport cost, or opening details. "
        "Use one attraction, one meal, one overnight stay and one group round trip. "
        "Set sample_total_vnd to null; it is calculated later. "
        "Set id to any nonempty placeholder; it is assigned later.\n\n"
        f"Example shape: {json.dumps(shape, ensure_ascii=False)}\n\n"
        f"Search answer: {result.text}\n\n"
        f"Source URLs: {json.dumps(sources, ensure_ascii=False)}"
    )
    sample = chat_json(prompt, model=extraction_model)
    if not isinstance(sample, dict):
        raise ValueError("Extraction did not return a JSON object")
    validate_sample(sample, shape)
    sample["sample_total_vnd"] = calculate_total(sample)
    print(json.dumps(save_web_sample(template, sample, sources), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
