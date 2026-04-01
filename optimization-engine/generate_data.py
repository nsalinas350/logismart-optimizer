import pandas as pd
import numpy as np

# Metropolitan area of Medellin Bounding Box
LAT_RANGE = (6.15, 6.35)
LON_RANGE = (-75.65, -75.50)

# Fixed coordinates for the Depot (Medellin's center)
DEPOT_LAT = 6.2471
DEPOT_LON = -75.5724

def generate_synthetic_locations(n_customers=50):
    """
    Generates a logistics dataset: 1 fixed Depot + N random customers.
    """
    np.random.seed(42)
    
    # 1. Create the Depot entry
    data = {
        'location_name': ['Main_Depot'],
        'latitude': [DEPOT_LAT],
        'longitude': [DEPOT_LON],
        'demand_kg': [0], # The depot has no delivery demand
        'type': ['Depot']
    }
    
    # 2. Generate random customers
    customers = {
        'location_name': [f"Customer_{i+1}" for i in range(n_customers)],
        'latitude': np.random.uniform(LAT_RANGE[0], LAT_RANGE[1], n_customers),
        'longitude': np.random.uniform(LON_RANGE[0], LON_RANGE[1], n_customers),
        'demand_kg': np.random.randint(10, 500, n_customers),
        'type': ['Customer'] * n_customers
    }
    
    # Combine both using Pandas
    df_depot = pd.DataFrame(data)
    df_customers = pd.DataFrame(customers)
    df_final = pd.concat([df_depot, df_customers], ignore_index=True)
    
    # Save to CSV
    df_final.to_csv('medellin_customers.csv', index=False)
    print(f"✅ Dataset created: 1 Depot at Alpujarra and {n_customers} customers.")

if __name__ == "__main__":
    generate_synthetic_locations()