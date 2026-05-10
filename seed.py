from app import create_app
from database.models import db, City, Activity

app = create_app()

GLOBAL_DATA = {
    'USA': ['New York', 'Los Angeles', 'Chicago', 'Miami', 'San Francisco', 'Las Vegas'],
    'France': ['Paris', 'Lyon', 'Marseille', 'Nice', 'Bordeaux'],
    'Italy': ['Rome', 'Venice', 'Florence', 'Milan', 'Naples', 'Amalfi'],
    'Japan': ['Tokyo', 'Kyoto', 'Osaka', 'Sapporo', 'Hiroshima'],
    'UK': ['London', 'Edinburgh', 'Manchester', 'Birmingham', 'Liverpool'],
    'Spain': ['Madrid', 'Barcelona', 'Seville', 'Valencia', 'Ibiza'],
    'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Gold Coast'],
    'India': ['New Delhi', 'Mumbai', 'Jaipur', 'Goa', 'Agra', 'Bangalore'],
    'Brazil': ['Rio de Janeiro', 'Sao Paulo', 'Salvador', 'Brasilia', 'Fortaleza'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    'Thailand': ['Bangkok', 'Chiang Mai', 'Phuket', 'Pattaya', 'Krabi'],
    'Mexico': ['Mexico City', 'Cancun', 'Guadalajara', 'Tulum', 'Oaxaca'],
    'South Africa': ['Cape Town', 'Johannesburg', 'Durban', 'Pretoria'],
    'China': ['Beijing', 'Shanghai', "Xi'an", 'Chengdu', 'Guangzhou']
}

with app.app_context():
    # We won't clear the db to avoid breaking foreign keys, just add missing.
    print("Seeding database with global dataset...")
    
    cities_added = 0
    for country, cities in GLOBAL_DATA.items():
        for city_name in cities:
            existing = City.query.filter_by(name=city_name, country=country).first()
            if not existing:
                import random
                cost_index = random.choice(['$', '$$', '$$$', '$$$$'])
                popularity = random.randint(70, 100)
                new_city = City(name=city_name, country=country, cost_index=cost_index, popularity=popularity, description=f"A beautiful destination in {country}.")
                db.session.add(new_city)
                cities_added += 1
                
    db.session.commit()
    print(f"Added {cities_added} new cities. Total cities: {City.query.count()}")
    
    # Add dummy activities for a few
    if Activity.query.count() < 10:
        print("Adding dummy activities...")
        for city in City.query.limit(10).all():
            for i in range(3):
                act = Activity(
                    city_id=city.id,
                    name=f"{city.name} Walking Tour {i+1}",
                    type='Sightseeing',
                    cost=25.0,
                    duration=120,
                    description=f"Explore the best of {city.name}"
                )
                db.session.add(act)
        db.session.commit()
    
    print("Seeding complete.")
