from math import sin, cos, sqrt, atan2, radians

# approximate radius of earth in km
def calcDistance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def calculateZone(distance):
		tl_y = coords["lat"] + distance
		tl_x = coords["lon"] - distance
		br_y = coords["lat"] - distance
		br_x = coords["lon"] + distance

		return {
			"tl_y": tl_y,
			"tl_x": tl_x,
			"br_y": br_y,
			"br_x": br_x
		}

def calculateZoneOverpy(distance):
	south_edge = coords["lat"] - distance
	north_edge = coords["lat"] + distance
	west_edge = coords["lon"] - distance
	east_edge = coords["lon"] + distance
	return {
		"s": south_edge,
		"n": north_edge,
		"w": west_edge,
		"e": east_edge
	}