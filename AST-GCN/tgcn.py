# -*- coding: utf-8 -*-

#import numpy as np
import tensorflow as tf
from tensorflow.contrib.rnn import RNNCell
from utils import calculate_laplacian
import numpy as np
import pandas as pd

class tgcnCell(RNNCell):
    """Temporal Graph Convolutional Network """

    def call(self, inputs, **kwargs):
        pass

    def __init__(self, num_units, adj, num_nodes, input_size=None,
                 act=tf.nn.tanh, reuse=None):

        super(tgcnCell, self).__init__(_reuse=reuse)
        self._act = act
        self._nodes = num_nodes
        self._units = num_units
        self._adj = []
        self._adj.append(calculate_laplacian(adj))


    @property
    def state_size(self):
        return self._nodes * self._units

    @property
    def output_size(self):
        return self._units

    def __call__(self, inputs, state, scope=None):

        with tf.variable_scope(scope or "tgcn"):
            with tf.variable_scope("gates"):
                value = tf.nn.sigmoid(
                    self._gc(inputs, state, 2 * self._units, bias=1.0, scope=scope))
                r, u = tf.split(value=value, num_or_size_splits=2, axis=1)
            with tf.variable_scope("candidate"):
                r_state = r * state
                c = self._act(self._gc(inputs, r_state, self._units, scope=scope))
            new_h = u * state + (1 - u) * c
        return new_h, new_h


    def _gc(self, inputs, state, output_size, bias=0.0, scope=None):
        ## inputs:(-1,num_nodes)
        inputs = tf.expand_dims(inputs, 2)
#        print('inputs_shape:',inputs.shape)
        ## state:(batch,num_node,gru_units)
        state = tf.reshape(state, (-1, self._nodes, self._units))
#        print('state_shape:',state.shape)
        ## concat
        x_s = tf.concat([inputs, state], axis=2)
#        print('x_s_shape:',x_s.shape)
        
        
#        kgembedding = np.array(pd.read_csv(r'/DHH/sz_gcn/sz_data/sz_poi_transR_embedding20.csv',header=None))
#        kgeMatrix = np.repeat(kgembedding[np.newaxis, :, :], self._units, axis=0)
#        kgeMatrix = tf.reshape(tf.constant(kgeMatrix, dtype=tf.float32), (self._units, -1))
#        kgMatrix = tf.reshape(kgeMatrix,(-1,self._nodes, 20))
#        
#        ## inputs:(-1,num_nodes)
#        inputs = tf.expand_dims(inputs, 2)
#        ## state:(batch,num_node,gru_units)
#        state = tf.reshape(state, (-1, self._nodes, self._units))
#        ## concat
#        print('kgMatrix_shape:',kgMatrix.shape)
#        print('inputs_shape:',inputs.shape)
#        print('state_shape:',state.shape)
#        kg_x = tf.concat([inputs, kgMatrix],axis = 2)
#        print('kg_x_shape:',kg_x.shape)
#        x_s = tf.concat([kg_x, state], axis=2)
        input_size = x_s.get_shape()[2].value       # gru_units + 1
        ## (num_node,input_size,-1)
        x0 = tf.transpose(x_s, perm=[1, 2, 0])  # (num_node, gru_units + 1, batch)
        x0 = tf.reshape(x0, shape=[self._nodes, -1])    # (num_node, batch * (gru_units + 1))
        scope = tf.get_variable_scope()
        with tf.variable_scope(scope):
            for m in self._adj:
                x1 = tf.sparse_tensor_dense_matmul(m, x0)
#                print(x1)
            x = tf.reshape(x1, shape=[self._nodes, input_size,-1])  # (num_node, gru_units + 1, batch)
            x = tf.transpose(x,perm=[2,0,1])    # (batch, num_node, gru_units + 1)
            x = tf.reshape(x, shape=[-1, input_size])   # (batch * num_node, gru_units + 1)
            weights = tf.get_variable(
                'weights', [input_size, output_size], initializer=tf.contrib.layers.xavier_initializer())
            x = tf.matmul(x, weights)  # (batch_size * num_node, output_size)
            biases = tf.get_variable(
                "biases", [output_size], initializer=tf.constant_initializer(bias, dtype=tf.float32))
            x = tf.nn.bias_add(x, biases)
            x = tf.reshape(x, shape=[-1, self._nodes, output_size])
            x = tf.reshape(x, shape=[-1, self._nodes * output_size])
        return x
