def main():
    from video_game.states.flappybird_state import FlappyBirdState
    from video_game.players.flappybird_player import create_player
    from . import game_regression

    canvas_shape = (30, 30)
    state = FlappyBirdState(canvas_shape = canvas_shape)

    game_regression.main('flappybird', state, create_player)

