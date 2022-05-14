import os
import json
import time
import overpy
import threading
from FlightRadar24.api import FlightRadar24API

import math
from math import cos, sin, atan2

from utils import calcDistance

from copy import copy

import pygame

class FlightManager:
	def __init__(self):
		self.flights = {}
		self.render_flights = {}
		self.zone = calculateZone(ZONE)
		self.bounds = fr_api.get_bounds(self.zone)

		threading.Thread(target=self.getFlightsThread, daemon=True).start()

	def getFlightsThread(self):
		#later filter certain attributes
		while True:
			self.flights = fr_api.get_flights(bounds = self.bounds)
			print(len(self.flights))
			time.sleep(REFRESH_SECS)

	def decideFlights(self):
		flights = copy(self.flights)
		for f in flights:
			f_x = f.longitude
			f_y = f.latitude

			r_x = coords["lon"] - f_x
			r_y = coords["lat"] - f_y


			r_x = r_x * RENDER_MULTIPLIER
			r_y = r_y * RENDER_MULTIPLIER


			r_x *= -1

			f_angle = atan2(r_y, r_x)

			r_x += HALF_WIDTH
			r_y += HALF_HEIGHT


			if r_x < 0 or r_x > WIDTH or r_y < 0 or r_y > HEIGHT:
				print("out of screen")


			#if angle >= f_angle and angle < f_angle + 1:
			self.render_flights[f.id] = {
				"aircraft": f.number,
				"time": time.time(),
				"x": r_x,
				"y": r_y,
				"angle": f_angle,
				"f_x": f_x,
				"f_y": f_y
			}

	def renderPlanes(self):
		render_time = 4 #secs max 5 (main line rotating speed)
		for _id in copy(self.render_flights):
			f = self.render_flights[_id]
			start = f["time"]
			now = time.time()
			total = now-start


			if total >= render_time:
				del self.render_flights[_id]
				continue

			c = max(0, 255-255*(total/render_time))
			color = (0,c,0)
			pygame.draw.circle(win, color, (f["x"], f["y"]), 5, 4)

			txt = font1.render(
				f"{f['aircraft']}",
				True,
				color
			)
			win.blit(txt, (f["x"]+5, f["y"]+5))
			dist = calcDistance(coords["lat"], coords["lon"], f["f_y"], f["f_x"])

			txt = font1.render(
				f"{dist:.2f}km",
				True,
				color
			)
			win.blit(txt, (f["x"]+5, f["y"]+25))

class RoadManager:
	def __init__(self):
		self.roads = {}
		self.render_roads = {}
		self.zone = calculateZoneOverpy(ZONE)
		self.roads = self.getRoads()
		
	def getRoads(self):
		z = self.zone
		query = f"""
			[out:json][timeout:25];
			(
			way["highway"="primary"]({z["s"]},{z["w"]},{z["n"]},{z["e"]});
			);
			out body;
			>;
			out skel qt;
			"""
		res = over_api.query(query)
		print(res)

os.makedirs("cache", exist_ok=True)

with open('coords.json') as f:
	coords = json.load(f)["coords"]

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

WIDTH = 1024
HEIGHT = 768
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

CIRCLE_R = HALF_HEIGHT - 20 #radius
CIRCLE_CENTER = (HALF_WIDTH, HALF_HEIGHT) #x,y

RENDER_MULTIPLIER = CIRCLE_R * 2
ZONE = 0.05
CIRCLE_R_KM = calcDistance(coords["lat"], coords["lon"], coords["lat"], coords["lon"] + ZONE)

REFRESH_SECS = 2
FPS = 60

angle = 0
toAdd = math.pi*2/FPS / 5 #5 seconds

over_api = overpy.Overpass()
fr_api = FlightRadar24API()

f_mngr = FlightManager()
r_mngr = RoadManager()

pygame.init()
clock = pygame.time.Clock()

pygame.font.init()
font1 = pygame.font.SysFont('Arial', 15)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Radar")

running = True
while running:
	d = clock.tick(FPS)
	win.fill((0, 0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	if angle >= math.pi*2:
		angle = 0

	f_mngr.decideFlights()
	f_mngr.renderPlanes()

	pygame.draw.circle(win, (0,255,0), CIRCLE_CENTER, CIRCLE_R, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R/3, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R/3*2, 1)

	p_r = CIRCLE_R
	p_x = p_r * cos(angle) + CIRCLE_CENTER[0]
	p_y = p_r * sin(angle) + CIRCLE_CENTER[1]
	pygame.draw.line(win, (0,255,0), CIRCLE_CENTER, (p_x, p_y), 1) #main lajna


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
		f"{int(CIRCLE_R_KM)}km radius",
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

	pygame.display.update()
	angle += toAdd

pygame.quit()
quit()
