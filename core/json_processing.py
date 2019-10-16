# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 15 12:00:00 2019

@author: bdaniere

"""
import logging
from shapely.geometry import Point, LineString
import geopandas as gpd
import pandas as pd
import argparse
import numpy as np
import re

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')
# max colwidth for pd.DataFrame = 250 characters
# max colwidth for pd.DataFrame = 250 characters (limit of dbf type)
pd.set_option('max_colwidth', 250)
pd.set_option('max_columns', 255)
pd.set_option('large_repr', 'truncate')

""" Classes / methods / functions """


def split_initial_data(osm_data):
    """
    Use list comprehension for isolate geographic object (with alpha-numeric attribute)
     & node object (coordonate only)
     & relation object

    :return osm_data_element: list of dict containing data from the overpass request
    :return osm_all_node: list of dict containing all node data from the overpass request (geographical coordinates)
    """
    logging.info(" -- json to df -- split initial data ")

    osm_data_element = [dict_value for dict_value in osm_data['elements'] if
                        ('tags' in dict_value and dict_value['type'] in ['way', 'node'])]
    osm_all_node = {dict_value['id']: (dict_value['lon'], dict_value['lat']) for dict_value in
                    osm_data['elements'] if dict_value['type'] == 'node'}

    osm_data_relation = [dict_value for dict_value in osm_data['elements'] if dict_value['type'] == 'relation']

    return osm_data_element, osm_all_node


def rename_key_tag_to_geom_type(osm_data_element):
    """
    Rename the key 'type' by 'geom_type'
    :param osm_data_element: list of dict containing data from the overpass request
    :return osm_data_element: list of dict containing data from the overpass request (after rename operation)
    """

    logging.info(" -- json to df -- split initial data ")

    def rename_type_key(line):
        """
        sub fucntion for rename key in dict
        """
        line['geom_type'] = line['type']
        del line['type']
        return line

    osm_data_element = [rename_type_key(osm_element) for osm_element in osm_data_element]
    return osm_data_element


def extract_key_tags(osm_data_element):
    """
    Import 'tags' key content in each object & drop 'tags' key - in osm_data_element

    :param osm_data_element: list of dict containing data from the overpass request
    :return: osm_data_element : input osm_data_element with each 'tags' sub-keys in first level of dictionary
    """
    logging.info(" -- json to df -- extraction of alpha-numerical information ")

    [osm_data_element[index].update(osm_data_element[index]['tags']) for index, value in
     enumerate(osm_data_element)]
    for index, element in enumerate(osm_data_element):
        del osm_data_element[index]['tags']

    return osm_data_element


def split_data_by_geom_type(osm_data_element):
    """
    List all unique value in osm_data_element['geom_type']

    :param osm_data_element: list of dict containing data from the overpass request
                            (with each 'tags' sub-keys in first level of dictionary)
    :return osm_data_element_by_geom: dictionary with osm_data_element, separated by geometry type
                                    ( {geom_type : data} )
    """
    logging.info(" -- json to df -- data separation based on geom type ")

    json_geom_type = {data_obj['geom_type'] for data_obj in osm_data_element}
    osm_data_element_by_geom = dict()

    for geom_type in json_geom_type:
        osm_data_element_by_geom[geom_type] = [data_object for data_object in osm_data_element if
                                               data_object['geom_type'] == geom_type]

    return osm_data_element_by_geom


def formatting_way_geom_type(osm_data_element_by_geom, osm_all_node):
    """
    Replace "nodes" value in osm_data_element_by_geom[way] by geographic coordinates
    AND Differentiation of LineString and Polygon rows

    :param osm_data_element_by_geom: dictionary with osm_data_element, separated by geometry type
    :param osm_all_node: list of dict containing all node data from the overpass request (geographical coordinates)
    :return osm_data_element_by_geom['way']: dictionary with osm_data_element, separated by geometry type - "way" type
    """
    logging.info(" -- json to df -- reconstruction of 'way' type geometry ")

    for index_line, content_line in enumerate(osm_data_element_by_geom['way']):
        content_line['nodes'] = [osm_all_node[id_node] for id_node in content_line['nodes']]
        if content_line['nodes'][0] == content_line['nodes'][-1]:
            osm_data_element_by_geom['way'][index_line]['geom_type'] = 'polygon'

    return osm_data_element_by_geom['way']


def split_way_and_polygon(osm_data_element_by_geom):
    """
    Separation of LineString entities from Polygon entities in osm_data_element_by_geom dictionary

    :param osm_data_element_by_geom: dictionary with osm_data_element, separated by geometry type
    :return osm_data_element_by_geom : dictionary with osm_data_element, separated by geometry type
                                        (with polygon key)
    """
    for geom_type in ['polygon', 'way']:
        osm_data_element_by_geom[geom_type] = [data_object for data_object in osm_data_element_by_geom['way'] if
                                               data_object['geom_type'] == geom_type]

    return osm_data_element_by_geom


def json_to_df(osm_data_element_by_geom):
    """
    Transform json to pandas.DataFrame (with unique geometry type)

    :param osm_data_element_by_geom:  dictionary with osm_data_element, separated by geometry type (dict)
    :return osm_data_element_by_geom: dictionary with osm_data_element, separated by geometry type (pd.DataFrame)
    """
    logging.info(" -- json to df -- Transform json formatted to pd.DataFrame")

    for geom_type in osm_data_element_by_geom.keys():
        osm_data_element_by_geom[geom_type] = pd.DataFrame(osm_data_element_by_geom[geom_type])

    return osm_data_element_by_geom


def main(osm_data):
    """
    Transform the overpass query result (json format) to pd.DataFrame
    :param osm_data: result to the OSM request (json format)
    :return: dict of DataFrame -by geom_type-
    """
    logging.info("Transform json result to dict of DataFrame")

    osm_data_element, osm_all_node = split_initial_data(osm_data)
    osm_data_element = rename_key_tag_to_geom_type(osm_data_element)
    osm_data_element = extract_key_tags(osm_data_element)
    osm_data_element_by_geom = split_data_by_geom_type(osm_data_element)
    osm_data_element_by_geom['way'] = formatting_way_geom_type(osm_data_element_by_geom, osm_all_node)
    osm_data_element_by_geom = split_way_and_polygon(osm_data_element_by_geom)
    osm_data_element_by_geom = json_to_df(osm_data_element_by_geom)

    return osm_data_element_by_geom
