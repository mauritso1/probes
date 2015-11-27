import basicTrilateration
import sys
from numpy import array
import math


def rssiToDistance(levelInDb, freqInMHz=5200):
    result = (27.55 - (20 * math.log10(freqInMHz)) + math.fabs(levelInDb)) / 20.0
    return math.pow(10, result)


point_data = {
    'a': array([0, 0, 1]),
    'b': array([20, 30, 1]),
    'c': array([20, 0, 65])
     }

distance_data = [6,4,6]

identifiers = [
    'a',
    'b',
    'c'
    ]

point_estimate = basicTrilateration.trilaterateLM(point_data,distance_data,identifiers)

print "POINT ESTIMATE:"
print 'x: %s, y: %s, z: %s' % (point_estimate.params['x'].value, point_estimate.params['y'].value, point_estimate.params['z'].value)
print rssiToDistance(float(sys.argv[1]))
