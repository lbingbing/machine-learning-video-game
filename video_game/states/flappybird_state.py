import random
import copy
import numpy as np

BIRD_HEIGHT = 2
BIRD_WIDTH  = 2

NOP = 0
FLY = 1

BACKGROUND = 0
BIRD       = 1
WALL       = -1
TARGET     = 2

GRAVITY = 1
FLY_SPEED = -2

HISTORY_LENGTH = 1

SPACE_LENGTH_LOW = 6
SPACE_LENGTH_HIGH = 15
WALL_WIDTH_LOW = 4
WALL_WIDTH_HIGH = 6
WALL_DELAY_COUNT_LOW = 15
WALL_DELAY_COUNT_HIGH = 30

class FlappyBirdState:

    def __init__(self, canvas_shape):
        self.height = canvas_shape[0]
        self.width = canvas_shape[1]
        self.depth = HISTORY_LENGTH + 1
        self.reset()

    def reset(self):
        self.bird_y = self.height//2-1
        self.bird_x = 2
        self.speed = 0
        self.walls = []
        self.targets = []
        self.action_done = False
        self.last_score = 0
        self.score = 0
        self.end = False
        self.age = 0

        self.generate_wall_and_target()
        self.render()

        self.canvas_history = []
        for i in range(HISTORY_LENGTH):
            self.canvas_history.append(copy.deepcopy(self.canvas))

    def __str__(self):
        return '\n'.join(map(lambda row: ''.join(map(lambda e: '{:2d}'.format(e), row)), self.canvas))

    def get_score(self):
        return self.score

    def get_age(self):
        return self.age

    def get_last_score(self):
        return self.last_score

    def get_action_done(self):
        return self.action_done

    def is_end(self):
        return self.end

    def get_legal_actions(self):
        return [NOP, FLY]

    def do_action(self, action):
        assert(not self.action_done)
        self.action_done = True
        if action == FLY:
            self.speed = FLY_SPEED

    def update_wall_and_targets(self):
        for wall in self.walls:
            wall[1] -= 1
            wall[3] -= 1
        for target in self.targets:
            target[1] -= 1

    def is_hit_boundary(self):
        return self.bird_y < 0 or self.bird_y+BIRD_HEIGHT > self.height

    def is_hit_wall(self):
        for wall_y0, wall_x0, wall_y1, wall_x1 in self.walls:
            if (wall_y0 < self.bird_y+BIRD_HEIGHT and self.bird_y < wall_y1) and \
               (wall_x0 < self.bird_x+BIRD_WIDTH and self.bird_x < wall_x1):
                return True
        return False

    def handle_hit_target(self):
        self.last_score = 0
        target_to_delete = None
        for target in self.targets:
            if target[0] >= self.bird_y and target[0] < self.bird_y + BIRD_HEIGHT and \
               target[1] >= self.bird_x and target[1] < self.bird_x + BIRD_WIDTH:
                self.last_score = 1
                self.score += 1
                target_to_delete = target
                break
        if target_to_delete != None:
            self.targets.remove(target_to_delete)

    def generate_wall_and_target(self):
        self.wall_delay_counter = random.randint(WALL_DELAY_COUNT_LOW, WALL_DELAY_COUNT_HIGH)
        wall_width = random.randint(WALL_WIDTH_LOW, WALL_WIDTH_HIGH)

        space_length = random.randint(SPACE_LENGTH_LOW, SPACE_LENGTH_HIGH)
        wall_y1 = random.randint(0, self.height - space_length)
        wall_y2 = wall_y1 + space_length
        self.walls.append([0, self.width, wall_y1, self.width+wall_width])
        self.walls.append([wall_y2, self.width, self.height, self.width+wall_width])

        target_y = random.randint(0, self.height-1)
        target_x = self.width + random.randint(wall_width, self.wall_delay_counter-1)
        self.targets.append([target_y, target_x])

    def delete_wall_and_target(self):
        while True:
            if self.walls and self.walls[0][3] < 0:
                del self.walls[0]
            else:
                break
        while True:
            if self.targets and self.targets[0][1] < 0:
                del self.targets[0]
            else:
                break

    def render(self):
        self.canvas = [[BACKGROUND for j in range(self.width)] for i in range(self.height)]
        for i in range(self.bird_y, self.bird_y+BIRD_HEIGHT):
            if i >=0 and i < self.height:
                for j in range(self.bird_x, self.bird_x+BIRD_WIDTH):
                    if j >=0 and j < self.width:
                        self.canvas[i][j] = BIRD
        for wall_y0, wall_x0, wall_y1, wall_x1 in self.walls:
            for i in range(wall_y0, wall_y1):
                if i >=0 and i < self.height:
                    for j in range(wall_x0, wall_x1):
                        if j >=0 and j < self.width:
                            self.canvas[i][j] = WALL
        for target_y, target_x in self.targets:
            if target_y >=0 and target_y < self.height and \
               target_x >=0 and target_x < self.width:
                self.canvas[target_y][target_x] = TARGET

    def update(self):
        del self.canvas_history[0]
        self.canvas_history.append(copy.deepcopy(self.canvas))

        self.bird_y += self.speed
        self.update_wall_and_targets()
        if self.is_hit_boundary() or self.is_hit_wall():
            self.end = True
            self.render()
            return
        self.handle_hit_target()
        self.speed += GRAVITY
        self.delete_wall_and_target()
        if self.wall_delay_counter > 0:
            self.wall_delay_counter -= 1
        else:
            self.generate_wall_and_target()
        self.action_done = False
        self.age += 1
        self.render()

    def to_state_m(self):
        state_m = np.array(self.canvas).reshape(self.height, self.width, 1)
        history_m = np.transpose(np.array(self.canvas_history), axes = (1, 2, 0))
        res = np.concatenate((history_m, state_m), axis = 2)
        return res.reshape(1, self.height, self.width, HISTORY_LENGTH + 1)

    def get_action_dim(self):
        return 2

    def action_to_action_index(self, action):
        return action

    def action_index_to_action(self, action_index):
        return action_index

    def get_legal_action_mask_m(self):
        legal_action_mask_m = np.zeros((1, self.get_action_dim()))
        legal_action_indexes = [self.action_to_action_index(action) for action in self.get_legal_actions()]
        legal_action_mask_m[:, legal_action_indexes] = 1
        return legal_action_mask_m

