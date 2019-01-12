HUMAN_PLAYER              = 'human'
MONITOR_PLAYER            = 'monitor'
RANDOM_PLAYER             = 'random'
DQN_PLAYER                = 'dqn'
POLICYNET_PLAYER          = 'policynet'

PLAYER_TYPES = [
                HUMAN_PLAYER,
                MONITOR_PLAYER,
                RANDOM_PLAYER,
                DQN_PLAYER,
                POLICYNET_PLAYER,
               ]

class Player:
    type = None

def is_human(player):
    return player.type == HUMAN_PLAYER

def is_monitor(player):
    return player.type == MONITOR_PLAYER

