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
    gmaps = googlemaps.Client(key='AIzaSyCeoTnfT0MwM8M2sU9amxCZUBxr1Fn_RSQ')
    client_key = 'AIzaSyCeoTnfT0MwM8M2sU9amxCZUBxr1Fn_RSQ'
    ''' Break path into 512 points per segment '''
    # API Limit = 512 locations per request
    path_segments = []
    polyline_encoded_segments = []
    for chunk in chunks(lat_lon_coords, 400):
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
        elevation_results = []
        for resultset in response['results']:
            elevation_results.append(resultset['elevation'])
        pass

def main(lat_lon_coords):
    lat_lon_elevation  = get_elevation_data(lat_lon_coords)

if __name__ == '__main__':
    # Open KML and extract Lat-lon coords:
    with open('ASC2016.kml', 'r') as fp:
        doc = fp.read()
    print(doc)
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

