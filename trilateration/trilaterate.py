import basicTrilateration
import sys
from numpy import array
import math

point_data = {
    '710Nr': array([0, 20, 0]),
    '710Nm': array([50, 0, 0]),
    'HG655D': array([40, 30, 0])
     }


#def rssiToDistance(levelInDb, freqInMHz=2460):
#    result = (18 - (20 * math.log10(freqInMHz)) + math.fabs(levelInDb)) / 20.0
#    return math.pow(10, result)

def toDistance(rssi):
    return 10**((rssi+55.0)/-20.0)


distance_data = [10, 20, 40]

identifiers = [
    '710Nr',
    '710Nm',
    'HG655D'
    ]

point_estimate = basicTrilateration.trilaterateLM(point_data,distance_data,identifiers)

#print "POINT ESTIMATE:"
print 'x: %s, y: %s, z: %s' % (point_estimate.params['x'].value, point_estimate.params['y'].value, point_estimate.params['z'].value)
#print rssiToDistance(float(sys.argv[1]))
