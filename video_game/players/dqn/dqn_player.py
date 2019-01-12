from video_game.players import player

class DqnPlayer(player.Player):
    type = player.DQN_PLAYER

    def __init__(self, state_shape, action_dim, model_path):

        self.model = self.create_model(state_shape = state_shape, action_dim = action_dim, model_path = model_path)
        self.model.load()

    def create_model(self, state_shape, history_length, action_dim, model_path):
        pass

    def get_action(self, state):
        return self.model.get_opt_action(state)

