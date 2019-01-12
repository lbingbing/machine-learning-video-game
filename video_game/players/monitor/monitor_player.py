from multiprocessing.connection import Client
import time

from video_game.players import player

class MonitorPlayer(player.Player):
    type = player.MONITOR_PLAYER

    def __init__(self):
        while True:
            try:
                self.conn = Client(('localhost', 7777), authkey=b'machine-learning-video-game-monitor-player')
                break
            except ConnectionError:
                time.sleep(1)

    def get_action(self, state):
        action, next_state = self.conn.recv()
        self.conn.send('ok')
        assert(action in state.get_legal_actions())
        return action, next_state

