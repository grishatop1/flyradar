from math import sin, cos, sqrt, atan2, radians
import pygame
from settings import *

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

def drawDecorations(font1, win, box_size_km):
	pygame.draw.line(
		win,
		(127,127,127),
		(0, HALF_HEIGHT),
		(WIDTH, HALF_HEIGHT),
		1
	)

	pygame.draw.line(
		win,
		(127,127,127),
		(HALF_WIDTH, 0),
		(HALF_WIDTH, HEIGHT),
		1
	)

	txt = font1.render(
		f"{int(box_size_km)}km receiving box",
		True,
		(255,255,255)
	)
	win.blit(txt, (HALF_WIDTH + CIRCLE_R + 5, HALF_HEIGHT + 5))

	#on each side of the screen, make north south east and west text
	txt = font1.render(
		"N",
		True,
		(255,255,255)
	)
	win.blit(txt, (HALF_WIDTH-txt.get_width()/2, 0))

	txt = font1.render(
		"S",
		True,
		(255,255,255)
	)
	win.blit(txt, (HALF_WIDTH-txt.get_width()/2, HEIGHT-txt.get_height()))

	txt = font1.render(
		"E",
		True,
		(255,255,255)
	)
	win.blit(txt, (WIDTH-txt.get_width()/2-(HALF_HEIGHT/3), HALF_HEIGHT-txt.get_height()/2))

	txt = font1.render(
		"W",
		True,
		(255,255,255)
	)
	win.blit(txt, (HALF_WIDTH-txt.get_width()/2-HALF_HEIGHT, HALF_HEIGHT-txt.get_height()/2))