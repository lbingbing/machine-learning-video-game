from .dqn_player import DqnPlayer
from .snake_dqn import SnakeDqnModel

class SnakeDqnPlayer(DqnPlayer):
    def create_model(self, state_shape, action_dim, model_path):
        return SnakeDqnModel(state_shape = state_shape, action_dim = action_dim, model_path = model_path)

