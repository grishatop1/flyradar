import sys
import time
import socket
import random
import threading
import subprocess

import math
from math import cos, sin

from copy import copy

import pygame

def ping(ip):
	result = ''
	try:
		response = subprocess.check_output(
			['ping', '-c', '1', ip],
			stderr=subprocess.STDOUT,  # get all output
			universal_newlines=True  # return string not bytes
		)
		for word in response.split():
			if "time=" in word:
				result = word.strip("time=ms")
	except subprocess.CalledProcessError:
		result = 999999999999
	return int(float(result))


class PingManager:
	def __init__(self, ips):
		self.ips = ips
		self.info = {}
		self.rendercircles = {}

		for i, ip in enumerate(self.ips):
			angle = i*(628/len(self.ips))/100 + math.pi/6
			self.info[ip] = {}
			self.info[ip]["angle"] = angle
			self.info[ip]["last_ms"] = 0
			self.info[ip]["render_ms"] = 0

	def spawnThreads(self):
		for ip in self.ips:
			threading.Thread(target=self.pingThread, args=(ip,)).start()

	def pingThread(self, ip):
		start = time.time()
		result = ping(ip)
		end = time.time()
		total = (end-start)
		if total < REFRESH_SECS:
			self.info[ip]["last_ms"] = result

	def decideIps(self):
		for ip in self.info:
			if self.info[ip]["last_ms"] > CIRCLE_R:
				continue
			if angle >= self.info[ip]["angle"] and angle < self.info[ip]["angle"] + 0.2:
				self.info[ip]["render"] = time.time()

	def renderIps(self):
		render_time = 4 #secs max 5 (main line rotating speed)
		for ip in copy(self.info):
			if not "render" in self.info[ip]:
				continue
			if self.info[ip]["render"] is False:
				continue

			start = self.info[ip]["render"]
			now = time.time()
			total = now-start

			if self.info[ip]["render_ms"]:
				p_r = self.info[ip]["render_ms"]
			else:
				p_r = self.info[ip]["last_ms"]
				self.info[ip]["render_ms"] = p_r


			if total >= render_time:
				self.info[ip]["render"] = False
				self.info[ip]["render_ms"] = None
				continue

			p_angle = self.info[ip]["angle"]
			if self.info[ip]["render_ms"] >= 150:
				p_r *= 1.25
			elif 150 > self.info[ip]["render_ms"] >= 100:
				p_r *= 1.5
			elif 100 > self.info[ip]["render_ms"] >= 50:
				p_r *= 1.75
			else:
				p_r *= 2
			p_x = p_r * cos(p_angle) + CIRCLE_CENTER[0]
			p_y = p_r * sin(p_angle) + CIRCLE_CENTER[1]

			c = max(0, 255-255*(total/render_time))
			color = (0,c,0)
			pygame.draw.circle(win, color, (p_x, p_y), 5, 4)

			txt = font1.render(
				f"{ip} {self.info[ip]['render_ms']}ms",
				True,
				color
			)
			win.blit(txt, (p_x+5, p_y+5))

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

REFRESH_SECS = 1

angle = 0
toAdd = math.pi*2/FPS / 5 #5 seconds

ips = sys.argv[1:]
ping_manager = PingManager(ips)

ping_mngr_elapsed = 2500
revolutions = 0

running = True
while running:
	d = clock.tick(FPS)
	win.fill((0, 0, 0))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	ping_mngr_elapsed += d

	if ping_mngr_elapsed > REFRESH_SECS*1000: # 0.5s
		ping_manager.spawnThreads()
		ping_mngr_elapsed = 0

	if angle >= math.pi*2:
		angle = 0

	ping_manager.decideIps()
	ping_manager.renderIps()

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

	pygame.display.update()
	angle += toAdd

pygame.quit()
quit()
