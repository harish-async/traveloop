from flask import Blueprint, jsonify
from database.models import City

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/countries', methods=['GET'])
def get_countries():
    # Get distinct countries
    countries = [result[0] for result in City.query.with_entities(City.country).distinct().all()]
    return jsonify({'countries': sorted(countries)})

@api_bp.route('/cities/<country>', methods=['GET'])
def get_cities(country):
    cities = City.query.filter_by(country=country).order_by(City.name).all()
    city_data = [{'id': c.id, 'name': c.name, 'cost_index': c.cost_index} for c in cities]
    return jsonify({'cities': city_data})
