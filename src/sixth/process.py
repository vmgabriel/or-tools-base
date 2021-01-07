"""
Module for connection with google for solve VRP
"""

# Libraries
from __future__ import division
from __future__ import print_function
from typing import List
from csv import reader
import requests
import json
import urllib


def read_csv(file_path: str, delimiter: str = ',') -> List[str]:
    """
    Read a file csv

    file_path: str -> Route of file ej: "./a/b/c.csv"
    delimiter: str -> delimiter for csv ej
    return [[],[],[],[]]
    """
    with open(file_path) as csv_file:
        csv_reader = reader(csv_file, delimiter=delimiter)
        return list(map(lambda x: x[0], list(csv_reader)[1:]))


def create_data() -> dict:
    """get all data"""
    data = {}
    file_path = 'src/sixth/data.csv'
    data['API_KEY'] = ''
    data['addreses'] = read_csv(file_path)
    return data


def send_request(origin_addresses, dest_addresses, API_key):
    """
    Build and send request for the given origin
    and destination addresses.
    """
    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    request += '?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
        dest_address_str + '&key=' + API_key
    # jsonResult = urllib.urlopen(request).read()
    response = json.loads(jsonResult)
    return response


def build_distance_matrix(response):
    """build distance matrix"""
    distance_matrix = []
    for row in response['rows']:
        row_list = [
            row['elements'][j]['distance']['value']
            for j in range(len(row['elements']))
        ]
        distance_matrix.append(row_list)
    return distance_matrix


def create_distance_matrix(data):
    """Create distence matrix"""
    addresses = data["addresses"]
    API_key = data["API_key"]
    # Distance Matrix API only accepts 100 elements per request, so get rows in
    # multiple requests.
    max_elements = 100
    num_addresses = len(addresses)  # 16 in this example.
    # Maximum number of rows that can be computed per request
    # (6 in this example).
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

        # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix


def run():
    """Run and solve the problem"""
    # create the data
    data = create_data()

    # Verify the distance
    distance_matrix = create_distance_matrix(data)
    print(distance_matrix)
