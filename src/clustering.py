"""
Pure Python & NumPy implementation of Unsupervised Clustering and Distance Metrics.
Algorithms:
1. Haversine Distance Matrix calculation
2. K-Means (Lloyd's Algorithm + K-Means++ initialization)
3. DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
4. Evaluation Metrics: Inertia/Elbow, Silhouette Score, and Davies-Bouldin Index
"""

import numpy as np
import pandas as pd

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (in decimal degrees) in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def compute_distance_matrix(coords):
    """
    Computes NxN pairwise Haversine distance matrix in kilometers.
    coords: array of shape (N, 2) where col 0 is lat, col 1 is lon.
    """
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_distance(coords[i, 0], coords[i, 1], coords[j, 0], coords[j, 1])
            matrix[i, j] = d
            matrix[j, i] = d
    return matrix

class CustomStandardScaler:
    """Feature Scaling (StandardScaler)."""
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        X = np.asarray(X)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X):
        X = np.asarray(X)
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def inverse_transform(self, X):
        X = np.asarray(X)
        return (X * self.scale_) + self.mean_

class CustomKMeans:
    """
    K-Means Clustering implementation with K-Means++ initialization and Lloyd's iterations.
    """
    def __init__(self, n_clusters=4, max_iter=300, random_state=42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = None

    def _kmeans_plus_plus_init(self, X):
        np.random.seed(self.random_state)
        n_samples = X.shape[0]
        centers = [X[np.random.randint(n_samples)]]
        
        for _ in range(1, self.n_clusters):
            min_dist_sq = np.array([
                min(np.sum((x - c)**2) for c in centers)
                for x in X
            ])
            denom = np.sum(min_dist_sq)
            probs = (min_dist_sq / denom) if denom > 0 else np.full(n_samples, 1.0 / n_samples)
            next_idx = np.random.choice(n_samples, p=probs)
            centers.append(X[next_idx])
            
        return np.array(centers)

    def fit(self, X):
        X = np.asarray(X)
        self.cluster_centers_ = self._kmeans_plus_plus_init(X)
        
        for _ in range(self.max_iter):
            dists = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_, axis=2)
            labels = np.argmin(dists, axis=1)
            
            new_centers = np.array([
                X[labels == k].mean(axis=0) if np.sum(labels == k) > 0 else self.cluster_centers_[k]
                for k in range(self.n_clusters)
            ])
            
            if np.allclose(self.cluster_centers_, new_centers, atol=1e-5):
                break
            self.cluster_centers_ = new_centers

        self.labels_ = labels
        self.inertia_ = float(np.sum([
            np.sum((X[labels == k] - self.cluster_centers_[k])**2)
            for k in range(self.n_clusters)
        ]))
        return self

    def predict(self, X):
        X = np.asarray(X)
        dists = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_, axis=2)
        return np.argmin(dists, axis=1)

class CustomDBSCAN:
    """
    Density-Based Spatial Clustering of Applications with Noise (DBSCAN).
    """
    def __init__(self, eps=0.35, min_samples=4):
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None

    def fit(self, X):
        X = np.asarray(X)
        n = len(X)
        labels = np.full(n, -1, dtype=int)
        visited = np.zeros(n, dtype=bool)
        cluster_id = 0
        
        dist_matrix = np.linalg.norm(X[:, np.newaxis] - X[np.newaxis, :], axis=2)

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            
            neighbors = np.where(dist_matrix[i] <= self.eps)[0].tolist()
            if len(neighbors) < self.min_samples:
                labels[i] = -1
            else:
                labels[i] = cluster_id
                queue = neighbors[:]
                while queue:
                    neighbor = queue.pop(0)
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        n_neighbors = np.where(dist_matrix[neighbor] <= self.eps)[0].tolist()
                        if len(n_neighbors) >= self.min_samples:
                            queue.extend([pt for pt in n_neighbors if pt not in queue])
                    if labels[neighbor] == -1:
                        labels[neighbor] = cluster_id
                cluster_id += 1

        self.labels_ = labels
        return self

def calculate_silhouette_score(X, labels):
    """Computes mean Silhouette Coefficient."""
    X = np.asarray(X)
    labels = np.asarray(labels)
    unique_labels = [l for l in np.unique(labels) if l != -1]
    
    if len(unique_labels) < 2:
        return 0.0

    n = len(X)
    s_scores = []
    dist_matrix = np.linalg.norm(X[:, np.newaxis] - X[np.newaxis, :], axis=2)
    
    for i in range(n):
        c_i = labels[i]
        if c_i == -1:
            continue
            
        same_cluster_indices = np.where(labels == c_i)[0]
        if len(same_cluster_indices) <= 1:
            s_scores.append(0.0)
            continue
            
        a_i = np.sum(dist_matrix[i, same_cluster_indices]) / (len(same_cluster_indices) - 1)
        
        b_candidates = []
        for other_c in unique_labels:
            if other_c == c_i:
                continue
            other_indices = np.where(labels == other_c)[0]
            if len(other_indices) > 0:
                b_candidates.append(np.mean(dist_matrix[i, other_indices]))
                
        b_i = min(b_candidates) if b_candidates else 0.0
        denom = max(a_i, b_i)
        s_scores.append((b_i - a_i) / denom if denom > 0 else 0.0)
            
    return float(np.mean(s_scores)) if s_scores else 0.0

def calculate_davies_bouldin(X, labels):
    """Computes Davies-Bouldin index for clustering evaluation."""
    X = np.asarray(X)
    labels = np.asarray(labels)
    unique_labels = [l for l in np.unique(labels) if l != -1]
    k = len(unique_labels)
    
    if k < 2:
        return 0.0
        
    centroids = np.array([X[labels == l].mean(axis=0) for l in unique_labels])
    dispersions = np.array([np.mean(np.linalg.norm(X[labels == l] - centroids[i], axis=1)) for i, l in enumerate(unique_labels)])
    
    r_matrix = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            if i != j:
                dist_centers = np.linalg.norm(centroids[i] - centroids[j])
                if dist_centers > 0:
                    r_matrix[i, j] = (dispersions[i] + dispersions[j]) / dist_centers
                    
    max_r = np.max(r_matrix, axis=1)
    return float(np.mean(max_r))

def find_optimal_k(features, k_range=range(2, 7)):
    """Elbow and Silhouette analysis over a range of K values."""
    metrics = []
    for k in k_range:
        km = CustomKMeans(n_clusters=k, random_state=42)
        km.fit(features)
        sil = calculate_silhouette_score(features, km.labels_)
        db = calculate_davies_bouldin(features, km.labels_)
        
        metrics.append({
            "k": k,
            "inertia": round(km.inertia_, 3),
            "silhouette_score": round(sil, 4),
            "davies_bouldin": round(db, 4)
        })
    return pd.DataFrame(metrics)

def cluster_delivery_zones(df, n_clusters=4, algorithm="kmeans", eps=0.35, min_samples=4):
    """
    Main clustering interface for K-Means and DBSCAN.
    """
    deliveries = df[df["is_depot"] == 0].copy()
    coords = deliveries[["latitude", "longitude"]].values
    
    scaler = CustomStandardScaler()
    scaled_coords = scaler.fit_transform(coords)
    
    if algorithm == "kmeans":
        model = CustomKMeans(n_clusters=n_clusters, random_state=42)
        model.fit(scaled_coords)
        labels = model.labels_
    elif algorithm == "dbscan":
        model = CustomDBSCAN(eps=eps, min_samples=min_samples)
        model.fit(scaled_coords)
        labels = model.labels_
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Supported: kmeans, dbscan")
        
    deliveries["cluster"] = labels
    depot_rows = df[df["is_depot"] == 1].copy()
    depot_rows["cluster"] = -1
    
    combined = pd.concat([depot_rows, deliveries]).sort_index()
    return combined, model, scaler
