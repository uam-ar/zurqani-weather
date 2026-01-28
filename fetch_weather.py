#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

# =========================
# CONFIG (EDIT THESE)
# =========================
LAT = 42.2814      # <-- campus latitude
LON = -85.5889     # <-- campus longitude
TZ  = "America/Chicago"  # <-- campus timezone (IANA)
DAYS = 7           # forecast length

# Open-Meteo: current + hourly + daily in one call (no API key)
URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    f"&timezone={TZ}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,weather_code"
    "&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code"
    f"&forecast_days={DAYS}"
)

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "UniversityWeatherBot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def compact_payload(raw: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()

    current = raw.get("current", {})
    daily = raw.get("daily", {})

    # Build daily array
    times = daily.get("time", []) or []
    tmax  = daily.get("temperature_2m_max", []) or []
    tmin  = daily.get("temperature_2m_min", []) or []
    pprob = daily.get("precipitation_probability_max", []) or []
    psum  = daily.get("precipitation_sum", []) or []
    wcode = daily.get("weather_code", []) or []

    days = []
    for i in range(min(len(times), len(tmax), len(tmin))):
        days.append({
            "date": times[i],
            "tmax_c": tmax[i],
            "tmin_c": tmin[i],
            "precip_prob_pct": pprob[i] if i < len(pprob) else None,
            "precip_sum_mm": psum[i] if i < len(psum) else None,
            "weather_code": wcode[i] if i < len(wcode) else None,
        })

    payload = {
        "meta": {
            "source": "open-meteo",
            "lat": LAT,
            "lon": LON,
            "timezone": TZ,
            "generated_utc": now
        },
        "current": {
            "time": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
            "weather_code": current.get("weather_code"),
        },
        "daily": days
    }
    return payload

def main():
    raw = fetch_json(URL)
    payload = compact_payload(raw)

    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("Wrote weather.json")

if __name__ == "__main__":
    main()
