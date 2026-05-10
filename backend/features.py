from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import db, Trip, Expense, ChecklistItem, Note

features_bp = Blueprint('features', __name__)

def check_trip_access(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return None
    return trip

@features_bp.route('/trips/<int:trip_id>/budget', methods=['GET', 'POST'])
@login_required
def budget(trip_id):
    trip = check_trip_access(trip_id)
    if not trip:
        return redirect(url_for('trips.dashboard'))

    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        description = request.form.get('description')
        
        try:
            expense = Expense(trip_id=trip.id, category=category, amount=float(amount), description=description)
            db.session.add(expense)
            db.session.commit()
            flash('Expense added.', 'success')
        except:
            flash('Invalid amount.', 'danger')
        return redirect(url_for('features.budget', trip_id=trip.id))
        
    total_cost = sum(e.amount for e in trip.expenses)
    return render_template('budget.html', trip=trip, total_cost=total_cost)

@features_bp.route('/trips/<int:trip_id>/checklist', methods=['GET', 'POST'])
@login_required
def checklist(trip_id):
    trip = check_trip_access(trip_id)
    if not trip:
        return redirect(url_for('trips.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            item_name = request.form.get('item_name')
            new_item = ChecklistItem(trip_id=trip.id, item_name=item_name)
            db.session.add(new_item)
        elif action == 'toggle':
            item_id = request.form.get('item_id')
            item = ChecklistItem.query.get(item_id)
            if item and item.trip_id == trip.id:
                item.is_packed = not item.is_packed
        
        db.session.commit()
        return redirect(url_for('features.checklist', trip_id=trip.id))
        
    return render_template('checklist.html', trip=trip)

@features_bp.route('/trips/<int:trip_id>/notes', methods=['GET', 'POST'])
@login_required
def notes(trip_id):
    trip = check_trip_access(trip_id)
    if not trip:
        return redirect(url_for('trips.dashboard'))

    if request.method == 'POST':
        content = request.form.get('content')
        new_note = Note(trip_id=trip.id, content=content)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('features.notes', trip_id=trip.id))
        
    return render_template('notes.html', trip=trip)
