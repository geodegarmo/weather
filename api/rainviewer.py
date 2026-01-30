from typing import Any

import httpx

RAINVIEWER_API = "https://api.rainviewer.com/public/weather-maps.json"


async def fetch_radar_timestamps() -> dict[str, Any] | None:
    """
    Fetch available radar timestamps from RainViewer API.

    Returns:
        API response with radar frame timestamps and tile URLs
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RAINVIEWER_API, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def get_radar_tile_url(radar_data: dict, frame_index: int = -1) -> str | None:
    """
    Get the tile URL for a specific radar frame.

    Args:
        radar_data: Response from fetch_radar_timestamps()
        frame_index: Index of radar frame (-1 for most recent)

    Returns:
        Tile URL template string for use with Folium
    """
    try:
        radar_frames = radar_data.get("radar", {}).get("past", [])
        if not radar_frames:
            return None

        frame = radar_frames[frame_index]
        path = frame["path"]
        host = radar_data.get("host", "https://tilecache.rainviewer.com")

        return f"{host}{path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
    except (KeyError, IndexError):
        return None


def get_all_radar_frames(radar_data: dict) -> list[dict]:
    """
    Get all available radar frames with timestamps and tile URLs.

    Returns:
        List of dicts with 'time' (unix timestamp) and 'url' keys
    """
    frames = []
    try:
        host = radar_data.get("host", "https://tilecache.rainviewer.com")
        radar_frames = radar_data.get("radar", {}).get("past", [])

        for frame in radar_frames:
            path = frame["path"]
            time = frame["time"]
            url = f"{host}{path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
            frames.append({"time": time, "url": url})
    except (KeyError, TypeError):
        pass

    return frames
