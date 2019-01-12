import tensorflow as tf

class Model:
    def __init__(self, state_shape, action_dim, model_path):
        self.model_path = model_path + '/model'

        self.graph = tf.Graph()
        with self.graph.as_default():
            self.input_state_t = tf.placeholder(dtype = tf.float32, shape = (None, ) + state_shape)

            self.learning_rate = tf.placeholder(dtype = tf.float32)

            self.create_network(action_dim)

            self.saver = tf.train.Saver()

        self.sess = tf.Session(graph = self.graph)

    def create_network(self, action_dim):
        pass

    def init_parameters(self):
        with self.graph.as_default():
            init_op = tf.global_variables_initializer()
            self.sess.run(init_op)

    def save(self):
        self.saver.save(self.sess, self.model_path)

    def load(self):
        self.saver.restore(self.sess, self.model_path)

    def get_parameters(self):
        with self.graph.as_default():
            variables_dict = {variable.name: self.sess.run(variable) for variable in tf.trainable_variables()}
        return variables_dict

    def train(self):
        pass

