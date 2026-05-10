from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database.models import User, Trip
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def user_profile():
    today = datetime.now().date()
    past_trips = Trip.query.filter(Trip.user_id == current_user.id, Trip.end_date < today).all()
    future_trips = Trip.query.filter(Trip.user_id == current_user.id, Trip.start_date >= today).all()
    
    return render_template('profile.html', user=current_user, past_trips=past_trips, future_trips=future_trips)

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    from flask import request, flash, redirect, url_for
    from database.models import db
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        current_user.phone_number = request.form.get('phone_number', current_user.phone_number)
        current_user.city = request.form.get('city', current_user.city)
        current_user.country = request.form.get('country', current_user.country)
        current_user.bio = request.form.get('bio', current_user.bio)
        
        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('profile.settings'))
        
    return render_template('settings.html', user=current_user)

@profile_bp.route('/public/trip/<int:trip_id>')
def public_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if not trip.is_public:
        return "This itinerary is private.", 403
    return render_template('trip_view.html', trip=trip, is_public=True)

@profile_bp.route('/admin')
@login_required
def admin_dashboard():
    # Simplistic admin check
    if current_user.email != 'admin@traveloop.com':
        return "Access Denied. You must be an admin.", 403
        
    total_users = User.query.count()
    total_trips = Trip.query.count()
    return render_template('admin.html', total_users=total_users, total_trips=total_trips)
