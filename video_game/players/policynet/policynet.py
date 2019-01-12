import tensorflow as tf
import numpy as np

from board_game.players.model import Model

class PolicyNetModel(Model):
    def create_network(self, action_dim):
        self.input_target_P_t = tf.placeholder(dtype = tf.float32, shape = (None, action_dim))
        self.input_advantage_t = tf.placeholder(dtype = tf.float32, shape = (None, 1))

        self.create_policynet_network()

        self.P_logits_t = tf.layers.dense(inputs = self.policynet_out_t, units = action_dim)
        self.P_t = tf.nn.softmax(logits = self.P_logits_t)

        self.loss = tf.reduce_mean(-tf.log(tf.reduce_sum(self.P_t * self.input_target_P_t, axis = 1)) * self.input_advantage_t)
        self.optimizer = tf.train.AdamOptimizer(learning_rate = self.learning_rate).minimize(self.loss)

    def create_policynet_network(self):
        pass

    def train(self, state_m_time_batch, action_m_time_batch, advantage_m_time_batch, learning_rate):
        self.sess.run(self.optimizer, feed_dict = {self.input_state_t: state_m_time_batch, self.input_target_P_t: action_m_time_batch, self.input_advantage_t: advantage_m_time_batch, self.learning_rate: learning_rate})

    def get_P(self, state_m):
        return self.sess.run([self.P_logits_t, self.P_t], feed_dict = {self.input_state_t: state_m})

    def get_action(self, state, player_id):
        state_m = state.to_state_m()
        _, action_m = self.get_P(state_m)
        action_m = action_m.reshape(-1)
        legal_action_m = np.zeros(state.get_action_dim())
        legal_action_indexes = [state.action_to_action_index(legal_action) for legal_action in state.get_legal_actions(player_id)]
        legal_action_m[legal_action_indexes] = action_m[legal_action_indexes]
        legal_action_m /= np.sum(legal_action_m)
        action_index = np.random.choice(state.get_action_dim(), p = legal_action_m)
        action = state.action_index_to_action(action_index)
        return action

