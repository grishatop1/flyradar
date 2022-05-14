import sys
import json
import time
import threading
from FlightRadar24.api import FlightRadar24API

import math
from math import cos, sin, atan2

from copy import copy

import pygame

fr_api = FlightRadar24API()

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


class FlightManager:
	def __init__(self):
		self.flights = {}
		self.render_flights = {}
		self.zone = calculateZone(0.3)
		print(self.zone)
		self.bounds = fr_api.get_bounds(self.zone)

		self.render_multiplayer = 400

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

			r_x = r_x * self.render_multiplayer
			r_y = r_y * self.render_multiplayer

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
				"angle": f_angle
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

pygame.init()
FPS = 60
clock = pygame.time.Clock()

pygame.font.init()
font1 = pygame.font.SysFont('Arial', 15)

WIDTH = 1024
HEIGHT = 768
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Radar")

CIRCLE_R = HALF_HEIGHT - 20 #radius
CIRCLE_CENTER = (HALF_WIDTH, HALF_HEIGHT) #x,y

REFRESH_SECS = 2

angle = 0
toAdd = math.pi*2/FPS / 5 #5 seconds

f_mngr = FlightManager()

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
	win.blit(txt, (HALF_WIDTH-txt.get_width()/2, HALF_HEIGHT-txt.get_height()/2))

	txt = font1.render(
		"W",
		True,
		(255,255,255)
	)
	win.blit(txt, (HALF_WIDTH-txt.get_width()/2, HALF_HEIGHT-txt.get_height()/2))

	pygame.display.update()
	angle += toAdd

pygame.quit()
quit()
