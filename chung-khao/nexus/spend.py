"""Thông tin chi tiêu và hạn mức key/team từ gateway."""

from .client import http


def get_spend() -> dict:
    key_data = http().get("/key/info").raise_for_status().json().get("info", {})
    team_id = key_data.get("team_id")
    team_data = {}
    if team_id:
        team_data = http().get("/team/info", params={"team_id": team_id}).raise_for_status().json().get("team_info", {})
    spend = float(team_data.get("spend", key_data.get("spend", 0)) or 0)
    budget = team_data.get("max_budget")
    return {
        "key_spend": float(key_data.get("spend", 0) or 0),
        "team_spend": spend,
        "team_budget": budget,
        "remaining": max(0.0, float(budget) - spend) if budget is not None else None,
        "rpm_limit": team_data.get("rpm_limit", key_data.get("metadata", {}).get("model_rpm_limit")),
        "tpm_limit": team_data.get("tpm_limit", key_data.get("metadata", {}).get("model_tpm_limit")),
    }
