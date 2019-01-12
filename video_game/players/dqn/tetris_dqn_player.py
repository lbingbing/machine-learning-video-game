from .dqn_player import DqnPlayer
from .tetris_dqn import TetrisDqnModel

class TetrisDqnPlayer(DqnPlayer):
    def create_model(self, state_shape, action_dim, model_path):
        return TetrisDqnModel(state_shape = state_shape, action_dim = action_dim, model_path = model_path)

