import numpy as np
import random
import pygame

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

    def get_coords(self, array: np.array, reverse: bool) -> list:
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

    def simulate_right_turn(self) -> np.array:
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

    def simulate_left_turn(self) -> np.array:
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

    def can_fit(self, piece_array: np.array) -> bool:
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


class Game:

    def __init__(self, screen: pygame.surface.Surface, config):
        self.screen = screen
        self.config = config

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

        self.font = pygame.font.SysFont(self.config.data["font_name"], self.config.data["font_size"])
        self.counter = 0

        self.key_binds = self.config.data["key_binds"]

    def start_game(self, client):
        # when starting the game, we need a client to communicate with the server
        self.client = client

        self.active_piece = ActivePiece(self, self.config, self.client.get_color())
        self.insert_blocks()


        self.next_color = int(self.client.get_color())

    def insert_blocks(self):
        """""
        insert the moving blocks at the top of the screen
        """""
        y = self.active_piece.pos[0] + self.active_piece.array.shape[0]
        x = self.active_piece.pos[1] + self.active_piece.array.shape[1]
        # if there's grid put block where the blocks must generate
        for color_value in range(self.config.data["first_fixed_block"], self.config.data["last_fixed_block"] + 1):
            if color_value in self.grid[self.active_piece.pos[0]:y, self.active_piece.pos[1]:x]:
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

# updates the render

# updates the opponent's data

    def update_opponent_grid(self, grid):
        for y in range(grid.shape[0]):

            for x in range(grid.shape[1]):

                if grid[y, x] in range(self.config.data["first_fixed_block"], self.config.data["last_fixed_block"] + 1):
                    self.screen.blit(blocks[grid[y, x]]["image"], (
                        self.playing_screen_size[0] + self.config.data["sidebar_offset"] + x * BLOCK_SIZE // 3,
                        170 + y * BLOCK_SIZE // 3,
                        BLOCK_SIZE // 3, BLOCK_SIZE // 3))

    def update_opponent_score(self, score):
        score_text = self.font.render(f"Opponent's score : {score}", 1, self.config.data["colors"]["white"])
        self.screen.blit(score_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"], 400))

    # updates the user's data

    def update_next_block(self):
        next_array = blocks[self.next_color]["arrays"][0]

        for y in range(next_array.shape[0]):

            for x in range(next_array.shape[1]):

                if next_array[y, x] == self.config.data["moving_block"]:
                    self.screen.blit(blocks[self.next_color]["image"], (
                        self.playing_screen_size[0] + self.config.data["sidebar_offset"] + x * BLOCK_SIZE,
                        70 + y * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE))

    def update_score(self):
        score_text = self.font.render(f"Score : {self.score}", 1, self.config.data["colors"]["white"])
        self.screen.blit(score_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"], 150))

    def update_texts(self):
        blocks_text = self.font.render("Next block:", 1, self.config.data["colors"]["white"])
        self.screen.blit(blocks_text, (self.playing_screen_size[0] + self.config.data["sidebar_offset"], 10))

    def render(self):
        """""
        update the displays on the right side of the screen
        """""
        pygame.draw.rect(self.screen, self.config.data["colors"]["black"], (
            (self.playing_screen_size[0] + self.config.data["sidebar_offset"], 0),
            (self.screen.get_width() - self.playing_screen_size[0], self.screen.get_height())))

        self.update_score()
        self.update_texts()
        self.update_next_block()

        self.get_opponent_data()

        # creating the right part of the screen
        pygame.draw.rect(self.screen, self.config.data["colors"]["blue"],
                         ((self.playing_screen_size[0], 0), (10, self.screen.get_height())))


    def update_blocks(self):
        # updating the blocks
        self.screen.fill(self.config.data["bg_color"])
        non_zero = np.argwhere(self.grid != 0)

        for y, x in non_zero:

            if self.is_fixed_block((y, x)):
                self.screen.blit(blocks[int(self.grid[y, x])]["image"],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

            else:
                self.screen.blit(blocks[self.active_piece.color_value]["image"],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

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

        self.counter += 1

    def spawn_new_blocks(self):
        for co in self.active_piece.coords:
            # creating the put blocks with the blocks color
            self.grid[co[0], co[1]] = self.active_piece.color_value

        # else, we create new blocks
        self.active_piece = ActivePiece(self, self.config, self.next_color)

        self.insert_blocks()
        self.next_color = int(self.client.get_color())

    def send_data(self):
        """""
        sends the grid and the score to the server
        """""
        self.client.send_request({"type": "PUT", "name": "GRID", "args": self.grid.tolist()})
        self.client.send_request({"type": "PUT", "name": "SCORE", "args": self.score})

    def get_opponent_data(self):
        # waits for server to send the opponent's data
        while self.client.response["name"] != "GRID":
            pass
        # updates the opponen'ts grid after transforming the response into a list
        self.update_opponent_grid(np.array(self.client.response["args"]))

        while self.client.response["name"] != "SCORE":
            pass
        self.update_opponent_score(self.client.response["args"])



    def update(self):

        self.update_blocks()

        self.check_lines()

        self.handle_falling()

        self.send_data()

        self.render()

        if self.over:
            return "game_over"
