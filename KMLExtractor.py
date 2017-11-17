"""
KMLExtractor.py
"""
# from fastkml import kml
import polyline
import re
import googlemaps
from datetime import datetime
import numpy as np
from urllib import parse
from urllib import request
import simplejson
from geopy.distance import vincenty
import pickle
import pandas as pd
from pathlib import Path

__author__ = 'Chris Campell'
__version__ = "9/29/2017"

ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json'

def chunks(l, n):
    """
    chunks: Breaks the specified list into slices of size 'n'.
    :param l: The list to partition by 'n'.
    :param n: The size of the partition.
    :return generator: A generator iterating over partitions of size 'n' from the specified input list.
    """
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_elevation_data(lat_lon_coords, **elvtn_args):
    df_route = pd.DataFrame(columns=['Lat','Lon','Elv'])
    gmaps = googlemaps.Client(key='AIzaSyCeoTnfT0MwM8M2sU9amxCZUBxr1Fn_RSQ')
    client_key = 'AIzaSyCeoTnfT0MwM8M2sU9amxCZUBxr1Fn_RSQ'
    ''' Break path into 512 points per segment '''
    # API Limit = 512 locations per request
    path_segments = []
    elevation_results = []
    polyline_encoded_segments = []
    for chunk in chunks(lat_lon_coords, 512):
        path_segments.append(chunk)
        path_string = ''
        for segment in path_segments:
            for lat, lon in segment:
                path_string = path_string + str(lat) + ',' + str(lon) + '|'
        # Remove the pipe character from the last coordinate:
        path_string = path_string[0:-1]
        elvtn_args.update({
            'path': path_string,
            'samples': str(1)
        })
        # Build the request url:
        url = ELEVATION_BASE_URL + '?locations=enc:' + polyline.encode(chunk, 5) + '&key=' + client_key
        response = simplejson.load(request.urlopen(url=url))
        elevation_result = []
        for resultset in response['results']:
            elevation_result.append(resultset['elevation'])
        elevation_results.append(elevation_result)
    i = 0
    for segment_id, segment in enumerate(path_segments):
        j = 0
        for lat, lon in segment:
            df_route.loc[i] = pd.Series({'Lat': lat, 'Lon': lon, 'Elv': elevation_results[segment_id][j]})
            j += 1
            i += 1
    return df_route


def vincenty_df_series(series):
    """
    vincenty_df_series: Wrapper for geopy's vincenty distance function; computes the vincenty distance on a pd.Series
        object.
    :param series: The dataframe series for which vincenty is to be applied too.
    :return:
    """
    return vincenty(series[1], series[0]).meters


def main(lat_lon_coords):
    route = Path('df_route.pkl')
    if route.is_file():
        df_route = pd.read_pickle(str(route))
    else:
        df_route = get_elevation_data(lat_lon_coords)
        df_route.to_pickle('df_route.pkl')
    # TODO: https://stackoverflow.com/questions/23151246/iterrows-pandas-get-next-rows-value
    # TODO: Create new df with start_lat, start_lon and do next_lat, next_lon in a single row.
    #   Then apply vincenty func. map to each row.
    lat_lon_df = df_route[['Lat','Lon']].join(df_route[['Lat','Lon']].shift(), how='left', lsuffix='_left', rsuffix='_right')
    # Zip the original columns into a tuple (lat, lon)
    lat_lon_df['LatLon_Left'] = list(zip(lat_lon_df.Lat_left, lat_lon_df.Lon_left))
    del(lat_lon_df['Lat_left'])
    del(lat_lon_df['Lon_left'])
    # Zip the offset columns into a tuple (lat, lon)
    lat_lon_df['LatLon_Right'] = list(zip(lat_lon_df.Lat_right, lat_lon_df.Lon_right))
    del(lat_lon_df['Lat_right'])
    del(lat_lon_df['Lon_right'])
    # remove the first row:
    lat_lon_df = lat_lon_df.iloc[1:]
    # Apply vincenty(LatLon_Right, LatLon_Left).meters to each row:
    lat_lon_df['vincenty_dist_meters'] = lat_lon_df.apply(vincenty_df_series, axis=1)
    pass

if __name__ == '__main__':
    # Open KML and extract Lat-lon coords:
    with open('ASC2016.kml', 'r') as fp:
        doc = fp.read()
    split_doc = doc.split('\n')
    no_spaces = [i.replace(' ', '') for i in split_doc]
    regex = re.compile('^(\-?\d+(\.\d+)?),(\-?\d+(\.\d+)?)', re.MULTILINE)
    lat_lon_coords = []
    for line in no_spaces:
        if regex.match(line):
            lon = line.split(',')[0]
            lat = line.split(',')[1]
            lat_lon_coords.append((float(lat), float(lon)))
    main(lat_lon_coords)

