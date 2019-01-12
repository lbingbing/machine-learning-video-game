from board_game.players import player

class PolicyNetPlayer(player.Player):
    type = player.POLICYNET_PLAYER

    def __init__(self, player_id, board_shape, action_dim, model_path):
        super().__init__(player_id)

        self.model = self.create_model(board_shape = board_shape, action_dim = action_dim, model_path = model_path)
        self.model.load()

    def create_model(self, board_shape, action_dim, model_path):
        pass

    def get_action(self, state):
        super().get_action(state)
        return self.model.get_action(state, self.player_id)

