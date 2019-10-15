# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 11 11:00:00 2019

@author: bdaniere

"""

import pandas as pd
import geopandas as gpd
import logging
import requests
import os

from core import statics_functions
from core import dataframe_processing

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')
ch_dir = os.getcwd().replace('\\', '/')

# max colwidth for pd.DataFrame = 250 characters
# max colwidth for pd.DataFrame = 250 characters (limit of dbf type)
pd.set_option('max_colwidth', 250)
pd.set_option('max_columns', 255)
pd.set_option('large_repr', 'truncate')

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


def json_result_to_df(osm_data):
    """
    Transform the overpass query result (json format) to geopandas.GeoDataFrame
    :param osm_data: result to the OSM request (json format)
    :return: GeoDataFrame
    """
    logging.info("Transform json result to dict of DataFrame")

    # Use list comprehension for isolate geographic object & node object
    osm_data_element = [dict_value for dict_value in osm_data['elements'] if 'tags' in dict_value]
    osm_all_node = {dict_value['id']: (dict_value['lon'], dict_value['lat']) for dict_value in osm_data['elements'] if
                    dict_value['type'] == 'node'}

    # import 'tags' key content in each object & drop 'tags' key
    [osm_data_element[index].update(osm_data_element[index]['tags']) for index, value in enumerate(osm_data_element)]
    for index, element in enumerate(osm_data_element):
        del osm_data_element[index]['tags']

    # list all unique value in osm_data_element['type']
    json_geom_type = {data_obj['type'] for data_obj in osm_data_element}
    osm_data_element_by_geom = dict()
    for geom_type in json_geom_type:
        osm_data_element_by_geom[geom_type] = [data_object for data_object in osm_data_element if
                                               data_object['type'] == geom_type]

    # replace "nodes" key in osm_data_element_by_geom[way] by geographic coordinates
    way_element = osm_data_element_by_geom['way']
    for index_line, content_line in enumerate(way_element):
        content_line['nodes'] = [osm_all_node[id_node] for id_node in content_line['nodes']]

    # Transform json to pandas.DataFrame (with unique geometry type)
    for geom_type in osm_data_element_by_geom.keys():
        osm_data_element_by_geom[geom_type] = pd.DataFrame(osm_data_element_by_geom[geom_type])

    return osm_data_element_by_geom


def main():
    # Read Json parameter with ArgParse argument
    arg = statics_functions.parse_arguments()

    # Read osm query file / execute overpass request / tranform result to DataFrame dict
    file_content = read_osm_request(arg.overpass_query)
    osm_data = execute_overpass_request(file_content)
    gdf_data_dict = json_result_to_df(osm_data)

    output_gdf = dataframe_processing.DfToGdf(gdf_data_dict)
    output_gdf.main()

    if arg.output is not None:
        for gdf_name, gdf in output_gdf.df_dict.items():
            if gdf.empty is False:
                statics_functions.formatting_gdf_for_shp_export(gdf, ch_dir + "/output/", gdf_name)


""" PROCESS """

if __name__ == "__main__":
    main()
