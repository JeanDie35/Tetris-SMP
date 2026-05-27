from game import Game
from frames import Welcome, Settings, GameOver
from config import Config
from client import Client
import pygame
pygame.init()
pygame.font.init()

config = Config()

FPS = config.data["FPS"]
BG_COLOR = config.data["bg_color"]

clock = pygame.time.Clock()


"""""
Careful:
 I used numpy to store the position of every block. Although, axis 1 in numpy arrays is the y axis, axis 2 is the x axis
 The numpy array that stores the position of the blocks is called grid, there can be 3 different values:
    0 is when there's no block
    1 is for the blocks that you can move
    2-8 is for the bdlocks that you can't move anymore, the number depends on the color
"""""


running = True

pygame.display.set_caption(config.data["title"])
screen_size = (config.data["screen_width"], config.data["screen_height"])
screen = pygame.display.set_mode(screen_size)

client = Client(config)

# we try to connect to the server
client_key = client.connect()
# if the client is not already connected we stop the program
if client_key is None:
    running = False
    pygame.quit()

welcome = Welcome(screen, config, client)
game = Game(screen, config)
settings = Settings(screen, config)
game_over = GameOver(screen, config)

active_frame = welcome
next_frame = None

frames = {
    "game": game,
    "welcome": welcome,
    "settings": settings,
    "game_over": game_over
}

while running:

    # handles all the transitions that are triggered by the code
    internal_result = active_frame.update()

    if internal_result is not None:
        next_frame = frames[internal_result]
        # hiding the old widgets
        screen.fill(BG_COLOR)

        if next_frame == game_over and active_frame == game:
            # sends a request to the server saying that the game is over
            client.send_request("OVER")

            game_over.score = game.score
            game.reset()

        if next_frame == game and active_frame == welcome:

            game.start_game(client)

            # assigning the chosen keys to game
            for key in game.key_binds.keys():
                game.key_binds[key] = settings.get_key_movement(key)

        active_frame = next_frame

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            # saving all the data
            config.save_file()
            # sending a request to the server saying that we want to close the conn
            client.send_request("CLOSE")
            pygame.quit()
            running = False

        # handles the transitions that are triggered by the user
        external_result = active_frame.handle_events(event)

        if external_result is not None:

            # it means that we change the frame
            next_frame = frames[external_result]
            # hiding the old widgets
            screen.fill(BG_COLOR)

            if active_frame == settings and next_frame == welcome:
                # saving the chosen keys
                for movement in game.key_binds:
                    config.data["key_binds"][movement] = settings.get_key_movement(movement)

            active_frame = next_frame

    clock.tick(FPS)
