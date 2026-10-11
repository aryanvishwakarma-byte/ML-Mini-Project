import folium
import matplotlib.pyplot as plt
import numpy as np
import os

CLUSTER_COLORS = [
    "#E63946", # Red
    "#1D3557", # Deep Blue
    "#2A9D8F", # Teal / Green
    "#F4A261", # Orange
    "#9B5DE5", # Purple
    "#00BBF9", # Cyan
    "#E76F51", # Coral
    "#588157"  # Olive Green
]

CLUSTER_COLOR_NAMES = [
    ("🔴 Red", "#E63946"),
    ("🔵 Deep Blue", "#1D3557"),
    ("🟢 Teal Green", "#2A9D8F"),
    ("🟠 Orange", "#F4A261"),
    ("🟣 Purple", "#9B5DE5"),
    ("🔷 Cyan", "#00BBF9"),
    ("🔶 Coral", "#E76F51"),
    ("🟩 Olive", "#588157")
]

def get_cluster_color(cluster_id):
    """Returns hexadecimal color code for a given cluster."""
    if cluster_id == -1:
        return "#7F8C8D" # Grey for noise/unassigned
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

def get_cluster_color_label(cluster_id):
    """Returns human-readable emoji and color name for a given cluster."""
    if cluster_id == -1:
        return "⚪ Grey (Noise/Outliers)"
    name, _ = CLUSTER_COLOR_NAMES[cluster_id % len(CLUSTER_COLOR_NAMES)]
    return name


def generate_interactive_map(cluster_results, depot_info, output_html="outputs/mumbai_route_map.html"):
    """
    Builds a Leaflet/Folium map showing clusters, depots, delivery pins, and shortest paths.
    """
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    
    depot_lat = depot_info["latitude"].values[0]
    depot_lon = depot_info["longitude"].values[0]
    
    # Initialize Folium Map centered on Mumbai
    m = folium.Map(
        location=[depot_lat, depot_lon],
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    
    # Add Depot Marker
    folium.Marker(
        location=[depot_lat, depot_lon],
        popup=f"<b>MAIN CENTRAL DEPOT</b><br>{depot_info['customer_name'].values[0]}<br>BKC Hub",
        tooltip="Central Depot (BKC)",
        icon=folium.Icon(color="black", icon="home", prefix="fa")
    ).add_to(m)
    
    # Add each cluster's delivery stops and route lines
    for cluster_id, res in cluster_results.items():
        color = get_cluster_color(cluster_id)
        df_route = res["ordered_nodes_df"]
        
        # Draw shortest path polyline
        coordinates = list(zip(df_route["latitude"], df_route["longitude"]))
        folium.PolyLine(
            locations=coordinates,
            color=color,
            weight=3.5,
            opacity=0.85,
            tooltip=f"Zone {cluster_id} Route ({res['optimized_distance_km']} km)"
        ).add_to(m)
        
        # Add stop markers (skip depot duplicate entries)
        for _, row in df_route.iterrows():
            if row["is_depot"] == 1:
                continue
                
            popup_text = f"""
            <b>Order:</b> {row['order_id']}<br>
            <b>Zone:</b> Cluster {cluster_id}<br>
            <b>Customer:</b> {row['customer_name']}<br>
            <b>Area:</b> {row['area']}<br>
            <b>Weight:</b> {row['package_weight_kg']} kg<br>
            <b>Stop #:</b> {row['step']}
            """
            
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"Zone {cluster_id} - Stop #{row['step']}: {row['customer_name']} ({row['area']})"
            ).add_to(m)
            
    m.save(output_html)
    return output_html

def plot_static_clusters_and_routes(cluster_results, depot_info, output_png="outputs/mumbai_route_summary.png"):
    """
    Renders a high-resolution static Matplotlib figure of Mumbai Delivery Zones and Shortest Paths.
    """
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 12))
    
    depot_lat = depot_info["latitude"].values[0]
    depot_lon = depot_info["longitude"].values[0]
    
    for cluster_id, res in cluster_results.items():
        color = get_cluster_color(cluster_id)
        df_route = res["ordered_nodes_df"]
        
        # Plot route polyline
        ax.plot(
            df_route["longitude"], 
            df_route["latitude"], 
            color=color, 
            linestyle="-", 
            linewidth=1.8, 
            alpha=0.8, 
            label=f"Zone {cluster_id}: {res['num_deliveries']} stops ({res['optimized_distance_km']} km)"
        )
        
        # Plot customer delivery nodes
        deliveries_only = df_route[df_route["is_depot"] == 0]
        ax.scatter(
            deliveries_only["longitude"], 
            deliveries_only["latitude"], 
            color=color, 
            s=40, 
            edgecolors="black", 
            linewidth=0.5,
            zorder=3
        )
        
    # Plot Depot
    ax.scatter(
        [depot_lon], [depot_lat], 
        color="black", 
        s=160, 
        marker="*", 
        label="Central Depot (BKC)", 
        zorder=5
    )
    
    ax.set_title("Smart Delivery Zones: K-Means Clustering & Shortest Path Routing (Mumbai)", fontsize=13, weight="bold", pad=15)
    ax.set_xlabel("Longitude (°E)", fontsize=10)
    ax.set_ylabel("Latitude (°N)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()
    return output_png
