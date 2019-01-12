import tensorflow as tf
import numpy as np

from video_game.players.model import Model

class DqnModel(Model):
    def create_network(self, action_dim):
        self.input_target_Q_t = tf.placeholder(dtype = tf.float32, shape = (None, action_dim))
        self.input_Q_mask_t = tf.placeholder(dtype = tf.float32, shape = (None, action_dim))

        self.create_dqn_network()

        self.Q_logit_t = tf.layers.dense(inputs = self.dqn_out_t, units = action_dim)
        self.Q_t = tf.nn.tanh(self.Q_logit_t / 100) * 100

        self.q_loss = tf.reduce_mean(tf.square(tf.reduce_sum(self.Q_t * self.input_Q_mask_t - self.input_target_Q_t, axis = 1)))
        self.l2_loss = self.get_l2_loss_factor() * tf.add_n([tf.nn.l2_loss(v) for v in tf.trainable_variables() if 'bias' not in v.name])
        self.loss = self.q_loss + self.l2_loss
        self.optimizer = tf.train.AdamOptimizer(learning_rate = self.learning_rate).minimize(self.loss)

    def create_dqn_network(self):
        pass

    def get_l2_loss_factor(self):
        pass

    def train(self, state_m_batch, target_Q_m_batch, action_m_batch, learning_rate):
        loss, q_loss, l2_loss, _ = self.sess.run([self.loss, self.q_loss, self.l2_loss, self.optimizer], feed_dict = {self.input_state_t: state_m_batch, self.input_target_Q_t: target_Q_m_batch, self.input_Q_mask_t: action_m_batch, self.learning_rate: learning_rate})
        return loss, q_loss, l2_loss

    def get_Q(self, state_m):
        return self.sess.run([self.Q_logit_t, self.Q_t], feed_dict = {self.input_state_t: state_m})

    def get_legal_Q_m(self, state_m, legal_action_mask_m):
        Q_logit_m, Q_m = self.get_Q(state_m)
        legal_Q_logit_m = np.where(legal_action_mask_m, Q_logit_m, -np.inf)
        legal_Q_m = np.where(legal_action_mask_m, Q_m, -np.inf)
        return legal_Q_logit_m, legal_Q_m

    def get_opt_action(self, state):
        state_m = state.to_state_m()
        legal_action_mask_m = state.get_legal_action_mask_m()
        _, legal_Q_m = self.get_legal_Q_m(state_m, legal_action_mask_m)
        opt_action_index = np.asscalar(legal_Q_m.argmax(axis = 1))
        action = state.action_index_to_action(opt_action_index)
        return action

    def get_max_Q_m(self, state_m, legal_action_mask_m):
        legal_Q_logit_m, legal_Q_m = self.get_legal_Q_m(state_m, legal_action_mask_m)
        max_Q_m = np.max(legal_Q_m, axis = 1).reshape(-1, 1)
        max_Q_logit_m = np.max(legal_Q_logit_m, axis = 1).reshape(-1, 1)
        return max_Q_logit_m, max_Q_m

