import random
import itertools
import numpy as np

NOP    = 0
LEFT   = 1
RIGHT  = 2
ROTATE = 3
FIRE   = 4
FALL   = 5
LAND   = 6

BACKGROUND   = 0
LANDED_UNIT  = 1
FALLING_UNIT = -1

NORMAL_TYPE  = 0
DOT_TYPE     = 1
NEG_GUN_TYPE = 3
POS_GUN_TYPE = 2
BOMB_TYPE    = 4

BRICK_TYPES = (
        ( NORMAL_TYPE, 1, ((0, 0), (1, 0), (2, 0), (3, 0))),
        ( NORMAL_TYPE, 1, ((0, 0), (0, 1), (1, 0), (1, 1))),
        ( NORMAL_TYPE, 1, ((0, 0), (0, 1), (0, 2), (1, 1))),
        ( NORMAL_TYPE, 1, ((0, 0), (0, 1), (1, 1), (1, 2))),
        ( NORMAL_TYPE, 1, ((0, 0), (0, 1), (0, 2), (1, 0))),
        ( NORMAL_TYPE, 1, ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1))),
        ( NORMAL_TYPE, 1, ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2))),
        (    DOT_TYPE, 1, ((0, 0), )),
        (NEG_GUN_TYPE, 1, ((0, 0), (1, 0))),
        (POS_GUN_TYPE, 1, ((0, 0), (1, 0), (2, 0))),
        (   BOMB_TYPE, 1, ((0, 0), (0, 3), (1, 1), (1, 2), (2, 1), (2, 2))),
    )

BRICK_CUMULATIVE_WEIGHTS = list(itertools.accumulate(w for t, w, coords in BRICK_TYPES))

class TetrisState:

    def __init__(self, canvas_shape):
        self.height = canvas_shape[0]
        self.width = canvas_shape[1]
        self.depth = 1
        self.reset()

    def reset(self):
        self.landed_canvas = [[False for j in range(self.width)] for i in range(self.height)]
        self.action_done = False
        self.last_score = 0
        self.score = 0
        self.end = False
        self.age = 0

        self.generate_falling_brick()
        self.render()

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
        legal_actions = [NOP]
        if self.can_move_left():
            legal_actions.append(LEFT)
        if self.can_move_right():
            legal_actions.append(RIGHT)
        if self.falling_brick_type == NORMAL_TYPE and self.can_rotate():
            legal_actions.append(ROTATE)
        if self.falling_brick_type == NEG_GUN_TYPE or self.falling_brick_type == POS_GUN_TYPE:
            legal_actions.append(FIRE)
        if self.can_fall():
            legal_actions.append(FALL)
            legal_actions.append(LAND)
        return legal_actions

    def can_move_left(self):
        for y, x in self.falling_brick_positions:
            if x-1 < 0 or self.falling_brick_type != BOMB_TYPE and self.landed_canvas[y][x-1]:
                return False
        return True

    def move_left(self):
        for pos in self.falling_brick_positions:
            pos[1] -= 1

    def can_move_right(self):
        for y, x in self.falling_brick_positions:
            if x+1 >= self.width or self.falling_brick_type != BOMB_TYPE and self.landed_canvas[y][x+1]:
                return False
        return True

    def move_right(self):
        for pos in self.falling_brick_positions:
            pos[1] += 1

    def get_rotated_positions(self, positions):
        y_min = min(y for y, x in positions)
        y_max = max(y for y, x in positions)
        x_min = min(x for y, x in positions)
        x_max = max(x for y, x in positions)
        center_y = (y_min + y_max) // 2
        center_x = (x_min + x_max) // 2
        rotated_positions = []
        for y, x in positions:
            rotated_y = center_y - (x - center_x)
            rotated_x = center_x + (y - center_y)
            rotated_positions.append([rotated_y, rotated_x])
        new_y_max = max(y for y, x in rotated_positions)
        for pos in rotated_positions:
            pos[0] += y_max - new_y_max
        new_y_min = min(y for y, x in rotated_positions)
        if new_y_min < 0:
            for pos in rotated_positions:
                pos[0] -= new_y_min
        new_y_max = max(y for y, x in rotated_positions)
        if new_y_max >= self.height:
            for pos in rotated_positions:
                pos[0] -= new_y_max - (self.height - 1)
        new_x_min = min(x for y, x in rotated_positions)
        if new_x_min < 0:
            for pos in rotated_positions:
                pos[1] -= new_x_min
        new_x_max = max(x for y, x in rotated_positions)
        if new_x_max >= self.width:
            for pos in rotated_positions:
                pos[1] -= new_x_max - (self.width - 1)
        return rotated_positions

    def can_rotate(self):
        for y, x in self.get_rotated_positions(self.falling_brick_positions):
            if self.landed_canvas[y][x]:
                return False
        return True

    def rotate(self):
        self.falling_brick_positions = self.get_rotated_positions(self.falling_brick_positions)

    def fire(self):
        y, x = self.falling_brick_positions[-1]
        if self.falling_brick_type == NEG_GUN_TYPE:
            for y1 in range(y+1, self.height):
                if self.landed_canvas[y1][x]:
                    self.landed_canvas[y1][x] = False
                    break
        elif self.falling_brick_type == POS_GUN_TYPE:
            y1 = y
            while y1+1 < self.height and not self.landed_canvas[y1+1][x]:
                y1 += 1
            if y1 > y:
                self.landed_canvas[y1][x] = True
                self.check_full_row()

    def explode(self):
        y_min = min(y for y, x in self.falling_brick_positions)
        x_min = min(x for y, x in self.falling_brick_positions)
        for y in range(y_min, y_min+4):
            if y < self.height:
                for x in range(x_min, x_min+4):
                    if x < self.width:
                        self.landed_canvas[y][x] = False

    def can_fall(self):
        if self.falling_brick_type == DOT_TYPE:
            y, x = self.falling_brick_positions[0]
            if any(not self.landed_canvas[y1][x] for y1 in range(y+1, self.height)):
                return True
            else:
                return False
        else:
            for y, x in self.falling_brick_positions:
                if y+1 >= self.height or self.landed_canvas[y+1][x]:
                    return False
            return True

    def fall(self):
        for pos in self.falling_brick_positions:
            pos[0] += 1

    def land(self):
        while self.can_fall():
            self.fall()

    def do_action(self, action):
        assert(not self.action_done)
        self.action_done = True
        if action == LEFT:
            assert(self.can_move_left())
            self.move_left()
        elif action == RIGHT:
            assert(self.can_move_right())
            self.move_right()
        elif action == ROTATE:
            assert(self.can_rotate())
            self.rotate()
        elif action == FIRE:
            assert(self.falling_brick_type == NEG_GUN_TYPE or self.falling_brick_type == POS_GUN_TYPE)
            self.fire()
        elif action == FALL:
            assert(self.can_fall())
            self.fall()
        elif action == LAND:
            assert(self.can_fall())
            self.land()

    def land_brick(self):
        if self.falling_brick_type == NORMAL_TYPE or self.falling_brick_type == DOT_TYPE:
            for y, x in self.falling_brick_positions:
                self.landed_canvas[y][x] = True
            self.check_full_row()
        elif self.falling_brick_type == BOMB_TYPE:
            self.explode()

    def check_full_row(self):
        full_row_ids = [row_id for row_id in range(self.height-1, -1, -1) if all(self.landed_canvas[row_id])]
        if full_row_ids:
            for row_id in full_row_ids:
                del self.landed_canvas[row_id]
            for i in range(len(full_row_ids)):
                self.landed_canvas.insert(0, [False for j in range(self.width)])
            self.last_score = len(full_row_ids) ** 2
            self.score += self.last_score

    def flip_x(self):
        center_x = (max(x for y, x in self.falling_brick_positions) + min(x for y, x in self.falling_brick_positions)) // 2
        for pos in self.falling_brick_positions:
            pos[1] = center_x * 2 - pos[1]

    def generate_falling_brick(self):
        brick_type, weight, brick_shape = random.choices(BRICK_TYPES, cum_weights = BRICK_CUMULATIVE_WEIGHTS, k = 1)[0]
        self.falling_brick_type = brick_type
        w = max(x for y, x in brick_shape) - min(x for y, x in brick_shape) + 1
        offset = (self.width - w) // 2
        self.falling_brick_positions = [[y, offset+x] for y, x in brick_shape]
        if self.falling_brick_type == NORMAL_TYPE:
            if random.random() < 0.5:
                self.flip_x()
            for i in range(random.randint(0, 3)):
                self.rotate()
            y_min = min(y for y, x in self.falling_brick_positions)
            for pos in self.falling_brick_positions:
                pos[0] -= y_min
        if any(self.landed_canvas[y][x] for y, x in self.falling_brick_positions):
            if self.falling_brick_type == NORMAL_TYPE or self.falling_brick_type == DOT_TYPE:
                self.end = True
            elif self.falling_brick_type == NEG_GUN_TYPE or self.falling_brick_type == POS_GUN_TYPE:
                self.generate_falling_brick()
            elif self.falling_brick_type == BOMB_TYPE:
                self.explode()
                self.generate_falling_brick()

    def render(self):
        self.canvas = [[BACKGROUND for j in range(self.width)] for i in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.landed_canvas[y][x]:
                    self.canvas[y][x] = LANDED_UNIT
        for y, x in self.falling_brick_positions:
            self.canvas[y][x] = FALLING_UNIT

    def update(self):
        self.last_score = 0
        if self.can_fall():
            self.fall()
        else:
            self.land_brick()
            self.generate_falling_brick()
        self.action_done = False
        self.age += 1
        self.render()

    def to_state_m(self):
        return np.array(self.canvas).reshape(1, self.height, self.width, 1)

    def get_action_dim(self):
        return 7

    def action_to_action_index(self, action):
        return action

    def action_index_to_action(self, action_index):
        return action_index

    def get_legal_action_mask_m(self):
        legal_action_mask_m = np.zeros((1, self.get_action_dim()))
        legal_action_indexes = [self.action_to_action_index(action) for action in self.get_legal_actions()]
        legal_action_mask_m[:, legal_action_indexes] = 1
        return legal_action_mask_m

