# Global Intelligence API

A FastAPI REST API that aggregates real-time global intelligence data — aviation, maritime, natural hazards, and financial markets — inspired by [osirisai.live](https://www.osirisai.live).

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Open .env and fill in your keys (see API Keys section below)
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## Endpoints

### Health

```
GET /health
```
Returns `{"status": "ok"}` when the server is running.

---

### Natural Hazards

#### Earthquakes
```
GET /hazards/earthquakes
```
Data source: [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/) — **no API key needed**

| Parameter | Default | Description |
|---|---|---|
| `min_magnitude` | `5.0` | Minimum Richter magnitude |
| `limit` | `20` | Max number of results (max 500) |
| `days` | `7` | How many days to look back |

```bash
# Magnitude 6+ earthquakes in the last 30 days
curl "http://localhost:8000/hazards/earthquakes?min_magnitude=6&days=30"
```

<details>
<summary>Example response</summary>

```json
{
  "count": 3,
  "earthquakes": [
    {
      "id": "us7000n3b4",
      "magnitude": 6.2,
      "place": "98 km SE of Honiara, Solomon Islands",
      "time_ms": 1715600000000,
      "tsunami_alert": false,
      "status": "reviewed",
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us7000n3b4",
      "coordinates": {
        "latitude": -9.8,
        "longitude": 161.2,
        "depth_km": 35.0
      }
    }
  ]
}
```
</details>

---

#### Active Fires *(requires NASA FIRMS API key)*
```
GET /hazards/fires
```
Data source: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/area/)

| Parameter | Default | Description |
|---|---|---|
| `days` | `1` | Days to look back (1–10) |
| `region` | `world` | Region: `world`, `USA`, `Canada`, `Europe`, etc. |

```bash
# Active fires in Europe today
curl "http://localhost:8000/hazards/fires?region=Europe&days=1"
```

---

#### Weather
```
GET /hazards/weather
```
Data source: [Open-Meteo](https://open-meteo.com/) — **no API key needed**

| Parameter | Required | Description |
|---|---|---|
| `lat` | Yes | Latitude |
| `lon` | Yes | Longitude |

```bash
# Current weather in Amsterdam
curl "http://localhost:8000/hazards/weather?lat=52.37&lon=4.90"
```

<details>
<summary>Example response</summary>

```json
{
  "time": "2024-05-15T14:00",
  "temperature_2m": 18.3,
  "relative_humidity_2m": 62,
  "wind_speed_10m": 4.1,
  "precipitation": 0.0,
  "weather_code": 2
}
```
</details>

---

### Aviation

#### Live Flights
```
GET /aviation/flights
```
Data source: [OpenSky Network](https://opensky-network.org/) — **no key needed, optional auth increases limits**

| Parameter | Required | Description |
|---|---|---|
| `lamin` | No | South latitude of bounding box |
| `lomin` | No | West longitude of bounding box |
| `lamax` | No | North latitude of bounding box |
| `lomax` | No | East longitude of bounding box |

```bash
# All flights over Western Europe
curl "http://localhost:8000/aviation/flights?lamin=36&lomin=-10&lamax=60&lomax=30"

# All flights worldwide (very large response)
curl "http://localhost:8000/aviation/flights"
```

<details>
<summary>Example response</summary>

```json
{
  "time": 1715600000,
  "count": 842,
  "flights": [
    {
      "icao24": "3c6444",
      "callsign": "DLH123 ",
      "origin_country": "Germany",
      "latitude": 50.12,
      "longitude": 8.56,
      "baro_altitude": 11277.6,
      "velocity": 248.3,
      "true_track": 270.5,
      "on_ground": false
    }
  ]
}
```
</details>

---

#### Single Flight by ICAO24
```
GET /aviation/flight/{icao24}
```

```bash
# Look up a specific aircraft by its ICAO24 hex code
curl "http://localhost:8000/aviation/flight/3c6444"
```

---

### Maritime *(requires AISHub account)*

#### Vessel Positions
```
GET /maritime/vessels
```
Data source: [AISHub](https://www.aishub.net/) — **free registration required**

| Parameter | Required | Description |
|---|---|---|
| `latmin` | Yes | South latitude |
| `latmax` | Yes | North latitude |
| `lonmin` | Yes | West longitude |
| `lonmax` | Yes | East longitude |
| `mmsi` | No | Filter by MMSI number |

```bash
# Vessels in the North Sea
curl "http://localhost:8000/maritime/vessels?latmin=51&latmax=57&lonmin=2&lonmax=8"

# Specific vessel by MMSI
curl "http://localhost:8000/maritime/vessels?latmin=51&latmax=57&lonmin=2&lonmax=8&mmsi=244810000"
```

---

### Markets

#### Stock Prices
```
GET /markets/stocks
```
Data source: Yahoo Finance via yfinance — **no API key needed**

| Parameter | Default | Description |
|---|---|---|
| `symbols` | `AAPL,MSFT,GOOGL,AMZN` | Comma-separated ticker symbols |

```bash
curl "http://localhost:8000/markets/stocks?symbols=AAPL,MSFT,TSLA"
```

<details>
<summary>Example response</summary>

```json
{
  "AAPL": {
    "symbol": "AAPL",
    "price": 189.3,
    "currency": "USD",
    "market_cap": 2940000000000,
    "52w_high": 199.6,
    "52w_low": 164.1
  }
}
```
</details>

---

#### Global Indices
```
GET /markets/indices
```
Returns S&P 500, Dow Jones, NASDAQ, DAX, FTSE 100, Nikkei 225, AEX.

```bash
curl "http://localhost:8000/markets/indices"
```

---

#### Cryptocurrency
```
GET /markets/crypto
```
Data source: [CoinGecko](https://www.coingecko.com/en/api) — **no API key needed**

| Parameter | Default | Description |
|---|---|---|
| `coins` | `bitcoin,ethereum,solana,ripple` | CoinGecko coin IDs |

```bash
curl "http://localhost:8000/markets/crypto?coins=bitcoin,ethereum,cardano"
```

<details>
<summary>Example response</summary>

```json
{
  "bitcoin": {
    "price_usd": 62450.0,
    "market_cap_usd": 1228000000000,
    "change_24h_pct": -1.34
  }
}
```
</details>

---

## API Keys

| Service | Endpoint(s) | Required | Sign up |
|---|---|---|---|
| NASA FIRMS | `/hazards/fires` | Yes | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov/api/area/) |
| AISHub | `/maritime/vessels` | Yes | [aishub.net/register](https://www.aishub.net/register) |
| OpenSky Network | `/aviation/*` | No (optional) | [opensky-network.org](https://opensky-network.org/login) |

All other endpoints (earthquakes, weather, stocks, indices, crypto) work without any API key.

---

## Project Structure

```
.
├── main.py              # FastAPI app + router registration
├── requirements.txt
├── .env.example         # Copy to .env and fill in your keys
└── routers/
    ├── hazards.py       # /hazards/earthquakes, /fires, /weather
    ├── aviation.py      # /aviation/flights, /flight/{icao24}
    ├── maritime.py      # /maritime/vessels
    └── markets.py       # /markets/stocks, /indices, /crypto
```
