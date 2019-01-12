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
        from .dqn.snake_dqn_player import SnakeDqnPlayer
        model_path = 'snake_dqn_model_{0}_{1}'.format(state.height, state.width)
        model_path = os.path.join(os.path.dirname(__file__), 'dqn', model_path)
        p = SnakeDqnPlayer(state_shape = (state.height, state.width, state.depth), action_dim = state.get_action_dim(), model_path = model_path)
    elif player_type == player.POLICYNET_PLAYER:
        from .policynet.snake_policynet_player import SnakePolicyNetPlayer
        model_path = 'snake_policynet_model_{0}_{1}'.format(state.height, state.width)
        model_path = os.path.join(os.path.dirname(__file__), 'policynet', model_path)
        p = SnakePolicyNetPlayer(state_shape = (state.height, state.width, state.depth), action_dim = state.get_action_dim(), model_path = model_path)
    return p

