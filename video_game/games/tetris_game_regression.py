def main():
    from video_game.states.tetris_state import TetrisState
    from video_game.players.tetris_player import create_player
    from . import game_regression

    canvas_shape = (20, 10)
    state = TetrisState(canvas_shape = canvas_shape)

    game_regression.main('tetris', state, create_player)

