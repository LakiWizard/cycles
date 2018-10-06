
import pygame



def initialize(screen_width, screen_height):
    pygame.init()
    pygame.mixer.quit()

    screen_surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Cycles")

    return screen_surface

def deinitialize():
    pygame.quit()



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

        # hold a reference to the map you are on
        self.game_map = game_map

    def draw(self, screen_surface):
        pygame.draw.circle(screen_surface, self.color, (self.x, self.y), 10, 4)



def draw_all(game_map, player_list, screen_surface):
    game_map.draw(screen_surface)
    for p in player_list:
        p.draw(screen_surface)

    pygame.display.flip()



def main():
    map_size = (800, 600)

    game_map = GameMap(*map_size)

    blue = pygame.color.Color(50, 50, 220)
    red = pygame.color.Color(220, 50, 50)

    p1 = Player(100, 50, blue, game_map)
    p2 = Player(500, 350, red, game_map)
    players = [p1, p2]

    screen_surface = initialize(*map_size)

    clock = pygame.time.Clock()

    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_running = False

        draw_all(game_map, players, screen_surface)
        clock.tick(30)

    deinitialize()


main()
