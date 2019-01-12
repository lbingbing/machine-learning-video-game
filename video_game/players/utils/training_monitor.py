from multiprocessing.connection import Listener
import queue
import threading
import contextlib

class TrainingMonitor:

    def __init__(self):
        self.action_queue = queue.Queue()

        self.episodes = [[]]

        self.listener = Listener(('localhost', 7777), authkey=b'machine-learning-video-game-monitor-player')
        self.connections = []

        self.cv = threading.Condition()

        self.is_running = True

        self.buffer_action_thread = threading.Thread(target = self.buffer_action)
        self.buffer_action_thread.start()

        self.get_connection_thread = threading.Thread(target = self.get_connection)
        self.get_connection_thread.start()

        self.broadcast_thread = threading.Thread(target = self.broadcast)
        self.broadcast_thread.start()

    def send_action(self, item):
        self.action_queue.put(item)

    def buffer_action(self):
        while True:
            item = self.action_queue.get()
            if item == None:
                break
            action, is_end = item
            with self.cv:
                self.episodes[-1].append(action)
                if is_end:
                    self.episodes.append([])
                    if not self.connections:
                        del self.episodes[0:-1]
                self.cv.notify()

    def get_connection(self):
        while True:
            try:
                conn = self.listener.accept()
            except OSError:
                break
            with self.cv:
                self.connections.append({
                        'conn_obj' : conn,
                        'cur_episode_id' : 0,
                        'cur_action_id' : 0,
                        'sent' : False,
                    })
                self.cv.notify()

    def broadcast(self):
        with self.cv:
            while True:
                self.cv.wait_for(lambda: not self.is_running or any(e['cur_episode_id'] < len(self.episodes) and e['cur_action_id'] < len(self.episodes[e['cur_episode_id']]) for e in self.connections))
                if not self.is_running:
                    break

                disconnected_connections = []
                for conn_context in self.connections:
                    conn = conn_context['conn_obj']
                    if not conn_context['sent']:
                        if conn_context['cur_episode_id'] >= len(self.episodes) or conn_context['cur_action_id'] >= len(self.episodes[conn_context['cur_episode_id']]):
                            continue
                        action = self.episodes[conn_context['cur_episode_id']][conn_context['cur_action_id']]
                        try:
                            conn.send(action)
                            conn_context['sent'] = True
                        except ConnectionError:
                            disconnected_connections.append(conn_context)
                            continue
                    else:
                        try:
                            if conn.poll():
                                conn.recv()
                                conn_context['sent'] = False
                                conn_context['cur_action_id'] += 1
                                if conn_context['cur_action_id'] >= len(self.episodes[conn_context['cur_episode_id']]) and conn_context['cur_episode_id'] < len(self.episodes) - 1:
                                    conn_context['cur_episode_id'] += 1
                                    conn_context['cur_action_id'] = 0
                        except ConnectionError:
                            disconnected_connections.append(conn_context)
                            continue

                for conn_context in disconnected_connections:
                    self.connections.remove(conn_context)

                if self.connections:
                    min_episode_id = min(e['cur_episode_id'] for e in self.connections)
                    del self.episodes[0:min_episode_id]
                    for conn_context in self.connections:
                        conn_context['cur_episode_id'] -= min_episode_id
                else:
                    del self.episodes[0:-1]

    def close(self):
        with self.cv:
            self.is_running = False
            self.cv.notify()
        self.listener.close()
        self.send_action(None)

        self.broadcast_thread.join()
        self.get_connection_thread.join()
        self.buffer_action_thread.join()

@contextlib.contextmanager
def TrainingMonitorContext(is_training_monitor_on):
    if is_training_monitor_on:
        training_monitor = TrainingMonitor()
        try:
            yield training_monitor
        finally:
            training_monitor.close()
    else:
        yield None

