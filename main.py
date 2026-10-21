import os
import pandas as pd
import numpy as np

from src.clustering import cluster_delivery_zones, find_optimal_k
from src.shortest_path import solve_cluster_route
from src.visualization import generate_interactive_map, plot_static_clusters_and_routes, get_cluster_color

def run_pipeline(data_path="data/mumbai_deliveries.csv", n_clusters=4, algorithm="kmeans", sample_size=120):
    print("=" * 70)
    print("  SMART DELIVERY ZONES: K-MEANS CLUSTERING & SHORTEST PATH ROUTING")
    print("=" * 70)
    
    if not os.path.exists(data_path):
        from src.generate_dataset import generate_mumbai_dataset
        print(f"Dataset not found at {data_path}. Generating Mumbai dataset now...")
        df_all = generate_mumbai_dataset(1000, output_path=data_path)
    else:
        df_all = pd.read_csv(data_path)
        print(f"Loaded dataset from {data_path} ({len(df_all)} total records).")
        
    depot_info = df_all[df_all["is_depot"] == 1].copy()
    deliveries_all = df_all[df_all["is_depot"] == 0].copy()
    
    # Subsample deliveries
    active_deliveries = deliveries_all.head(sample_size).copy()
    df = pd.concat([depot_info, active_deliveries]).reset_index(drop=True)
    print(f"Active simulation running on {len(active_deliveries)} deliveries + 1 Central BKC Depot.")
    
    print(f"\n[Step 1] Performing Spatial Clustering using {algorithm.upper()} (k={n_clusters})...")
    clustered_df, model, _ = cluster_delivery_zones(df, n_clusters=n_clusters, algorithm=algorithm)
    
    # Save clustered data
    os.makedirs("outputs", exist_ok=True)
    clustered_df.to_csv("outputs/mumbai_clustered_deliveries.csv", index=False)
    
    print(f"\n[Step 2] Solving Shortest Path Routing within Each Delivery Zone...")
    cluster_results = {}
    total_dijkstra_km = 0.0
    total_greedy_km = 0.0
    total_shortest_km = 0.0
    
    routes_summary = []
    
    for c_id in sorted(clustered_df["cluster"].unique()):
        if c_id == -1:
            continue
            
        sub_df = clustered_df[clustered_df["cluster"] == c_id].copy()
        if len(sub_df) == 0:
            continue
            
        route_res = solve_cluster_route(sub_df, depot_info)
        cluster_results[c_id] = route_res
        
        dijkstra_km = route_res["dijkstra_distance_km"]
        greedy_km = route_res["greedy_distance_km"]
        shortest_km = route_res["shortest_distance_km"]
        method = route_res["selected_method"]
        
        total_dijkstra_km += dijkstra_km
        total_greedy_km += greedy_km
        total_shortest_km += shortest_km
        
        routes_summary.append({
            "Zone": f"Zone {c_id}",
            "Map Color": get_cluster_color(c_id),
            "Stops": route_res["num_deliveries"],
            "Dijkstra Tour (km)": dijkstra_km,
            "Greedy TSP (km)": greedy_km,
            "Selected Shortest (km)": shortest_km,
            "Winning Algorithm": method
        })
        
        route_res["ordered_nodes_df"].to_csv(f"outputs/zone_{c_id}_itinerary.csv", index=False)
        
    summary_df = pd.DataFrame(routes_summary)
    print("\n--- Route Optimization Summary (Dijkstra vs Greedy TSP) ---")
    print(summary_df.to_string(index=False))
    print("-" * 65)
    print(f"Total Fleet Distance (Dijkstra Tour):  {total_dijkstra_km:.2f} km")
    print(f"Total Fleet Distance (Greedy TSP):     {total_greedy_km:.2f} km")
    print(f"Total Fleet Distance (Selected Shortest): {total_shortest_km:.2f} km")
    
    print(f"\n[Step 3] Generating Route Maps and Visualizations...")
    html_map = generate_interactive_map(cluster_results, depot_info, "outputs/mumbai_route_map.html")
    static_png = plot_static_clusters_and_routes(cluster_results, depot_info, "outputs/mumbai_route_summary.png")
    
    print("\n[Done] Pipeline executed successfully!")
    print(f"  - Clustered Data: outputs/mumbai_clustered_deliveries.csv")
    print(f"  - Interactive Map: {html_map}")
    print(f"  - Route Visual:    {static_png}")
    print("=" * 70)
    
    return summary_df

if __name__ == "__main__":
    run_pipeline(n_clusters=4, sample_size=120)
