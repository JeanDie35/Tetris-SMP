import numpy as np
import pygame
import time

from config import Config

pygame.init()

BLOCK_SIZE = 25

# dic stores all the arrays for each type of block, with the rotated ones too
blocks = {
    2: {
        "arrays": [np.array([[0, 1, 0], [1, 1, 0], [0, 1, 0]]), np.array([[0, 0, 0], [1, 1, 1], [0, 1, 0]]),
                   np.array([[0, 1, 0], [0, 1, 1], [0, 1, 0]]), np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/blue_block.png"), (BLOCK_SIZE, BLOCK_SIZE))},
    3: {
        "arrays": [np.array([[1, 0, 0], [1, 1, 0], [0, 1, 0]]), np.array([[0, 0, 0], [0, 1, 1], [1, 1, 0]]),
                   np.array([[0, 1, 0], [0, 1, 1], [0, 0, 1]]), np.array([[0, 1, 1], [1, 1, 0]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/cyan_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    },
    4: {
        "arrays": [np.array([[0, 1, 0], [0, 1, 0], [1, 1, 0]]), np.array([[0, 0, 0], [1, 1, 1], [0, 0, 1]]),
                   np.array([[0, 1, 1], [0, 1, 0], [0, 1, 0]]), np.array([[1, 0, 0], [1, 1, 1]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/green_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    },
    5: {
        "arrays": [np.array([[1, 1, 0], [0, 1, 0], [0, 1, 0]]), np.array([[0, 0, 0], [1, 1, 1], [1, 0, 0]]),
                   np.array([[0, 1, 0], [0, 1, 0], [0, 1, 1]]), np.array([[0, 0, 1], [1, 1, 1]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/pink_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    },
    6: {
        "arrays": [np.array([[0, 1], [0, 1], [0, 1], [0, 1]]), np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1]]),
                   np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]), np.array([[0, 0, 0, 0], [1, 1, 1, 1]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/purple_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    },
    7: {
        "arrays": [np.array([[1, 1], [1, 1]]), np.array([[1, 1], [1, 1]]), np.array([[1, 1], [1, 1]]),
                  np.array([[1, 1], [1, 1]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/red_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    },
    8: {
        "arrays": [np.array([[0, 1, 0], [1, 1, 0], [1, 0, 0]]), np.array([[0, 0, 0], [1, 1, 0], [0, 1, 1]]),
                  np.array([[0, 0, 1], [0, 1, 1], [0, 1, 0]]), np.array([[1, 1, 0], [0, 1, 1]])],
        "image": pygame.transform.scale(pygame.image.load("assets/blocks/yellow_block.png"), (BLOCK_SIZE, BLOCK_SIZE))
    }
}


class ActivePiece:

    def __init__(self, game, config, color):
        self.color_value = int(color)
        self.config = config
        self.speed = 1
        self.state = 0
        self.array = blocks[self.color_value]["arrays"][self.state].copy()
        self.game = game
        # we get the coordinates of each block of the active_piece
        self.coords = self.get_coords(self.game.grid, True)
        # stores the actual positon of the array, so when it turns, it doesn't move right
        self.pos = [0, self.game.playing_screen_size[0] // 2 // BLOCK_SIZE]

    def get_coords(self, array: np.ndarray, reverse: bool) -> list:
        """""
        returns the coordinates of every ones in grid
        """""
        coords = np.argwhere(array == 1)
        # we sort the list with the biggest coords in the first place so when we make
        # the blocks go down 1 block they don't destroy each other
        # you must reverse it or not depending on where the block will move, to understand this better make grid scheme
        return sorted(map(list, coords), reverse=reverse)

    def get_next_right_state(self) -> int:
        state = self.state
        state += 1
        if state >= 4:
            state = 0
        return state

    def simulate_right_turn(self) -> np.ndarray:
        """""
        returns grid turned array
        """""
        return blocks[self.color_value]["arrays"][self.get_next_right_state()]

    def get_next_left_state(self) -> int:
        state = self.state
        state -= 1
        if state <= -1:
            state = 3
        return state

    def simulate_left_turn(self) -> np.ndarray:
        """""
        returns grid turned array
        """""
        return blocks[self.color_value]["arrays"][self.get_next_left_state()]

    def move(self, dx: int, dy: int):
        self.pos[0] += dy
        self.pos[1] += dx
        for coords in self.coords:
            # hiding the old block
            self.game.grid[coords[0], coords[1]] = 0
            self.game.grid[coords[0] + dy, coords[1] + dx] = 1

    def can_move(self, dx: int, dy: int) -> bool:
        """""
        checks if the blocks can move in grid direction
        """""
        movable = True
        for coords in self.coords:
            if not (0 <= coords[0] + dy < self.game.grid.shape[0]) or not (0 <= coords[1] + dx < self.game.grid.shape[1]) or self.game.is_fixed_block((coords[0] + dy, coords[1] + dx)):
                movable = False
                break
        return movable

    def can_fit(self, piece_array: np.ndarray) -> bool:
        """""
        checks if the array can fit at the moving blocks position
        """""
        fit = True
        arr_co = self.get_coords(piece_array, False)
        for coords in arr_co:

            if (not (0 <= coords[0] + self.pos[0] < self.game.grid.shape[0])
                    or not (0 <= coords[1] + self.pos[1] < self.game.grid.shape[1])
                    or self.game.is_fixed_block((coords[0] + self.pos[0], coords[1] + self.pos[1]))):
                fit = False
                break
        return fit


class GameUI:

    def __init__(self, screen: pygame.surface.Surface, config: Config, title, origin_x):
        self.screen = screen
        self.config = config

        self.title = title
        self.font = pygame.font.SysFont(self.config.data["font_name"], self.config.data["font_size"])
        self.playing_screen_size = (self.config.data["playing_screen_width"], self.config.data["playing_screen_height"])

        # abscissa of the top right corner of the UI, we don't put the 
        self.origin_x = origin_x

    def is_fixed_block(self, coords: list | tuple, grid) -> bool:
        return self.config.data["first_fixed_block"] <= grid[coords] <= self.config.data["last_fixed_block"]

    def render(self, grid, score, next_color, active_color=None):

        self.display_grid(grid, active_color)
        self.display_title()
        self.display_next_block_text()
        self.display_next_block(next_color)
        self.display_score(score)

        # draw the blue line
        pygame.draw.rect(self.screen, self.config.data["colors"]["blue"],
                         ((self.playing_screen_size[0] + self.origin_x, 0), (10, self.screen.get_height())))

        pygame.draw.rect(self.screen, self.config.data["colors"]["blue"],
                         ((self.config.data["game_screen_width"] + self.origin_x - 10, 0), (10, self.screen.get_height())))

    def display_grid(self, grid, active_color):
        # updating the blocks
        non_zero = np.argwhere(grid != 0)

        for y, x in non_zero:

            if self.is_fixed_block((y, x), grid):
                self.screen.blit(blocks[int(grid[y, x])]["image"],
                                 (x * BLOCK_SIZE + self.origin_x, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

            elif active_color != None:
                self.screen.blit(blocks[active_color]["image"],
                                 (x * BLOCK_SIZE + self.origin_x, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def display_title(self):
        title_text = self.font.render(self.title, 1, self.config.data["colors"]["white"])
        self.screen.blit(title_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"] + self.origin_x, 10))

    def display_next_block_text(self):
        blocks_text = self.font.render("Next block:", 1, self.config.data["colors"]["white"])
        self.screen.blit(blocks_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"] + self.origin_x, 40))

    def display_next_block(self, color):
        next_array = blocks[color]["arrays"][0]

        for y in range(next_array.shape[0]):

            for x in range(next_array.shape[1]):

                if next_array[y, x] == self.config.data["moving_block"]:
                    self.screen.blit(blocks[color]["image"], (
                        self.playing_screen_size[0] + self.config.data["sidebar_offset"] + x * BLOCK_SIZE + self.origin_x,
                        100 + y * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE))

    def display_score(self, score):

        score_text = self.font.render(f"Score : {score}", 1, self.config.data["colors"]["white"])
        self.screen.blit(score_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"] + self.origin_x, 200))



class Game:

    def __init__(self, screen: pygame.surface.Surface, config: Config):
        self.screen = screen
        self.config = config

        self.game_ui = {"you":GameUI(self.screen, self.config, "Your game", 0)}

        # server part
        self.client = None

        self.playing_screen_size = (self.config.data["playing_screen_width"], self.config.data["playing_screen_height"])
        # creating the numpy array
        self.arr_size = (self.playing_screen_size[1] // BLOCK_SIZE, self.playing_screen_size[0] // BLOCK_SIZE)
        self.grid = np.zeros(self.arr_size)

        self.line_broken = 0
        self.score = 0
        # var stores the normal speed, when k up isn't pressed
        self.base_speed = self.config.data["base_speed"]

        self.over = False

        self.counter = 0

        self.key_binds = self.config.data["key_binds"]

    def set_screen_size(self, size):
        self.screen = pygame.display.set_mode(size)

    def start_game(self, client):
        # when starting the game, we need a client to communicate with the server
        self.client = client

        self.active_piece = ActivePiece(self, self.config, self.client.get_color())
        self.insert_blocks()

        self.next_color = self.client.get_color()

        self.nb_players = self.client.get_nb_players()

        # if there's only 2 players playing
        if self.nb_players == 2:
            # we add another UI
            self.game_ui["opponent"] = GameUI(self.screen, self.config, "Opponent's game", self.config.data["game_screen_width"])
            # resize the screen
            self.set_screen_size((self.config.data["game_screen_width"] * 2, self.config.data["game_screen_height"]))

    def insert_blocks(self):
        """""
        insert the moving blocks at the top of the screen
        """""
        y = self.active_piece.pos[0] + self.active_piece.array.shape[0]
        x = self.active_piece.pos[1] + self.active_piece.array.shape[1]
        # if there's grid put block where the blocks must generate
        for color_value in range(self.config.data["first_fixed_block"], self.config.data["last_fixed_block"] + 1):
            if color_value in self.grid[self.active_piece.pos[0]:y, self.active_piece.pos[1]:x]:
                print("Game over 1")
                self.over = True
        self.grid[self.active_piece.pos[0]:y, self.active_piece.pos[1]:x] = self.active_piece.array

    def is_fixed_block(self, coords: list | tuple) -> bool:
        return self.config.data["first_fixed_block"] <= self.grid[coords] <= self.config.data["last_fixed_block"]

    def reset(self):
        """""
        resets all var to their original values
        """""
        self.line_broken = 0
        self.score = 0
        self.counter = 0
        self.over = False
        # creating the numpy array
        self.arr_size = (self.playing_screen_size[1] // BLOCK_SIZE, self.playing_screen_size[0] // BLOCK_SIZE)
        self.grid = np.zeros(self.arr_size)

        self.active_piece = ActivePiece(self, self.config, self.client.get_color())
        self.insert_blocks()

        # reset the screen's size
        self.set_screen_size((self.config.data["game_screen_width"], self.config.data["game_screen_height"]))

    def move_line_down(self, y: int):
        """""
        moves all row above y by one
        """""
        # move all the line higher than y by one block
        for i in range(y + 1):
            if y - i != 0:
                self.grid[y - i, :] = self.grid[y - i - 1, :]
            else:
                self.grid[y - i, :] = self.config.data["empty"]

    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:

            # cheats
            if event.key == pygame.K_c:
                self.move_line_down(self.grid.shape[0] - 1)

            if event.key == pygame.K_w:
                self.arr_size = (self.playing_screen_size[1] // BLOCK_SIZE, self.playing_screen_size[0] // BLOCK_SIZE)
                self.grid = np.zeros(self.arr_size)

                self.active_piece = ActivePiece(self, self.config, self.client.get_color())
                self.insert_blocks()

            if event.key == self.key_binds["turn right"] or event.key == self.key_binds["turn left"]:

                # getting the actual coords of the blocks
                self.active_piece.coords = self.active_piece.get_coords(self.grid, False)

                if event.key == self.key_binds["turn right"]:
                    turned_array = self.active_piece.simulate_right_turn()
                    next_state = self.active_piece.get_next_right_state()

                elif event.key == self.key_binds["turn left"]:
                    turned_array = self.active_piece.simulate_left_turn()
                    next_state = self.active_piece.get_next_left_state()

                # if it can turn
                if self.active_piece.can_fit(turned_array):
                    # hiding old blocks
                    for y, x in self.active_piece.coords:
                        self.grid[y, x] = 0

                    # updating the array
                    self.active_piece.array = turned_array
                    self.active_piece.state = next_state

                    self.insert_blocks()
                    # updating coords
                    self.active_piece.coords = self.active_piece.get_coords(self.grid, False)

                    for y, x in self.active_piece.coords:
                        self.grid[y, x] = 1

            if event.key == self.key_binds["right"]:

                # updating the coords before moving
                self.active_piece.coords = self.active_piece.get_coords(self.grid, True)

                # if it can move right, then it moves right
                if self.active_piece.can_move(1, 0):
                    self.active_piece.move(1, 0)

            elif event.key == self.key_binds["left"]:

                # checks if the shape can move left
                self.active_piece.coords = self.active_piece.get_coords(self.grid, False)

                # if it can move left, then it moves left
                if self.active_piece.can_move(-1, 0):
                    self.active_piece.move(-1, 0)

            if event.key == self.key_binds["speed up"]:
                self.active_piece.speed = 3 * self.base_speed

        elif event.type == pygame.KEYUP:

            if event.key == self.key_binds["speed up"]:
                self.active_piece.speed = self.base_speed

    def check_lines(self):
        # number of lines broken at the same time
        lines_in_a_row = 0

        # checks if grid line of grid is only made of 2s, if so we move all the lines higher than this line down
        for i in range(self.grid.shape[0]):

            if not self.config.data["empty"] in self.grid[i, :] and not self.config.data["moving_block"] in self.grid[i, :]:
                self.line_broken += 1
                lines_in_a_row += 1
                self.score += self.config.data["score_per_line"] * lines_in_a_row
                self.move_line_down(i)

                if self.line_broken % 10 == 0:
                    self.base_speed += 0.5

    def handle_falling(self):
        """""
        makes the moving blocks fall
        """""
        if self.counter % int(self.config.data["fall_tick_rate"] / self.active_piece.speed) == 0:

            # getting the coords of the blocks before moving them
            self.active_piece.coords = self.active_piece.get_coords(self.grid, True)

            # if the block can move down then it moves down
            if self.active_piece.can_move(0, 1):
                self.active_piece.move(0, 1)
            else:
                self.spawn_new_blocks()
                # if the game is over, we don't add the points
                if not self.over:
                    self.score += self.config.data["score_per_block"]

            print("grid : ", self.grid)

        self.counter += 1

    def spawn_new_blocks(self):
        for co in self.active_piece.coords:
            # creating the put blocks with the blocks color
            self.grid[co[0], co[1]] = self.active_piece.color_value

        # else, we create new blocks
        self.active_piece = ActivePiece(self, self.config, self.next_color)

        self.insert_blocks()
        self.next_color = self.client.get_color()

    def send_data(self):
        """""
        sends the grid and the score to the server
        """""

        # we don't send the grid if there's more than 2 players online or less because we can't display three grids
        if self.nb_players == 2:
            grid = self.grid.copy()
            # we transform the 1 with the active color so that the other computer can know what color it is
            grid[grid==1] = self.active_piece.color_value
            # transform the grid into a list of int
            grid = grid.astype(int).tolist()
            self.client.send_request({"type": "TRANSFER", "name": "GRID", "args": grid})

            self.client.send_request({"type": "TRANSFER", "name": "SCORE", "args": self.score})

            self.client.send_request({"type": "TRANSFER", "name": "NEXT_COLOR", "args": self.next_color})

    def render(self):
        # we fill the entire screen with black so we can recreate the whole ui
        self.screen.fill(self.config.data["bg_color"])

        self.game_ui["you"].render(self.grid, self.score, self.next_color,
                                       active_color=self.active_piece.color_value)

        # when we have all the informations about the opponent we can display its data
        if 'GRID' in self.client.responses and self.client.responses['GRID'] is not None:
            grid = np.array(self.client.responses["GRID"])

            if 'SCORE' in self.client.responses and self.client.responses['SCORE'] is not None:
                score = self.client.responses["SCORE"]

                if 'NEXT_COLOR' in self.client.responses and self.client.responses['NEXT_COLOR'] is not None:
                    next_color = self.client.responses["NEXT_COLOR"]

                    self.game_ui["opponent"].render(grid, score, next_color)


    def update(self):

        self.check_lines()

        self.handle_falling()

        self.send_data()

        self.render()

        if self.over:
            print("Game over 2")
            return "game_over"
