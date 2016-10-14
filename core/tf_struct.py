# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 14:33:11 2016

@author: lewisli
"""

import numpy as np
import matplotlib.pyplot as plt

class DataSet(object):

  def __init__(self, images, labels=None):
    """Construct a DataSet for use with TensorFlow
    
    Args:
        images: 3D np array containing (2D) images. 
        labels: labels corresponding to images (optional)
    """
    
    self._num_dims = images.ndim - 1
    self._num_examples = images.shape[self._num_dims]
    self._num_rows = images.shape[0]
    self._num_cols = images.shape[1]

    # Check to see if labels is set
    if labels is None:
        self._supervised = False
        labels = np.zeros(self._num_examples)
    else:
        assert self._num_examples == labels.shape[0], (
          'images.shape: %s labels.shape: %s' % (images.shape,
                                                 labels.shape))
        self._supervised = True

    # Convert shape from [rows, columns, num_examples]
    # to [num examples,rows*columns,]
    images = images.reshape(self._num_rows*self._num_cols,self. _num_examples)

    # Do we need to normalize images???
    images = images.astype(np.float32).transpose()
    images = (images-images.min())/(images.max() - images.min())
    
    self._images = images
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def images(self):
    return self._images

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size):
    """Return the next `batch_size` examples from this data set."""
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Shuffle the data
      perm = np.arange(self._num_examples)
      np.random.shuffle(perm)
      self._images = self._images[perm]
      self._labels = self._labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples
      
    end = self._index_in_epoch
    return self._images[start:end], self._labels[start:end]
    
  def display_image(self,index,save_path=None):
        fig, ax = plt.subplots(facecolor='white')
        ax.imshow(self._images[index,:].reshape(self._num_rows,\
            self._num_rows),origin='lower')
        if save_path is not None:
            pass
        plt.show()
