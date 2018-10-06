
import pygame


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

    def draw(self, screen_surface):
        screen_surface.fill(self.background)


class Player():
    def __init__(self, x, y, color, game_map):
        self.x = x
        self.y = y
        self.color = color  # pygame.Color object

        self.direction = "up"
        self.input_dict = None

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

        self.direction = new_direction

    def update(self):
        status_good = "moving"
        status_crashed = "crashed"

        if self.x < 0 or self.x > self.game_map.width or self.y < 0 or self.y > self.game_map.height:
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
        pygame.draw.circle(screen_surface, self.color, (self.x, self.y), 10, 4)



def draw_all(game_map, player_list, screen_surface):
    game_map.draw(screen_surface)
    for p in player_list:
        p.draw(screen_surface)

    pygame.display.flip()



def main():
    global all_events

    map_size = (800, 600)

    game_map = GameMap(*map_size)

    blue = pygame.color.Color(50, 50, 220)
    red = pygame.color.Color(220, 50, 50)

    p1 = Player(100, 50, blue, game_map)
    p1.input_dict = p1_input
    p2 = Player(500, 350, red, game_map)
    p2.input_dict = p2_input
    players = [p1, p2]

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

        draw_all(game_map, players, screen_surface)
        clock.tick(60)

    deinitialize()


main()
