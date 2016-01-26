one_metre_rssi = -45
length = 24.1
width = 18.6


pythagoras = lambda a, b: sqrt(a**2 + b**2)
rssi_to_distance = lambda rssi: 10**((rssi - one_metre_rssi)/-25.0)
distance_to_rssi = lambda d: -10 * 2.5 * log10(d) + one_metre_rssi


point_data = {
    'HG655D': array([14, length, 0]),
    '710Nr': array([0, 11.5, 0]),
    '710Nm': array([17, 0, 0])
     }
identifiers = [
    'HG655D',
    '710Nr',
    '710Nm',
    ]
max_rssi = {
    'HG655D': distance_to_rssi(pythagoras(14, width)),
    '710Nr': distance_to_rssi(pythagoras(length, 11.5)),
    '710Nm': distance_to_rssi(pythagoras(17, width))
    }


def trilaterate(distance_dict):
    distance_data = [distance_dict[router_id] for router_id in identifiers]
    point_estimate = basicTrilateration.trilaterateLM(point_data, distance_data, identifiers)
    return point_estimate