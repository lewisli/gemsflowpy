# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 14:37:50 2016

@author: lewisli
"""

import numpy as np
import itertools
import matplotlib.pyplot as plt
import os.path


#from gemsflowpy.core import tf_struct

class process_3dsl_results(object):
    def __init__(self,project_dir,num_reals):
        self._project_dir = project_dir
        self._num_reals = num_reals
        self._run_names = ['Run' + str(i) for i in range(0,self._num_reals)]
        

class process_well_results(process_3dsl_results):
    def __init__(self,project_dir,well_names,num_reals):
        super(process_well_results, self).__init__(project_dir,num_reals)
        self._well_names = well_names
    
    def read_results(self):
        
        for run_name,well_name in itertools.product(self._run_names,\
                                                    self._well_names):
            well_path=self._project_dir+run_name+'/'+run_name+'.'\
                +well_name+'.wel'
        
        
        
        
        pass
        
        
project_dir = '/Volumes/Scratch2/Data/SpatialForecasting/Case2/'
well_names = ['P1','P2','P3']
num_reals = 1
wells_reader = process_well_results(project_dir,well_names,num_reals)
wells_reader.read_results()        

##%% Load Data
##num_realizations = 500
##num_time_steps = 3
##grid_size = np.array([100,100,25])
#project_dir = '/media/Scratch2/Data/SpatialForecasting/SpatialForecasting/Case2/'
##
##
##num_cells = np.prod(grid_size)
##data = np.zeros([grid_size[0],grid_size[1],num_realizations])
##sat_map_dir = project_dir
##poro_map_dir = project_dir + 'include/'
##
##for real_no in range(0,num_realizations):
##    real_str = str(real_no)
##    saturation_map_path = sat_map_dir + 'Run' + real_str + '/Run' + real_str \
##        + '.sat'
##    porosity_map_path =   poro_map_dir + 'Facies_map__real' + real_str \
##        + '_PORO.inc'
##
##    
##    # Load porosity map
##    num_header_lines = 1 # Number of header lines in porosity file
##    porosity_map = np.genfromtxt(porosity_map_path,skip_header=num_header_lines,dtype=float)
##    porosity_map = porosity_map.flatten('C')
##    porosity_map = porosity_map.reshape(grid_size,order='F')
##    
##    
##    # Load saturation map
##    # Number of header lines in saturation file per time step
##    num_header_lines = 2 
##    # Number of header lines at top of saturation file
##    num_skip = 3 
##    num_to_skip = (num_cells+num_header_lines)*num_time_steps+\
##        num_skip+num_header_lines
##       
##    saturation_map = np.genfromtxt(saturation_map_path,skip_header=\
##        num_to_skip,usecols=(0),dtype=float,max_rows=num_cells)
##    saturation_map = np.reshape(saturation_map,grid_size,order='F')
##        
##    # Compute OOIP Map
##    OOIP = np.multiply(porosity_map,saturation_map)
##    data[:,:,real_no] = np.mean(OOIP,axis=2).transpose()
##    
##    print( 'Reading realization ' + str(real_no))
##
##    
### Save 
##save_dir = project_dir + 'numpy/'
##np.save(save_dir + 'avg_saturation', data)
#
##%% Construct a tensor_struct from a dataset
#data = np.load(project_dir+'/numpy/avg_saturation.npy')
#ooip_dataset = tf_struct.DataSet(data)
#
#
##%%
##%% Tensor flow shit
#import tensorflow as tf
#
## Hyper Parameters
#learning_rate = 0.1
#training_epochs = 100
#batch_size = 10
#display_step = 1
#examples_to_show = 10
#
## Network Parameters
#n_hidden_1 = 2048 # 1st layer num features
#n_hidden_2 = 1024 # 2nd layer num features
##n_hidden_3 = 256 # 3rd layer num features
#n_input = 100*100 # MNIST data input (img shape: 28*28)
#
## tf Graph input (only pictures)
#X = tf.placeholder("float", [None, n_input])
#
#weights = {
#    'encoder_h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
#    'encoder_h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
#    #'encoder_h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3])),
#    'decoder_h1': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_1])),
#    'decoder_h2': tf.Variable(tf.random_normal([n_hidden_1, n_input])),
#    #'decoder_h3': tf.Variable(tf.random_normal([n_hidden_1, n_input])),
#}
#biases = {
#    'encoder_b1': tf.Variable(tf.random_normal([n_hidden_1])),
#    'encoder_b2': tf.Variable(tf.random_normal([n_hidden_2])),
#    #'encoder_b3': tf.Variable(tf.random_normal([n_hidden_3])),
#    'decoder_b1': tf.Variable(tf.random_normal([n_hidden_1])),
#    'decoder_b2': tf.Variable(tf.random_normal([n_input])),
#    #'decoder_b3': tf.Variable(tf.random_normal([n_input])),
#}
#
#
## Building the encoder
#def encoder(x):
#    # Encoder Hidden layer with sigmoid activation #1
#    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']),
#                                   biases['encoder_b1']))
#    # Decoder Hidden layer with sigmoid activation #2
#    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']),
#                                   biases['encoder_b2']))
#                                   
#    # Decoder Hidden layer with sigmoid activation #2
##    layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['encoder_h3']),
##                                   biases['encoder_b3']))
#    return layer_2
#
#
## Building the decoder
#def decoder(x):
#    # Encoder Hidden layer with sigmoid activation #1
#    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']),
#                                   biases['decoder_b1']))
#    # Decoder Hidden layer with sigmoid activation #2
#    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']),
#                                   biases['decoder_b2']))
#                                   
#    # Decoder Hidden layer with sigmoid activation #3
##    layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['decoder_h3']),
##                                   biases['decoder_b3']))
#    return layer_2
#
## Construct model
#encoder_op = encoder(X)
#decoder_op = decoder(encoder_op)
#
## Prediction
#y_pred = decoder_op
## Targets (Labels) are the input data.
#y_true = X
#
## Define loss and optimizer, minimize the squared error
#cost = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
#optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(cost)
#
## Initializing the variables
#init = tf.initialize_all_variables()
##
###%%
#
#config = tf.ConfigProto(
#        device_count = {'GPU': 0}
#    )
#sess = tf.Session()
#
#with tf.Session(config=config) as sess:
#    sess.run(init)
#    total_batch = int(ooip_dataset.num_examples/batch_size)
#    # Training cycle
#    for epoch in range(training_epochs):
#        # Loop over all batches
#        for i in range(total_batch):
#            batch_xs, batch_ys = ooip_dataset.next_batch(batch_size)
#            
#            # Run optimization op (backprop) and cost op (to get loss value)
#            _, c = sess.run([optimizer, cost], feed_dict={X: batch_xs})
#        # Display logs per epoch step
#        if epoch % display_step == 0:
#            print("Epoch:", '%04d' % (epoch+1),
#                  "cost=", "{:.9f}".format(c))
#
#    print("Optimization Finished!")
#
#    # Applying encode and decode over test set
#    encode_decode = sess.run(
#        y_pred, feed_dict={X: ooip_dataset.images[:examples_to_show]})
#    # Compare original images with their reconstructions
#    f, a = plt.subplots(2, 10, figsize=(10, 2))
#    for i in range(examples_to_show):
#        a[0][i].imshow(np.reshape(ooip_dataset.images[i], (100, 100)))
#        a[1][i].imshow(np.reshape(encode_decode[i], (100, 100)))
#    f.show()
#    plt.draw()
#    plt.waitforbuttonpress()
#    
##%%
#encode_decode = sess.run(
#        y_pred, feed_dict={X: ooip_dataset.images[:examples_to_show]})
#    # Compare original images with their reconstructions
#f, a = plt.subplots(2, 10, figsize=(10, 2))
#for i in range(examples_to_show):
#    a[0][i].imshow(np.reshape(ooip_dataset.images[i], (100, 100)))
#    a[1][i].imshow(np.reshape(encode_decode[i], (100, 100)))
#f.show()
#plt.draw()
#plt.waitforbuttonpress()

