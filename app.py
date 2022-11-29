import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
#from geopy.geocoders import Nominatim


################################################################################
# SETUP
################################################################################

app = Flask(__name__)


load_dotenv()

pp = PrettyPrinter(indent=4)


################################################################################
# ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)


def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'


@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    units = request.args.get('units')
    api_key = os.getenv('API_KEY')
    API_URL = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={api_key}'

    result_json = requests.get(API_URL).json()

    pp.pprint(result_json)

    datetime_object = (datetime.now()).strftime('%A, %B %d, %Y')

    context = {
        'date': datetime_object,
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')
    city1_data = compare_city_info(city1, units)
    city2_data = compare_city_info(city2, units)
    datetime_object = (datetime.now()).strftime('%A, %B, %d, %Y')

    context = {
        'city1': city1_data,
        'city2': city2_data,
        'units_letter': get_letter_for_units(units),
        'date': datetime_object,
        'city1_sunset': datetime.fromtimestamp(city1_data['sys']['sunset']),
        'city2_sunset': datetime.fromtimestamp(city2_data['sys']['sunset'])
    }

    return render_template('comparison_results.html', **context)


def compare_city_info(city, units):
    '''Helper function comparing 2 cities'''
    api_key = os.getenv('API_KEY')
    response = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={api_key}')
    data = response.json()
    return data


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
