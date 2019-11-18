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
from core import json_processing

"""
Globals variables 
"""
logging.basicConfig(level=logging.INFO, format="%(asctime)s -- %(levelname)s -- %(message)s")
ch_dir = os.getcwd().replace("\\", "/")

""" Classes / methods / functions """


############## TO DO ##############
# Voir pour virer le texte ou le formater pour qu'il soit un poil plus jolie 
# En sortie : uniquement des way et des nodes ... pas cool
#   => virer les nodes du process
# 
def recover_territory(territory_name):

    osm_territoy_request = f"""
    	[out:json];
		(
	    	relation
			  ["boundary"="administrative"]
			  ["name:en"="{territory_name}"];

				);
		(._;>;);
		out;
		"""

    territory_data = execute_overpass_request(osm_territoy_request)
    territory_data_dict = json_processing.main(territory_data)
    territory_gdf = dataframe_processing.DfToGdf(territory_data_dict)
    territory_gdf.main()
    import pdb; pdb.set_trace()



############## ############## ##############


def read_osm_request(file):
    """
    Reading the file containing the overpass request
    :param file: path to the file containing the overpass request
    :return: file content
    """
    logging.info("Read input osm_request file")
    # Rajouter des controles sur la validité de la requête

    with open(file, "r") as osm_request_file:
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
    response = requests.get(overpass_url, params={"data": overpass_query})
    data = response.json()

    return data


def main():
    # Read Json parameter with ArgParse argument
    arg = statics_functions.parse_arguments()

    # Read osm query file / execute overpass request / tranform result to DataFrame dict
    file_content = read_osm_request(arg.overpass_query)
    osm_data = execute_overpass_request(file_content)
    gdf_data_dict = json_processing.main(osm_data)

    output_gdf = dataframe_processing.DfToGdf(gdf_data_dict)
    output_gdf.main()

    if arg.output is not None:
        for gdf_name, gdf in output_gdf.df_dict.items():
            if gdf.empty is False:
                statics_functions.formatting_gdf_for_shp_export(
                    gdf, ch_dir + "/output/", gdf_name
                )

    ### Testing territory filter
    if arg.territory is not None:
        recover_territory(arg.territory)


""" PROCESS """

if __name__ == "__main__":
    main()
