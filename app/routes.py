from flask import Flask, Blueprint, request, jsonify, send_from_directory, current_app as app
import pandas as pd
import numpy as np
import requests
import atexit
import shutil
from model import *

API_KEY = '00f95217d3b04a0c9e1af341b4e1608a'
current_csv_path = './data/updated_beaches.csv'
backup_csv = './data/backup.csv'

main = Blueprint('main', __name__)
app = Flask(__name__, static_folder='static', template_folder='templates')

# Up to this point we imported the libraries and defined some global variables for later use

def get_coordinates(address, county, state="Florida"):
    # This function is gonna retrieve the latitude and longitude of the places
    
    place_name = f"{address}, {county} County, {state}"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={place_name}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        location = data['results'][0]['geometry']
        return (location['lat'], location['lng'])
    else:
        return (None, None)

def reverse_geocode(lat, lon):
    # This function is gonna do the opposite as the one before, giving us a place name by its position
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        return data['results'][0]['formatted']
    else:
        return None


def manhattan_distance(lat1, lon1, lat2, lon2):
    # This function calculates the manhattan distance between two places
    return abs(lat2 - lat1) + abs(lon2 - lon1)

def backup_data(current_data_loc, backup_data_loc):
    # This function is about making sure our data remains intact after the user finishes, that way they can find new beaches without going back
    shutil.copyfile(current_data_loc, backup_data_loc)

# This line runs the previous function when the user finishes their session without
atexit.register(lambda: backup_data(current_csv_path, backup_csv))

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/calculate-route', methods=['POST'])
def calculate_route():
    # This is going to be our main function where all the magic is gonna happen

    # This first few lines are gonna read the input from the user
    data = request.json
    address = data.get('address')
    county = data.get('county')

    if not address or not county:
        return jsonify({'error': 'Address, and county are required.'}), 40
    
    # This lines are gonna give us the location of the user
    starting_location = get_coordinates(address, county)
    if starting_location == (None, None):
        return jsonify({'error': 'Invalid starting location'}), 40
    
    # Now we move on to data preprocessing
    df = pd.read_csv(current_csv_path)
    starting_location_list = [county, 'Starting Location', starting_location[0], starting_location[1]]
    df.loc[len(df.index)] = starting_location_list
    distances = []
    for index, beach in df.iterrows():
        if beach['NAME'] != 'Starting Location':
            dist = manhattan_distance(starting_location[0], starting_location[1], beach['latitude'], beach['longitude'])
            distances.append({'beach': beach['NAME'], 'distance': dist})

    # This next few lines are gonna collect us the distances and save them along with the beaches names
    distances.sort(key=lambda x: x['distance'])
    closest_beaches = []
    for b in range(9):
        closest_beaches.append(distances[b]['beach'])

    closest_distances = []
    for d in range(9):
        closest_distances.append(distances[d]['distance'])


    return jsonify({
        'closest_beaches': closest_beaches,
        'distance': closest_distances
    })

    # return jsonify({"county": 'Mirabel condao',
    #                 'address': address})


if __name__ == '__main__':
    app.run(debug=True)