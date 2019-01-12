from .tk_game import BaseApp
from video_game.states import tetris_state

class TetrisApp(BaseApp):

    def set_intervals(self):
        self.update_interval_in_millisecond = 50
        self.async_response_poll_interval_in_millisecond = 50

    def init_state(self):
        canvas_shape = (20, 10)
        self.state = tetris_state.TetrisState(canvas_shape = canvas_shape)

    def create_player(self, state, player_type):
        from video_game.players.tetris_player import create_player
        return create_player(state, player_type)

    def get_unit_size(self):
        return 20

    def bind_human_player_events(self):
        self.root.bind('<Left>', lambda e: self.try_move_left())
        self.root.bind('<Right>', lambda e: self.try_move_right())
        self.root.bind('<Up>', lambda e: self.try_rotate())
        self.root.bind('<Down>', lambda e: self.try_fall())
        self.root.bind('<KeyPress-a>', lambda e: self.try_fire())
        self.root.bind('<KeyPress-space>', lambda e: self.try_land())

    def try_move_left(self):
        if not self.state.get_action_done() and tetris_state.LEFT in self.state.get_legal_actions():
            self.state.do_action(tetris_state.LEFT)

    def try_move_right(self):
        if not self.state.get_action_done() and tetris_state.RIGHT in self.state.get_legal_actions():
            self.state.do_action(tetris_state.RIGHT)

    def try_rotate(self):
        if not self.state.get_action_done() and tetris_state.ROTATE in self.state.get_legal_actions():
            self.state.do_action(tetris_state.ROTATE)

    def try_fire(self):
        if not self.state.get_action_done() and tetris_state.FIRE in self.state.get_legal_actions():
            self.state.do_action(tetris_state.FIRE)

    def try_fall(self):
        if not self.state.get_action_done() and tetris_state.FALL in self.state.get_legal_actions():
            self.state.do_action(tetris_state.FALL)

    def try_land(self):
        if not self.state.get_action_done() and tetris_state.LAND in self.state.get_legal_actions():
            self.state.do_action(tetris_state.LAND)

    def get_transcript_save_path(self):
        return os.path.join(os.path.dirname(__file__), 'tetris.trans')

    def draw(self):
        for i in range(self.state.height):
            for j in range(self.state.width):
                if self.state.canvas[i][j] == tetris_state.BACKGROUND:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#ffffff')
                elif self.state.canvas[i][j] == tetris_state.LANDED_UNIT:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#333333')
                elif self.state.canvas[i][j] == tetris_state.FALLING_UNIT:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#888888')
                else:
                    assert(0)

def main():
    from .utils import get_cmd_options

    args = get_cmd_options('tetris tk game')
    app = TetrisApp(args.player_type, args.save_transcript)
    app.mainloop()

