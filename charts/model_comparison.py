from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_temperature_comparison_chart(
    gfs_data: dict[str, Any] | None,
    ecmwf_data: dict[str, Any] | None,
) -> go.Figure:
    """Create a Plotly chart comparing temperature forecasts between models."""
    fig = go.Figure()

    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Scatter(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["temperature_2m"],
                mode="lines",
                name="GFS",
                line=dict(color="#1f77b4", width=2),
            )
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Scatter(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["temperature_2m"],
                mode="lines",
                name="ECMWF",
                line=dict(color="#ff7f0e", width=2),
            )
        )

    fig.update_layout(
        title="Temperature Forecast Comparison (GFS vs ECMWF)",
        xaxis_title="Time",
        yaxis_title="Temperature (C)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode="x unified",
    )

    return fig


def create_precipitation_comparison_chart(
    gfs_data: dict[str, Any] | None,
    ecmwf_data: dict[str, Any] | None,
) -> go.Figure:
    """Create a Plotly chart comparing precipitation forecasts between models."""
    fig = go.Figure()

    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Bar(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["precipitation"],
                name="GFS",
                marker_color="#1f77b4",
                opacity=0.7,
            )
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Bar(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["precipitation"],
                name="ECMWF",
                marker_color="#ff7f0e",
                opacity=0.7,
            )
        )

    fig.update_layout(
        title="Precipitation Forecast Comparison (GFS vs ECMWF)",
        xaxis_title="Time",
        yaxis_title="Precipitation (mm)",
        barmode="group",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode="x unified",
    )

    return fig


def create_wind_comparison_chart(
    gfs_data: dict[str, Any] | None,
    ecmwf_data: dict[str, Any] | None,
) -> go.Figure:
    """Create a Plotly chart comparing wind speed forecasts between models."""
    fig = go.Figure()

    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Scatter(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["wind_speed_10m"],
                mode="lines",
                name="GFS",
                line=dict(color="#1f77b4", width=2),
                fill="tozeroy",
                fillcolor="rgba(31, 119, 180, 0.2)",
            )
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Scatter(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["wind_speed_10m"],
                mode="lines",
                name="ECMWF",
                line=dict(color="#ff7f0e", width=2),
                fill="tozeroy",
                fillcolor="rgba(255, 127, 14, 0.2)",
            )
        )

    fig.update_layout(
        title="Wind Speed Forecast Comparison (GFS vs ECMWF)",
        xaxis_title="Time",
        yaxis_title="Wind Speed (km/h)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode="x unified",
    )

    return fig


def create_multi_variable_dashboard(
    gfs_data: dict[str, Any] | None,
    ecmwf_data: dict[str, Any] | None,
) -> go.Figure:
    """Create a comprehensive dashboard with subplots for multiple weather variables."""
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Temperature (C)",
            "Precipitation (mm)",
            "Wind Speed (km/h)",
            "Humidity (%)",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # Temperature (row 1, col 1)
    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Scatter(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["temperature_2m"],
                mode="lines",
                name="GFS",
                line=dict(color="#1f77b4"),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Scatter(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["temperature_2m"],
                mode="lines",
                name="ECMWF",
                line=dict(color="#ff7f0e"),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    # Precipitation (row 1, col 2)
    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Bar(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["precipitation"],
                name="GFS Precip",
                marker_color="#1f77b4",
                opacity=0.7,
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Bar(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["precipitation"],
                name="ECMWF Precip",
                marker_color="#ff7f0e",
                opacity=0.7,
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    # Wind Speed (row 2, col 1)
    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Scatter(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["wind_speed_10m"],
                mode="lines",
                name="GFS Wind",
                line=dict(color="#1f77b4"),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Scatter(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["wind_speed_10m"],
                mode="lines",
                name="ECMWF Wind",
                line=dict(color="#ff7f0e"),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # Humidity (row 2, col 2)
    if gfs_data and "hourly" in gfs_data:
        fig.add_trace(
            go.Scatter(
                x=gfs_data["hourly"]["time"],
                y=gfs_data["hourly"]["relative_humidity_2m"],
                mode="lines",
                name="GFS Humidity",
                line=dict(color="#1f77b4"),
                showlegend=False,
            ),
            row=2,
            col=2,
        )

    if ecmwf_data and "hourly" in ecmwf_data:
        fig.add_trace(
            go.Scatter(
                x=ecmwf_data["hourly"]["time"],
                y=ecmwf_data["hourly"]["relative_humidity_2m"],
                mode="lines",
                name="ECMWF Humidity",
                line=dict(color="#ff7f0e"),
                showlegend=False,
            ),
            row=2,
            col=2,
        )

    fig.update_layout(
        height=600,
        title_text="Weather Model Comparison Dashboard",
        showlegend=True,
        legend=dict(yanchor="top", y=1.02, xanchor="left", x=0.01, orientation="h"),
    )

    return fig
