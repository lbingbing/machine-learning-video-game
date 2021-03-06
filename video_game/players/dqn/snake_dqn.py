import tensorflow as tf

from .dqn import DqnModel

class SnakeDqnModel(DqnModel):
    def create_dqn_network(self):
        conv_t = tf.layers.conv2d(inputs = self.input_state_t, filters = 16, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu)
        conv_t = tf.layers.conv2d(inputs = conv_t, filters = 32, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu)
        conv_t = tf.layers.conv2d(inputs = conv_t, filters = 64, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu)
        conv_t = tf.layers.conv2d(inputs = conv_t, filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu)
        conv_t = tf.layers.conv2d(inputs = conv_t, filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu)
        flatten_t = tf.layers.flatten(inputs = conv_t)
        dense_t = tf.layers.dense(inputs = flatten_t, units = 128, activation = tf.nn.relu)
        self.dqn_out_t = tf.layers.dense(inputs = dense_t, units = 128, activation = tf.nn.relu)

    def get_l2_loss_factor(self):
        return 0.0001

