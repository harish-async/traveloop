from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import db, Trip, City
from datetime import datetime

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch upcoming trips for the current user (where end_date hasn't passed yet)
    today = datetime.now().date()
    upcoming_trips = Trip.query.filter(Trip.user_id == current_user.id, Trip.end_date >= today).order_by(Trip.start_date).all()
    
    # Fetch some recommended places (random or top popularity)
    recommended_cities = City.query.order_by(City.popularity.desc()).limit(5).all()
    
    return render_template('dashboard.html', upcoming_trips=upcoming_trips, recommended_cities=recommended_cities)

@trips_bp.route('/all')
@login_required
def my_trips():
    # Fetch all trips for the current user, ordered by start date (newest first)
    all_trips = Trip.query.filter(Trip.user_id == current_user.id).order_by(Trip.start_date.desc()).all()
    return render_template('my_trips.html', trips=all_trips)

@trips_bp.route('/create-trip', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        description = request.form.get('description')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                flash('End date must be after start date.', 'danger')
                return redirect(url_for('trips.create_trip'))
                
            new_trip = Trip(
                user_id=current_user.id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                description=description
            )
            
            db.session.add(new_trip)
            db.session.commit()
            
            flash('Trip created successfully! Now add some stops.', 'success')
            return redirect(url_for('trips.dashboard')) # Will change to itinerary builder later
            
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('trips.create_trip'))

    # Also show recommended destinations on the create trip page as per wireframe
    recommended_cities = City.query.order_by(City.popularity.desc()).limit(3).all()
    return render_template('create_trip.html', recommended_cities=recommended_cities)

@trips_bp.route('/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('trips.dashboard'))
    return render_template('trip_view.html', trip=trip)

@trips_bp.route('/<int:trip_id>/builder', methods=['GET', 'POST'])
@login_required
def trip_builder(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('trips.dashboard'))
        
    if request.method == 'POST':
        # Add stop
        city_id = request.form.get('city_id')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        order_index = len(trip.stops) + 1
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            from database.models import Stop
            new_stop = Stop(
                trip_id=trip.id,
                city_id=city_id,
                start_date=start_date,
                end_date=end_date,
                order_index=order_index
            )
            db.session.add(new_stop)
            db.session.commit()
            flash('Stop added successfully!', 'success')
            return redirect(url_for('trips.trip_builder', trip_id=trip.id))
        except Exception as e:
            flash(f'Error adding stop: {e}', 'danger')
            
    cities = City.query.all()
    return render_template('trip_builder.html', trip=trip, cities=cities)

@trips_bp.route('/search/cities')
@login_required
def search_cities():
    query = request.args.get('q', '')
    if query:
        cities = City.query.filter(City.name.ilike(f'%{query}%')).all()
    else:
        cities = City.query.all()
    return render_template('city_search.html', cities=cities, query=query)

@trips_bp.route('/search/activities')
@login_required
def search_activities():
    stop_id = request.args.get('stop_id', type=int)
    from database.models import Activity, Stop, db
    
    stop = None
    trip_id = None
    if stop_id:
        stop = Stop.query.get(stop_id)
        if stop:
            trip_id = stop.trip_id
            
    query = request.args.get('q', '')
    activities = []
    
    if stop:
        city = stop.city
        existing_activities = Activity.query.filter_by(city_id=city.id).all()
        
        # Lazy Loading Activity Generation
        if len(existing_activities) < 3:
            import random
            templates = [
                ("Historical Center Walking Tour", "Sightseeing"),
                ("Culinary & Street Food Experience", "Food"),
                ("Panoramic Views & Skyline Tour", "Sightseeing"),
                ("Guided Museum & Culture Pass", "Culture"),
                ("Local Market & Shopping Exploration", "Shopping"),
                ("Sunset Cruise or Nature Walk", "Nature")
            ]
            for t_name, t_type in templates:
                act = Activity(
                    city_id=city.id,
                    name=f"{city.name} {t_name}",
                    type=t_type,
                    cost=random.randint(15, 100),
                    duration=random.randint(60, 240),
                    description=f"Experience the best of {city.name} with this curated activity."
                )
                db.session.add(act)
            db.session.commit()
            existing_activities = Activity.query.filter_by(city_id=city.id).all()
            
        activities = existing_activities
        if query:
            activities = [a for a in activities if query.lower() in a.name.lower()]
    else:
        if query:
            activities = Activity.query.filter(Activity.name.ilike(f'%{query}%')).limit(50).all()
        else:
            activities = Activity.query.limit(50).all()
            
    return render_template('activity_search.html', activities=activities, query=query, stop_id=stop_id, trip_id=trip_id)

@trips_bp.route('/<int:trip_id>/stop/<int:stop_id>/add_activity', methods=['POST'])
@login_required
def add_activity_to_stop(trip_id, stop_id):
    activity_id = request.form.get('activity_id')
    from database.models import StopActivity, db
    sa = StopActivity(
        stop_id=stop_id,
        activity_id=activity_id,
        scheduled_time="Anytime"
    )
    db.session.add(sa)
    db.session.commit()
    flash('Activity added to your itinerary!', 'success')
    return redirect(url_for('trips.trip_builder', trip_id=trip_id))

@trips_bp.route('/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    from database.models import db, Trip
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('trips.dashboard'))
        
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted successfully.', 'success')
    return redirect(url_for('trips.my_trips'))

@trips_bp.route('/<int:trip_id>/stop/<int:stop_id>/delete', methods=['POST'])
@login_required
def delete_stop(trip_id, stop_id):
    from database.models import db, Stop, Trip
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('trips.dashboard'))
        
    stop = Stop.query.get_or_404(stop_id)
    if stop.trip_id != trip.id:
        flash('Invalid stop', 'danger')
        return redirect(url_for('trips.trip_builder', trip_id=trip.id))
        
    db.session.delete(stop)
    db.session.commit()
    flash('Stop removed from itinerary.', 'success')
    return redirect(url_for('trips.trip_builder', trip_id=trip.id))
