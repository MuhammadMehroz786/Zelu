"""Meta Marketing API — campaign creation and management."""

import httpx
from config.settings import settings

BASE_URL = "https://graph.facebook.com/v21.0"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.META_ADS_ACCESS_TOKEN}"}


def create_campaign(
    name: str,
    objective: str = "OUTCOME_SALES",
    targeting: dict = None,
    ad_copy: dict = None,
    creatives: list = None,
    daily_budget: int = 1000,
) -> dict:
    """Create a full Meta Ads campaign (campaign + ad set + ads)."""
    account_id = settings.META_ADS_ACCOUNT_ID

    # Step 1: Create campaign
    campaign_response = httpx.post(
        f"{BASE_URL}/act_{account_id}/campaigns",
        headers=_headers(),
        json={
            "name": name,
            "objective": objective,
            "status": "PAUSED",  # always start paused for safety
            "special_ad_categories": [],
        },
        timeout=30,
    )
    campaign_response.raise_for_status()
    campaign_id = campaign_response.json().get("id")

    # Step 2: Create ad set
    ad_set_payload = {
        "name": f"{name} - Ad Set",
        "campaign_id": campaign_id,
        "daily_budget": daily_budget,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "OFFSITE_CONVERSIONS",
        "status": "PAUSED",
        "targeting": targeting or {"geo_locations": {"countries": ["US"]}},
    }

    ad_set_response = httpx.post(
        f"{BASE_URL}/act_{account_id}/adsets",
        headers=_headers(),
        json=ad_set_payload,
        timeout=30,
    )
    ad_set_response.raise_for_status()
    ad_set_id = ad_set_response.json().get("id")

    # Step 3: Create ads with creatives
    ads_created = []
    if creatives and ad_copy:
        variations = ad_copy if isinstance(ad_copy, list) else ad_copy.get("variations", [])
        for i, creative in enumerate(creatives[:4]):
            variation = variations[i] if i < len(variations) else {}
            try:
                ad = _create_ad(
                    account_id=account_id,
                    ad_set_id=ad_set_id,
                    name=f"{name} - Ad {i+1}",
                    image_url=creative.get("url"),
                    primary_text=variation.get("primary_text", ""),
                    headline=variation.get("headline", ""),
                    description=variation.get("description", ""),
                )
                ads_created.append(ad)
            except Exception as e:
                ads_created.append({"error": str(e), "variation": i + 1})

    return {
        "campaign_id": campaign_id,
        "ad_set_id": ad_set_id,
        "ads": ads_created,
        "status": "PAUSED",
        "note": "Campaign created in PAUSED state. Review and activate manually.",
    }


def _create_ad(account_id, ad_set_id, name, image_url, primary_text, headline, description) -> dict:
    """Create a single ad within an ad set."""
    # First create the ad creative
    creative_response = httpx.post(
        f"{BASE_URL}/act_{account_id}/adcreatives",
        headers=_headers(),
        json={
            "name": f"{name} Creative",
            "object_story_spec": {
                "link_data": {
                    "message": primary_text,
                    "name": headline,
                    "description": description,
                    "image_url": image_url,
                    "call_to_action": {"type": "LEARN_MORE"},
                },
            },
        },
        timeout=30,
    )
    creative_response.raise_for_status()
    creative_id = creative_response.json().get("id")

    # Then create the ad
    ad_response = httpx.post(
        f"{BASE_URL}/act_{account_id}/ads",
        headers=_headers(),
        json={
            "name": name,
            "adset_id": ad_set_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        },
        timeout=30,
    )
    ad_response.raise_for_status()

    return {
        "ad_id": ad_response.json().get("id"),
        "creative_id": creative_id,
        "status": "PAUSED",
    }


def get_campaign_insights(campaign_id: str, date_range: str = "last_7d") -> dict:
    """Get performance insights for a campaign."""
    response = httpx.get(
        f"{BASE_URL}/{campaign_id}/insights",
        headers=_headers(),
        params={
            "fields": "impressions,clicks,ctr,cpc,conversions,spend,actions",
            "date_preset": date_range,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
