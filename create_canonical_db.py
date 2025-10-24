"""
Create canonical database with sample data for Project Samarth
"""

import duckdb
import pandas as pd
import numpy as np
import os

def create_canonical_database():
    """Create canonical database with sample agriculture and climate data"""
    
    # Create db directory
    os.makedirs('db', exist_ok=True)
    
    # Connect to DuckDB
    conn = duckdb.connect('db/canonical.duckdb')
    
    # Create sample agriculture production data
    states = ['Maharashtra', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Gujarat', 
              'Rajasthan', 'Madhya Pradesh', 'Karnataka', 'Andhra Pradesh', 'Tamil Nadu']
    
    crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Groundnut', 'Soybean']
    
    years = list(range(2010, 2015))
    
    # Generate agriculture data
    agri_data = []
    for state in states:
        for crop in crops:
            for year in years:
                # Generate realistic production data
                base_production = np.random.uniform(100, 1000)  # tonnes
                area = np.random.uniform(50, 500)  # hectares
                
                agri_data.append({
                    'state': state,
                    'district': f"{state.split()[0]} District",
                    'year': year,
                    'crop': crop,
                    'production_tonnes': round(base_production, 2),
                    'area_hectares': round(area, 2),
                    'yield_kg_per_ha': round((base_production * 1000) / area, 2)
                })
    
    agri_df = pd.DataFrame(agri_data)
    
    # Create agriculture table
    conn.execute("""
        CREATE TABLE agri_production (
            state VARCHAR,
            district VARCHAR,
            year INTEGER,
            crop VARCHAR,
            production_tonnes DOUBLE,
            area_hectares DOUBLE,
            yield_kg_per_ha DOUBLE
        )
    """)
    
    # Insert agriculture data
    conn.execute("INSERT INTO agri_production SELECT * FROM agri_df")
    
    # Generate climate data
    climate_data = []
    for state in states:
        for year in years:
            # Generate realistic rainfall data (mm)
            annual_rainfall = np.random.uniform(500, 2000)
            
            # Generate monthly distribution
            monthly_rainfall = np.random.dirichlet(np.ones(12)) * annual_rainfall
            
            climate_data.append({
                'state': state,
                'district': f"{state.split()[0]} District",
                'year': year,
                'rainfall_mm': round(annual_rainfall, 2),
                'jan_rainfall': round(monthly_rainfall[0], 2),
                'feb_rainfall': round(monthly_rainfall[1], 2),
                'mar_rainfall': round(monthly_rainfall[2], 2),
                'apr_rainfall': round(monthly_rainfall[3], 2),
                'may_rainfall': round(monthly_rainfall[4], 2),
                'jun_rainfall': round(monthly_rainfall[5], 2),
                'jul_rainfall': round(monthly_rainfall[6], 2),
                'aug_rainfall': round(monthly_rainfall[7], 2),
                'sep_rainfall': round(monthly_rainfall[8], 2),
                'oct_rainfall': round(monthly_rainfall[9], 2),
                'nov_rainfall': round(monthly_rainfall[10], 2),
                'dec_rainfall': round(monthly_rainfall[11], 2),
                'temperature_avg': round(np.random.uniform(20, 35), 2)
            })
    
    climate_df = pd.DataFrame(climate_data)
    
    # Create climate table
    conn.execute("""
        CREATE TABLE climate_obs (
            state VARCHAR,
            district VARCHAR,
            year INTEGER,
            rainfall_mm DOUBLE,
            jan_rainfall DOUBLE,
            feb_rainfall DOUBLE,
            mar_rainfall DOUBLE,
            apr_rainfall DOUBLE,
            may_rainfall DOUBLE,
            jun_rainfall DOUBLE,
            jul_rainfall DOUBLE,
            aug_rainfall DOUBLE,
            sep_rainfall DOUBLE,
            oct_rainfall DOUBLE,
            nov_rainfall DOUBLE,
            dec_rainfall DOUBLE,
            temperature_avg DOUBLE
        )
    """)
    
    # Insert climate data
    conn.execute("INSERT INTO climate_obs SELECT * FROM climate_df")
    
    # Create indexes for better performance
    conn.execute("CREATE INDEX idx_agri_state_year ON agri_production(state, year)")
    conn.execute("CREATE INDEX idx_climate_state_year ON climate_obs(state, year)")
    
    # Verify data
    agri_count = conn.execute("SELECT COUNT(*) FROM agri_production").fetchone()[0]
    climate_count = conn.execute("SELECT COUNT(*) FROM climate_obs").fetchone()[0]
    
    print(f"Created canonical database with:")
    print(f"- Agriculture records: {agri_count}")
    print(f"- Climate records: {climate_count}")
    print(f"- Database saved to: db/canonical.duckdb")
    
    conn.close()

if __name__ == "__main__":
    create_canonical_database()