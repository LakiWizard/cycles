
import pygame
import random


all_events = None

def initialize(screen_width, screen_height):
    pygame.init()
    pygame.mixer.quit()

    screen_surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Cycles")

    return screen_surface

def deinitialize():
    pygame.quit()



p1_input = {"left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s}

p2_input = {"left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN}


class GameMap():
    def __init__(self, w, h):
        self.width = w
        self.height = h

        self.background = pygame.color.Color(0, 0, 0)  # map background is black

        # contains all the players that are on the map
        self.players = []

        # contains all the obstacles on the map
        self.obstacles = []

    def fill_with_obstacles(self, num):
        # randomly put num obstacles on the map
        for i in range(num):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            w = 30
            h = 15

            o = Obstacle(x, y, w, h)
            self.obstacles.append(o)

    def draw(self, screen_surface):
        screen_surface.fill(self.background)


class Obstacle():
    def __init__(self, x, y, w, h):
        # mostly a glorified rectangle
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.color = pygame.color.Color(204, 102, 0)

        # to speed up drawing a bit
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen_surface):
        screen_surface.fill(self.color, self.rect)


class Line():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def point_on_line(x, y, line):
    # check if a point is on a line
    x1 = line.x1
    x2 = line.x2
    y1 = line.y1
    y2 = line.y2

    x_ok = False
    y_ok = False

    if x1 == x2:
        if x == x1:
            x_ok = True

            if y1 > y2:
                if y <= y1 and y >= y2:
                    y_ok = True
            elif y1 < y2:
                if y >= y1 and y <= y2:
                    y_ok = True
            # they are equal
            else:
                if y == y1:
                    y_ok = True

        if x_ok and y_ok:
            return True
        else:
            return False

    if y1 == y2:
        if y == y1:
            y_ok = True

            if x1 > x2:
                if x <= x1 and x >= x2:
                        x_ok = True
            elif x1 < x2:
                if x >= x1 and x <= x2:
                    x_ok = True
            # they are equal
            else:
                if x == x1:
                    x_ok = True

        if x_ok and y_ok:
            return True
        else:
            return False


def is_opposing_direction(d1, d2):
    # check if two directions are opposing

    if (d1, d2) == ("up", "down"):
        return True
    if (d1, d2) == ("down", "up"):
        return True
    if (d1, d2) == ("left", "right"):
        return True
    if (d1, d2) == ("right", "left"):
        return True

    return False


def is_in_rect(x, y, rx, ry, rw, rh):
    """
    rx, ry, ... -> rect values
    """
    # check if a point is within a rect
    x1 = rx
    y1 = ry
    x2 = x1 + rw
    y2 = y1 + rh

    x_ok = False
    y_ok = False

    if x >= x1 and x <= x2:
        x_ok = True
    if y >= y1 and y <= y2:
        y_ok = True

    ok = x_ok and y_ok
    return ok


class Player():
    def __init__(self, x, y, color, game_map):
        self.x = x
        self.y = y
        self.color = color  # pygame.Color object

        self.direction = "up"
        self.input_dict = None

        # the first element will always be the current trail
        self.lines = []

        # hold a reference to the map you are on
        self.game_map = game_map

    def handle_input(self):
        global all_events

        valid_input = self.input_dict.values()
        user_input = None

        for e in all_events:
            if e.type == pygame.KEYDOWN:
                if e.key in valid_input:
                    user_input = e.key
        if user_input is None:
            return None

        reversed_dict = {value: key for key, value in self.input_dict.items()}
        new_direction = reversed_dict[user_input]

        # you cant go in reverse
        if is_opposing_direction(new_direction, self.direction):
            return None

        self.direction = new_direction

        # start new line when changing direction
        self.start_new_line()

    def start_new_line(self):
        new_line = Line(self.x, self.y, self.x, self.y)
        self.lines.insert(0, new_line)

    def check_collision(self):
        status_good = "moving"
        status_crashed = "crashed"

        # check for all the lines
        all_lines = []
        for p in self.game_map.players:
            for line in p.lines:
                all_lines.append(line)

        all_lines.remove(self.lines[0])
        for line in all_lines:
            if point_on_line(self.x, self.y, line):
                return status_crashed

        # check for all the obstacles
        for o in self.game_map.obstacles:
            if is_in_rect(self.x, self.y, o.x, o.y, o.w, o.h):
                return status_crashed

        return status_good

    def update(self):
        status_good = "moving"
        status_crashed = "crashed"

        if self.x < 0 or self.x > self.game_map.width or self.y < 0 or self.y > self.game_map.height:
            return status_crashed

        if len(self.lines) == 0:
            self.start_new_line()
        else:
            current_line = self.lines[0]
            current_line.x2 = self.x
            current_line.y2 = self.y

        collision = self.check_collision()
        if collision == "crashed":
            print("crashed!!!")

        if self.direction == "up":
            self.y -= 1
            return status_good
        elif self.direction == "down":
            self.y += 1
            return status_good
        elif self.direction == "left":
            self.x -= 1
            return status_good
        elif self.direction == "right":
            self.x += 1
            return status_good

    def draw(self, screen_surface):
        for line in self.lines:
            pygame.draw.line(screen_surface, self.color, (line.x1, line.y1), (line.x2, line.y2))
        pygame.draw.circle(screen_surface, self.color, (self.x, self.y), 10, 4)



def draw_all(game_map, screen_surface):
    game_map.draw(screen_surface)

    for p in game_map.players:
        p.draw(screen_surface)

    for o in game_map.obstacles:
        o.draw(screen_surface)

    pygame.display.flip()


def start_level(map_size):
    """
    map_size -> tuple(w, h)
    """
    global p1_input, p2_input

    # start a game level, do all the needed preparations
    # return a GameMap object

    game_map = GameMap(*map_size)

    game_map.fill_with_obstacles(10)

    blue = pygame.color.Color(50, 50, 220)
    red = pygame.color.Color(220, 50, 50)

    p1 = Player(100, 50, blue, game_map)
    p1.input_dict = p1_input
    p2 = Player(500, 350, red, game_map)
    p2.input_dict = p2_input
    players = [p1, p2]

    game_map.players.append(p1)
    game_map.players.append(p2)

    return game_map


def main():
    global all_events

    map_size = (800, 600)

    game_map = start_level(map_size)
    # for now we can assume there are only 2 players
    p1 = game_map.players[0]
    p2 = game_map.players[1]

    screen_surface = initialize(*map_size)

    clock = pygame.time.Clock()

    game_running = True
    while game_running:
        all_events = pygame.event.get()

        for e in all_events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                game_running = False

        p1.handle_input()
        p2.handle_input()
        p1.update()
        p2.update()

        draw_all(game_map, screen_surface)
        clock.tick(60)

    deinitialize()


main()
