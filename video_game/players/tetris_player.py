import os

from . import player

def create_player(state, player_type):
    p = None
    if player_type == player.HUMAN_PLAYER:
        from .human.human_player import HumanPlayer
        p = HumanPlayer()
    elif player_type == player.MONITOR_PLAYER:
        from .monitor.monitor_player import MonitorPlayer
        p = MonitorPlayer()
    elif player_type == player.RANDOM_PLAYER:
        from .random.random_player import RandomPlayer
        p = RandomPlayer()
    elif player_type == player.DQN_PLAYER:
        from .dqn.tetris_dqn_player import TetrisDqnPlayer
        model_path = 'tetris_dqn_model_{0}_{1}'.format(state.height, state.width)
        model_path = os.path.join(os.path.dirname(__file__), 'dqn', model_path)
        p = TetrisDqnPlayer(state_shape = (state.height, state.width, state.depth), action_dim = state.get_action_dim(), model_path = model_path)
    elif player_type == player.POLICYNET_PLAYER:
        from .policynet.tetris_policynet_player import TetrisPolicyNetPlayer
        model_path = 'tetris_policynet_model_{0}_{1}'.format(state.height, state.width)
        model_path = os.path.join(os.path.dirname(__file__), 'policynet', model_path)
        p = TetrisPolicyNetPlayer(state_shape = (state.height, state.width, state.depth), action_dim = state.get_action_dim(), model_path = model_path)
    return p

