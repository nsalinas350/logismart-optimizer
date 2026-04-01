import pandas as pd
import numpy as np

def calculate_distance_matrix():
    """
    Generates a matrix of distances using the Euclidean 
    distance formula: sqrt((x2-x1)^2 + (y2-y1)^2)
    """
    # 1. Load our synthetic data
    df = pd.read_csv('medellin_customers.csv')
    
    # 2. Extract coordinates as NumPy Arrays
    coords = df[['latitude', 'longitude']].values
    
    # 3. Calculate the distance matrix
    # This creates a 51x51 antisymmetric matrix where matrix[i][j] is the distance from i to j
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dist_matrix = np.sqrt(np.sum(diff**2, axis=-1))
    
    # 4. Save the matrix for the optimization step
    np.save('distance_matrix.npy', dist_matrix)
    print(f"✅ Distance matrix calculated: {dist_matrix.shape} elements.")
    print(f"Sample distance (Depot to Customer 1): {dist_matrix[0][1]:.4f} units")

if __name__ == "__main__":
    calculate_distance_matrix()