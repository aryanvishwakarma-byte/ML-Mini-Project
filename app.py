import streamlit as st
import pandas as pd
import numpy as np
import os
import folium
import streamlit.components.v1 as components

from src.clustering import (
    cluster_delivery_zones, 
    CustomStandardScaler
)
from src.shortest_path import solve_cluster_route
from src.visualization import (
    generate_interactive_map, 
    get_cluster_color, 
    get_cluster_color_label, 
    CLUSTER_COLORS
)

st.set_page_config(
    page_title="Smart Delivery Zones: Mumbai Routing",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section with Project & Algorithms Overview
st.title("🚚 Smart Delivery Zones: Mumbai Fleet Routing")
st.markdown("""
**An End-to-End Application of Unsupervised Machine Learning & Shortest Path Graph Optimization**

* **Clustering Algorithms:** **K-Means Clustering** (with K-Means++ centroid initialization) & **DBSCAN** (Density-Based Spatial Clustering with Noise Detection).
* **Cluster Validation Techniques:** **Elbow Method** (Within-Cluster Sum of Squares / Inertia minimization) & **Silhouette Analysis** (Inter vs. Intra cluster separation scoring).
* **Shortest Path Optimization:** **Dijkstra's Algorithm**, **Greedy Nearest Neighbor TSP**, and **2-Opt Edge-Exchange Local Search** for closed-loop truck delivery circuits starting from the central BKC depot.
""")

st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Model & Routing Controls")

data_path = "data/mumbai_deliveries.csv"
if not os.path.exists(data_path):
    from src.generate_dataset import generate_mumbai_dataset
    generate_mumbai_dataset(1000, output_path=data_path)

df_all = pd.read_csv(data_path)
depot_info = df_all[df_all["is_depot"] == 1].copy()
deliveries_all = df_all[df_all["is_depot"] == 0].copy()

total_available = len(deliveries_all)

# Algorithm Selection: Only K-Means and DBSCAN
algorithm = st.sidebar.selectbox(
    "Select Clustering Algorithm",
    options=["kmeans", "dbscan"],
    format_func=lambda x: {
        "kmeans": "K-Means (Lloyd's + K-Means++)",
        "dbscan": "DBSCAN (Density-Based Spatial)"
    }[x]
)

if algorithm == "kmeans":
    n_clusters = st.sidebar.slider("Number of Delivery Zones (k)", min_value=2, max_value=8, value=4)
    eps = 0.35
    min_samples = 4
else:
    n_clusters = 4
    eps = st.sidebar.slider("DBSCAN Epsilon (Neighborhood Radius)", min_value=0.1, max_value=0.8, value=0.35, step=0.05)
    min_samples = st.sidebar.slider("Min Samples (Core Density)", min_value=2, max_value=12, value=4)

st.sidebar.markdown("---")
st.sidebar.info("""
**📍 Central Logistics Depot:**  
Bandra Kurla Complex (BKC), Mumbai  
**📦 Dataset Pool:**  
1,000 synthetic GPS delivery points
""")

# Tabs (Removed Cluster Evaluation Tab as requested)
tab1, tab2, tab3 = st.tabs(["🗺️ Route Map & Overview", "📋 Detailed Itineraries", "📦 Raw Dataset & Sample Filter"])

# Tab 3: Raw Dataset & Sample Filter
with tab3:
    st.subheader("📦 Mumbai Deliveries Dataset (1,000 Records)")
    st.markdown("""
    Use the slider below to select the range of delivery entries to include in the active simulation. 
    **Any changes here automatically re-cluster the points, re-compute the shortest paths, and update the interactive map!**
    """)
    
    # Range selector for dataset entries
    entry_range = st.slider(
        "Select Range of Delivery Entries to Use in Simulation:",
        min_value=1,
        max_value=total_available,
        value=(1, min(120, total_available)),
        step=1,
        help="Choose start and end row indices of customer delivery orders"
    )
    
    start_idx, end_idx = entry_range
    num_selected = end_idx - start_idx + 1
    
    st.success(f"**Currently Active:** Using **{num_selected}** deliveries (Orders from index `{start_idx}` to `{end_idx}`) + 1 Central Depot.")
    
    # Filter the deliveries based on range (1-indexed for user intuition)
    active_deliveries = deliveries_all.iloc[start_idx - 1 : end_idx].copy()
    
    # Combine with depot
    df_active = pd.concat([depot_info, active_deliveries]).reset_index(drop=True)
    
    st.dataframe(df_active, use_container_width=True)

# Run clustering on active dataset
clustered_df, model, scaler = cluster_delivery_zones(
    df_active, 
    n_clusters=n_clusters, 
    algorithm=algorithm, 
    eps=eps, 
    min_samples=min_samples
)

# Run shortest path routing per cluster
cluster_results = {}
total_unopt = 0.0
total_opt = 0.0
summary_rows = []

for c_id in sorted(clustered_df["cluster"].unique()):
    if c_id == -1:
        continue
    sub_df = clustered_df[clustered_df["cluster"] == c_id].copy()
    if len(sub_df) == 0:
        continue
        
    route_res = solve_cluster_route(sub_df, depot_info)
    cluster_results[c_id] = route_res
    
    init_km = route_res["initial_distance_km"]
    opt_km = route_res["optimized_distance_km"]
    saved_km = round(init_km - opt_km, 2)
    pct = ((init_km - opt_km) / init_km * 100) if init_km > 0 else 0
    
    total_unopt += init_km
    total_opt += opt_km
    
    color_hex = get_cluster_color(c_id)
    color_label = get_cluster_color_label(c_id)
    
    summary_rows.append({
        "Zone": f"Zone {c_id}",
        "Map Color": color_label,
        "Assigned Stops": route_res["num_deliveries"],
        "Initial TSP Distance": f"{init_km:.2f} km",
        "Optimized Shortest Path": f"{opt_km:.2f} km",
        "Distance Saved": f"{saved_km:.2f} km",
        "Optimization %": f"{pct:.1f}%"
    })

summary_table = pd.DataFrame(summary_rows)

# Tab 1: Route Map and Overview
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Delivery Zones", len(cluster_results))
    col2.metric("Active Deliveries", len(active_deliveries))
    col3.metric("Optimized Total Distance", f"{total_opt:.2f} km")
    total_reduction_pct = ((total_unopt - total_opt) / total_unopt * 100) if total_unopt > 0 else 0
    col4.metric("Distance Saved (2-Opt)", f"{total_unopt - total_opt:.2f} km", delta=f"{total_reduction_pct:.1f}% reduction")
    
    st.subheader("🗺️ Interactive Mumbai Delivery Map")
    st.caption("Each colored line represents a distinct truck route starting and ending at the Central BKC Logistics Hub.")
    
    map_path = "outputs/app_temp_map.html"
    generate_interactive_map(cluster_results, depot_info, map_path)
    
    with open(map_path, "r", encoding="utf-8") as f:
        html_data = f.read()
    components.html(html_data, height=580)
    
    st.subheader("📊 Route Optimization & Zone Color Legend")
    st.caption("The table below matches each delivery zone directly to the route color shown on the map above:")
    
    # Clean, reliable Streamlit native dataframe table
    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True
    )

# Tab 2: Detailed Turn-by-Turn Itineraries
with tab2:
    st.subheader("📋 Turn-by-Turn Truck Itineraries")
    if len(cluster_results) > 0:
        selected_zone = st.selectbox(
            "Select Zone Itinerary to View:", 
            options=list(cluster_results.keys()),
            format_func=lambda x: f"Zone {x} ({get_cluster_color_label(x)}) - {cluster_results[x]['num_deliveries']} stops"
        )
        if selected_zone in cluster_results:
            res = cluster_results[selected_zone]
            zone_color_label = get_cluster_color_label(selected_zone)
            zone_hex = get_cluster_color(selected_zone)
            st.markdown(f"**Dispatched Route for Zone {selected_zone}** (Color: **{zone_color_label}** `{zone_hex}`): **{res['num_deliveries']} customer stops**, **{res['optimized_distance_km']} km** total round-trip distance.")
            st.dataframe(
                res["ordered_nodes_df"][["step", "order_id", "customer_name", "area", "package_weight_kg", "latitude", "longitude"]], 
                use_container_width=True
            )
    else:
        st.warning("No clusters detected. Please adjust your parameters in the sidebar.")
