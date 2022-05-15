WIDTH = 1024
HEIGHT = 768
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

CIRCLE_R = HALF_HEIGHT - 20 #radius
CIRCLE_CENTER = (HALF_WIDTH, HALF_HEIGHT) #x,y

ZONE = 0.5
RENDER_MULTIPLIER = CIRCLE_R / ZONE #pixels per km

REFRESH_SECS = 1
FPS = 60

TOADD = 3.1415*2/FPS / 5 #5 seconds