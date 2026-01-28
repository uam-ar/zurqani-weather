#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

# =========================
# CONFIG (EDIT THIS)
# =========================
PLACE_NAME = "Monticello, AR"
LAT = 33.6289
LON = -91.7909
TZ = "America/Chicago"  # Open-Meteo timezone for daily dates
# =========================

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max"
    f"&timezone={TZ}"
)

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "zurqani-weather (github pages widget)"
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)

def safe_get(dct, *keys, default=None):
    cur = dct
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def main():
    data = fetch_json(OPEN_METEO_URL)

    current = safe_get(data, "current", default={}) or {}
    daily = safe_get(data, "daily", default={}) or {}

    # Build daily array for 7 days
    dates = daily.get("time", []) or []
    tmax = daily.get("temperature_2m_max", []) or []
    tmin = daily.get("temperature_2m_min", []) or []
    wcode = daily.get("weather_code", []) or []
    pprob = daily.get("precipitation_probability_max", []) or []

    daily_out = []
    for i in range(min(7, len(dates))):
        daily_out.append({
            "date": dates[i],
            "tmax_c": tmax[i] if i < len(tmax) else None,
            "tmin_c": tmin[i] if i < len(tmin) else None,
            "weather_code": wcode[i] if i < len(wcode) else None,
            "precip_prob_pct": pprob[i] if i < len(pprob) else None,
        })

    out = {
        "meta": {
            "place_name": PLACE_NAME,
            "lat": LAT,
            "lon": LON,
            "timezone": TZ,
            "source": "open-meteo",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
        },
        "current": {
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
        },
        "daily": daily_out
    }

    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote weather.json")

if __name__ == "__main__":
    main()
