import pandas as pd
import numpy as np
from pulp import *
from visualize_route import generate_route_map

def solve_logistics_route():
    # 1. Load Data
    dist_matrix = np.load('distance_matrix.npy')
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
    prob.solve(PULP_CBC_CMD(timeLimit=600, gapRel=0.15))

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

        curr_node = 0
        visited_nodes = 0
        total_locations = n
        route_is_complete = True
        route_list = []

        # We use a while loop to follow the 'breadcrumb trail' of the route
        while visited_nodes < total_locations:
            found_next = False
            
            for next_node in range(total_locations):
                # 1. Get the value of the decision variable x[i][j]
                # Using value() to extract the float from the PuLP object
                val = value(x[curr_node][next_node])
                
                # 2. Null-check: If solver timed out, some variables might be None
                if val is not None and val > 0.9:
                    # 3. Identify the visit order (u) for the destination
                    # The Depot (0) doesn't have a 'u' variable in our optimized range
                    step_order = value(u[next_node]) if next_node in u else 0
                                   
                    location_label = df.iloc[next_node]['location_name']
                    print(f"Step {visited_nodes + 1:2}: From {curr_node:2} ---> To {next_node:2} | {location_label}")

                    # 4. Move to the next node and mark as found
                    route_list.append(next_node)
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
            
            final_sequence = [0] + route_list
            return final_sequence
        else:
            print("⚠️ Warning: Partial route generated. Increase timeLimit or gapRel.")
        print("="*50 + "\n")

    else:
        print(f"\n[!] Critical: Solver failed with status {LpStatus[prob.status]}.")



if __name__ == "__main__":
    df = pd.read_csv('medellin_customers.csv')
    sequence = solve_logistics_route()
    generate_route_map(df, sequence)