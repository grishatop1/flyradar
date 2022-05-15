from settings import *

import os
import json
import time
import math
import hashlib
import threading

from math import cos, sin, atan2, radians
from utils import *
from copy import copy

import pygame
import overpy
from FlightRadar24.api import FlightRadar24API
import airportsdata

airports = airportsdata.load('IATA')

class FlightManager:
	def __init__(self):
		self.flights = []
		self.render_flights = {}
		self.zone = calculateZone(ZONE)
		self.bounds = fr_api.get_bounds(self.zone)
		self.triangle = Triangle()

		threading.Thread(target=self.getFlightsThread, daemon=True).start()

	def getFlightsThread(self):
		while True:
			self.flights = fr_api.get_flights(bounds = self.bounds)
			time.sleep(REFRESH_SECS)

	def decideFlights(self):
		flights = copy(self.flights)
		for f in flights:
			#if angle >= f_angle and angle < f_angle + 1:
			self.render_flights[f.id] = [
				f, time.time()
			]

	def offsetPlanes(self, f_x, f_y):
		fr_x = coords["lon"] - f_x
		fr_y = coords["lat"] - f_y
		r_x = fr_x * RENDER_MULTIPLIER
		r_y = fr_y * RENDER_MULTIPLIER
		r_x *= -1
		f_angle = atan2(r_y, r_x)
		r_x += HALF_WIDTH
		r_y += HALF_HEIGHT
		return [fr_x,fr_y,r_x,r_y,f_angle]

	def renderPlanes(self):
		render_time = 4 #secs max 5 (main line rotating speed)
		render_f = copy(self.render_flights)
		remove_selection = True
		for _id, (f, start) in render_f.items():
			now = time.time()
			total = now-start

			if total >= render_time:
				del self.render_flights[_id]
				continue

			f_x = f.longitude
			f_y = f.latitude

			fr_x, fr_y, r_x, r_y, f_angle = self.offsetPlanes(f_x, f_y)

			if pitagor(m_x, m_y, r_x, r_y) < 10:
				if m1:
					i_panel.selectFlight(f.id)
					remove_selection = False
				pygame.draw.circle(win, (255,255,255), (r_x-3,r_y-3), 10,2)

			#if r_x < 0 or r_x > WIDTH or r_y < 0 or r_y > HEIGHT:
			#	pass
			c = max(0, 255-255*(total/render_time))

			if f.on_ground:
				c = 127

			color = (0,c,0)

			heading = radians(f.heading-90)

			pygame.draw.line(win, (40,40,50),
			(r_x, r_y),
			(r_x + cos(heading)*1000, r_y + sin(heading)*1000), 1)

			self.triangle.render(heading, r_x, r_y, color)

			txt = font1.render(
				f"{f.callsign}",
				True,
				color
			)
			win.blit(txt, (r_x+5, r_y+5))
			dist = calcDistance(coords["lat"], coords["lon"], f_y, f_x)

			txt = font1.render(
				f"{dist:.2f}km",
				True,
				color
			)
			win.blit(txt, (r_x+5, r_y+25))

		if remove_selection and m1:
			i_panel.deselect()

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

class InfoPanel:
	def __init__(self):
		self.SIZE = ()
		self.f_selected = None
		self.info = [
			["Latitude", "latitude"],
			["Longitude", "longitude"],
			["Heading", "heading"],
			["Callsign", "callsign"],
			["Aircraft", "aircraft_code"],
			["Ground speed", "ground_speed"],
			["From", "origin_airport_iata"],
			["To", "destination_airport_iata"]
		]
		self.surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)

	def selectFlight(self, f):
		self.f_selected = f

	def deselect(self):
		self.f_selected = None

	def draw(self):
		self.surf.fill((0,0,0,0))
		offset_y = 5
		margin = 3
		max_width = 0
		try:
			f = f_mngr.render_flights[self.f_selected][0]
		except KeyError:
			self.deselect()
			return

		fr_x, fr_y, r_x, r_y, f_angle = f_mngr.offsetPlanes(f.longitude, f.latitude)

		pygame.draw.circle(win, (255,255,255), (r_x-3,r_y-3), 10,2)

		for info, f_info in self.info:
			data = getattr(f, f_info)
			if f_info == "heading":
				data = degrees_to_cardinal(data)
			elif f_info == "origin_airport_iata":
				try:
					data = airports(data)
				except:
					continue
			elif f_info == "destination_airport_iata":
				try:
					data = airports(data)
				except:
					continue
			txt = font1.render(
				f"{info}: {data}",
				True,
				(0,255,0)
			)
			self.surf.blit(txt, (5, offset_y))
			offset_y += txt.get_height() + margin
			if txt.get_width() > max_width:
				max_width = txt.get_width()

		pygame.draw.rect(self.surf, (0,255,0),
			(0, 0, max_width + 10, offset_y + 5), 5
		)

	def update(self):
		if not self.f_selected:
			return
		self.draw()
		win.blit(self.surf, (0,0))

os.makedirs("cache", exist_ok=True)

if not os.path.exists("coords.json"):
	print("Please set your coordinates in coords.json")
	with open("coords.json", "w") as f:
		data = {
			"coords": {
				"lat": 0,
				"lon": 0
			}
		}
		json.dump(data, f)
	exit()
else:
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

angle = 0

over_api = overpy.Overpass()
fr_api = FlightRadar24API()

r_mngr = RoadManager()
f_mngr = FlightManager()
i_panel = InfoPanel()

box_size_km = calcDistance(coords["lat"], coords["lon"], coords["lat"] + ZONE, coords["lon"] + ZONE)

pygame.init()
clock = pygame.time.Clock()

pygame.font.init()
font1 = pygame.font.SysFont('Arial', 15)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Radar")

f_mngr.triangle.setSurface(win)


running = True
while running:
	d = clock.tick(FPS)
	win.fill((0, 0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	m_x, m_y = pygame.mouse.get_pos()
	m1, m_scroll, m2 = pygame.mouse.get_pressed()

	if angle >= math.pi*2:
		angle = 0

	f_mngr.decideFlights()

	r_mngr.renderRoads()

	pygame.draw.circle(win, (0,255,0), CIRCLE_CENTER, CIRCLE_R, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R//3, 1)
	pygame.draw.circle(win, (90,90,90), CIRCLE_CENTER, CIRCLE_R//3*2, 1)

	f_mngr.renderPlanes()

	p_r = CIRCLE_R
	p_x = p_r * cos(angle) + CIRCLE_CENTER[0]
	p_y = p_r * sin(angle) + CIRCLE_CENTER[1]

	drawDecorations(font1, win, box_size_km)
	pygame.draw.line(win, (0,255,0), CIRCLE_CENTER, (p_x, p_y), 1) #main lajna

	i_panel.update()

	pygame.display.update()
	angle += TOADD

pygame.quit()
quit()
