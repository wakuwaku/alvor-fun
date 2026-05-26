import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

OPENSKY_USER = os.getenv("OPENSKY_USERNAME")
OPENSKY_PASS = os.getenv("OPENSKY_PASSWORD")

FIELDS = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source",
]


def _parse_states(data: dict) -> list:
    states = data.get("states") or []
    return [dict(zip(FIELDS, s)) for s in states]


@router.get("/flights", summary="Live flight positions (OpenSky Network)")
async def get_flights(
    lamin: Optional[float] = Query(None, description="Bounding box — south latitude"),
    lomin: Optional[float] = Query(None, description="Bounding box — west longitude"),
    lamax: Optional[float] = Query(None, description="Bounding box — north latitude"),
    lomax: Optional[float] = Query(None, description="Bounding box — east longitude"),
):
    params = {}
    if all(v is not None for v in [lamin, lomin, lamax, lomax]):
        params = {"lamin": lamin, "lomin": lomin, "lamax": lamax, "lomax": lomax}

    auth = (OPENSKY_USER, OPENSKY_PASS) if OPENSKY_USER and OPENSKY_PASS else None

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://opensky-network.org/api/states/all",
            params=params,
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail="OpenSky rate limit reached — try again later or add credentials.")
        resp.raise_for_status()
        data = resp.json()

    flights = _parse_states(data)
    return {"time": data.get("time"), "count": len(flights), "flights": flights}


@router.get("/flight/{icao24}", summary="Single aircraft by ICAO24 hex address")
async def get_flight(icao24: str):
    auth = (OPENSKY_USER, OPENSKY_PASS) if OPENSKY_USER and OPENSKY_PASS else None

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://opensky-network.org/api/states/all",
            params={"icao24": icao24.lower()},
            auth=auth,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

    states = data.get("states") or []
    if not states:
        raise HTTPException(status_code=404, detail=f"No active flight found for ICAO24 '{icao24}'")

    return dict(zip(FIELDS, states[0]))
