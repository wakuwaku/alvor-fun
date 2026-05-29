# Global Intelligence API

A FastAPI REST API that aggregates real-time global intelligence data — aviation, maritime, natural hazards, and financial markets — inspired by [osirisai.live](https://www.osirisai.live).

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```env
NASA_FIRMS_API_KEY=your_key_here
AISSTREAM_API_KEY=your_key_here
OPENSKY_USERNAME=your_username_here   # optional
OPENSKY_PASSWORD=your_password_here   # optional
```

### 3. Run the server

```bash
uvicorn main:app --reload --port 8004
```

The API is available at `http://localhost:8004`.  
Interactive docs (Swagger UI): `http://localhost:8004/docs`

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
curl "http://localhost:8004/hazards/earthquakes?min_magnitude=6&days=30"
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
Data source: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/area/) — get a free key at [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov/api/area/)

| Parameter | Default | Description |
|---|---|---|
| `days` | `1` | Days to look back (1–10) |
| `region` | `world` | Region: `world`, `USA`, `Canada`, `Europe`, etc. |

```bash
curl "http://localhost:8004/hazards/fires?region=Europe&days=1"
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
curl "http://localhost:8004/hazards/weather?lat=52.37&lon=4.90"
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
Data source: [OpenSky Network](https://opensky-network.org/) — **no key needed, optional credentials reduce rate limiting**

| Parameter | Required | Description |
|---|---|---|
| `lamin` | No | South latitude of bounding box |
| `lomin` | No | West longitude of bounding box |
| `lamax` | No | North latitude of bounding box |
| `lomax` | No | East longitude of bounding box |

```bash
# Flights over Western Europe
curl "http://localhost:8004/aviation/flights?lamin=36&lomin=-10&lamax=60&lomax=30"

# All flights worldwide (large response)
curl "http://localhost:8004/aviation/flights"
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
curl "http://localhost:8004/aviation/flight/3c6444"
```

---

### Maritime *(requires aisstream.io API key)*

#### Vessel Positions
```
GET /maritime/vessels
```
Data source: [aisstream.io](https://aisstream.io) — free key, email signup required

Opens a WebSocket stream, collects vessel positions within the bounding box for `timeout` seconds, then returns the results.

| Parameter | Required | Default | Description |
|---|---|---|---|
| `latmin` | Yes | — | South latitude |
| `latmax` | Yes | — | North latitude |
| `lonmin` | Yes | — | West longitude |
| `lonmax` | Yes | — | East longitude |
| `mmsi` | No | — | Filter by MMSI number |
| `limit` | No | `50` | Max vessels to collect (max 500) |
| `timeout` | No | `8` | Seconds to collect data (max 30) |

```bash
# Vessels in the North Sea
curl "http://localhost:8004/maritime/vessels?latmin=51&latmax=57&lonmin=2&lonmax=8"

# Specific vessel by MMSI
curl "http://localhost:8004/maritime/vessels?latmin=51&latmax=57&lonmin=2&lonmax=8&mmsi=244810000"
```

<details>
<summary>Example response</summary>

```json
{
  "count": 50,
  "vessels": [
    {
      "mmsi": "244690666",
      "name": "BRABANT",
      "latitude": 52.04367,
      "longitude": 5.10149,
      "speed_knots": 3.2,
      "course": 185.0,
      "heading": 183,
      "nav_status": 0,
      "time_utc": "2024-05-15 14:00:00"
    }
  ]
}
```
</details>

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
curl "http://localhost:8004/markets/stocks?symbols=AAPL,MSFT,TSLA"
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
Returns live prices for S&P 500, Dow Jones, NASDAQ, DAX, FTSE 100, Nikkei 225, AEX. **No API key needed.**

```bash
curl "http://localhost:8004/markets/indices"
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
curl "http://localhost:8004/markets/crypto?coins=bitcoin,ethereum,cardano"
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
| aisstream.io | `/maritime/vessels` | Yes | [aisstream.io](https://aisstream.io) |
| OpenSky Network | `/aviation/*` | No (optional) | [opensky-network.org](https://opensky-network.org/login) |

All other endpoints (earthquakes, weather, stocks, indices, crypto) work without any API key.

---

## Project Structure

```
.
├── main.py              # FastAPI app + router registration
├── requirements.txt
├── .env                 # API keys (create this file)
└── routers/
    ├── hazards.py       # /hazards/earthquakes, /fires, /weather
    ├── aviation.py      # /aviation/flights, /flight/{icao24}
    ├── maritime.py      # /maritime/vessels  (aisstream.io WebSocket)
    └── markets.py       # /markets/stocks, /indices, /crypto
```
