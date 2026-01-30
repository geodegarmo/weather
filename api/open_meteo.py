from typing import Any

import httpx

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"


async def fetch_model_forecast(
    latitude: float,
    longitude: float,
    model: str = "gfs_seamless",
    variables: list[str] | None = None,
) -> dict[str, Any] | None:
    """
    Fetch forecast data from Open-Meteo API for a specific model.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        model: Weather model - "gfs_seamless" or "ecmwf_ifs"
        variables: List of weather variables to fetch

    Returns:
        API response dict or None on error
    """
    if variables is None:
        variables = [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "weather_code",
        ]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "models": model,
        "hourly": ",".join(variables),
        "timezone": "auto",
        "forecast_days": 7,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPEN_METEO_BASE, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


async def fetch_multi_model_comparison(
    latitude: float,
    longitude: float,
    variables: list[str] | None = None,
) -> dict[str, dict[str, Any] | None]:
    """
    Fetch forecasts from both GFS and ECMWF models for comparison.

    Returns:
        Dict with "gfs" and "ecmwf" keys containing respective forecasts
    """
    gfs_data = await fetch_model_forecast(latitude, longitude, "gfs_seamless", variables)
    ecmwf_data = await fetch_model_forecast(latitude, longitude, "ecmwf_ifs", variables)

    return {
        "gfs": gfs_data,
        "ecmwf": ecmwf_data,
    }
