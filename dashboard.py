import asyncio
from datetime import datetime
from typing import Any

import httpx
import streamlit as st
from streamlit_folium import st_folium

from api import fetch_multi_model_comparison, fetch_radar_timestamps, get_all_radar_frames
from charts import (
    create_multi_variable_dashboard,
    create_precipitation_comparison_chart,
    create_temperature_comparison_chart,
    create_wind_comparison_chart,
)
from maps import create_alerts_map, create_forecast_map, create_location_picker_map, create_radar_map

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}


async def make_nws_request(url: str) -> dict[str, Any] | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


async def fetch_alerts(state: str) -> list[dict] | None:
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return None
    return data["features"]


async def fetch_forecast(latitude: float, longitude: float) -> list[dict] | None:
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data:
        return None
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return None
    return forecast_data["properties"]["periods"]


# Initialize session state for selected locations
if "forecast_lat" not in st.session_state:
    st.session_state.forecast_lat = 40.7128
if "forecast_lon" not in st.session_state:
    st.session_state.forecast_lon = -74.0060
if "model_lat" not in st.session_state:
    st.session_state.model_lat = 40.7128
if "model_lon" not in st.session_state:
    st.session_state.model_lon = -74.0060
if "radar_lat" not in st.session_state:
    st.session_state.radar_lat = 39.8283
if "radar_lon" not in st.session_state:
    st.session_state.radar_lon = -98.5795

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")
st.title("Weather Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Weather Alerts", "Forecast", "Model Comparison", "Radar"])

# Tab 1: Weather Alerts
with tab1:
    st.header("Weather Alerts by State")
    state_code = st.selectbox(
        "Select a state",
        options=list(US_STATES.keys()),
        format_func=lambda x: f"{US_STATES[x]} ({x})",
    )

    if st.button("Get Alerts", key="alerts_btn"):
        with st.spinner("Fetching alerts..."):
            alerts = asyncio.run(fetch_alerts(state_code))

        if alerts is None:
            st.error("Unable to fetch alerts. Please try again.")
        elif len(alerts) == 0:
            st.success(f"No active alerts for {US_STATES[state_code]}")
        else:
            st.warning(f"{len(alerts)} active alert(s) for {US_STATES[state_code]}")

            col_map, col_list = st.columns([2, 1])
            with col_map:
                alerts_map = create_alerts_map(alerts, state_code)
                st_folium(alerts_map, width=700, height=500, returned_objects=[])

            with col_list:
                for alert in alerts:
                    props = alert["properties"]
                    with st.expander(
                        f"{props.get('event', 'Unknown Event')} - {props.get('severity', 'Unknown')}"
                    ):
                        st.markdown(f"**Area:** {props.get('areaDesc', 'Unknown')}")
                        st.markdown(f"**Severity:** {props.get('severity', 'Unknown')}")
                        st.markdown(f"**Description:**\n{props.get('description', 'No description')}")
                        if props.get("instruction"):
                            st.markdown(f"**Instructions:**\n{props.get('instruction')}")

# Tab 2: Forecast
with tab2:
    st.header("Weather Forecast")
    st.markdown("**Click on the map to select a location**, or enter coordinates manually.")

    col_map, col_controls = st.columns([2, 1])

    with col_map:
        forecast_picker = create_location_picker_map(
            center_lat=st.session_state.forecast_lat,
            center_lon=st.session_state.forecast_lon,
            zoom=5,
            selected_lat=st.session_state.forecast_lat,
            selected_lon=st.session_state.forecast_lon,
        )
        map_data = st_folium(
            forecast_picker,
            width=600,
            height=400,
            key="forecast_map_picker",
        )

        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.forecast_lat = clicked["lat"]
            st.session_state.forecast_lon = clicked["lng"]
            st.rerun()

    with col_controls:
        st.subheader("Selected Location")
        new_lat = st.number_input(
            "Latitude",
            value=st.session_state.forecast_lat,
            format="%.4f",
            key="forecast_lat_input",
        )
        new_lon = st.number_input(
            "Longitude",
            value=st.session_state.forecast_lon,
            format="%.4f",
            key="forecast_lon_input",
        )

        if new_lat != st.session_state.forecast_lat or new_lon != st.session_state.forecast_lon:
            st.session_state.forecast_lat = new_lat
            st.session_state.forecast_lon = new_lon
            st.rerun()

        st.caption("NWS forecasts only work for US locations")

        if st.button("Get Forecast", key="forecast_btn", type="primary"):
            with st.spinner("Fetching forecast..."):
                periods = asyncio.run(
                    fetch_forecast(st.session_state.forecast_lat, st.session_state.forecast_lon)
                )

            if periods is None:
                st.error("Unable to fetch forecast. Make sure coordinates are within the US.")
            else:
                st.session_state.forecast_data = periods

    if "forecast_data" in st.session_state and st.session_state.forecast_data:
        st.divider()
        st.subheader(f"Forecast for ({st.session_state.forecast_lat:.4f}, {st.session_state.forecast_lon:.4f})")
        for period in st.session_state.forecast_data[:5]:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(
                        label=period["name"],
                        value=f"{period['temperature']}°{period['temperatureUnit']}",
                        delta=f"{period['windSpeed']} {period['windDirection']}",
                    )
                with col2:
                    st.write(period["detailedForecast"])
                st.divider()

# Tab 3: Model Comparison
with tab3:
    st.header("Weather Model Comparison")
    st.markdown("Compare **GFS** (US) and **ECMWF** (European) models. **Click the map to select a location.**")

    col_map, col_controls = st.columns([2, 1])

    with col_map:
        model_picker = create_location_picker_map(
            center_lat=st.session_state.model_lat,
            center_lon=st.session_state.model_lon,
            zoom=4,
            selected_lat=st.session_state.model_lat,
            selected_lon=st.session_state.model_lon,
        )
        map_data = st_folium(
            model_picker,
            width=600,
            height=400,
            key="model_map_picker",
        )

        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.model_lat = clicked["lat"]
            st.session_state.model_lon = clicked["lng"]
            st.rerun()

    with col_controls:
        st.subheader("Selected Location")
        new_lat = st.number_input(
            "Latitude",
            value=st.session_state.model_lat,
            format="%.4f",
            key="model_lat_input",
        )
        new_lon = st.number_input(
            "Longitude",
            value=st.session_state.model_lon,
            format="%.4f",
            key="model_lon_input",
        )

        if new_lat != st.session_state.model_lat or new_lon != st.session_state.model_lon:
            st.session_state.model_lat = new_lat
            st.session_state.model_lon = new_lon
            st.rerun()

        st.caption("Data from Open-Meteo API (works globally)")

        if st.button("Compare Models", key="compare_btn", type="primary"):
            with st.spinner("Fetching model data from GFS and ECMWF..."):
                model_data = asyncio.run(
                    fetch_multi_model_comparison(st.session_state.model_lat, st.session_state.model_lon)
                )

            gfs_data = model_data.get("gfs")
            ecmwf_data = model_data.get("ecmwf")

            if not gfs_data and not ecmwf_data:
                st.error("Unable to fetch model data. Please try again.")
            else:
                st.session_state.gfs_data = gfs_data
                st.session_state.ecmwf_data = ecmwf_data

    if "gfs_data" in st.session_state or "ecmwf_data" in st.session_state:
        gfs_data = st.session_state.get("gfs_data")
        ecmwf_data = st.session_state.get("ecmwf_data")

        if gfs_data or ecmwf_data:
            st.divider()
            st.subheader("Multi-Variable Dashboard")
            dashboard_fig = create_multi_variable_dashboard(gfs_data, ecmwf_data)
            st.plotly_chart(dashboard_fig, use_container_width=True)

            var_tab1, var_tab2, var_tab3 = st.tabs(["Temperature", "Precipitation", "Wind"])

            with var_tab1:
                temp_fig = create_temperature_comparison_chart(gfs_data, ecmwf_data)
                st.plotly_chart(temp_fig, use_container_width=True)

            with var_tab2:
                precip_fig = create_precipitation_comparison_chart(gfs_data, ecmwf_data)
                st.plotly_chart(precip_fig, use_container_width=True)

            with var_tab3:
                wind_fig = create_wind_comparison_chart(gfs_data, ecmwf_data)
                st.plotly_chart(wind_fig, use_container_width=True)

# Tab 4: Radar
with tab4:
    st.header("Live Radar")
    st.markdown("**Click on the map to recenter.** Radar imagery powered by RainViewer.")

    col_controls, col_zoom = st.columns([2, 1])

    with col_controls:
        st.subheader("Map Center")
        col1, col2 = st.columns(2)
        with col1:
            new_lat = st.number_input(
                "Latitude",
                value=st.session_state.radar_lat,
                format="%.4f",
                key="radar_lat_input",
            )
        with col2:
            new_lon = st.number_input(
                "Longitude",
                value=st.session_state.radar_lon,
                format="%.4f",
                key="radar_lon_input",
            )

        if new_lat != st.session_state.radar_lat or new_lon != st.session_state.radar_lon:
            st.session_state.radar_lat = new_lat
            st.session_state.radar_lon = new_lon

    with col_zoom:
        radar_zoom = st.slider("Zoom Level", min_value=3, max_value=10, value=5)

    if st.button("Load Radar", key="radar_btn", type="primary"):
        with st.spinner("Fetching radar data..."):
            radar_data = asyncio.run(fetch_radar_timestamps())

        if not radar_data:
            st.error("Unable to fetch radar data. Please try again.")
        else:
            st.session_state.radar_frames = get_all_radar_frames(radar_data)

    if "radar_frames" in st.session_state and st.session_state.radar_frames:
        frames = st.session_state.radar_frames

        frame_idx = st.slider(
            "Radar Frame (drag to animate)",
            min_value=0,
            max_value=len(frames) - 1,
            value=len(frames) - 1,
            key="radar_frame_slider",
        )

        selected_frame = frames[frame_idx]
        frame_time = datetime.fromtimestamp(selected_frame["time"])
        st.caption(f"Radar Time: {frame_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        radar_map = create_radar_map(
            center_lat=st.session_state.radar_lat,
            center_lon=st.session_state.radar_lon,
            zoom=radar_zoom,
            radar_tile_url=selected_frame["url"],
            selected_lat=st.session_state.radar_lat,
            selected_lon=st.session_state.radar_lon,
        )

        map_data = st_folium(
            radar_map,
            width=None,
            height=600,
            key="radar_map_display",
        )

        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.radar_lat = clicked["lat"]
            st.session_state.radar_lon = clicked["lng"]
            st.rerun()
    else:
        st.info("Click 'Load Radar' to view radar imagery. You can then click on the map to recenter.")
