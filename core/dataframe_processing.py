# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 14 12:00:00 2019

@author: bdaniere

"""
import logging
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd
import pandas as pd
import argparse
import numpy as np
import re

from core import statics_functions

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')

""" Classes / methods / functions """


def geocode_df(df, latitude_field, longitude_field, epsg):
    """
    Transform a DataFrame to GeoDataFrame based on x, y field
    :type df: DataFrame with node type data
    :type latitude_field: Series
    :type longitude_field: Series
    :type epsg: integer
    :return: GeoDataFrame (epsg : epsg)
    """

    logging.info("Geocode json result - nodes")

    geometry = [Point(xy) for xy in zip(df[longitude_field], df[latitude_field])]
    crs = {'init': 'epsg:' + str(epsg)}
    df = df.drop(columns=[longitude_field, latitude_field])

    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    return gdf


def geocode_way(df, node_column, epsg):
    """
    Transform a DataFrame to GeoDataFrame base on 'nodes' fields
    :param df: DataFrame with way type data
    :param node_column: Series contain list of tuple (x,y)
    :param epsg: integer
    :return:
    """
    logging.info("Geocode json result - ways")

    df['geometry'] = df[node_column].apply(lambda x: LineString(x))
    crs = {'init': 'epsg:' + str(epsg)}
    df = df.drop(columns=[node_column])
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=df.geometry)

    return gdf


def geocode_polygon(df, node_column, epsg):
    """
    Transform a DataFrame to GeoDataFrame base on 'nodes' fields
    :param df: DataFrame with way type data
    :param node_column: Series contain list of tuple (x,y)
    :param epsg: integer
    :return:
    """
    logging.info("Geocode json result - polygon")

    df['geometry'] = df[node_column].apply(lambda x: Polygon(x))
    crs = {'init': 'epsg:' + str(epsg)}
    df = df.drop(columns=[node_column])
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=df.geometry)

    return gdf


class DfToGdf:

    def __init__(self, input_dfs):
        self.df_dict = input_dfs

        assert type(self.df_dict) == dict, "DfToGdf class input_data isn't dictionary type"

    def create_geom_column(self):
        """
        Transform json geographic coordinate to Shapely Coordinate (for create gpd.GeoDataFrame)
        :return:
        """

        # 1 / process "node" type data
        if not self.df_dict['node'].empty:
            self.df_dict['node'] = geocode_df(self.df_dict['node'], 'lat', 'lon', 4326)

        # 2 / process 'way' type data
        if not self.df_dict['way'].empty:
            self.df_dict['way'] = geocode_way(self.df_dict['way'], 'nodes', 4326)

        # 2 / process 'way' type data
        if not self.df_dict['polygon'].empty:
            self.df_dict['polygon'] = geocode_polygon(self.df_dict['polygon'], 'nodes', 4326)

    def main(self):

        self.create_geom_column()

        # For each gdf, correct geometry and add index
        for gdf in self.df_dict.values():
            if not gdf.empty:
                try:
                    gdf = statics_functions.create_index(gdf)
                    gdf = statics_functions.clean_gdf_by_geometry(gdf)
                except :
                    import pdb
                    pdb.set_trace()
