from .dqn_player import DqnPlayer
from .flappybird_dqn import FlappyBirdDqnModel

class FlappyBirdDqnPlayer(DqnPlayer):
    def create_model(self, state_shape, action_dim, model_path):
        return FlappyBirdDqnModel(state_shape = state_shape, action_dim = action_dim, model_path = model_path)

