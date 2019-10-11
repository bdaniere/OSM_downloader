# -*- coding: utf-8 -*-
"""
Created on thu Oct 11 11:00:00 2019

@author: bdaniere

"""

import requests
import geopandas as gpd
import pandas as pd
import json
import logging
import requests
import os

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')
ch_dir = os.getcwd().replace('\\', '/')

# temp variable
temp_file = "osm_rquest.txt"

""" Classes / methods / functions """


def read_osm_request(file):
    """
    Reading the file containing the overpass request
    :param file: path to the file containing the overpass request
    :return: file content
    """
    # Rajouter des controles sur la validité de la requête
    with open(file, 'r') as osm_request_file:
        osm_request = osm_request_file.read()

    assert len(osm_request) != 0, "The query file is empty "
    return osm_request


def execute_overpass_request(overpass_query):
    """
    Sending the request to OSM and recovering data
    source https://towardsdatascience.com/loading-data-from-openstreetmap-with-python-and-the-overpass-api-513882a27fd0

    :param overpass_query:
    :return:
    """
    # Rajouter des controle pour s'assurer que le resultat est non vide
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': overpass_query})

    data = response.json()

    return data


def main(file):
    file_content = read_osm_request(file)
    osm_data = execute_overpass_request(file_content)

    import pdb;
    pdb.set_trace()


if __name__ == "__main__":
    main(temp_file)
