from .tk_game import BaseApp
from video_game.states import flappybird_state

class FlappyBirdApp(BaseApp):

    def set_intervals(self):
        self.update_interval_in_millisecond = 50
        self.async_response_poll_interval_in_millisecond = 50

    def init_state(self):
        canvas_shape = (30, 30)
        self.state = flappybird_state.FlappyBirdState(canvas_shape = canvas_shape)

    def create_player(self, state, player_type):
        from video_game.players.flappybird_player import create_player
        return create_player(state, player_type)

    def get_unit_size(self):
        return 15

    def bind_human_player_events(self):
        self.root.bind('<KeyPress-space>', lambda e: (self.state.get_action_done() or self.state.do_action(flappybird_state.FLY)))

    def get_transcript_save_path(self):
        return os.path.join(os.path.dirname(__file__), 'flappybird.trans')

    def draw(self):
        for i in range(self.state.height):
            for j in range(self.state.width):
                if self.state.canvas[i][j] == flappybird_state.BACKGROUND:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#ffffff')
                elif self.state.canvas[i][j] == flappybird_state.BIRD:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#ff0000')
                elif self.state.canvas[i][j] == flappybird_state.WALL:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#000000')
                elif self.state.canvas[i][j] == flappybird_state.TARGET:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#0000ff')
                else:
                    assert(0)

def main():
    from .utils import get_cmd_options

    args = get_cmd_options('flappybird tk game')
    app = FlappyBirdApp(args.player_type, args.save_transcript)
    app.mainloop()

