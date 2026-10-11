import numpy as np
import pandas as pd
import os

# Set random seed for reproducibility
np.random.seed(42)

# Key hubs and neighborhoods across Mumbai Metropolitan Area
MUMBAI_REGIONS = [
    # South Mumbai
    {"area": "Colaba", "lat": 18.9067, "lon": 72.8147, "density": 10},
    {"area": "Nariman Point / Marine Drive", "lat": 18.9256, "lon": 72.8242, "density": 12},
    {"area": "Fort / CSMT", "lat": 18.9398, "lon": 72.8354, "density": 14},
    {"area": "Girgaon / Malabar Hill", "lat": 18.9554, "lon": 72.8066, "density": 10},
    {"area": "Byculla", "lat": 18.9750, "lon": 72.8300, "density": 10},
    {"area": "Worli / Lower Parel", "lat": 19.0016, "lon": 72.8258, "density": 16},
    {"area": "Dadar", "lat": 19.0178, "lon": 72.8478, "density": 15},
    
    # Central Suburbs
    {"area": "Kurla / BKC", "lat": 19.0657, "lon": 72.8687, "density": 18},
    {"area": "Ghatkopar", "lat": 19.0860, "lon": 72.9090, "density": 14},
    {"area": "Bhandup / Mulund", "lat": 19.1550, "lon": 72.9400, "density": 12},
    {"area": "Powai", "lat": 19.1176, "lon": 72.9060, "density": 15},
    
    # Western Suburbs
    {"area": "Bandra West", "lat": 19.0596, "lon": 72.8295, "density": 16},
    {"area": "Juhu / Vile Parle", "lat": 19.1025, "lon": 72.8376, "density": 14},
    {"area": "Andheri East / SEEPZ", "lat": 19.1136, "lon": 72.8697, "density": 18},
    {"area": "Andheri West / Lokhandwala", "lat": 19.1363, "lon": 72.8277, "density": 16},
    {"area": "Goregaon", "lat": 19.1663, "lon": 72.8526, "density": 14},
    {"area": "Malad / Kandivali", "lat": 19.1950, "lon": 72.8450, "density": 16},
    {"area": "Borivali", "lat": 19.2307, "lon": 72.8567, "density": 14},
    
    # Navi Mumbai & Eastern Fringe
    {"area": "Vashi (Navi Mumbai)", "lat": 19.0771, "lon": 72.9986, "density": 12},
    {"area": "Thane West", "lat": 19.2183, "lon": 72.9781, "density": 14}
]

# Central Distribution Hub (BKC Hub)
CENTRAL_DEPOT = {
    "order_id": "DEPOT-000",
    "customer_name": "Main Mumbai Central Logistics Hub (BKC)",
    "area": "Bandra Kurla Complex",
    "latitude": 19.0657,
    "longitude": 72.8687,
    "package_weight_kg": 0.0,
    "time_window": "00:00-23:59",
    "priority": "DEPOT",
    "is_depot": 1
}

def generate_mumbai_dataset(num_points=1000, output_path="data/mumbai_deliveries.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    records = []
    records.append(CENTRAL_DEPOT)
    
    customer_first_names = ["Aarav", "Ananya", "Rohan", "Pooja", "Vikram", "Sneha", "Aditya", "Neha", 
                            "Rahul", "Priya", "Karan", "Tanvi", "Siddharth", "Ishita", "Arjun", "Kavya",
                            "Manish", "Divya", "Sameer", "Rhea", "Varun", "Anjali", "Gaurav", "Simran"]
    customer_last_names = ["Sharma", "Patel", "Mehta", "Deshmukh", "Shah", "Kulkarni", "Verma", "Joshi", 
                           "Fernandes", "Nair", "Sawant", "Gupta", "Chavan", "Pawar", "Shetty", "Merchant",
                           "Bhat", "Rane", "Gokhale", "Kadam", "Tiwari", "Pandey", "Mishra", "Patil"]
    
    time_windows = ["09:00 - 12:00", "12:00 - 15:00", "15:00 - 18:00", "18:00 - 21:00"]
    priorities = ["Standard", "High", "Express"]
    
    order_counter = 1
    
    total_density = sum(r["density"] for r in MUMBAI_REGIONS)
    counts_per_region = [int(np.round((r["density"] / total_density) * num_points)) for r in MUMBAI_REGIONS]
    
    # Adjust total to match num_points
    diff = num_points - sum(counts_per_region)
    counts_per_region[0] += diff
    
    for region, count in zip(MUMBAI_REGIONS, counts_per_region):
        for _ in range(count):
            lat_jitter = np.random.normal(0, 0.012)
            lon_jitter = np.random.normal(0, 0.012)
            
            c_name = f"{np.random.choice(customer_first_names)} {np.random.choice(customer_last_names)}"
            weight = round(float(np.random.uniform(0.5, 12.0)), 2)
            tw = np.random.choice(time_windows)
            priority = np.random.choice(priorities, p=[0.60, 0.25, 0.15])
            
            records.append({
                "order_id": f"MUM-{order_counter:04d}",
                "customer_name": c_name,
                "area": region["area"],
                "latitude": round(region["lat"] + lat_jitter, 6),
                "longitude": round(region["lon"] + lon_jitter, 6),
                "package_weight_kg": weight,
                "time_window": tw,
                "priority": priority,
                "is_depot": 0
            })
            order_counter += 1
            
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} records (1 Depot + {len(df)-1} Deliveries) at: {output_path}")
    return df

if __name__ == "__main__":
    df = generate_mumbai_dataset(1000)
    print(df.head())
