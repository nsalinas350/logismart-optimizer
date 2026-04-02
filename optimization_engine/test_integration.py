from optimize_routes import solve_logistics_route
from visualize_route import generate_route_map
import pandas as pd

# 1. Ejecutar el motor y obtener la secuencia
print("🚀 Starting Optimization...")
sequence, distance = solve_logistics_route(timeLimit = 1200, gap_rel=0.10)

if sequence:
    print(f"✅ Route found with distance: {distance:.4f}")
    
    # 2. Cargar el DF para el mapa
    df = pd.read_csv('medellin_customers.csv')
    
    # 3. Generar el mapa usando la secuencia retornada
    generate_route_map(df, sequence)
else:
    print("❌ Failed to find a route.")