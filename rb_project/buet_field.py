'''import folium
import json

# Sample data (extended with no-fly zones)
route_data = {
    "source_lat": 23.725394,
    "source_lon": 90.394234,
    "destination_lat": 23.726138,
    "destination_lon": 90.394920,
    "trip": {
        "legs": [
            {
                "description": "leg1",
                "summary": {
                    "has_time_restrictions": False,
                    "has_no_fly_zone": False,
                    "min_lat": 23.725394,
                    "min_lon": 90.394234,
                    "max_lat": 23.725235,
                    "max_lon": 90.394950,
                    "min_altitude": 200,
                    "max_altitude": 500,
                    "time": 5.0,
                    "length": 0.58,
                    "cost": 257.358
                }
            },
            {
                "description": "leg2",
                "summary": {
                    "has_time_restrictions": False,
                    "has_no_fly_zone": True,  # This leg has a no-fly zone!
                    "min_lat": 23.725235,
                    "min_lon": 90.394950,
                    "max_lat": 23.726138,
                    "max_lon": 90.394920,
                    "min_altitude": 300,
                    "max_altitude": 500,
                    "time": 5.0,
                    "length": 0.58,
                    "cost": 257.358
                }
            }
        ]
    },
    "no_fly_zones": [  # Added no-fly zones (circular & rectangular)
        {
            "type": "circle",
            "lat": 23.7258,
            "lon": 90.3946,
            "radius": 150,  # meters
            "reason": "Military Zone"
        },
        {
            "type": "rectangle",
            "min_lat": 23.7255,
            "min_lon": 90.3943,
            "max_lat": 23.7260,
            "max_lon": 90.3948,
            "reason": "Airport Restricted Area"
        }
    ]
}

# Create Folium map with satellite view
m = folium.Map(
    location=[route_data["source_lat"], route_data["source_lon"]],
    zoom_start=17,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery"
)

# Add source & destination markers
folium.Marker(
    [route_data["source_lat"], route_data["source_lon"]],
    popup="<b>Source</b>",
    icon=folium.Icon(color="green", icon="plane")
).add_to(m)

folium.Marker(
    [route_data["destination_lat"], route_data["destination_lon"]],
    popup="<b>Destination</b>",
    icon=folium.Icon(color="red", icon="flag")
).add_to(m)

# Draw the drone route legs
for leg in route_data["trip"]["legs"]:
    start_point = [leg["summary"]["min_lat"], leg["summary"]["min_lon"]]
    end_point = [leg["summary"]["max_lat"], leg["summary"]["max_lon"]]

    # Style legs differently if they pass through no-fly zones
    line_color = "red" if leg["summary"]["has_no_fly_zone"] else "blue"

    folium.PolyLine(
        [start_point, end_point],
        color=line_color,
        weight=3,
        opacity=0.8,
        popup=f"<b>{leg['description']}</b><br>Altitude: {leg['summary']['min_altitude']}-{leg['summary']['max_altitude']}m<br>Time: {leg['summary']['time']} min"
    ).add_to(m)

# Add no-fly zones
for zone in route_data["no_fly_zones"]:
    if zone["type"] == "circle":
        folium.Circle(
            location=[zone["lat"], zone["lon"]],
            radius=zone["radius"],
            color="red",
            fill=True,
            fill_opacity=0.2,
            popup=f"<b>NO-FLY ZONE</b><br>{zone['reason']}"
        ).add_to(m)
    elif zone["type"] == "rectangle":
        folium.Rectangle(
            bounds=[[zone["min_lat"], zone["min_lon"]], [zone["max_lat"], zone["max_lon"]]],
            color="red",
            fill=True,
            fill_opacity=0.2,
            popup=f"<b>NO-FLY ZONE</b><br>{zone['reason']}"
        ).add_to(m)

m.save("drone_route_with_no_fly_zones.html")
print("Interactive 2D map saved!")'''

import folium
import plotly.graph_objects as go
import pandas as pd

# ================== SAMPLE DATA ==================
route_data = {
    "source_lat": 23.725394,
    "source_lon": 90.394234,
    "destination_lat": 23.726138,
    "destination_lon": 90.394920,
    "trip": {
        "legs": [
            {
                "description": "leg1",
                "summary": {
                    "has_no_fly_zone": False,
                    "min_lat": 23.725394, "min_lon": 90.394234,
                    "max_lat": 23.725235, "max_lon": 90.394950,
                    "min_altitude": 200, "max_altitude": 500,
                }
            },
            {
                "description": "leg2",
                "summary": {
                    "has_no_fly_zone": True,  # This leg violates a no-fly zone!
                    "min_lat": 23.725235, "min_lon": 90.394950,
                    "max_lat": 23.726138, "max_lon": 90.394920,
                    "min_altitude": 300, "max_altitude": 500,
                }
            }
        ]
    },
    "no_fly_zones": [
        {
            "type": "circle",
            "lat": 23.7258, "lon": 90.3946,
            "radius": 150,  # meters
            "reason": "Government Building"
        },
        {
            "type": "rectangle",
            "min_lat": 23.7255, "min_lon": 90.3943,
            "max_lat": 23.7260, "max_lon": 90.3948,
            "reason": "Airport Restricted Airspace"
        }
    ]
}

# ================== 2D VISUALIZATION (FOLIUM) ==================
print("Generating 2D map...")

m = folium.Map(
    location=[route_data["source_lat"], route_data["source_lon"]],
    zoom_start=17,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery"
)

# Add route legs
for leg in route_data["trip"]["legs"]:
    start = [leg["summary"]["min_lat"], leg["summary"]["min_lon"]]
    end = [leg["summary"]["max_lat"], leg["summary"]["max_lon"]]
    color = "red" if leg["summary"]["has_no_fly_zone"] else "blue"
    folium.PolyLine(
        [start, end],
        color=color,
        weight=4,
        popup=f"{leg['description']} (Alt: {leg['summary']['min_altitude']}-{leg['summary']['max_altitude']}m)"
    ).add_to(m)

# Add no-fly zones
for zone in route_data["no_fly_zones"]:
    if zone["type"] == "circle":
        folium.Circle(
            location=[zone["lat"], zone["lon"]],
            radius=zone["radius"],
            color="red",
            fill=True,
            fill_opacity=0.3,
            popup=f"NO-FLY: {zone['reason']}"
        ).add_to(m)
    elif zone["type"] == "rectangle":
        folium.Rectangle(
            bounds=[[zone["min_lat"], zone["min_lon"]], [zone["max_lat"], zone["max_lon"]]],
            color="red",
            fill=True,
            fill_opacity=0.3,
            popup=f"NO-FLY: {zone['reason']}"
        ).add_to(m)

# Add markers
folium.Marker(
    [route_data["source_lat"], route_data["source_lon"]],
    popup="START",
    icon=folium.Icon(color="green", icon="play")
).add_to(m)

folium.Marker(
    [route_data["destination_lat"], route_data["destination_lon"]],
    popup="END",
    icon=folium.Icon(color="red", icon="stop")
).add_to(m)

m.save("drone_route_2d2.html")
print("✅ 2D map saved to drone_route_2d.html")

# ================== 3D VISUALIZATION (PLOTLY) ==================
print("Generating 3D visualization...")

# Prepare route data for 3D
lats, lons, alts = [], [], []
for leg in route_data["trip"]["legs"]:
    lats.extend([leg["summary"]["min_lat"], leg["summary"]["max_lat"]])
    lons.extend([leg["summary"]["min_lon"], leg["summary"]["max_lon"]])
    alts.extend([leg["summary"]["min_altitude"], leg["summary"]["max_altitude"]])

# Create 3D figure
fig = go.Figure()

# Add drone route (3D line)
fig.add_trace(go.Scatter3d(
    x=lons, y=lats, z=alts,
    mode="lines+markers",
    line=dict(color="blue", width=8),
    marker=dict(size=4, color=alts, colorscale="Viridis"),
    name="Drone Path"
))

# Add no-fly zones (as 3D cylinders/boxes)
for zone in route_data["no_fly_zones"]:
    if zone["type"] == "circle":
        fig.add_trace(go.Mesh3d(
            x=[zone["lon"]] * 4,
            y=[zone["lat"]] * 4,
            z=[0, 1000, 1000, 0],  # Cylinder from ground to 1000m
            opacity=0.3,
            color="red",
            name=f"No-Fly: {zone['reason']}"
        ))
    elif zone["type"] == "rectangle":
        fig.add_trace(go.Mesh3d(
            x=[zone["min_lon"], zone["max_lon"], zone["max_lon"], zone["min_lon"]],
            y=[zone["min_lat"], zone["min_lat"], zone["max_lat"], zone["max_lat"]],
            z=[0, 0, 1000, 1000],  # Box from ground to 1000m
            opacity=0.3,
            color="red",
            name=f"No-Fly: {zone['reason']}"
        ))

# Configure layout
fig.update_layout(
    scene=dict(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        zaxis_title="Altitude (m)",
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))  # Adjust 3D view angle
    ),
    title="3D Drone Route with No-Fly Zones"
)

fig.write_html("drone_route_3d2.html")
print("✅ 3D visualization saved to drone_route_3d.html")

print("\nOpen the generated HTML files in a browser to view the maps!")