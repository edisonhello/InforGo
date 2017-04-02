import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import random
import sys
import os.path


LOG_DIR = 'log/tensorboard'
argv = sys.argv


class Bingo(object):

    def __init__(self, board=None):

        if board is None:
            self.board = [[[0 for i in range(4)] for j in range(4)] for k in range(4)]
            self.height = [[0 for i in range(4)] for j in range(4)]
            self.player = 1

        else:
            self.board = [[[0 for i in range(4)] for j in range(4)] for k in range(4)]
            for h in range(4):
                for r in range(4):
                    for c in range(4):
                        self.board[h][r][c] = board[h][r][c][0][0]

            self.height = [[0 for i in range(4)] for j in range(4)]
            cnt = 0
            for h in range(4):
                for r in range(4):
                    for c in range(4):
                        if self.board[h][r][c] != 0:
                            self.height[r][c] = h + 1
                            cnt += 1
            if cnt % 2 == 0:
                self.player = 1
            else:
                self.player = 2
        

        # player = 1 for the player who play first and player = 2 for the opposite
        self.player = 1

        self.random_permutation = []
        self.random_permutation_ind = 0

        if os.path.isfile('_random.txt'):
            random_f = open('_random.txt', 'r')
            for k in range(4):
                for i in range(4):
                    for j in range(4):
                        r, c = map(int, random_f.readline().split())
                        self.random_permutation.append((r, c))

            random_f.close()

        else:
            for k in range(4):
                for i in range(4):
                    for j in range(4):
                        self.random_permutation.append((i, j))

            random.shuffle(self.random_permutation)


    def place(self, row, col):
        '''
        place a cube on position(height, row, col), and return whether the operation is valid
        '''

        if not self.valid_action(row, col):
            return False

        # if the position is already taken
        height = self.height[row][col]
        
        # place the cube
        self.board[height][row][col] = self.player
        self.change_player()

        self.height[row][col] += 1

        return True

    def full(self):
        '''
        Return whether the board is full
        '''
        for r in range(4):
            for c in range(4):
                if self.height[r][c] < 4:
                    return False
        return True

    def valid_action(self, row, col):
        '''
        Return whether the action is valid
        '''
        if row < 0 or row > 4 or col < 0 or col > 4:
            return False

        if self.height[row][col] >= 4:
            return False

        return True

    def play(self, row, col):
        '''
        Current Player play at (row, col)
        if Draw: return 3
        if invalid action: return -1
        if player win: return current player
        if nothing happens: return 0
        '''
        player = self.player

        if self.full():
            return 3

        if not self.place(row, col):
            return -1


        if self.win(player):
            return player
        
        if self.full():
            return 3

        return 0
        
    def change_player(self):
        '''
        switch player
        '''
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1

    def win(self, player):
        '''
        return True if player won, False otherwise by checking all possible winning combination
        '''
        for h in range(4):
            for r in range(4):
                flag = True
                for c in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True

        for h in range(4):
            for c in range(4):
                flag = True
                for r in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True

        for r in range(4):
            for c in range(4):
                flag = True
                for h in range(4):
                    if self.board[h][r][c] != player:
                        flag = False
                if flag:
                    return True
        
        for h in range(4):
            flag = True
            for i in range(4):
                if self.board[h][i][i] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[h][i][3 - i] != player:
                    flag = False
            if flag:
                return True
        
        for r in range(4):
            flag = True
            for i in range(4):
                if self.board[i][r][i] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[i][r][3 - i] != player:
                    flag = False
            if flag:
                return True

        for c in range(4):
            flag = True
            for i in range(4):
                if self.board[i][i][c] != player:
                    flag = False
            if flag:
                return True
            flag = True
            for i in range(4):
                if self.board[i][3 - i][c] != player:
                    flag = False
            if flag:
                return True
        
        flag = True
        for i in range(4):
            if self.board[i][i][i] != player:
                flag = False
        if flag:
            return True
        flag = True
        for i in range(4):
            if self.board[i][i][3 - i] != player:
                flag = False
        if flag:
            return True  
        flag = True
        for i in range(4):
            if self.board[i][3 - i][i] != player:
                flag = False
        if flag:
            return True
        flag = True
        for i in range(4):
            if self.board[3 - i][i][i] != player:
                flag = False
        if flag:
            return True

        return False

    def restart(self):
        '''
        restart the game
        '''
        self.__init__()

    def undo_action(self, row, col):
        '''
        Undo the last action at (row, col)
        '''
        self.height[row][col] -= 1
        self.board[self.height[row][col]][row][col] = 0
        
    def get_state(self):
        state = np.zeros([4, 4, 4, 1, 1])
        for h in range(4):
            for r in range(4):
                for c in range(4):
                    state[h][r][c][0][0] = self.board[h][r][c]
        return state


class MDP(object):
    '''
    Markov Decision Process
    which can be represented as M(S, D, A, P, gamma, R)
    '''
    def __init__(self, reward_function):
        # R(s, a) is the reward obtaining by taking action a at state s
        self.R = reward_function
        self.bingo = Bingo()

    def get_initial_state(self):
        '''
        Refresh the game and return the Initial state s0 based on D
        '''
        self.bingo.restart()
        return np.zeros(shape=[4, 4, 4, 1, 1])

    def get_state(self):
        '''
        Return current state, which is a 4x4x4 bingo board, and compress it to a 1D array for the sake of simplicity
        '''
        return self.bingo.get_state()

    def get_reward(self, s, flag, player):
        '''
        Return the reward of taking action a at state s
        '''
        return self.R(s, flag, player)

    def take_action(self, action, player):
        '''
        Take action and Return whether the action is valid, whether the player win or not, new state and the reward
        '''
        row, col = action
        flag = self.bingo.play(row, col)

        new_state = self.get_state()
        reward = self.get_reward(new_state, flag, player)

        return flag, new_state, reward

    def valid_action(self, action):
        row, col = action
        return self.bingo.valid_action(row, col)

    def undo_action(self, action):
        row, col = action
        self.bingo.undo_action(row, col)



class InforGo(object):
    '''
    A Neural Network model for training 3D-bingo AI
    input-layer: 4 x 4 x 4 board
    convolution-layer: stride = 1 x 1 x 1
    hidden-layer: relu function
    output-layer: value for the input state
    '''
    def __init__(self, reward_function, n_epoch=100, n_hidden_layer=1, n_node_hidden=[32], activation_function='Relu', output_function=None, learning_rate=0.00001, gamma=0.99, regularization_param=0.001, decay_step=10000, decay_rate=0.96, filter_depth=1, filter_height=1, filter_width=1, out_channel=5, search_depth=3):

        # number of epoches
        self.n_epoch = n_epoch

        # Learning rate decay
        self.global_step = tf.Variable(0, trainable=False)
        self.learning_rate = tf.train.exponential_decay(learning_rate, self.global_step, decay_step, decay_rate, staircase=True)

        # Discount factor between 0 to 1
        self.gamma = gamma

        # R(s) is the reward obtain by achieving state s
        self.reward_function = reward_function

        # Number of nodes in hidden layer
        self.n_hidden_layer = n_hidden_layer
        self.n_node_hidden = n_node_hidden
        
        self.search_depth = search_depth

        if activation_function == 'Relu':
            self.activation_function = lambda k: tf.nn.relu(k, name='Relu')
        elif activation_function == 'Sigmoid':
            self.activation_function = lambda k: tf.sigmoid(k, name='Sigmoid')
        elif activation_function == 'Tanh':
            self.activation_function = lambda k: tf.tanh(k, name='Tanh')


        if output_function is None:
            self.output_function = lambda k: k
        elif output_function == 'Softmax':
            self.output_function = lambda k: tf.nn.softmax(k)

        # L2 regularization paramater
        self.regularization_param = regularization_param
        
        self.MDP = MDP(reward_function)

        # Neural Network Setup

        # input layer: 4 x 4 x 4 Tensor representing the state
        with tf.name_scope('Input-Layer'):
            self.inp = tf.placeholder(shape=[4, 4, 4, 1, 1], dtype=tf.float64, name='input')

        # 3D-Convolution layer
        with tf.name_scope('Convolution-Layer'):
            self.conv_layer_w = tf.cast(tf.Variable(tf.random_uniform(shape=[filter_depth, filter_height, filter_width, 1, out_channel])), tf.float64, name='weight')
            self.conv_layer = tf.nn.conv3d(input=self.inp, filter=self.conv_layer_w, strides=[1, 1, 1, 1, 1], padding='SAME', name='Conv-Layer')

            # Flatten the convolution layer
            self.conv_layer_output = tf.reshape(self.conv_layer, [1, -1], name='Flattend')
            self.conv_layer_length = 4 * 4 * 4 * out_channel

        
        self.weight_and_bias = [{} for i in range(self.n_hidden_layer + 1)]
        
        with tf.name_scope('Weight_and_Bias'):
            self.weight_and_bias[0] = {
                'Weight': self.get_weight(self.conv_layer_length, self.n_node_hidden[0], 0),
                'Bias': self.get_bias(self.n_node_hidden[0], 0)
            }
            for i in range(1, self.n_hidden_layer):
                self.weight_and_bias[i] = {
                    'Weight': self.get_weight(self.n_node_hidden[i - 1], self.n_node_hidden[i], i),
                    'Bias': self.get_bias(self.n_node_hidden[i], i)
                }
            self.weight_and_bias[self.n_hidden_layer] = {
                'Weight': self.get_weight(self.n_node_hidden[self.n_hidden_layer - 1], 1, self.n_hidden_layer),
                'Bias': self.get_bias(1, self.n_hidden_layer)
            }

        self.hidden_layer = [{} for i in range(self.n_hidden_layer)]

        with tf.name_scope('Hidden_Layer'):
            self.hidden_layer[0] = {
                'Output': tf.add(tf.matmul(self.conv_layer_output, self.weight_and_bias[0]['Weight']), self.weight_and_bias[0]['Bias'])
            }
            for i in range(1, self.n_hidden_layer):
                self.hidden_layer[i - 1]['Activated_Output'] = self.activation_function(self.hidden_layer[i - 1]['Output'])
                self.hidden_layer[i] = {
                    'Output': tf.add(tf.matmul(self.hidden_layer[i - 1]['Activated_Output'], self.weight_and_bias[i]['Weight']), self.weight_and_bias[i]['Bias'])
                }
            self.hidden_layer[self.n_hidden_layer - 1]['Activated_Output'] = self.hidden_layer[self.n_hidden_layer - 1]['Output']

        with tf.name_scope('Output_Layer'):
            self.output = tf.add(tf.matmul(self.hidden_layer[self.n_hidden_layer - 1]['Activated_Output'], self.weight_and_bias[self.n_hidden_layer]['Weight'], ), self.weight_and_bias[self.n_hidden_layer]['Bias'])
            self.V = self.output_function(self.output)

        with tf.name_scope('Training_Model'):
            # Q-value to update the weight
            self.V_desired = tf.placeholder(shape=[1, 1], dtype=tf.float64)

            # Cost function
            def L2_Regularization():
                self.L2_value = 0
                for i in range(0, self.n_hidden_layer + 1):
                    self.L2_value += tf.nn.l2_loss(self.weight_and_bias[i]['Weight']) + tf.nn.l2_loss(self.weight_and_bias[i]['Bias'])
                return self.L2_value

            self.loss = tf.add(tf.reduce_sum(tf.square(self.V_desired - self.V)), self.regularization_param / self.n_epoch * L2_Regularization())
        
            # use gradient descent to optimize our model
            self.trainer = tf.train.GradientDescentOptimizer(self.learning_rate)
            self.model = self.trainer.minimize(self.loss, global_step=self.global_step)

        init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(init)
    
    def get_weight(self, n, m, layer):
        '''
        Weight to the layer-th hidden layer, with size n x m
        '''
        if os.path.exists('Weight/{}.txt'.format(layer)):
            f = open('Weight/{}.txt'.format(layer), 'r')
            w = np.zeros([n, m])
            for i in range(n):
                for j in range(m):
                    w[i, j] = float(f.readline())
            f.close()
            return tf.Variable(tf.cast(w, tf.float64))
        else:
            return tf.Variable(tf.truncated_normal(shape=[n, m], mean=0.0, stddev=1.0, dtype=tf.float64))

    def get_bias(self, n, layer):
        '''
        Bias to the layer-th hidden layer, with size 1 x n
        '''
        if os.path.exists('Bias/{}.txt'.format(layer)):
            f = open('Bias/{}.txt'.format(layer), 'r')
            b = np.zeros([1, n])
            for i in range(n):
                b[0, i] = float(f.readline())
            f.close()
            return tf.Variable(tf.cast(b, tf.float64))
        else:
            return tf.Variable(tf.truncated_normal(shape=[1, n], mean=0.0, stddev=1.0, dtype=tf.float64))

    def decode_action(self, action_num):
        action = [0, 0]
        for i in range(2):
            action[i] = action_num % 4
            action_num //= 4
        return action

    def train(self):
        '''
        Main Learning Process
        return final score, graph_x, graph_y
        '''

        percentage = 0
        record = self.get_record()

        for epoch in range(self.n_epoch):

            if percentage < (epoch) / self.n_epoch * 100.:
                print("Training Complete: {}%".format(percentage))
                percentage += 1

            for directory in record.keys():
                for file_name in record[directory]:
                    f = open('{}/{}'.format(directory, file_name), 'r')
                    s = self.MDP.get_initial_state()

                    while True:
                        height, row, col = map(int, f.readline().split())

                        if (height, row, col) == (-1, -1, -1):
                            break

                        v = self.sess.run(self.V, feed_dict={self.inp: s})
                        flag, new_s, R = self.MDP.take_action((row, col), 1)

                        new_v = self.sess.run(self.V, feed_dict={self.inp: new_s})
                        v_desired = np.zeros([1, 1])
                        v_desired[0][0] = v[0][0] + self.sess.run(self.learning_rate) * (R + self.gamma * new_v[0][0] - v[0][0]) 
                        self.sess.run(self.model, feed_dict={self.V_desired: v_desired, self.inp: s})

                        s = new_s

                        height, row, col = map(int, f.readline().split())
                        if (height, row, col) == (-1, -1, -1):
                            break

                        v = self.sess.run(self.V, feed_dict={self.inp: s})
                        flag, new_s, R = self.MDP.take_action((row, col), 2)

                        new_v = self.sess.run(self.V, feed_dict={self.inp: new_s})

                        # TODO: self.learning_rate is decaying, might have bug
                        v_desired[0][0] = v[0][0] + self.sess.run(self.learning_rate) * (R + self.gamma * new_v[0][0] - v[0][0]) 
                        self.sess.run(self.model, feed_dict={self.V_desired: v_desired, self.inp: s})

                        s = new_s

        self.store_weight_and_bias()

    def get_record(self):
        directory = [x[0] for x in os.walk('./saves')]
        directory = directory[1:]
        filename = {}
        for d in directory:
            tmp = [x[2] for x in os.walk(d)]
            filename[d] = [x for x in tmp[0]]
        return filename

    def store_weight_and_bias(self):
        for i in range(self.n_hidden_layer + 1):
            f = open('Weight/{}.txt'.format(i), 'w')
            w = self.sess.run(self.weight_and_bias[i]['Weight'])
            for j in range(self.sess.run(tf.shape(self.weight_and_bias[i]['Weight']))[0]):
                for k in range(self.sess.run(tf.shape(self.weight_and_bias[i]['Weight']))[1]):
                    f.write('{}\n'.format(w[j, k]))
            f.close()

            f = open('Bias/{}.txt'.format(i), 'w')
            b = self.sess.run(self.weight_and_bias[i]['Bias'])
            for j in range(self.sess.run(tf.shape(self.weight_and_bias[i]['Bias']))[1]):
                f.write('{}\n'.format(b[0, j]))
            f.close()


    def store_random_permutation(self):
        random_f = open("_random.txt", "w")
        for i in self.MDP.bingo.random_permutation:
            r, c = i
            random_f.write(str(r) + ' ' + str(c))
            random_f.write('\n')
        random_f.close()


    def play(self):
        
        s = self.MDP.get_initial_state()

        print("[DEBUG] game started")

        while True:
            _, action = self.Minimax(Bingo(s), self.search_depth, 'Max')
            # TODO: send action to the web server
            row, col = self.decode_action(action)
            self.emit_action(row, col)
            action = (row, col)
            flag, s, _ = self.MDP.take_action(action, 1)
            if flag == 1:
                print("[DEBUG] AI win")
                break
            opponent = self.read_opponent_action()
            flag, s, _ = self.MDP.take_action(opponent, 2)
            if flag == 2:
                print("[DEBUG] user win")
                break

    def Minimax(self, bingo, depth, level):

        state = bingo.get_state()

        # TODO: alpha-beta pruning
        if depth == 0:
            return self.evaluate(state), None
        
        value, action = 0, 0
        current_player = 0
        next_level = 'Osas'
        func = lambda a, b: 0

        if level == 'Max':
            value = 0
            current_player = 1
            next_level = 'Min'
            func = lambda a, b: max(a, b)

        else:
            value = 7122
            current_player = 2
            next_level = 'Max'
            func = lambda a, b: min(a, b)

        for i in range(16):
            if self.MDP.valid_action(self.decode_action(i)):

                r, c = self.decode_action(i)
                bingo.place(r, c)
                new_bingo = Bingo(bingo.get_state())
                bingo.undo_action(r, c)

                val, a = self.Minimax(new_bingo, depth - 1, next_level)
                value = func(value, val)
                if value == val:
                    action = i

        return value, action

    def evaluate(self, state):
        V = self.sess.run(self.V, feed_dict={self.inp: state})
        return V[0][0]
    
    def read_opponent_action(self):
        # TODO: read opponent's action from web server
        r, c = map(int, input().split())
        return r, c

    def generate_move(self):
        '''
        1. if player2 can win
        2. if player1 is going to win
        3. random
        '''
        # TODO: for testing pruposes
        
        
    def emit_action(self, row, col):
        # TODO: emit action to web server
        print("{}, {}".format(row, col))

if __name__ == '__main__':

    def main():
        # TODO: more arguments are required, deal with uncertain length of n_node_hidden
        
        cmd = argv[1]
        
        # TODO: redesign a reward function
        def reward_function(state, flag, player):
            if flag == 3 or flag == 0:
                return 0
            if flag == player:
                return 1
            if flag != player:
                return -1
            return 0

        argv_len = len(argv)
        ind = 2
        parameter = {'reward_function': reward_function}

        float_parameter = ['learning_rate', 'decay_rate', 'regularization_param', 'gamma']
        string_parameter = ['activation_function', 'output_function']

        while ind < argv_len:
            if argv[ind] == 'n_node_hidden':
                parameter['n_node_hidden'] = []
                for i in range(parameter['n_hidden_layer']):
                    parameter['n_node_hidden'].append(int(argv[ind + i + 1]))
                ind += parameter['n_hidden_layer'] + 1
            elif argv[ind] in float_parameter:
                parameter[argv[ind]] = float(argv[ind + 1])
                ind += 2
            elif argv[ind] in string_parameter:
                parameter[argv[ind]] = argv[ind + 1]
                ind += 2
            else:
                parameter[argv[ind]] = int(argv[ind + 1])
                ind += 2


        AI = InforGo(**parameter)
        if cmd == 'train':
            AI.train()
        if cmd == 'play':
            AI.play()

    main()
