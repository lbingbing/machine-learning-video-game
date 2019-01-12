def get_config():
    import os

    from video_game.states.tetris_state import TetrisState
    from .tetris_dqn import TetrisDqnModel

    canvas_shape = (20, 10)
    print('canvas_shape:', canvas_shape)

    state = TetrisState(canvas_shape = canvas_shape)
    model_path = 'tetris_dqn_model_{0}_{1}'.format(canvas_shape[0], canvas_shape[1])
    model_path = os.path.join(os.path.dirname(__file__), model_path)
    model = TetrisDqnModel(state_shape = canvas_shape + (state.depth, ), action_dim = state.get_action_dim(), model_path = model_path)

    config = {
        'model_path' : model_path,
        'replay_memory_size' : 256 * 1024,
        'search_rate' : 0.1,
        'discount' : 0.999,
        'batch_size' : 64,
        'epoch_num' : 1,
        'learning_rate' : 0.0001,
        'episode_num' : 2000000,
    }

    def get_reward(state):
        if state.is_end():
            return -10
        elif state.get_last_score() > 0:
            return 10 * state.get_last_score()
        else:
            return 0

    return state, model, config, get_reward

def main():
    from . import dqn_train

    dqn_train.main('tetris', get_config)

