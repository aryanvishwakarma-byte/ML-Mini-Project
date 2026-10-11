import heapq
import numpy as np
import pandas as pd
import networkx as nx

def dijkstra_shortest_path(distance_matrix, start_node, target_node):
    """
    Classic Dijkstra algorithm finding the exact shortest path between two nodes in a graph.
    Returns (path, cost)
    """
    n = len(distance_matrix)
    distances = {i: float('inf') for i in range(n)}
    distances[start_node] = 0.0
    previous = {i: None for i in range(n)}
    
    # Priority Queue of (distance, node)
    pq = [(0.0, start_node)]
    
    while pq:
        current_dist, u = heapq.heappop(pq)
        
        if current_dist > distances[u]:
            continue
            
        if u == target_node:
            break
            
        for v in range(n):
            weight = distance_matrix[u][v]
            if weight > 0 and current_dist + weight < distances[v]:
                distances[v] = current_dist + weight
                previous[v] = u
                heapq.heappush(pq, (distances[v], v))
                
    # Reconstruct path
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    
    return path, distances[target_node]

def nearest_neighbor_tsp(distance_matrix, start_node=0):
    """
    Greedy Nearest Neighbor Heuristic for TSP.
    Starts at start_node (depot), visits closest unvisited stop repeatedly,
    and finally returns to start_node.
    Returns (route_indices, total_distance)
    """
    n = len(distance_matrix)
    unvisited = set(range(n))
    unvisited.remove(start_node)
    
    route = [start_node]
    current = start_node
    total_dist = 0.0
    
    while unvisited:
        next_node = min(unvisited, key=lambda node: distance_matrix[current][node])
        total_dist += distance_matrix[current][next_node]
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    # Return to depot
    total_dist += distance_matrix[current][start_node]
    route.append(start_node)
    
    return route, total_dist

def two_opt_swap(route, i, k):
    """Performs 2-opt edge swap reversing segment between i and k."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def two_opt_optimize(route, distance_matrix, max_iterations=500):
    """
    2-Opt local search optimization algorithm.
    Iteratively untangles crossed paths in a TSP route to find the shortest closed tour.
    """
    def route_distance(r):
        return sum(distance_matrix[r[idx]][r[idx + 1]] for idx in range(len(r) - 1))
    
    best_route = route[:]
    best_distance = route_distance(best_route)
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(1, len(best_route) - 2):
            for k in range(i + 1, len(best_route) - 1):
                new_route = two_opt_swap(best_route, i, k)
                new_dist = route_distance(new_route)
                
                if new_dist < best_distance - 1e-6:
                    best_route = new_route
                    best_distance = new_dist
                    improved = True
                    break
            if improved:
                break
                
    return best_route, best_distance

def solve_cluster_route(sub_df, depot_row):
    """
    Takes deliveries for a specific cluster and the central depot.
    Computes local distance matrix, initial nearest neighbor tour, and 2-opt shortest path.
    """
    from src.clustering import compute_distance_matrix
    
    # Combined: index 0 is always depot, 1..M are cluster deliveries
    cluster_nodes = pd.concat([depot_row, sub_df]).reset_index(drop=True)
    coords = cluster_nodes[["latitude", "longitude"]].values
    dist_matrix = compute_distance_matrix(coords)
    
    initial_route, init_dist = nearest_neighbor_tsp(dist_matrix, start_node=0)
    opt_route, opt_dist = two_opt_optimize(initial_route, dist_matrix)
    
    # Map route indices back to original order_ids & details
    route_details = []
    for step_num, idx in enumerate(opt_route):
        row = cluster_nodes.iloc[idx]
        route_details.append({
            "step": step_num,
            "order_id": row["order_id"],
            "customer_name": row["customer_name"],
            "area": row["area"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "package_weight_kg": row["package_weight_kg"],
            "is_depot": row["is_depot"]
        })
        
    return {
        "ordered_nodes_df": pd.DataFrame(route_details),
        "route_indices": opt_route,
        "initial_distance_km": round(init_dist, 2),
        "optimized_distance_km": round(opt_dist, 2),
        "num_deliveries": len(sub_df)
    }
