import random
import copy
import numpy as np

UP    = 0
DOWN  = 1
LEFT  = 2
RIGHT = 3

BACKGROUND = 0
SNAKE_BODY = 1
SNAKE_HEAD = 2
TARGET     = -1

HISTORY_LENGTH = 1

class SnakeState:

    def __init__(self, canvas_shape):
        self.height = canvas_shape[0]
        self.width = canvas_shape[1]
        self.depth = HISTORY_LENGTH + 1
        self.reset()

    def reset(self):
        self.direction = RIGHT
        self.snake_positions = [(self.height//2-1, self.width//2), (self.height//2-1, self.width//2-1)]
        self.backgournd_positions = [(i, j) for i in range(self.height) for j in range(self.width) if (i, j) not in self.snake_positions]
        self.action_done = False
        self.last_score = 0
        self.end = False
        self.age = 0

        self.generate_target()
        self.render()

        self.canvas_history = []
        for i in range(HISTORY_LENGTH):
            self.canvas_history.append(copy.deepcopy(self.canvas))

    def __str__(self):
        return '\n'.join(map(lambda row: ''.join(map(lambda e: '{:2d}'.format(e), row)), self.canvas))

    def get_score(self):
        return len(self.snake_positions) - 2

    def get_age(self):
        return self.age

    def get_last_score(self):
        return self.last_score

    def get_action_done(self):
        return self.action_done

    def is_end(self):
        return self.end

    def get_legal_actions(self):
        if self.direction == UP:
            legal_actions = [UP, LEFT, RIGHT]
        elif self.direction == DOWN:
            legal_actions = [DOWN, LEFT, RIGHT]
        elif self.direction == LEFT:
            legal_actions = [UP, DOWN, LEFT]
        elif self.direction == RIGHT:
            legal_actions = [UP, DOWN, RIGHT]
        return legal_actions

    def do_action(self, action):
        assert(not self.action_done)
        self.action_done = True
        if action == UP and self.direction != DOWN:
            self.direction = UP
        elif action == DOWN and self.direction != UP:
            self.direction = DOWN
        elif action == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif action == RIGHT and self.direction != LEFT:
            self.direction = RIGHT

    def generate_target(self):
        self.target_position = random.choice(self.backgournd_positions)
        self.backgournd_positions.remove(self.target_position)

    def render(self):
        self.canvas = [[BACKGROUND for j in range(self.width)] for i in range(self.height)]
        self.canvas[self.snake_positions[0][0]][self.snake_positions[0][1]] = SNAKE_HEAD
        for pos in self.snake_positions[1:]:
            self.canvas[pos[0]][pos[1]] = SNAKE_BODY
        self.canvas[self.target_position[0]][self.target_position[1]] = TARGET

    def update(self):
        del self.canvas_history[0]
        self.canvas_history.append(copy.deepcopy(self.canvas))

        next_y = self.snake_positions[0][0] 
        next_x = self.snake_positions[0][1]
        if self.direction == UP:
            next_y -= 1
        elif self.direction == DOWN:
            next_y += 1
        elif self.direction == LEFT:
            next_x -= 1
        elif self.direction == RIGHT:
            next_x += 1
        else:
            assert(0)
        if next_y < 0 or next_y >= self.height or next_x < 0 or next_x >= self.width or \
           (next_y, next_x) in self.snake_positions[:-1]:
            self.end = True
            return
        if (next_y, next_x) == self.target_position:
            self.last_score = 0
            self.generate_target()
        else:
            self.last_score = 1
            tail_y = self.snake_positions[-1][0]
            tail_x = self.snake_positions[-1][1]
            del self.snake_positions[-1]
            if (next_y, next_x) != (tail_y, tail_x):
                self.backgournd_positions.remove((next_y, next_x))
                self.backgournd_positions.append((tail_y, tail_x))
        self.snake_positions.insert(0, (next_y, next_x))
        self.action_done = False
        self.age += 1
        self.render()

    def to_state_m(self):
        state_m = np.array(self.canvas).reshape(self.height, self.width, 1)
        history_m = np.transpose(np.array(self.canvas_history), axes = (1, 2, 0))
        res = np.concatenate((history_m, state_m), axis = 2)
        return res.reshape(1, self.height, self.width, HISTORY_LENGTH + 1)

    def get_action_dim(self):
        return 4

    def action_to_action_index(self, action):
        return action

    def action_index_to_action(self, action_index):
        return action_index

    def get_legal_action_mask_m(self):
        legal_action_mask_m = np.zeros((1, self.get_action_dim()))
        legal_action_indexes = [self.action_to_action_index(action) for action in self.get_legal_actions()]
        legal_action_mask_m[:, legal_action_indexes] = 1
        return legal_action_mask_m

