"""Meta Ad Library API — competitor ad intelligence."""

import httpx
from config.settings import settings

BASE_URL = "https://graph.facebook.com/v21.0/ads_archive"


def search_ads(
    query: str,
    limit: int = 20,
    ad_type: str = "ALL",
    country: str = "US",
) -> dict:
    """Search Meta Ad Library for active ads."""
    params = {
        "search_terms": query,
        "ad_type": ad_type,
        "ad_reached_countries": f'["{country}"]',
        "ad_active_status": "ACTIVE",
        "fields": "id,ad_creation_time,ad_creative_bodies,ad_creative_link_titles,ad_creative_link_descriptions,page_name,spend",
        "limit": limit,
        "access_token": settings.META_AD_LIBRARY_ACCESS_TOKEN,
    }

    response = httpx.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    ads = []
    for ad in data.get("data", []):
        ads.append({
            "id": ad.get("id"),
            "page_name": ad.get("page_name"),
            "created": ad.get("ad_creation_time"),
            "bodies": ad.get("ad_creative_bodies", []),
            "titles": ad.get("ad_creative_link_titles", []),
            "descriptions": ad.get("ad_creative_link_descriptions", []),
        })

    return {
        "ads": ads,
        "total": len(ads),
        "query": query,
    }
