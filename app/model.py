"""
Note! Use the original updated_beaches.csv rather than my new updated2_beaches.csv.

Note from Tirso: Imported the json library since u didnt had it. Changed your preprocessing code and took it out since
the point is to have the data preprocessed from the notebook, before we run the site, set a standar value of 9 for the 
number of beaches we are getting and also commented your final lines since i only need the functions by themselves.
"""

import pandas as pd
from geopy.distance import geodesic
import numpy as np
from scipy.spatial.distance import squareform, pdist
import random
from itertools import permutations
import json

def preprocess(file_path):
    
    """
    Preprocesses csv dataset.
    """
    
    filtered_df = pd.read_csv(file_path)
    
    # Zip this data into coordinates
    filtered_df['coordinates'] = list(zip(filtered_df['latitude'], filtered_df['longitude']))
    filtered_df = filtered_df.drop(['latitude', 'longitude'], axis=1)
    
    # Deal with duplicates
    filtered_df = filtered_df.drop([63, 30, 113, 109, 85, 147, 32]) # Duplicate names, not actually beach locations
    filtered_df.drop_duplicates(inplace=True)
    filtered_df = filtered_df[filtered_df['NAME']!='UNSURVEYED'] # Missing name
    filtered_df = filtered_df[filtered_df['COUNTY']!= 'SARASOAT'] # Typo
    filtered_df = filtered_df.drop_duplicates(subset='coordinates') # Drop duplicate coordinates

    return filtered_df
    

# Function to calculate the nearest n beaches from the starting beach
def calculate_nearest_beaches(df, starting_beach, n):
    
    """
    Calculate nearest n beaches from starting beach, using geodesic distance between lat/long coordinates.
    
    Inputs: 
        - df: DataFrame of all beach data, 
        - starting_beach: string, precise name of starting beach according to provided df
        - n: int, number of nearest beaches to calculate

    Output:
        - DataFrame containing name of beach and geodesic distance (in miles) from starting beach
    """
    
    starting_beach_coord = df[df.NAME == starting_beach.upper()].coordinates.iloc[0]
    df = df.copy()
    df['geodesic_distance'] = df['coordinates'].apply(lambda x: geodesic(starting_beach_coord, x).miles)
    df = df.sort_values(by='geodesic_distance', ascending=True).head(n + 1)
    return df[['NAME', 'coordinates', 'geodesic_distance']]

# Function to calculate the distance matrix
def calculate_distance_matrix(df):
    
    """
    Calculate distance matrix between every point in a dataframe.

    Input:
        - Dataframe, including coordinates
    Output:
        - Distance matrix (list of lists, including distance from each point to every other point)
    """
    
    coords = df['coordinates'].tolist()
    distance_matrix = squareform(pdist(coords, lambda u, v: geodesic(u, v).miles))
    return distance_matrix

# Nearest Neighbor Algorithm to find the optimal route and calculate total distance
def nearest_neighbor_algorithm(distance_matrix):
    
    """
    Uses Nearest Neighbor algorithm to find a good route.

    Input: 
        - Distance matrix (list of lists, including distance from each point to every other point)
    Output:
        - Route (list of location names)
        - Total distance (miles)
        - Distances (list of distances between each location, miles)
    """
    
    n = len(distance_matrix)
    visited = [False] * n
    route = [0]  # Start from the initial location
    visited[0] = True
    total_distance = 0.0
    distances = []

    for _ in range(1, n):
        last_visited = route[-1]
        next_city = np.argmin([distance_matrix[last_visited][j] if not visited[j] else float('inf') for j in range(n)])
        route.append(next_city)
        visited[next_city] = True
        distance = round(distance_matrix[last_visited][next_city], 2)
        distances.append(distance)
        total_distance += distance

    return route, total_distance, distances
    
def calculate_random_route(distance_matrix):
    
    """
    Uses randomization to calculate a baseline route.

    Input: 
        - Distance matrix (list of lists, including distance from each point to every other point)
    Output:
        - Route (list of location names)
        - Total distance (miles)
        - Distances (list of distances between each location, miles)    
    """
    
    n = len(distance_matrix)
    route = list(range(1, n))  # Start from the second location
    random.shuffle(route)
    route = [0] + route  # Add the starting location at the beginning
    total_distance = 0.0
    distances = []

    for i in range(n - 1):
        distance = distance_matrix[route[i]][route[i + 1]]
        distances.append(f"{distance:.2f}")
        total_distance += distance

    return route, total_distance, distances

# Brute Force Algorithm to find the optimal route and calculate total distance
def calculate_brute_force_route(distance_matrix):

    """
    Uses a brute force approach to find the best route.

    Input: 
        - Distance matrix (list of lists, including distance from each point to every other point)
    Output:
        - Route (list of location names)
        - Total distance (miles)
        - Distances (list of distances between each location, miles)   
    """
    
    n = len(distance_matrix)
    min_distance = float('inf')
    best_route = None
    best_distances = []

    for perm in permutations(range(1, n)):
        current_route = [0] + list(perm)
        current_distance = 0.0
        distances = []

        for i in range(n - 1):
            distance = distance_matrix[current_route[i]][current_route[i + 1]]
            distances.append(f"{distance:.2f}")
            current_distance += distance

        # Complete the route by returning to the starting point
        total_distance = current_distance

        if total_distance < min_distance:
            min_distance = total_distance
            best_route = current_route
            best_distances = distances

    return best_route, min_distance, best_distances

# Main function to call the other functions and get the optimal route and total distance
def calculate_closest_route(df, starting_beach, n=9, algorithm='nearest neighbors'):
    
    """
    Calculate optimal route from start to finish, calling other functions. Choose between performance/efficiency levels.

    Inputs: 
        - df: DataFrame of all location data
        - starting_beach: string, precise name of starting location/beach according to provided df
        - n: int, number of nearest locations to calculate. Refer to algorithm parameter for guidance on maximum size of n.
        - algorithm: string, one of three options:
            - 'nearest neighbors': best value of performance and efficiency (n has no upper limit)
            - 'random': most efficient, but poor performance (baseline model, n has no upper limit)
            - 'brute force': highest performance, lowest efficiency (n cannot exceed 9 without massive performance loss)
    Outputs:
        - optimal route: ordered list of locations, beginning with starting location
        - total distance: float, total distance traveled from starting location to final location, miles
        - distances: ordered list of distances between each location, miles
    """
    
    nearest_beaches = calculate_nearest_beaches(df, starting_beach, n)
    distance_matrix = calculate_distance_matrix(nearest_beaches)
    
    if algorithm.lower() == 'nearest neighbors':
        route_indices, total_distance, distances = nearest_neighbor_algorithm(distance_matrix)
    if algorithm.lower() == 'random':
        route_indices, total_distance, distances = calculate_random_route(distance_matrix)
    if algorithm.lower() == 'brute force':
        route_indices, total_distance, distances = calculate_brute_force_route(distance_matrix)
    
    optimal_route = nearest_beaches.iloc[route_indices]
    
    route = optimal_route.NAME.tolist()
    distances = [float(d) for d in distances]  # Convert distances to float
    
    return route, distances, round(total_distance, 2)
    # result = {
    #     'optimal_route_sequence': route,
    #     'distances_between_beaches': distances,
    #     'total_distance': round(total_distance, 2)
    # }
    
    # return json.dumps(result, indent=4)
    
    # print(f'Optimal route sequence: {route}\n')
    # print(f'Distance between each beach: {distances} miles.\n')
    # print(f'Total distance of route: {total_distance:.2f} miles.')
    
    # return optimal_route, total_distance, distances
""" 
if __name__ == "__main__":
    # Load the filtered DataFrame
    filtered_df = pd.read_csv('updated_beaches.csv')
    
    # User input for starting beach and number of additional beaches
    starting_beach = input("Enter the starting beach: ")
    n = int(input("Enter the number of additional beaches: "))
    
    # Calculate the route using the desired algorithm
    result_json = calculate_closest_route(filtered_df, starting_beach, n, algorithm='brute force')

    print(result_json) """