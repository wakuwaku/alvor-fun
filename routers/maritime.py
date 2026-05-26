import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

AISHUB_USER = os.getenv("AISHUB_USERNAME", "")


@router.get("/vessels", summary="Live vessel positions (AISHub) — requires free account")
async def get_vessels(
    latmin: float = Query(..., description="South latitude"),
    latmax: float = Query(..., description="North latitude"),
    lonmin: float = Query(..., description="West longitude"),
    lonmax: float = Query(..., description="East longitude"),
    mmsi: Optional[str] = Query(None, description="Filter by MMSI number"),
):
    if not AISHUB_USER:
        raise HTTPException(
            status_code=503,
            detail="AISHUB_USERNAME is not configured. Register free at https://www.aishub.net/register",
        )

    params = {
        "username": AISHUB_USER,
        "format": 1,
        "output": "json",
        "compress": 0,
        "latmin": latmin,
        "latmax": latmax,
        "lonmin": lonmin,
        "lonmax": lonmax,
    }
    if mmsi:
        params["mmsi"] = mmsi

    async with httpx.AsyncClient() as client:
        resp = await client.get("http://data.aishub.net/ws.php", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

    # AISHub returns [metadata_dict, [vessel_list]]
    vessels = data[1] if isinstance(data, list) and len(data) > 1 else []
    return {"count": len(vessels), "vessels": vessels}
