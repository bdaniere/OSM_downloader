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


def json_result_to_df(osm_data):
    """
    Transform the overpass query result (json format) to geopandas.GeoDataFrame
    :param osm_data: result to the OSM request (json format)
    :return: GeoDataFrame
    """
    logging.info("Transform json result to dict of DataFrame")

    # Use list comprehension for isolate geographic object & node object
    osm_data_element = [dict_value for dict_value in osm_data['elements'] if 'tags' in dict_value]
    osm_all_node = [dict_value for dict_value in osm_data['elements'] if dict_value['type'] == 'node']

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

    def id_to_coordinate(index_node, node_id, index_obj):
        """
        Function allowing to replace the identifiers of the nodes by their geographical coordinates
        (contained in osm_all_node list)

        :param index_node: index of actual osm_data_element_by_geom['way'][content_line][nodes]
        :param node_id: id of actual osm_data_element_by_geom['way'][content_line][nodes]
        :param index_obj: index of actual osm_data_element_by_geom['way']
        """

        for osm_node in osm_all_node:
            if osm_node['id'] == node_id:
                way_element[index_obj]['nodes'][index_node] = osm_node['lon'], osm_node['lat']

    [id_to_coordinate(index_id_node, id_node, index_line) for index_line, content_line in enumerate(way_element) for
     index_id_node, id_node in enumerate(content_line['nodes'])]


    # Transform json to pandas.DataFrame (with unique geometry type)
    for geom_type in osm_data_element_by_geom.keys():
        osm_data_element_by_geom[geom_type] = pd.DataFrame(osm_data_element_by_geom[geom_type])

    return osm_data_element_by_geom




def main(file):
    # Read Json parameter with ArgParse argument
    arg = statics_functions.parse_arguments()

    # Read osm query file / execute overpass request / tranform result to DataFrame dict
    file_content = read_osm_request(arg.overpass_query)
    osm_data = execute_overpass_request(file_content)
    gdf_data_dict = json_result_to_df(osm_data)

    toto_obj = dataframe_processing.DfToGdf(gdf_data_dict)
    toto_obj.main()

    if arg.output is not None:
        for gdf_name, gdf in toto_obj.df_dict.items():
            if gdf.empty is False:
                statics_functions.formatting_gdf_for_shp_export(gdf, ch_dir + "/output/", gdf_name)


""" PROCESS """

if __name__ == "__main__":
    main(temp_file)
