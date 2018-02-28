# Author: Yuke Zhu
# Modified by: Kaichun Mo

# -*- coding: utf-8 -*-
import sys
import os
import h5py
import json
import numpy as np
import random
import skimage.io
import scipy.misc as misc
from skimage.transform import resize

# At every location, there may be multiple images generated with
# different jittered view point and guassian noise
# current observation and feature is sampled from n_feat_per_location samples
# target observation and feature is taken from sample id 0

class THORDiscreteEnvironment(object):

  def __init__(self, config=dict()):

    # configurations
    self.h5_file_path = config.get('h5_file_path')
    self.valid_locs_file_path = self.h5_file_path.replace('.h5', '.locs.json')
    self.h5_file      = h5py.File(self.h5_file_path, 'r')

    self.random_start        = config.get('random_start', True)
    self.terminal_state_id   = config.get('terminal_state_id', -1)

    print('Preloading all imgs...')
    self.imgs = self.h5_file['observation'][()]
    self.n_feat_per_location = self.imgs.shape[1]
    print('Loaded.')

    with open(self.valid_locs_file_path, 'r') as fin:
        self.valid_locs_list = json.load(fin)

    self.locations   = self.h5_file['location'][()]
    self.rotations   = self.h5_file['rotation'][()]
    self.n_locations = self.locations.shape[0]

    if self.terminal_state_id >= 0:
        self.terminals = np.zeros(self.n_locations)
        self.terminals[self.terminal_state_id] = 1
        self.terminal_states, = np.where(self.terminals)

    self.transition_graph = self.h5_file['graph'][()]

    self.generate_overhead_grids()
    self.reset()

  def update_overhead_grids_starting_position(self):
      if self.cur_x is not None:
          if self.terminal_state_id >= 0 and \
                  (self.cur_x == self.target_x and self.cur_y == self.target_y):
              self.draw_target_arrow()
          else:
              x1 = self.cur_x * self.overhead_img_grid_size + 5
              x2 = (self.cur_x + 1) * self.overhead_img_grid_size - 5
              y1 = self.cur_y * self.overhead_img_grid_size + 5
              y2 = (self.cur_y + 1) * self.overhead_img_grid_size - 5
              self.overhead_map[x1: x2, y1: y2, :] = 255

      cur_loc_x = self.locations[self.current_state_id][0]
      cur_loc_y = self.locations[self.current_state_id][1]

      self.cur_x = cur_loc_x
      self.cur_y = cur_loc_y

      cur_rot = self.rotations[self.current_state_id]

      cur_arrow_img = misc.imresize(self.blue_arrow_img, [self.overhead_img_grid_size-10, self.overhead_img_grid_size-10])
      
      cur_arrow_img= misc.imrotate(cur_arrow_img, 360 - cur_rot)

      x1 = cur_loc_x * self.overhead_img_grid_size + 5
      x2 = (cur_loc_x + 1) * self.overhead_img_grid_size - 5
      y1 = cur_loc_y * self.overhead_img_grid_size + 5
      y2 = (cur_loc_y + 1) * self.overhead_img_grid_size - 5

      self.overhead_map[x1: x2, y1: y2, :] = cur_arrow_img


  def generate_overhead_grids(self, img_size=800):
      num_loc = self.locations.shape[0]
      max_x = 0; max_y = 0;
      for i in range(num_loc):
          if self.locations[i][0] > max_x: max_x = self.locations[i][0]
          if self.locations[i][1] > max_y: max_y = self.locations[i][1]
      print('grid size: %d x %d' % (max_x, max_y))

      num_grid = max(max_x, max_y) + 1
      grid_size = img_size / num_grid
      new_img_size = grid_size * num_grid

      self.overhead_img_grid_size = grid_size

      map_img = np.zeros((new_img_size, new_img_size, 3), dtype=np.uint8)

      for i in range(num_loc):
          x = self.locations[i][0]; y = self.locations[i][1];
          x1 = grid_size * x + 5; x2 = grid_size * (x + 1) - 5;
          y1 = grid_size * y + 5; y2 = grid_size * (y + 1) - 5;
          map_img[x1: x2, y1: y2, :] = 255

      self.overhead_map = map_img

      # preload the blue arrow image
      self.blue_arrow_img = misc.imread('blue_arrow.jpg')

      # preload the red arrow image
      red_arrow_img_with_alpha = misc.imrotate(misc.imread('red_arrow.png'), 180)
      img_x = red_arrow_img_with_alpha.shape[0]
      img_y = red_arrow_img_with_alpha.shape[1]
      ratio = np.array(red_arrow_img_with_alpha[:, :, 3], dtype=np.float32) / 255.0
      ratio = np.tile(np.expand_dims(ratio, axis=-1), [1, 1, 3])
      self.red_arrow_img = (red_arrow_img_with_alpha[:, :, :3] * ratio + \
              np.ones((img_x, img_y, 3), dtype=np.uint8) * 255 * (1 - ratio)).astype(np.uint8)
      

      self.cur_x = None
      self.cur_y = None

      if self.terminal_state_id >= 0:
          self.draw_target_arrow()

  def draw_target_arrow(self):
      target_loc_x = self.locations[self.terminal_state_id][0]
      target_loc_y = self.locations[self.terminal_state_id][1]
      target_rot = self.rotations[self.terminal_state_id]

      self.target_x = target_loc_x
      self.target_y = target_loc_y

      cur_arrow_img = misc.imresize(self.red_arrow_img, [self.overhead_img_grid_size-10, self.overhead_img_grid_size-10])
      cur_arrow_img = misc.imrotate(cur_arrow_img, 360 - target_rot)
      
      x1 = target_loc_x * self.overhead_img_grid_size + 5
      x2 = (target_loc_x + 1) * self.overhead_img_grid_size - 5
      y1 = target_loc_y * self.overhead_img_grid_size + 5
      y2 = (target_loc_y + 1) * self.overhead_img_grid_size - 5

      self.overhead_map[x1: x2, y1: y2, :] = cur_arrow_img

  def get_overhead_map_img(self):
      return self.overhead_map


  # public methods

  def reset(self, random_start=True, start_loc=-1):
    if random_start:
        # randomize initial state
        while True:
            k = random.randrange(self.n_locations)
            if k in self.valid_locs_list:
                break

    else:
        assert start_loc >= 0, "start_loc < 0"
        k = start_loc

    # reset parameters
    self.current_state_id = k
    self.current_img_id = random.randrange(self.n_feat_per_location)
    self.update_overhead_grids_starting_position()

  def step(self, action):
    k = self.current_state_id
    if self.transition_graph[k][action] != -1:
      self.current_state_id = self.transition_graph[k][action]
      self.current_img_id = random.randrange(self.n_feat_per_location)

  def update(self):
    self.update_overhead_grids_starting_position()

  # private methods

  @property
  def observation(self):
    return self.imgs[self.current_state_id][self.current_img_id]

  @property
  def target_observation(self):
    return self.h5_file['observation'][self.terminal_state_id][0]

  @property
  def x(self):
    return self.locations[self.current_state_id][0]

  @property
  def z(self):
    return self.locations[self.current_state_id][1]

  @property
  def r(self):
    return self.rotations[self.current_state_id]

