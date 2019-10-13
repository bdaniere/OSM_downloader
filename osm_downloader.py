# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 11 11:00:00 2019

@author: bdaniere

"""

import pandas as pd
import logging
import requests
import os

from core import statics_functions

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')
ch_dir = os.getcwd().replace('\\', '/')

# temp variable
temp_file = "osm_request.txt"

""" Classes / methods / functions """


def read_osm_request(file):
    """
    Reading the file containing the overpass request
    :param file: path to the file containing the overpass request
    :return: file content
    """
    logging.info("Read input osm_request file")
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
    logging.info("Execute overpass query")

    # Rajouter des controle pour s'assurer que le resultat est non vide
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    return data


def json_result_to_gdf(osm_data):
    """
    Transform the overpass query result (json format) to geopandas.GeoDataFrame
    :param osm_data: result to the OSM request (json format)
    :return: GeoDataFrame
    """
    logging.info("Transform json result to GeoDataFrame")

    # add key 'tags' in key 'element
    for index, line in enumerate(osm_data['elements']):
        for keys in line['tags'].keys():
            osm_data['elements'][index][keys] = line['tags'][keys]

        del osm_data['elements'][index]['tags']

    # Transform json to pandas.DataFrame
    osm_data_df = pd.DataFrame(osm_data['elements'])
    osm_data_gdf = statics_functions.geocode_df(osm_data_df, 'lat', 'lon', 4326)

    # Check the data quality & create basic index
    osm_data_gdf = statics_functions.create_index(osm_data_gdf)
    osm_data_gdf = statics_functions.clean_gdf_by_geometry(osm_data_gdf)

    return osm_data_gdf


def main(file):
    # Read Json parameter with ArgParse argument
    arg = statics_functions.parse_arguments()

    file_content = read_osm_request(arg.overpass_query)
    osm_data = execute_overpass_request(file_content)
    gdf_data = json_result_to_gdf(osm_data)

    if arg.output is not None:
        statics_functions.formatting_gdf_for_shp_export(gdf_data, ch_dir + "/output/", arg.output)


""" PROCESS """

if __name__ == "__main__":
    main(temp_file)
