import os
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
    # Defining folder rute, going up a level from optimization-engine
    data_folder = os.path.join(os.getcwd(), 'data')

    # Check if the folder exist; if not, create it
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"📁 Folder created: {data_folder}")

    # Define the full file path
    file_path = os.path.join(data_folder, 'medellin_customers.csv')

    # Save the file
    df_final.to_csv(file_path, index=False)
    print(f"✅ Dataset initialized: 1 central depot and {n_customers} nodes generated.")
    print(f"✅ File saved successfully in: {file_path}")

if __name__ == "__main__":
    generate_synthetic_locations()