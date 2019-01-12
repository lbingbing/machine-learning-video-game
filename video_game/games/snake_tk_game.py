from .tk_game import BaseApp
from video_game.states import snake_state

class SnakeApp(BaseApp):

    def set_intervals(self):
        self.update_interval_in_millisecond = 100
        self.async_response_poll_interval_in_millisecond = 100

    def init_state(self):
        canvas_shape = (10, 10)
        self.state = snake_state.SnakeState(canvas_shape = canvas_shape)

    def create_player(self, state, player_type):
        from video_game.players.snake_player import create_player
        return create_player(state, player_type)

    def get_unit_size(self):
        return 30

    def bind_human_player_events(self):
        self.root.bind('<Up>', lambda e: (self.state.get_action_done() or self.state.do_action(snake_state.UP)))
        self.root.bind('<Down>', lambda e: (self.state.get_action_done() or self.state.do_action(snake_state.DOWN)))
        self.root.bind('<Left>', lambda e: (self.state.get_action_done() or self.state.do_action(snake_state.LEFT)))
        self.root.bind('<Right>', lambda e: (self.state.get_action_done() or self.state.do_action(snake_state.RIGHT)))

    def get_transcript_save_path(self):
        return os.path.join(os.path.dirname(__file__), 'snake.trans')

    def draw(self):
        for i in range(self.state.height):
            for j in range(self.state.width):
                if self.state.canvas[i][j] == snake_state.BACKGROUND:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#ffffff')
                elif self.state.canvas[i][j] == snake_state.SNAKE_BODY:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#333333')
                elif self.state.canvas[i][j] == snake_state.SNAKE_HEAD:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#000000')
                elif self.state.canvas[i][j] == snake_state.TARGET:
                    self.canvas.itemconfigure(self.canvas_unit_objs[i][j], fill = '#ff0000')

def main():
    from .utils import get_cmd_options

    args = get_cmd_options('snake tk game')
    app = SnakeApp(args.player_type, args.save_transcript)
    app.mainloop()

