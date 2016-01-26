import basicTrilateration
import sys
from numpy import array
import math


point_data = {
    'HG655D': array([0, 0, 0]),
    '710Nr': array([20, 30, 0]),
    '710Nm': array([0, 60, 0])
     }


identifiers = [
    'HG655D',
    '710Nr',
    '710Nm'
    ]


def rssi_to_distance(rssi): 
    return 10**((rssi + 55.0)/-20.0)


def trilaterate_rssi(rssi_dict):
    distance_data = [rssi_to_distance(rssi_dict[router_id]) for router_id in identifiers]
    point_estimate = basicTrilateration.trilaterate(point_data, distance_data, identifiers)
    return point_estimate[0], point_estimate[1]


