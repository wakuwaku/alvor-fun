import csv
import io
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

FIRMS_KEY = os.getenv("NASA_FIRMS_API_KEY", "")


@router.get("/earthquakes", summary="Recent earthquakes (USGS)")
async def get_earthquakes(
    min_magnitude: float = Query(5.0, description="Minimum Richter magnitude"),
    limit: int = Query(20, ge=1, le=500, description="Max results"),
    days: int = Query(7, ge=1, le=90, description="Look-back period in days"),
):
    starttime = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&minmagnitude={min_magnitude}&limit={limit}"
        f"&orderby=time&starttime={starttime}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    features = data.get("features", [])
    return {
        "count": len(features),
        "earthquakes": [
            {
                "id": f["id"],
                "magnitude": f["properties"]["mag"],
                "place": f["properties"]["place"],
                "time_ms": f["properties"]["time"],
                "tsunami_alert": bool(f["properties"]["tsunami"]),
                "status": f["properties"]["status"],
                "url": f["properties"]["url"],
                "coordinates": {
                    "latitude": f["geometry"]["coordinates"][1],
                    "longitude": f["geometry"]["coordinates"][0],
                    "depth_km": f["geometry"]["coordinates"][2],
                },
            }
            for f in features
        ],
    }


@router.get("/fires", summary="Active fires (NASA FIRMS) — requires API key")
async def get_fires(
    days: int = Query(1, ge=1, le=10, description="Days to look back (1–10)"),
    region: str = Query("world", description="Region: world, USA, Canada, Europe, …"),
):
    if not FIRMS_KEY:
        raise HTTPException(
            status_code=503,
            detail="NASA_FIRMS_API_KEY is not configured. Get a free key at https://firms.modaps.eosdis.nasa.gov/api/area/",
        )
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{FIRMS_KEY}/VIIRS_SNPP_NRT/{region}/{days}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30)
        resp.raise_for_status()

    reader = csv.DictReader(io.StringIO(resp.text))
    fires = list(reader)
    return {"count": len(fires), "fires": fires}


@router.get("/weather", summary="Current weather at a location (Open-Meteo, no key needed)")
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
        "weather_code,precipitation&wind_speed_unit=ms"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    return data.get("current", {})
