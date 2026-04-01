import pandas as pd
import numpy as np
from pulp import *

def solve_logistics_route():
    # 1. Load Data
    df = pd.read_csv('medellin_customers.csv')
    dist_matrix = np.load('distance_matrix.npy')
    n = len(df) # Should be 51
    
    # 2. Define the Optimization Problem
    # We want to MINIMIZE the total travel distance
    prob = LpProblem("Medellin_Route_Optimization", LpMinimize)
    
    # 3. Decision Variables
    # x[i][j] = 1 if the truck travels from point i to point j, 0 otherwise
    x = LpVariable.dicts('route', (range(n), range(n)), cat='Binary')
    
    # 4. Objective Function: sum of (distance * decision_variable)
    prob += lpSum([dist_matrix[i][j] * x[i][j] for i in range(n) for j in range(n)])
    
    # 5. Constraints
    # Constraint A: Leave each location exactly once
    for i in range(n):
        prob += lpSum([x[i][j] for j in range(n) if i != j]) == 1
        
    # Constraint B: Arrive at each location exactly once
    for j in range(n):
        prob += lpSum([x[i][j] for i in range(n) if i != j]) == 1

    # 6. Solve the problem
    print("Solving the optimal route for Medellin... 🚚")
    prob.solve()
    
    print(f"Status: {LpStatus[prob.status]}")
    print(f"Total Optimized Distance: {value(prob.objective):.4f} units")

if __name__ == "__main__":
    solve_logistics_route()