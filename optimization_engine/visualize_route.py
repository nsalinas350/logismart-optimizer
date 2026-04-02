import folium
import pandas as pd

def generate_route_map(df, route_sequence, output_file='route_map.html'):
    """
    Generates an interactive HTML map using Folium.
    df: The dataframe with coordinates and names.
    route_sequence: A list of node IDs in the order they are visited (e.g., [0, 5, 12, ..., 0]).
    """
    
    # 1. Initialize the map centered in Medellin
    # We'll use the Depot (Node 0) as the starting center
    depot_lat = df.iloc[0]['latitude']
    depot_lon = df.iloc[0]['longitude']
    
    # m = folium.Map(location=[depot_lat, depot_lon], zoom_start=13, control_scale=True)
    m = folium.Map(location=[depot_lat, depot_lon], control_scale=True)

    # 2. Add markers for each location
    for index, row in df.iterrows():
        color = 'red' if row['type'] == 'Depot' else 'blue'
        icon = 'home' if row['type'] == 'Depot' else 'info-sign'
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>{row['location_name']}</b><br>Demand: {row.get('demand_kg', 0)}kg",
            tooltip=row['location_name'],
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)

    # 3. Create the path (Polylines)
    # We extract the coordinates in the order of the route_sequence
    route_coords = []
    for node_id in route_sequence:
        lat = df.iloc[node_id]['latitude']
        lon = df.iloc[node_id]['longitude']
        route_coords.append([lat, lon])

    # Add a line connecting the points
    folium.PolyLine(
        locations=route_coords,
        weight=5,
        color='darkblue',
        opacity=0.8,
        tooltip="Optimized Route Path"
    ).add_to(m)

    # 4. Save the map
    m.fit_bounds(route_coords)
    m.save(output_file)
    print(f"✅ Map successfully generated: {output_file}")

# Example of how to integrate it (Test mode)
if __name__ == "__main__":
    # Load your data to test
    df_test = pd.read_csv('medellin_customers.csv')
    # Dummy sequence for testing (Replace with your solver's output)
    test_sequence = [0, 5, 10, 0] 
    generate_route_map(df_test, test_sequence)