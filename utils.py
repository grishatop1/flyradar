from math import sin, cos, sqrt, atan2, radians

# approximate radius of earth in km
def calcDistance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = radians(abs(lat1))
    lon1 = radians(abs(lon1))
    lat2 = radians(abs(lat2))
    lon2 = radians(abs(lon2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance