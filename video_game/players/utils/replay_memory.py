import random
import pickle

class ReplayMemory:
    def __init__(self, max_size):
        self.max_size = max_size
        self.mem = []
        self.wr_ptr = 0

    def save(self, data):
            if len(self.mem) == self.max_size:
                self.mem[self.wr_ptr] = data
                self.wr_ptr = (self.wr_ptr+1) % self.max_size
            else:
                self.mem.append(data)

    def sample(self):
        return random.choice(self.mem)

def save_to_file(replay_memory, path):
    with open(path, 'wb') as f:
        pickle.dump(replay_memory, f)

def load_from_file(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

