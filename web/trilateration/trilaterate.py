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

distance_data = [170, 150, 170]


def rssiToDistance(levelInDb, freqInMHz=2460):
    result = (27.55 - (20 * math.log10(freqInMHz)) + math.fabs(levelInDb)) / 25.0
    return math.pow(10, result)


#print "POINT ESTIMATE:"
#print 'x: %s, y: %s, z: %s' % (point_estimate.params['x'].value, point_estimate.params['y'].value, point_estimate.params['z'].value)
#print rssiToDistance(float(sys.argv[1]))
