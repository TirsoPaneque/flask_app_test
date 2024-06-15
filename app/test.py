import pandas as pd
import requests

def manhattan_distance(lat1, lon1, lat2, lon2):
    # This function calculates the manhattan distance between two places
    return abs(lat2 - lat1) + abs(lon2 - lon1)

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

API_KEY = '00f95217d3b04a0c9e1af341b4e1608a'
current_csv_path = './data/updated_beaches.csv'
backup_csv = './data/backup.csv'
county = 'Miami'
address = '123 Main Street'
starting_location = get_coordinates(address, county)


df = pd.read_csv(current_csv_path)
starting_location_list = [county, 'Starting Location', starting_location[0], starting_location[1]]
df.loc[len(df.index)] = starting_location_list
distances = []
for index, beach in df.iterrows():
    if beach['NAME'] != 'Starting Location':
        dist = manhattan_distance(starting_location[0], starting_location[1], beach['latitude'], beach['longitude'])
        distances.append({'beach': beach['NAME'], 'distance': dist})

distances.sort(key=lambda x: x['distance'])
closest_beaches = []
for b in range(9):
    closest_beaches.append(distances[b]['beach'])

closest_distances = []
for d in range(9):
    closest_distances.append(distances[d]['distance'])

print(closest_beaches)