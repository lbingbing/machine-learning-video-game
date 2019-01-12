import random
import itertools
import numpy as np
import os
import copy

from video_game.players.utils import replay_memory
from video_game.players.utils.utils import get_cmd_options
from video_game.players.utils.training_monitor import TrainingMonitorContext

#np.set_printoptions(threshold = np.nan)

def sample(model, rmemory, state, search_rate, get_reward, training_monitor):
    while True:
        state_m = state.to_state_m()
        if random.random() < search_rate:
            legal_actions = state.get_legal_actions()
            action = random.choice(legal_actions)
        else:
            action = model.get_opt_action(state)
        state.do_action(action)
        state.update()
        action_index = state.action_to_action_index(action)
        n_state_m = state.to_state_m()
        n_state_legal_action_mask_m = state.get_legal_action_mask_m()
        r = get_reward(state)
        is_end = state.is_end()

        if training_monitor != None:
            training_monitor.send_action(((action, copy.deepcopy(state)), is_end))

        rmemory.save((state_m, action_index, r, n_state_m, n_state_legal_action_mask_m, is_end))

        if is_end:
            break

def train(model, rmemory, action_dim, discount, batch_size, learning_rate, epoch_num):
    losses = []
    for epoch_id in range(epoch_num):
        transitions = [rmemory.sample() for i in range(batch_size)]
        state_m_l, action_index_l, r_l, n_state_m_l, n_state_legal_action_mask_m_l, is_end_l = zip(*transitions)
        state_m_batch = np.concatenate(state_m_l, axis = 0)
        n_state_m_batch = np.concatenate(n_state_m_l, axis = 0)
        n_state_legal_action_mask_m_batch = np.concatenate(n_state_legal_action_mask_m_l, axis = 0)
        Q_mask_batch = np.zeros((batch_size, action_dim))
        for sample_id, action_index in enumerate(action_index_l):
            Q_mask_batch[sample_id, action_index] = 1
        _, max_n_Q_m_batch = model.get_max_Q_m(n_state_m_batch, n_state_legal_action_mask_m_batch)
        is_end_m_batch = np.array(is_end_l).reshape(-1, 1)
        target_Q_m_batch = np.array(r_l).reshape(-1, 1).astype(dtype = np.float32)
        target_Q_m_batch += np.where(is_end_m_batch, 0, max_n_Q_m_batch) * discount
        target_Q_m_batch = target_Q_m_batch * Q_mask_batch
        loss, q_loss, l2_loss = model.train(state_m_batch, target_Q_m_batch, Q_mask_batch, learning_rate)
        losses.append((loss, q_loss, l2_loss))
    return (sum(e) / len(losses) for e in zip(*losses))

def main(game_type, get_config):
    title = 'train {0} dqn model'.format(game_type)

    args = get_cmd_options(title)

    print(title)
    state, model, config, get_reward = get_config()

    config['replay_memory_file_path'] = os.path.join(os.path.dirname(__file__), '{0}_dqn_replay_memory.pickle'.format(game_type))

    for k, v in config.items():
        print('{0}: {1}'.format(k, v))

    model_path = config['model_path']
    replay_memory_file_path = config['replay_memory_file_path']
    replay_memory_size = config['replay_memory_size']
    search_rate = config['search_rate']
    discount = config['discount']
    batch_size = config['batch_size']
    epoch_num = config['epoch_num']
    learning_rate = config['learning_rate']
    episode_num = config['episode_num']

    save_flag_file_path = os.path.join(os.path.dirname(__file__), '{0}_dqn_train.save'.format(game_type))
    saved_flag_file_path = os.path.join(os.path.dirname(__file__), '{0}_dqn_train.saved'.format(game_type))
    stop_flag_file_path = os.path.join(os.path.dirname(__file__), '{0}_dqn_train.stop'.format(game_type))
    stopped_flag_file_path = os.path.join(os.path.dirname(__file__), '{0}_dqn_train.stopped'.format(game_type))

    if os.path.isdir(model_path):
        model.load()
        print('model loaded')
    else:
        model.init_parameters()
        print('model initialized')
    if os.path.isfile(replay_memory_file_path):
        rmemory = replay_memory.load_from_file(replay_memory_file_path)
        print('replay memory loaded')
    else:
        rmemory = replay_memory.ReplayMemory(max_size = replay_memory_size)
        print('replay memory initialized')

    with TrainingMonitorContext(args.training_monitor_on) as training_monitor:
        for episode_id in range(1, episode_num+1):
            state.reset()
            sample(model, rmemory, state, search_rate, get_reward, training_monitor)
            loss, q_loss, l2_loss = train(model, rmemory, state.get_action_dim(), discount, batch_size, learning_rate, epoch_num)
            if episode_id % 1 == 0:
                score = state.get_score()
                age = state.get_age()
                state.reset()
                max_Q_logit, max_Q = map(np.asscalar, model.get_max_Q_m(state.to_state_m(), state.get_legal_action_mask_m()))
                print('episode: {0} L: {1:.4f} ({2:.4f}/{3:.4f}) m_Q_l: {4:.2f} m_Q: {5:.6f} score: {6} age: {7}'.format(episode_id, loss, q_loss, l2_loss, max_Q_logit, max_Q, score, age))
            if os.path.isfile(save_flag_file_path):
                model.save()
                print('model saved')
                replay_memory.save_to_file(rmemory, replay_memory_file_path)
                print('replay memory saved')
                os.rename(save_flag_file_path, saved_flag_file_path)
            if os.path.isfile(stop_flag_file_path):
                print('stopped')
                os.rename(stop_flag_file_path, stopped_flag_file_path)
                break

