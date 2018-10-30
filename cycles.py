
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
    def __init__(self, x, y, w, h):
        # these are the original measures, which will no be changed
        self.orig_x = x
        self.orig_y = y
        self.orig_width = w
        self.orig_height = h
        self.orig_rect = pygame.Rect(x, y, w, h)

        # these may be changed by shrink_map
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        # full background and background for the still-existing parts
        self.full_bkg = pygame.color.Color(204, 102, 0)
        self.field_bkg = pygame.color.Color(0, 0, 0)

        # the rect, for drawing
        self.rect = pygame.Rect(x, y, w, h)

        # contains all the players that are on the map
        self.players = []

        # contains all the obstacles on the map
        self.obstacles = []

    def shrink(self, num):
        # reduce the map width and height by num
        self.width -= num
        self.height -= num
        self.x += num // 2
        self.y += num // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def fill_with_obstacles(self, num):
        # randomly put num obstacles on the map
        for i in range(num):
            x = random.randint(self.x, self.width)
            y = random.randint(self.y, self.height)
            w = 30
            h = 15

            o = Obstacle(x, y, w, h)
            self.obstacles.append(o)

    def draw(self, screen_surface):
        screen_surface.fill(self.full_bkg, self.orig_rect)
        screen_surface.fill(self.field_bkg, self.rect)

        for p in self.players:
            p.draw(screen_surface)

        for o in self.obstacles:
            o.draw(screen_surface)


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

        # count your own score
        self.score = 0

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

        map_x = self.game_map.x
        map_y = self.game_map.y
        map_w = self.game_map.width
        map_h = self.game_map.height
        if self.x < map_x or self.x > map_x+map_w or self.y < map_y or self.y > map_y+map_h:
            return status_crashed

        if len(self.lines) == 0:
            self.start_new_line()
        else:
            current_line = self.lines[0]
            current_line.x2 = self.x
            current_line.y2 = self.y

        collision = self.check_collision()
        if collision == "crashed":
            return status_crashed

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



class TopBar():
    def __init__(self, x, y, w, h, font_object, p1, p2):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font_object

        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.light_grey = pygame.Color(210, 210, 210)

        self.rect = pygame.Rect(x, y, w, h)

        # the player objects, used for counting the scores
        self.p1 = p1
        self.p2 = p2

        self.p1_color = p1.color
        self.p2_color = p2.color

    def draw(self, screen_surface, shrink_counter, fps_rate):
        screen_surface.fill(self.black, self.rect)

        pos1 = (self.x, self.y+self.h)
        pos2 = (self.x+self.w, self.y+self.h)
        pygame.draw.line(screen_surface, self.white, pos1, pos2, 3)

        text_x = self.x+5
        text_height = self.font.size("whatever")[1]

        text1 = self.font.render("Cycles", False, self.light_grey)
        screen_surface.blit(text1, (text_x, self.y))

        text_x += 10

        # essentialy drawing the scores where the text is colored
        # the players' colors and the actual numbers are white.
        # it is indeed needlesly complicated, but pygame seems
        # to have no easy way of drawing multi-colored text.
        text2 = self.font.render("P1 score:", False, self.p1_color)
        screen_surface.blit(text2, (text_x, self.y+text_height*2))
        score1_x = self.font.size("P1 score:")[0] + text_x
        score1 = self.font.render(str(self.p1.score), False, self.white)
        screen_surface.blit(score1, (score1_x, self.y+text_height*2))

        text3 = self.font.render("P2 score:", False, self.p2_color)
        screen_surface.blit(text3, (text_x, self.y+text_height*3))
        score2_x = self.font.size("P2 score:")[0] + text_x
        score2 = self.font.render(str(self.p2.score), False, self.white)
        screen_surface.blit(score2, (score2_x, self.y+text_height*3))

        # show how many seconds to map reduction
        counter_x = self.x + self.w - 200
        counter_y = self.y + self.h - 30
        seconds = int(shrink_counter / fps_rate)
        counter_text = self.font.render("Reducing in: {}".format(seconds), False, self.white)
        screen_surface.blit(counter_text, (counter_x, counter_y))



def pause_game(screen_surface, font, screen_size):
    white = pygame.Color(255, 255, 255)
    text1 = font.render("Press P to continue", False, white)

    text_x = screen_size[0] // 2 - 80
    text_y = screen_size[1] // 2

    screen_surface.blit(text1, (text_x, text_y))
    pygame.display.flip()

    clock = pygame.time.Clock()

    pressed = False
    while not pressed:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                pressed = True

        clock.tick(10)

def end_game_dialog(screen_surface, font, screen_size):
    white = pygame.Color(255, 255, 255)

    text1 = font.render("(F)inish game or (r)ematch?", False, white)

    text_x = screen_size[0] // 2 - 135
    text_y = screen_size[1] // 2

    screen_surface.blit(text1, (text_x, text_y))
    pygame.display.flip()

    clock = pygame.time.Clock()

    response = None
    while response is None:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_f:
                    response = "finish"
                if e.key == pygame.K_r:
                    response = "rematch"

        clock.tick(10)

    return response


def start_level(p1, p2):
    """
    map_size -> tuple(w, h)
    """
    # start a game level, do all the needed preparations
    # return a GameMap object

    # first reset the stuff that may be left over from the previous
    # match.
    p1.lines.clear()
    p2.lines.clear()
    p1.direction = "up"
    p2.direction = "up"
    p1.x = 120
    p1.y = 290
    p2.x = 500
    p2.y = 350

    game_map = GameMap(0, 100, 800, 500)
    game_map.fill_with_obstacles(10)
    game_map.players.append(p1)
    game_map.players.append(p2)

    p1.game_map = game_map
    p2.game_map = game_map

    return game_map


def main():
    global all_events

    screen_size = (800, 600)

    blue = pygame.color.Color(41, 143, 255)
    red = pygame.color.Color(204, 0, 0)

    fps_rate = 60
    # shrink every 20 seconds
    shrink_rate = fps_rate * 20
    shrink_size = 20

    # for now we can assume there are only 2 players.
    # game_map arg can be None since that will be handled
    # in start_level.
    p1 = Player(0, 0, blue, None)
    p1.input_dict = p1_input
    p2 = Player(0, 0, red, None)
    p2.input_dict = p2_input

    screen_surface = initialize(*screen_size)

    clock = pygame.time.Clock()

    font1 = pygame.font.Font("DejaVuSansMono.ttf", 18)
    bar1 = TopBar(0, 0, 800, 100, font1, p1, p2)

    all_matches_finished = False
    while not all_matches_finished:

        game_map = start_level(p1, p2)

        # this will keep track of when the map gets reduced
        to_shrink = shrink_rate
        shrink_counter = shrink_rate

        game_running = True
        while game_running:
            all_events = pygame.event.get()

            for e in all_events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        game_running = False
                    elif e.key == pygame.K_p:
                        pause_game(screen_surface, font1, screen_size)

            p1.handle_input()
            p2.handle_input()

            status = p1.update()
            if status == "crashed":
                p2.score += 1
                game_running = False

            status = p2.update()
            if status == "crashed":
                p1.score += 1
                game_running = False

            # draw everything here
            game_map.draw(screen_surface)
            bar1.draw(screen_surface, shrink_counter, fps_rate)
            pygame.display.flip()

            clock.tick(fps_rate)

            shrink_counter -= 1
            if shrink_counter == 0:
                shrink_counter = shrink_rate
                game_map.shrink(shrink_size)

        choice = end_game_dialog(screen_surface, font1, screen_size)
        if choice == "finish":
            all_matches_finished = True

    deinitialize()


main()
