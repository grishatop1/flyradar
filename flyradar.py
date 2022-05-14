import os
import json
import time
import overpy
import hashlib
import threading
from FlightRadar24.api import FlightRadar24API

import math
from math import cos, sin, atan2, radians

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
		while True:
			self.flights = fr_api.get_flights(bounds = self.bounds)
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
				pass


			#if angle >= f_angle and angle < f_angle + 1:
			self.render_flights[f.id] = {
				"aircraft": f.number,
				"time": time.time(),
				"x": r_x,
				"y": r_y,
				"angle": f_angle,
				"f_x": f_x,
				"f_y": f_y,
				"heading": f.heading
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

			heading = radians(f["heading"]-90)
			pygame.draw.line(win, (40,40,50), (f["x"], f["y"]), (f["x"] + cos(heading)*1000, f["y"] + sin(heading)*1000), 1)

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
		self.checkCache()
		self.preRenderRoads()

	def checkCache(self):
		zone_hash = hashlib.md5(json.dumps(self.zone).encode()).hexdigest()
		if os.path.exists(f"cache/{zone_hash}.json"):
			with open(f"cache/{zone_hash}.json", "r") as f:
				self.roads = json.load(f)
		else:
			print("Getting road data in your region...")
			self.roads = self.getRoads()
			with open(f"cache/{zone_hash}.json", "w") as f:
				json.dump(self.roads, f)

	def getRoads(self):
		z = self.zone
		query = f"""
			[out:json];
			(
			way["highway"="primary"]({z["s"]},{z["w"]},{z["n"]},{z["e"]});
			);
			out body;
			>;
			out skel qt;
			"""
		res = over_api.query(query)
		
		roads = {}

		for way in res.ways:
			roads[way.id] = {}
			for n in way.nodes:
				roads[way.id][n.id] = {
					"lat": float(n.lat),
					"lon": float(n.lon)
				}
		
		return roads

	def preRenderRoads(self):
		s = pygame.Surface((WIDTH, HEIGHT))
		s.fill((0,0,0))

		for _id in self.roads:
			road = self.roads[_id]
			for i in range(len(road.values())):
				l = list(road.values())
				n_lat = l[i]["lat"]
				n_lon = l[i]["lon"]
				r_x = (n_lon - coords["lon"])
				r_y = (n_lat - coords["lat"])
				r_y *= -1
				r_x *= RENDER_MULTIPLIER
				r_y *= RENDER_MULTIPLIER
				r_x += HALF_WIDTH
				r_y += HALF_HEIGHT

				if (pitagor(HALF_WIDTH, HALF_HEIGHT, r_x, r_y) > CIRCLE_R):
					continue

				if i+1 < len(road.values()):
					n_lat2 = l[i+1]["lat"]
					n_lon2 = l[i+1]["lon"]
					r_x2 = (n_lon2 - coords["lon"])
					r_y2 = (n_lat2 - coords["lat"])
					r_y2 *= -1
					r_x2 *= RENDER_MULTIPLIER
					r_y2 *= RENDER_MULTIPLIER
					r_x2 += HALF_WIDTH
					r_y2 += HALF_HEIGHT
					

					pygame.draw.line(s, (65,65,65), (r_x, r_y), (r_x2, r_y2), 2)
		self.s = s

	def renderRoads(self):
		win.blit(self.s, (0,0))

os.makedirs("cache", exist_ok=True)

with open('coords.json') as f:
	coords = json.load(f)["coords"]

def pitagor(x1, y1, x2, y2):
	return math.sqrt((x2-x1)**2 + (y2-y1)**2)

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

ZONE = 0.5
CIRCLE_R_KM = calcDistance(coords["lat"], coords["lon"], coords["lat"], coords["lon"] + ZONE)
RENDER_MULTIPLIER = CIRCLE_R / ZONE #pixels per km

REFRESH_SECS = 1
FPS = 60

angle = 0
toAdd = math.pi*2/FPS / 5 #5 seconds

over_api = overpy.Overpass()
fr_api = FlightRadar24API()

r_mngr = RoadManager()
f_mngr = FlightManager()


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

	r_mngr.renderRoads()

	pygame.draw.circle(win, (0,255,0), CIRCLE_CENTER, CIRCLE_R, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R/3, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R/3*2, 1)

	f_mngr.renderPlanes()

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
