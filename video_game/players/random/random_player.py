import random

from video_game.players import player

class RandomPlayer(player.Player):
    type = player.RANDOM_PLAYER

    def get_action(self, state):
        return random.choice(state.get_legal_actions())

