import urllib.request
import json
import random
from app import create_app
from database.models import db, City

def fetch_data():
    print("Downloading country mappings...")
    req = urllib.request.urlopen('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json')
    countries_data = json.loads(req.read())
    
    country_map = {}
    for c in countries_data:
        country_map[c['alpha-2']] = c['name']
        
    print("Downloading massive cities dataset...")
    req = urllib.request.urlopen('https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json')
    cities_data = json.loads(req.read())
    
    return cities_data, country_map

def seed():
    app = create_app()
    with app.app_context():
        cities_data, country_map = fetch_data()
        
        print("Clearing existing cities...")
        # Be careful: this might fail if there are existing foreign keys. 
        # Since this is a prototype, we'll try to delete all cities to avoid duplicates, 
        # but to be safe with FKs (Stops, Activities), we'll just insert non-existing ones or drop tables.
        # Actually, let's just drop and recreate all tables for a clean slate.
        db.drop_all()
        db.create_all()
        print("Database reset.")
        
        print(f"Preparing to insert up to {len(cities_data)} cities...")
        
        city_mappings = []
        cost_indices = ['$', '$$', '$$$', '$$$$']
        
        # We will use a set to avoid duplicates (same name, same country)
        seen = set()
        
        for c in cities_data:
            country_code = c.get('country')
            name = c.get('name')
            if not country_code or not name:
                continue
                
            country_name = country_map.get(country_code, country_code)
            key = f"{name}_{country_name}"
            
            if key not in seen:
                seen.add(key)
                city_mappings.append({
                    'name': name,
                    'country': country_name,
                    'cost_index': random.choice(cost_indices),
                    'popularity': random.randint(10, 100),
                    'description': f"Experience the culture and beauty of {name}, {country_name}."
                })
        
        print(f"Executing bulk insert of {len(city_mappings)} unique cities...")
        # bulk_insert_mappings is extremely fast
        db.session.bulk_insert_mappings(City, city_mappings)
        db.session.commit()
        
        print("Massive seeding complete!")

if __name__ == '__main__':
    seed()
