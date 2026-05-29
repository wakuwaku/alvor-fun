import asyncio
import json
import os
from typing import Optional

import websockets
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

WS_URL = "wss://stream.aisstream.io/v0/stream"


@router.get("/vessels", summary="Live vessel positions (aisstream.io) — requires free API key")
async def get_vessels(
    latmin: float = Query(..., description="South latitude"),
    latmax: float = Query(..., description="North latitude"),
    lonmin: float = Query(..., description="West longitude"),
    lonmax: float = Query(..., description="East longitude"),
    mmsi: Optional[str] = Query(None, description="Filter by MMSI number"),
    limit: int = Query(50, ge=1, le=500, description="Max vessels to collect"),
    timeout: int = Query(8, ge=1, le=30, description="Seconds to collect data"),
):
    AISSTREAM_KEY = os.getenv("AISSTREAM_API_KEY", "")
    if not AISSTREAM_KEY:
        raise HTTPException(
            status_code=503,
            detail="AISSTREAM_API_KEY is not configured. Get a free key at https://aisstream.io",
        )

    subscription: dict = {
        "APIKey": AISSTREAM_KEY,
        "BoundingBoxes": [[[latmin, lonmin], [latmax, lonmax]]],
    }
    if mmsi:
        subscription["MMSI"] = [int(mmsi)]

    vessels: dict = {}
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(subscription))
            deadline = asyncio.get_event_loop().time() + timeout
            async for raw in ws:
                if asyncio.get_event_loop().time() >= deadline or len(vessels) >= limit:
                    break
                msg = json.loads(raw)
                if msg.get("MessageType") != "PositionReport":
                    continue
                meta = msg.get("MetaData", {})
                pr = msg["Message"]["PositionReport"]
                mmsi_val = str(pr.get("UserID", ""))
                if not mmsi_val:
                    continue
                vessels[mmsi_val] = {
                    "mmsi": mmsi_val,
                    "name": meta.get("ShipName", "").strip(),
                    "latitude": pr.get("Latitude"),
                    "longitude": pr.get("Longitude"),
                    "speed_knots": pr.get("Sog"),
                    "course": pr.get("Cog"),
                    "heading": pr.get("TrueHeading"),
                    "nav_status": pr.get("NavigationalStatus"),
                    "time_utc": meta.get("time_utc"),
                }
    except websockets.exceptions.ConnectionClosedError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    result = list(vessels.values())
    return {"count": len(result), "vessels": result}
