import asyncio

import httpx
import yfinance as yf
from fastapi import APIRouter, Query

router = APIRouter()

INDICES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225",
    "AEX": "^AEX",
}


def _fetch_tickers(symbols: list[str]) -> dict:
    result = {}
    for sym in symbols:
        info = yf.Ticker(sym).fast_info
        result[sym] = {
            "symbol": sym,
            "price": getattr(info, "last_price", None),
            "currency": getattr(info, "currency", None),
            "market_cap": getattr(info, "market_cap", None),
            "52w_high": getattr(info, "year_high", None),
            "52w_low": getattr(info, "year_low", None),
        }
    return result


@router.get("/stocks", summary="Stock prices (Yahoo Finance via yfinance)")
async def get_stocks(
    symbols: str = Query("AAPL,MSFT,GOOGL,AMZN", description="Comma-separated ticker symbols"),
):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    return await asyncio.to_thread(_fetch_tickers, symbol_list)


@router.get("/indices", summary="Major global stock indices")
async def get_indices():
    def fetch():
        return {name: _fetch_tickers([sym])[sym] | {"name": name} for name, sym in INDICES.items()}

    return await asyncio.to_thread(fetch)


@router.get("/crypto", summary="Cryptocurrency prices (CoinGecko, no key needed)")
async def get_crypto(
    coins: str = Query(
        "bitcoin,ethereum,solana,ripple",
        description="Comma-separated CoinGecko coin IDs",
    ),
):
    coin_list = [c.strip().lower() for c in coins.split(",") if c.strip()]
    ids = ",".join(coin_list)
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    return {
        coin: {
            "price_usd": info.get("usd"),
            "market_cap_usd": info.get("usd_market_cap"),
            "change_24h_pct": info.get("usd_24h_change"),
        }
        for coin, info in data.items()
    }
