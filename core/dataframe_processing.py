# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 14 12:00:00 2019

@author: bdaniere

"""
import logging
from shapely.geometry import Point
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
    :type df: DataFrame
    :type latitude_field: Series
    :type longitude_field: Series
    :type epsg: integer
    :return: GeoDataFrame (epsg : epsg)
    """

    logging.info("Geocode json result")

    geometry = [Point(xy) for xy in zip(df[longitude_field], df[latitude_field])]
    crs = {'init': 'epsg:' + str(epsg)}
    df = df.drop(columns=[longitude_field, latitude_field])

    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    return gdf


def geocode_way(df):
    # create empty DataFrames (with same df columns) for isolate node & line
    node_df = df.loc[df['types'] == 'nodes']
    way_df = df.loc[df['types'] == 'way']

    # create lat & lon column for node_df / geocode lat & lon
    # A voir pour la suite ==> SettingCopyWaringing  // mon premier export est OK mis a part que les geom n'apparaise pas sous Qgis ...
    node_df['lat'] = node_df['nodes'].apply(lambda x: x[0])
    node_df['lon'] = node_df['nodes'].apply(lambda x: x[1])
    node_df = node_df.drop(columns=['nodes'], axis=1)

    node_gdf = geocode_df(node_df, 'lat', 'lon', 4326)

    # process way_df geometry

    import pdb
    pdb.set_trace()


class DfToGdf:

    def __init__(self, input_dfs):
        self.df_dict = input_dfs

        assert type(self.df_dict) == dict, "DfToGdf class input_data isn't dictionary type"

    def main(self):
        # 1 / process "node" type data
        if not self.df_dict['node'].empty:
            self.df_dict['node'] = geocode_df(self.df_dict['node'], 'lat', 'lon', 4326)

        # 2 / process 'way' type data
        if not self.df_dict['way'].empty:
            self.df_dict['way'] = geocode_way(self.df_dict['way'])

        # For each gdf, correct geometry and add index
        for gdf in self.df_dict.values():
            if not gdf.empty:
                gdf = statics_functions.create_index(gdf)
                gdf = statics_functions.clean_gdf_by_geometry(gdf)

        return self.df_dict
