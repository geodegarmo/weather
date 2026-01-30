import folium

# US state center coordinates for default map views
STATE_CENTERS = {
    "AL": (32.806671, -86.791130),
    "AK": (61.370716, -152.404419),
    "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123),
    "CA": (36.116203, -119.681564),
    "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371),
    "DE": (39.318523, -75.507141),
    "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074),
    "HI": (21.094318, -157.498337),
    "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137),
    "IN": (39.849426, -86.258278),
    "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486),
    "KY": (37.668140, -84.670067),
    "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927),
    "MD": (39.063946, -76.802101),
    "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095),
    "MN": (45.694454, -93.900192),
    "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368),
    "MT": (46.921925, -110.454353),
    "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374),
    "NH": (43.452492, -71.563896),
    "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482),
    "NY": (42.165726, -74.948051),
    "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012),
    "OH": (40.388783, -82.764915),
    "OK": (35.565342, -96.928917),
    "OR": (44.572021, -122.070938),
    "PA": (40.590752, -77.209755),
    "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007),
    "SD": (44.299782, -99.438828),
    "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461),
    "UT": (40.150032, -111.862434),
    "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968),
    "WA": (47.400902, -121.490494),
    "WV": (38.491226, -80.954453),
    "WI": (44.268543, -89.616508),
    "WY": (42.755966, -107.302490),
}

SEVERITY_COLORS = {
    "Extreme": "#FF0000",
    "Severe": "#FF6600",
    "Moderate": "#FFCC00",
    "Minor": "#00FF00",
    "Unknown": "#808080",
}


def create_alerts_map(alerts: list[dict], state_code: str) -> folium.Map:
    """
    Create a Folium map displaying weather alerts as GeoJSON polygons.

    Args:
        alerts: List of alert features from NWS API (GeoJSON features)
        state_code: Two-letter state code for centering the map

    Returns:
        Folium Map object
    """
    center = STATE_CENTERS.get(state_code, (39.8283, -98.5795))
    m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")

    for alert in alerts:
        props = alert.get("properties", {})
        geometry = alert.get("geometry")

        severity = props.get("severity", "Unknown")
        color = SEVERITY_COLORS.get(severity, "#808080")
        event = props.get("event", "Unknown Event")
        area = props.get("areaDesc", "Unknown Area")

        popup_html = f"""
        <b>{event}</b><br>
        <b>Severity:</b> {severity}<br>
        <b>Area:</b> {area}
        """

        if geometry and geometry.get("type") in ["Polygon", "MultiPolygon"]:
            folium.GeoJson(
                geometry,
                style_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": c,
                    "weight": 2,
                    "fillOpacity": 0.4,
                },
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(m)
        else:
            folium.Marker(
                location=center,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
            ).add_to(m)

    return m


def create_forecast_map(
    latitude: float, longitude: float, forecast_data: list[dict] | None = None
) -> folium.Map:
    """
    Create a Folium map with the forecast location marked.

    Args:
        latitude: Forecast location latitude
        longitude: Forecast location longitude
        forecast_data: Optional forecast periods to show in popup

    Returns:
        Folium Map object
    """
    m = folium.Map(location=[latitude, longitude], zoom_start=10, tiles="CartoDB positron")

    popup_html = f"<b>Forecast Location</b><br>Lat: {latitude:.4f}<br>Lon: {longitude:.4f}"

    if forecast_data and len(forecast_data) > 0:
        first_period = forecast_data[0]
        popup_html += f"""<br><br>
        <b>{first_period.get('name', 'Current')}:</b><br>
        {first_period.get('temperature', 'N/A')}&deg;{first_period.get('temperatureUnit', 'F')}<br>
        {first_period.get('shortForecast', '')}
        """

    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue", icon="cloud", prefix="fa"),
    ).add_to(m)

    return m


def create_location_picker_map(
    center_lat: float = 39.8283,
    center_lon: float = -98.5795,
    zoom: int = 4,
    selected_lat: float | None = None,
    selected_lon: float | None = None,
    tiles: str = "CartoDB positron",
) -> folium.Map:
    """
    Create a clickable Folium map for selecting a location.

    Args:
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom: Initial zoom level
        selected_lat: Currently selected latitude (shows marker)
        selected_lon: Currently selected longitude (shows marker)
        tiles: Map tile style

    Returns:
        Folium Map object that captures click events
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=tiles,
    )

    if selected_lat is not None and selected_lon is not None:
        folium.Marker(
            location=[selected_lat, selected_lon],
            popup=f"Selected: {selected_lat:.4f}, {selected_lon:.4f}",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(m)

    return m


def create_radar_map(
    center_lat: float = 39.8283,
    center_lon: float = -98.5795,
    zoom: int = 4,
    radar_tile_url: str | None = None,
    selected_lat: float | None = None,
    selected_lon: float | None = None,
) -> folium.Map:
    """
    Create a Folium map with optional radar overlay.

    Args:
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom: Initial zoom level
        radar_tile_url: RainViewer tile URL template
        selected_lat: Selected point latitude (shows marker)
        selected_lon: Selected point longitude (shows marker)

    Returns:
        Folium Map object with radar overlay
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
    )

    if radar_tile_url:
        folium.TileLayer(
            tiles=radar_tile_url,
            attr="RainViewer",
            name="Radar",
            overlay=True,
            control=True,
            opacity=0.7,
        ).add_to(m)

    if selected_lat is not None and selected_lon is not None:
        folium.Marker(
            location=[selected_lat, selected_lon],
            popup=f"Selected: {selected_lat:.4f}, {selected_lon:.4f}",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(m)

    folium.LayerControl().add_to(m)

    return m
