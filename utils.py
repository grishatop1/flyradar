from math import sin, cos, sqrt, atan2, radians
import pygame

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

def pitagor(x1, y1, x2, y2):
	return sqrt((x2-x1)**2 + (y2-y1)**2)

class Triangle():
	def __init__(self):
		self.ANGLE_MOD = radians(135)
		self.SIZE_MOD = 5
		self.s = None

	def setSurface(self, surface):
		self.s = surface

	def render(self, heading, x, y, color):
		self.heading = heading
		self.X, self.Y = x, y
		self.color = color
		self.corners = self.setCorners()

		pygame.draw.polygon(self.s, self.color, self.corners)

	def setCorners(self):
		front = [cos(self.heading),
							sin(self.heading)]
		sideA = [cos(self.heading-self.ANGLE_MOD),
							sin(self.heading-self.ANGLE_MOD)]
		sideB = [cos(self.heading+self.ANGLE_MOD),
							sin(self.heading+self.ANGLE_MOD)]

		corners = [front, sideA, sideB]

		for corner in corners:
			corner[0]*=self.SIZE_MOD
			corner[1]*=self.SIZE_MOD
			corner[0]+=self.X-self.SIZE_MOD+1
			corner[1]+=self.Y-self.SIZE_MOD+1

		return corners
