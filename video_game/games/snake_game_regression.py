def main():
    from video_game.states.snake_state import SnakeState
    from video_game.players.snake_player import create_player
    from . import game_regression

    canvas_shape = (10, 10)
    state = SnakeState(canvas_shape = canvas_shape)

    game_regression.main('snake', state, create_player)

