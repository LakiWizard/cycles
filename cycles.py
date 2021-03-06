
import pygame
import random
import math

# for the about page button
import webbrowser


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

    def get_bounding_lines(self):
        # returns a list of 4 lines that are the edges of the rect
        rx1 = self.x
        rx2 = self.x+self.w
        ry1 = self.y
        ry2 = self.y+self.h

        edge1 = Line(rx1, ry1, rx2, ry1)
        edge2 = Line(rx1, ry1, rx1, ry2)
        edge3 = Line(rx2, ry1, rx2, ry2)
        edge4 = Line(rx1, ry2, rx2, ry2)

        return [edge1, edge2, edge3, edge4]


class Line():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Button():
    def __init__(self, x, y, w, h, font, parent_surface, text="", action=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)

        # text is button 'caption', action is function callback
        self.text = text
        self.action = action

        # pygame.Font object
        self.font = font

        self.color = pygame.color.Color(255, 255, 255)
        self.bkg_color = pygame.color.Color(0, 0, 0)

        # the surface it will be drawn on
        self.parent_surface = parent_surface

    def is_inside(self, x, y):
        # test if a point is inside this
        return self.rect.collidepoint(x, y)

    def draw(self, highlighted=False):
        # highlighted inverts primary and secondary color
        # mostly meant for mouse-over

        if not highlighted:
            primary_color = self.color
            second_color = self.bkg_color
        else:
            primary_color = self.bkg_color
            second_color = self.color

        text_surface = self.font.render(self.text, False, primary_color)

        # center-align the text
        text_w = self.font.size(self.text)[0]
        box_w = self.w
        x_margin = (box_w - text_w) // 2

        text_h = self.font.size(self.text)[1]
        box_h = self.h
        y_margin = (box_h - text_h) // 2

        # first fill with background, then text and boundary
        pygame.draw.rect(self.parent_surface, second_color, self.rect, 0)

        self.parent_surface.blit(text_surface, (self.x+x_margin, self.y+y_margin))

        # boundary always uses self.color
        pygame.draw.rect(self.parent_surface, self.color, self.rect, 1)



class ButtonHandler():
    def __init__(self, button_list, clock_interval):
        self.button_list = button_list
        self.clock = pygame.time.Clock()
        self.clock_interval = clock_interval

        self.clicked_on_button = None
        self.moused_on_button = None

    def update_events(self):
        # update clicked_on_button and moused_on_button
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()

                self.moused_on_button = None
                for button in self.button_list:
                    if button.is_inside(pos[0], pos[1]):
                        self.moused_on_button = button

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.clicked_on_button = self.moused_on_button

    def draw_buttons(self):
        # this doesnt do display.flip

        for button in self.button_list:
            if button is self.moused_on_button:
                button.draw(True)
            else:
                button.draw(False)

    def clock_tick(self):
        self.clock.tick(self.clock_interval)



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


def get_line_bounding_box(line):
    # returns ((x1, y1), (x2, y2))
    p1 = (min(line.x1, line.x2), min(line.y1, line.y2))
    p2 = (max(line.x1, line.x2), max(line.y1, line.y2))
    return (p1, p2)


def bounding_box_intersect(box1, box2):
    # check if the bounding boxes of two lines intersect
    # box1[0][0] -> box1[first_point][x]
    if (box1[0][0] <= box2[1][0]) and (box1[1][0] >= box2[0][0]) and (box1[0][1] <= box2[1][1]) and (box1[1][1] >= box2[0][1]):
        return True
    else:
        return False


def point_cross_product(x1, y1, x2, y2):
    # a mathematical something
    return x1 * y2 - x2 * y1


def point_on_line3(x, y, line):
    temp_line = Line(0, 0, line.x2-line.x1, line.y2-line.y1)
    temp_x = x-line.x1
    temp_y = y-line.y1

    x = point_cross_product(temp_line.x2, temp_line.y2, temp_x, temp_y)
    e = 0.000001
    return abs(x) < e


def point_right_of_line(x, y, line):
    # determine if point is right of line or not

    temp_line = Line(0, 0, line.x2-line.x1, line.y2-line.y1)
    temp_x = x-line.x1
    temp_y = y-line.y1

    return point_cross_product(temp_line.x2, temp_line.y2, temp_x, temp_y)


def segment_crosses_line(line1, line2):
    # check if a line segment crosses a line
    # here line is referred to as an infinite line to make this
    # distinction.
    return point_on_line3(line2.x1, line2.y1, line1) \
        or point_on_line3(line2.x2, line2.y2, line1) \
        or (point_right_of_line(line2.x1, line2.y1, line1) \
        ^ point_right_of_line(line2.x2, line2.y2, line1)) \


def line_through_line(line1, line2):
    box1 = get_line_bounding_box(line1)
    box2 = get_line_bounding_box(line2)
    if bounding_box_intersect(box1, box2) and segment_crosses_line(line1, line2) and segment_crosses_line(line2, line1):
        return True
    else:
        return False


def point_dist_squared(x1, y1, x2, y2):
    # a weird way to calculate the distance between 2 points
    # (no sqrt being used)
    return (x1 - x2)**2 + (y1 - y2)**2


def dist_to_line_segment(x, y, line):
    # calculate distance between a point and a line (segment)
    # mathematical stuff
    l = point_dist_squared(line.x1, line.y1, line.x2, line.y2)
    if (l == 0):
        # if the segment is just one point, then
        # calculate the point distance to it
        return math.sqrt(point_dist_squared(x, y, line.x1, line.y1))

    t = ((x-line.x1) * (line.x2-line.x1) + (y-line.y1) * (line.y2-line.y1)) / l
    t = max(0, min(1, t))

    new_x = line.x1 + t * (line.x2-line.x1)
    new_y = line.y1 + t * (line.y2-line.y1)
    result_squared = point_dist_squared(x, y, new_x, new_y)

    return math.sqrt(result_squared)


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
    # here 1 is substracted because just adding width
    # and height would not give real x2 and y2.
    # consider this:
    # x1 = 0
    # y1 = 0
    # width = 1
    # height = 1
    # here x2 and y2 would be 1 and 1, even though
    # we should have a 1x1 square.
    # in practice this caused the player to collide with
    # obstacles 1 pixel to the right and down of where they
    # really were.
    x2 = x1 + rw - 1
    y2 = y1 + rh - 1

    x_ok = False
    y_ok = False

    if x >= x1 and x <= x2:
        x_ok = True
    if y >= y1 and y <= y2:
        y_ok = True

    ok = x_ok and y_ok
    return ok


def line_in_rect(line, rect):
    # check if line intersects a rect

    # first check if any endings are inside rect, for possible
    # early exit.
    if is_in_rect(line.x1, line.y1, rect.x, rect.y, rect.w, rect.h):
        return True
    if is_in_rect(line.x2, line.y2, rect.x, rect.y, rect.w, rect.h):
        return True

    # if first test fails, then check if the line intersects
    # any of the edges of the rect.
    for edge in rect.get_bounding_lines():
        if line_through_line(line, edge):
            return True

    return False


def algo_tests():
    # some tests to check whether line_through_line and
    # line_in_rect work correctly.

    # line through line tests

    line1 = Line(4, 1, 4, 8)
    line2 = Line(2, 6, 9, 6)
    # should be true
    print("should be true:", line_through_line(line1, line2))
    line1 = Line(1, 1, 1, 5)
    line2 = Line(5, 1, 5, 6)
    # should be false
    print("should be false:", line_through_line(line1, line2))
    line1 = Line(2, 1, 2, 4)
    line2 = Line(2, 4, 4, 4)
    print("should be true:", line_through_line(line1, line2))

    line1 = Line(5, 2, 15, 2)
    line2 = Line(9, 4, 9, 8)
    print("should be false:", line_through_line(line1, line2))
    print()


    # line through rect tests

    rect1 = Obstacle(2, 1, 5-2, 4-1)
    line1 = Line(4, 2, 6, 2)
    # should be true
    print("should be true:", line_in_rect(line1, rect1))
    rect1 = Obstacle(2, 2, 4-2, 5-2)
    line1 = Line(4, 7, 6, 7)
    # should be false
    print("should be false:", line_in_rect(line1, rect1))
    rect1 = Obstacle(1, 2, 4-1, 5-2)
    line1 = Line(2, 3, 3, 3)
    print("should be true:", line_in_rect(line1, rect1))
    rect1 = Obstacle(1, 1, 4-1, 4-1)
    line1 = Line(4, 4, 4, 5)
    print("should be true:", line_in_rect(line1, rect1))
    print()

    # dist to line segment tests
    line1 = Line(0, 0, 0, 10)
    x = 1
    y = 5
    print("should be 1:", dist_to_line_segment(x, y, line1))
    line1 = Line(2, 5, 10, 5)
    x = 8
    y = 5
    print("should be 0:", dist_to_line_segment(x, y, line1))
    print()



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
            all_lines.extend(p.lines)

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
        pygame.draw.circle(screen_surface, self.color, (self.x, self.y), 8, 3)


class AIPlayer(Player):
    def __init__(self, x, y, color, game_map):
        super().__init__(x, y, color, game_map)

        # player lines that will be used for collision detection
        # to avoid iterating through every line on the map
        # every game turn.
        self.cached_lines = []
        self.turns_to_update_cache = 10
        self.cache_counter = 0

        # this is re-randomized on every change of direction
        self.test_line_length = random.randint(11, 16)

    def get_closest_lines(self, distance):
        # this also returns the line you are currently on
        lines = []
        for p in self.game_map.players:
            lines.extend(p.lines)

        nearby_lines = []
        for l in lines:
            dist = dist_to_line_segment(self.x, self.y, l)
            if dist <= distance:
                nearby_lines.append(l)

        #print("updated cache: {} lines cached from a total of {}".format(len(nearby_lines), len(lines)))
        return nearby_lines

    def update(self):
        # this should always be safely larger than the length of
        # test line used for collision testing, so as not to collide
        # with lines that were never added to the cache.
        # turns_to_update_cache should also not be too large.
        max_line_dist = 30

        if self.cache_counter == self.turns_to_update_cache:
            self.cached_lines = self.get_closest_lines(max_line_dist)
            self.cache_counter = 0
        else:
            self.cache_counter += 1

        #print("ai: line cache is", len(self.cached_lines))

        # make sure to return status from the parent method
        status = super().update()
        return status

    def line_is_clear(self, linearg):
        # check if this line intersects any obstacles, lines or
        # reaches map edge.

        # first check if it is in map bounds
        x = self.game_map.x
        y = self.game_map.y
        w = self.game_map.width
        h = self.game_map.height
        if not (is_in_rect(linearg.x1, linearg.y1, x, y, w, h) and is_in_rect(linearg.x2, linearg.y2, x, y, w, h)):
            # print("line not in map bounds")
            return False

        # remove own line as it would always cause errors later
        current_line = None
        if len(self.lines) > 0:
            current_line = self.lines[0]
        for line in self.cached_lines:
            if line is current_line:
                continue

            if line_through_line(linearg, line):
                # print("line goes through another line")
                # print("linearg: {}, {}, {}, {}".format(linearg.x1, linearg.y1, linearg.x2, linearg.y2))
                # print("problem line: {}, {}, {}, {}".format(line.x1, line.y1, line.x2, line.y2))
                return False

        # check for all the obstacles
        for o in self.game_map.obstacles:
            if line_in_rect(linearg, o):
                # print("line goes through obstacle")
                return False

        return True

    def get_line_in_direction(self, direction, length):
        # get a line that goes from current coordinates
        # in the given direction with the given length.
        x1 = self.x
        y1 = self.y

        if direction == "up":
            x2 = x1
            y2 = y1 - length
        elif direction == "down":
            x2 = x1
            y2 = y1 + length
        elif direction == "left":
            x2 = x1 - length
            y2 = y1
        elif direction == "right":
            x2 = x1 + length
            y2 = y1
        else:
            raise Exception("invalid direction: "+direction)

        return Line(x1, y1, x2, y2)

    def get_possible_directions(self):
        # all the directions in which we can turn
        possible_directions = ["up", "down", "left", "right"]

        possible_directions.remove(self.direction)

        if self.direction == "up":
            possible_directions.remove("down")
        elif self.direction == "down":
            possible_directions.remove("up")
        elif self.direction == "left":
            possible_directions.remove("right")
        elif self.direction == "right":
            possible_directions.remove("left")

        return possible_directions


    def handle_input(self):
        possible_directions = self.get_possible_directions()

        test_line = self.get_line_in_direction(self.direction, self.test_line_length)
        if self.line_is_clear(test_line):
            return None

        wanted_free_length = 250
        direction_to_go = None
        while direction_to_go is None:
            wanted_free_length -= 10
            if wanted_free_length < 10:
                direction_to_go = random.choice(possible_directions)

            for d in possible_directions:
                line = self.get_line_in_direction(d, wanted_free_length)
                if self.line_is_clear(line):
                    direction_to_go = d

        self.direction = direction_to_go
        # start new line when changing direction
        self.start_new_line()
        #print("ai: obstacles in the way, changing direction to:", self.direction)

        # re-randomize test line length
        self.test_line_length = random.randint(11, 16)

        # you cant go in reverse
        #if is_opposing_direction(new_direction, self.direction):
        #    return None



class TopBar():
    def __init__(self, x, y, w, h, font_object, player_list, game_mode):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font_object

        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.light_grey = pygame.Color(210, 210, 210)

        self.rect = pygame.Rect(x, y, w, h)

        self.game_mode = game_mode

        # the player objects, used for counting the scores
        self.p1 = player_list[0]
        self.p2 = player_list[1]

        if self.game_mode in ["1pffa", "2pffa"]:
            self.p3 = player_list[2]
            self.p4 = player_list[3]
            self.p5 = player_list[4]
            self.p6 = player_list[5]

    def draw(self, screen_surface, seconds_to_shrink):
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
        if self.game_mode in ["pvp", "pve"]:
            text2 = self.font.render("P1 score:", False, self.p1.color)
            screen_surface.blit(text2, (text_x, self.y+text_height*2))
            score1_x = self.font.size("P1 score:")[0] + text_x
            score1 = self.font.render(str(self.p1.score), False, self.white)
            screen_surface.blit(score1, (score1_x, self.y+text_height*2))

            text3 = self.font.render("P2 score:", False, self.p2.color)
            screen_surface.blit(text3, (text_x, self.y+text_height*3))
            score2_x = self.font.size("P2 score:")[0] + text_x
            score2 = self.font.render(str(self.p2.score), False, self.white)
            screen_surface.blit(score2, (score2_x, self.y+text_height*3))

        elif self.game_mode in ["1pffa", "2pffa"]:
            p1_text = self.font.render("P1:", False, self.p1.color)
            p2_text = self.font.render("P2:", False, self.p2.color)
            p3_text = self.font.render("P3:", False, self.p3.color)
            p4_text = self.font.render("P4:", False, self.p4.color)
            p5_text = self.font.render("P5:", False, self.p5.color)
            p6_text = self.font.render("P6:", False, self.p6.color)

            p1_score = self.font.render(str(self.p1.score), False, self.white)
            p2_score = self.font.render(str(self.p2.score), False, self.white)
            p3_score = self.font.render(str(self.p3.score), False, self.white)
            p4_score = self.font.render(str(self.p4.score), False, self.white)
            p5_score = self.font.render(str(self.p5.score), False, self.white)
            p6_score = self.font.render(str(self.p6.score), False, self.white)

            # p1
            screen_surface.blit(p1_text, (text_x, self.y+40))
            screen_surface.blit(p1_score, (text_x+40, self.y+40))

            # p2
            screen_surface.blit(p2_text, (text_x+100, self.y+40))
            screen_surface.blit(p2_score, (text_x+100+40, self.y+40))

            # and so on
            screen_surface.blit(p3_text, (text_x+200, self.y+40))
            screen_surface.blit(p3_score, (text_x+200+40, self.y+40))

            screen_surface.blit(p4_text, (text_x, self.y+65))
            screen_surface.blit(p4_score, (text_x+40, self.y+65))

            screen_surface.blit(p5_text, (text_x+100, self.y+65))
            screen_surface.blit(p5_score, (text_x+100+40, self.y+65))

            screen_surface.blit(p6_text, (text_x+200, self.y+65))
            screen_surface.blit(p6_score, (text_x+200+40, self.y+65))

        # show how many seconds to map reduction
        counter_x = self.x + self.w - 200
        counter_y = self.y + self.h - 30
        counter_text = self.font.render("Reducing in: {}".format(seconds_to_shrink), False, self.white)
        screen_surface.blit(counter_text, (counter_x, counter_y))



def main_menu(scr_size, scr_surface, font):
    button1_y = (scr_size[1] // 2) - 80
    button2_y = button1_y + 70
    button3_y = button2_y + 70
    button_w = 120
    button_x = (scr_size[0] - button_w) // 2

    button1 = Button(button_x, button1_y, button_w, 40, font, scr_surface, "Start")
    button2 = Button(button_x, button2_y, button_w, 40, font, scr_surface, "About")
    button3 = Button(button_x, button3_y, button_w, 40, font, scr_surface, "Exit")
    buttons = [button1, button2, button3]

    scr_surface.fill(pygame.Color(0, 0, 0))

    # 30 fps is enough when just rendering some buttons
    button_handler = ButtonHandler(buttons, 30)
    while True:
        button_handler.draw_buttons()
        pygame.display.flip()

        button_handler.update_events()

        button_clicked = button_handler.clicked_on_button
        if not button_clicked is None:
            break

        button_handler.clock_tick()

    if button_clicked is button1:
        return "start"
    elif button_clicked is button2:
        return "about"
    elif button_clicked is button3:
        return "exit"


def game_types_menu(scr_size, scr_surface, font):
    button1_y = (scr_size[1] // 2) - 120
    button2_y = button1_y + 70
    button3_y = button2_y + 70
    button4_y = button3_y + 70
    button_w = 200
    button_x = (scr_size[0] - button_w) // 2

    button1 = Button(button_x, button1_y, button_w, 40, font, scr_surface, "Player vs Player")
    button2 = Button(button_x, button2_y, button_w, 40, font, scr_surface, "Player vs AI")
    button3 = Button(button_x, button3_y, button_w, 40, font, scr_surface, "Solo FFA")
    button4 = Button(button_x, button4_y, button_w, 40, font, scr_surface, "Duo FFA")
    buttons = [button1, button2, button3, button4]

    scr_surface.fill(pygame.Color(0, 0, 0))

    button_handler = ButtonHandler(buttons, 30)
    while True:
        button_handler.draw_buttons()
        pygame.display.flip()

        button_handler.update_events()

        button_clicked = button_handler.clicked_on_button
        if not button_clicked is None:
            break

        button_handler.clock_tick()

    if button_clicked is button1:
        return "pvp"
    elif button_clicked is button2:
        return "pve"
    elif button_clicked is button3:
        return "1pffa"
    elif button_clicked is button4:
        return "2pffa"


def show_about_screen(scr_size, scr_surface):
    font = pygame.font.Font("DejaVuSansMono.ttf", 18)
    font_big = pygame.font.Font("DejaVuSansMono.ttf", 24)

    x_margin = 30

    white = pygame.Color(255, 255, 255)

    scr_surface.fill(pygame.Color(0, 0, 0))

    cycles = font_big.render("Cycles", False, white)
    cycles_y = 20
    scr_surface.blit(cycles, (x_margin, cycles_y))

    made_by_str = "Designed and programmed by LakiWizard"
    made_by_y = cycles_y + 100
    made_by = font.render(made_by_str, False, white)
    scr_surface.blit(made_by, (x_margin, made_by_y))

    web_page_str = "To get the latest version and source code, go to:"
    page_button_str = "https://github.com/LakiWizard/cycles/"

    web_page_y = made_by_y + 80
    page_button_y = web_page_y + 50

    web_page = font.render(web_page_str, False, white)
    page_button = Button(x_margin, page_button_y, 420, 30, font, scr_surface, page_button_str)
    page_button.color = pygame.Color(0, 0, 0)
    page_button.bkg_color = pygame.Color(255, 255, 255)
    scr_surface.blit(web_page, (x_margin, web_page_y))
    page_button.draw()

    readme_notice = "For more information, see README.md"
    readme_y = page_button_y + 80
    readme = font.render(readme_notice, False, white)
    scr_surface.blit(readme, (x_margin, readme_y))

    glhf_notice = "Have fun!"
    glhf_y = readme_y + 120
    glhf = font.render(glhf_notice, False, white)
    scr_surface.blit(glhf, (x_margin, glhf_y))

    back_w = 80
    back_x = (scr_size[0] // 2) - (back_w // 2)
    back_y = glhf_y + 80
    back_button  = Button(back_x, back_y, back_w, 40, font, scr_surface, "Back")
    back_button.draw()

    page_button.action = lambda: webbrowser.open_new_tab(page_button_str)
    back_button.action = lambda: None
    buttons = [page_button, back_button]

    #pygame.display.flip()

    button_handler = ButtonHandler(buttons, 30)
    while True:
        button_handler.draw_buttons()
        pygame.display.flip()

        button_handler.update_events()

        button_clicked = button_handler.clicked_on_button
        if not button_clicked is None:
            break

        button_handler.clock_tick()

    button_clicked.action()


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


def start_level(player_list):
    """
    map_size -> tuple(w, h)
    """
    # start a game level, do all the needed preparations
    # return a GameMap object

    # first reset the stuff that may be left over from the previous
    # match.
    if len(player_list) == 2:
        p1 = player_list[0]
        p2 = player_list[1]

        p1.lines.clear()
        p2.lines.clear()
        p1.direction = "up"
        p2.direction = "up"
        p1.x = 150
        p1.y = 350
        p2.x = 650
        p2.y = 350

        game_map = GameMap(0, 100, 800, 500)
        game_map.fill_with_obstacles(10)
        game_map.players.append(p1)
        game_map.players.append(p2)

        p1.game_map = game_map
        p2.game_map = game_map

    elif len(player_list) == 6:
        p1 = player_list[0]
        p2 = player_list[1]
        p3 = player_list[2]
        p4 = player_list[3]
        p5 = player_list[4]
        p6 = player_list[5]

        p1.direction = "up"
        p2.direction = "up"
        p3.direction = "up"
        p4.direction = "down"
        p5.direction = "down"
        p6.direction = "down"
        for p in player_list:
            p.lines.clear()

        # top row
        p1.x = 100
        p1.y = 250
        p2.x = 400
        p2.y = 250
        p3.x = 700
        p3.y = 250

        # bottom row
        p4.x = 100
        p4.y = 450
        p5.x = 400
        p5.y = 450
        p6.x = 700
        p6.y = 450

        game_map = GameMap(0, 100, 800, 500)
        game_map.fill_with_obstacles(10)
        for p in player_list:
            game_map.players.append(p)
            p.game_map = game_map

    else:
        raise Exception("unsupported number of players")

    return game_map


def play_game(scr_size, scr_surface, font, game_mode):
    global all_events

    screen_size = scr_size
    screen_surface = scr_surface

    blue = pygame.color.Color(41, 143, 255)
    red = pygame.color.Color(204, 0, 0)

    yellow = pygame.color.Color(255, 255, 0)
    green = pygame.color.Color(0, 255, 0)
    magenta = pygame.color.Color(255, 0, 255)
    white = pygame.color.Color(255, 255, 255)

    fps_rate = 60
    # shrink every 20 seconds
    shrink_rate = fps_rate * 20
    shrink_size = 20

    # game_map arg can be None since that will be handled
    # in start_level.
    all_players = []
    if game_mode == "pvp":
        p1 = Player(0, 0, blue, None)
        p1.input_dict = p1_input
        p2 = Player(0, 0, red, None)
        p2.input_dict = p2_input
        all_players = [p1, p2]
    elif game_mode == "pve":
        p1 = Player(0, 0, blue, None)
        p1.input_dict = p1_input
        p2 = AIPlayer(0, 0, red, None)
        all_players = [p1, p2]
    elif game_mode == "1pffa":
        p1 = Player(0, 0, blue, None)
        p1.input_dict = p1_input
        p2 = AIPlayer(0, 0, red, None)
        p3 = AIPlayer(0, 0, green, None)
        p4 = AIPlayer(0, 0, yellow, None)
        p5 = AIPlayer(0, 0, magenta, None)
        p6 = AIPlayer(0, 0, white, None)
        all_players = [p1, p2, p3, p4, p5, p6]
    elif game_mode == "2pffa":
        p1 = Player(0, 0, blue, None)
        p1.input_dict = p1_input
        p2 = Player(0, 0, red, None)
        p2.input_dict = p2_input
        p3 = AIPlayer(0, 0, green, None)
        p4 = AIPlayer(0, 0, yellow, None)
        p5 = AIPlayer(0, 0, magenta, None)
        p6 = AIPlayer(0, 0, white, None)
        all_players = [p1, p2, p3, p4, p5, p6]
    else:
        raise Exception("unsupported gamemode")

    clock = pygame.time.Clock()

    font1 = font
    bar1 = TopBar(0, 0, 800, 100, font1, all_players, game_mode)

    all_matches_finished = False
    while not all_matches_finished:

        game_map = start_level(all_players)

        # this will keep track of when the map gets reduced
        to_shrink = shrink_rate
        shrink_counter = shrink_rate

        game_running = True

        crashed_players = []
        while game_running:
            all_events = pygame.event.get()

            for e in all_events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        game_running = False
                    elif e.key == pygame.K_p:
                        pause_game(screen_surface, font1, screen_size)

            for p in all_players:
                if not p in crashed_players:
                    p.handle_input()

            status = ""
            for p in all_players:
                if not p in crashed_players:
                    status = p.update()
                    if status == "crashed":
                        crashed_players.append(p)

            if len(crashed_players) == len(all_players)-1:
                uncrashed_player = None
                for p in all_players:
                    if not p in crashed_players:
                        uncrashed_player = p

                uncrashed_player.score += 1
                game_running = False

            # just for debugging
            #lines = []
            #for p in game_map.players:
            #    lines.extend(p.lines)
            #print(len(lines))

            # draw everything here
            game_map.draw(screen_surface)

            seconds_to_shrink = int(shrink_counter / fps_rate)
            bar1.draw(screen_surface, seconds_to_shrink)

            pygame.display.flip()

            clock.tick(fps_rate)

            shrink_counter -= 1
            if shrink_counter == 0:
                shrink_counter = shrink_rate
                game_map.shrink(shrink_size)

        choice = end_game_dialog(screen_surface, font1, screen_size)
        if choice == "finish":
            all_matches_finished = True


def main():
    scr_size = (800, 600)
    scr_surface = initialize(*scr_size)

    font1 = pygame.font.Font("DejaVuSansMono.ttf", 18)

    finished = False
    while not finished:
        menu_choice = main_menu(scr_size, scr_surface, font1)
        if menu_choice == "start":
            game_mode = game_types_menu(scr_size, scr_surface, font1)
            play_game(scr_size, scr_surface, font1, game_mode)
        elif menu_choice == "about":
            show_about_screen(scr_size, scr_surface)
        elif menu_choice == "exit":
            finished = True

    deinitialize()

# algo_tests()

if __name__ == "__main__":
    main()
