from .policynet_player import PolicyNetPlayer
from .gomoku_policynet import GomokuPolicyNetModel

class GomokuPolicyNetPlayer(PolicyNetPlayer):
    def create_model(self, board_shape, action_dim, model_path):
        return GomokuPolicyNetModel(board_shape = board_shape, action_dim = action_dim, model_path = model_path)

