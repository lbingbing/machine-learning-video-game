import numpy as np

def get_entropy(Ps_m):
    return np.sum(-np.log(Ps_m + 1e-20) * Ps_m) / np.log(Ps_m.shape[0])

def get_cmd_options(title):
    import argparse

    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('--training_monitor_on', action='store_true', help='turn on training monitor')
    args = parser.parse_args()
    return args

