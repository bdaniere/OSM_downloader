# -*- coding: utf-8 -*-
# Python 3
"""
Created on thu Oct 11 11:00:00 2019

@author: bdaniere

"""
import logging
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import argparse
import numpy as np
import re

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')

""" Classes / methods / functions """


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("overpass_query", help="Input file contain overpass querry")
    parser.add_argument("-o", "--output", help="shapefile output path ")
    parser.add_argument("-t", "--territory", help="territory to use for process")

    return parser.parse_args()


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


def dbf_max_columns(gdf):
    """
    DBF files can not have more than 255 fields: deleting fields that exceed this constraint
    :param gdf: gpd.GeoDataFrame() with x columns
    :return gdf: gpd.GeoDataFrame() with x columns (max 255)
    """
    # drop empty columns
    gdf = gdf.dropna(how='all', axis=1)

    if len(gdf.columns) >= 255:
        logging.warning("-- formatting before export : DBF file constraint:" \
                        "the column limit is 255 - deletion of the last x columns")
        output_column = list(gdf.columns[:254])
        if 'geometry' not in [output_column]:
            output_column.append('geometry')

        gdf = gdf[output_column]

    return gdf


def formatting_gdf_for_shp_export(gdf, output_path, gdf_name):
    """ Formatting GeoDataFrame for export & export to shp
     :type gdf: GeoDataFrame
     :param output_path: complete path for the shapefile export
     :param output_name: name for the shapefile export
     """
    logging.info('formatting & export GeoDataFrame')

    gdf = dbf_max_columns(gdf)

    # shp constraint : max length of string value = 245
    geometry = gdf.geometry.copy()
    gdf = gdf.astype(str).apply(lambda x: x.str[:253])
    gdf.geometry = geometry

    for gdf_column in gdf.columns:
        # if type(gdf[gdf_column][gdf.index.min()]) == np.bool_:
        #     gdf[gdf_column] = gdf[gdf_column].astype(str)
        # if type(gdf[gdf_column][gdf.index.min()]) == pd._libs.tslib.Timestamp:
        #     gdf[gdf_column] = gdf[gdf_column].astype(str)
        if len(gdf_column) > 10:
            gdf = gdf.rename(columns={gdf_column: gdf_column[:10]})
            gdf_column = gdf_column[:10]
        if bool(re.search(':', gdf_column)):
            gdf = gdf.rename(columns={gdf_column: gdf_column.replace(":", "_")})

    gdf.to_file("{}/{}.shp".format(output_path, gdf_name), encoding='utf-8')


def clean_gdf_by_geometry(gdf):
    """ Clean a GeoDataFrame : drop null / invalid / empty geometry """

    logging.info("drop null & invalid & duplicate geometry")

    # Check geometry validity
    invalid_geometry = gdf[gdf.geometry.is_valid == False].count().max()
    if invalid_geometry > 0:
        gdf = gdf[gdf.geometry.is_valid == True]
        logging.info("We found and drop {} invalid geometry".format(invalid_geometry))
        logging.warning("these buildings will not be integrated into the PostGis output table")

    # check empty geometry
    null_geometry = gdf[gdf.geometry.is_valid == True].count().max()
    if null_geometry > 0:
        gdf = gdf[gdf.geometry.is_empty == False]

    # Check duplicates geometry
    unique_geometry = gdf.geometry.astype(str).nunique()
    number_duplicate_geometry = gdf.geometry.count() - unique_geometry

    if unique_geometry != gdf.geometry.count():
        wkb_geometry = gdf["geometry"].apply(lambda geom: geom.wkb)
        gdf = gdf.loc[wkb_geometry.drop_duplicates().index]

    logging.info("We found and drop {} duplicates geometry".format(number_duplicate_geometry))
    assert unique_geometry == gdf.geometry.count(), "Geometry problem in the input data: the deleted entity" \
                                                    "number is greater than the duplicate entity number"

    return gdf


def create_index(gdf):
    """ Increment index if ther are null or not_unique """

    if gdf.index.isnull().sum() > 0 or gdf.index.is_unique == False:
        gdf.index = range(1, len(gdf) + 1)
    return gdf
