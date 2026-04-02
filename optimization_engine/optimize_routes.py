import pandas as pd
import numpy as np
from pulp import *
from visualize_route import generate_route_map

def solve_logistics_route(csv_path='data/medellin_customers.csv',
                          matrix_path='data/distance_matrix.npy',
                          timeLimit=600, gap_rel=0.15):
    # 1. Load Data
    df = pd.read_csv(csv_path)
    dist_matrix = np.load(matrix_path)
    n = len(df) # Should be 51
    
    # 2. Define the Optimization Problem
    # We want to MINIMIZE the total travel distance
    # We need a long and uinique trip
    prob = LpProblem("Medellin_Route_Optimization", LpMinimize)
    
    # 3. Decision Variables
    # x[i][j] = 1 if the truck travels from point i to point j, 0 otherwise
    x = LpVariable.dicts('route', (range(n), range(n)), cat='Binary')
    # Create "visit order" variables (u) for customers
    u = LpVariable.dicts('visit_order', range(1,n), lowBound=1, upBound=n-1, cat='Continuous')
    
    # 4. Objective Function: sum of (distance * decision_variable)
    prob += lpSum([dist_matrix[i][j] * x[i][j] for i in range(n) for j in range(n)])
    
    # 5. Constraints
    # Constraint A: Leave each location exactly once
    for i in range(n):
        prob += lpSum([x[i][j] for j in range(n) if i != j]) == 1
        
    # Constraint B: Arrive at each location exactly once
    for j in range(n):
        prob += lpSum([x[i][j] for i in range(n) if i != j]) == 1

    # Constraint C: conttraint MTZ for surpiming subtours, only for customers, skipping the depot i=0
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                # If the truck goes from i to j, so u[j] >= u[i] + 1
                prob += u[i] - u[j] + (n * x[i][j]) <= n - 1

    # 6. Solve the problem
    print("\nSolving the optimal route for Medellin... 🚚")
    # Stop when te solution is within 5% of the theoretical optimum or after 600 seconds
    prob.solve(PULP_CBC_CMD(timeLimit=timeLimit, gapRel=gap_rel))

    # --- 7. TECHNICAL STATUS ---
    print("-" * 45)
    print(f"Solver Status: {LpStatus[prob.status]}")
    print(f"Objective (Total Distance): {value(prob.objective):.4f} units")
    print("-" * 45)

    # --- 8. USER REPORT: ORDERED ROUTE ---
    # Status 1 = Optimal, 0 = Not Solved (but may have a valid sub-optimal solution)
    if prob.status in [1, 0]: 
        print("\n" + "="*50)
        print("       LOGISMART: OPTIMIZED ROUTE PLAN (MEDELLIN)      ")
        print("="*50)

        route_sequence = []
        curr_node = 0
        visited_nodes = 0
        route_is_complete = True

        # We use a while loop to follow the 'breadcrumb trail' of the route
        while visited_nodes < n:
            found_next = False
            route_sequence.append(curr_node) # Saving the current node
            
            for next_node in range(n):
                # 1. Get the value of the decision variable x[i][j]
                # Using value() to extract the float from the PuLP object
                val = value(x[curr_node][next_node])
                
                # 2. Null-check: If solver timed out, some variables might be None
                if val is not None and val > 0.9:
                    # 3. Identify the visit order (u) for the destination       
                    location_label = df.iloc[next_node]['location_name']
                    print(f"Step {visited_nodes + 1:2}: From {curr_node:2} ---> To {next_node:2} | {location_label}")

                    # 4. Move to the next node and mark as found
                    curr_node = next_node
                    visited_nodes += 1
                    found_next = True
                    break # Exit the 'for' loop to move to the next step in the 'while'
            
            # If we couldn't find a path with value > 0.9, the chain is broken
            if not found_next:
                print(f"\n[!] ALERT: Route chain broken at Node {curr_node}.")
                print("    The solver timed out before finding all connections.")
                route_is_complete = False
                break

        print("="*50)
        if route_is_complete:
            print("✅ Success: Full Hamiltonian Path identified.")
        else:
            print("⚠️ Warning: Partial route generated. Increase timeLimit or gapRel.")
        print("="*50 + "\n")
        return route_sequence, value(prob.objective)
        
    else:
        print(f"\n[!] Critical: Solver failed with status {LpStatus[prob.status]}.")
        return None, None



if __name__ == "__main__":
    df = pd.read_csv('data/medellin_customers.csv')
    sequence, distance = solve_logistics_route()
    generate_route_map(df, sequence)