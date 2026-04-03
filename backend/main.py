from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import RedirectResponse
import uvicorn
import sys
import os
import pandas as pd

# In order to access to the folders in the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from optimization_engine.optimize_routes import solve_logistics_route
from optimization_engine.visualize_route import generate_route_map
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Logismart API")

# To connect to the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the output folder, if not exitst
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# Serve the path file as a static resource
app.mount("/maps", StaticFiles(directory="outputs"), name="maps")


@app.get("/run-optimization")
def run_tsp(precision: float = 0.15, seconds: int = 600):
    # Definimos las rutas desde la raíz del proyecto
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_file = os.path.join(base_path, 'data', 'medellin_customers.csv')
    matrix_file = os.path.join(base_path, 'data', 'distance_matrix.npy')
    # output_map = os.path.join(base_path, 'route_map.html')

    output_map_name = "route_medellin.html"
    output_path = os.path.join("outputs", output_map_name)

    try:
        # Ejecutar el motor
        sequence, distance = solve_logistics_route(
            csv_path=csv_file, 
            matrix_path=matrix_file, 
            gap_rel=precision,
            timeLimit=seconds
        )

        if sequence:
            # Generar mapa
            df = pd.read_csv(csv_file)
            generate_route_map(df, sequence, output_file=output_path)
            
            return {
                "message": "Optimization Complete",
                "distance": round(distance, 4),
                "config_used": {
                    "gap_target": precision,
                    "max_time_sec": seconds
                },
                "map_url": f"http://127.0.0.1:8000/maps/{output_map_name}",
                "path": sequence
            }
        
            # # If you only want the map
            # return RedirectResponse(url=f"/maps/{output_map_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    # Configure tehe  server to run 'uvicorn backend.main:app --reload' from this python file
    uvicorn.run(
        "main:app",      # El archivo y la instancia de FastAPI
        host="127.0.0.1", 
        port=8000, 
        reload=True      # Mantiene el auto-restart activo
    )
    # Run the interface from http://127.0.0.1:8000/docs or http://localhost:8000/docs