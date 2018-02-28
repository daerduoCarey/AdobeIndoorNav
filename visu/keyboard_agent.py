# Author: Yuke Zhu
# Modified by: Kaichun Mo

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import time
import sys
import signal
import argparse
import numpy as np
import scipy.misc as misc

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("scene_name", type=str, help="scene_name")
parser.add_argument("--h5_dir", type=str, default='panorama_images_cropped_rgb_images', help="data_dir [default: panorama_images_cropped_rgb_images]")
parser.add_argument('--with_overhead_map', action='store_false', help='with overhead map [default: True]')
parser.add_argument('--with_target', type=int, default=None, help='with target [default: None]')
args = parser.parse_args()

from env_visu import THORDiscreteEnvironment
from simple_viewer import SimpleImageViewer

#
# Navigate the scene using your keyboard
#

def key_press(key, mod):

  global human_agent_action, human_wants_restart, stop_requested, snapshot_requested
  if key == ord('R') or key == ord('r'): # r/R
    human_wants_restart = True
  if key == ord('Q') or key == ord('q'): # q/Q
    stop_requested = True
  if key == ord('S') or key == ord('s'):
      snapshot_requested = True
  if key == 0xFF52: # up
    human_agent_action = 0
  if key == 0xFF53: # right
    human_agent_action = 1
  if key == 0xFF51: # left
    human_agent_action = 2
  if key == 0xFF54: # down
    human_agent_action = 3

def stitch_images(img_list):
    img_x, img_y, _ = img_list[0].shape
    imgs = [img_list[0]]
    for i in range(1, len(img_list)):
        imgs.append(misc.imresize(img_list[i], [img_x, img_y]))
    return np.concatenate(imgs, axis=1)

def rollout(env):

  global human_agent_action, human_wants_restart, stop_requested, snapshot_requested
  human_agent_action = None
  human_wants_restart = False
  while True:
    if snapshot_requested:
        snapshot_requested = False
        fn = str(time.time())+'.png'
        misc.imsave(fn, env.observation)
        print('Snapshot saved to: %s' % fn)

    # waiting for keyboard input
    if human_agent_action is not None:
      # move actions
      env.step(human_agent_action)
      env.update()
      human_agent_action = None

    # waiting for reset command
    if human_wants_restart:
      # reset agent to random location
      env.reset()
      human_wants_restart = False

    # check quit command
    if stop_requested: break

    # print(env.current_state_id/4)
    img_to_show = [img_convert(env.observation)]

    if args.with_target is not None:
        img_to_show.append(img_convert(env.target_observation))

    if args.with_overhead_map:
        img_to_show.append(env.get_overhead_map_img())

    final_img = stitch_images(img_to_show)
    viewer.imshow(final_img)

def img_convert(input_img):
    if len(input_img.shape) == 3:
        return input_img

    if len(input_img.shape) == 2:
        return np.tile(np.expand_dims(input_img, axis=-1), (1, 1, 3))


if __name__ == '__main__':

  scene_dump = os.path.join('../data', args.h5_dir, args.scene_name+'.h5')

  print("Loading scene dump {}".format(scene_dump))

  if args.with_target is not None:
      env = THORDiscreteEnvironment({
        'h5_file_path': scene_dump,
        'preload_imgs': True,
        'terminal_state_id': args.with_target,
      })
  else:
      env = THORDiscreteEnvironment({
        'h5_file_path': scene_dump,
        'preload_imgs': True,
        })

  human_agent_action = None
  human_wants_restart = False
  stop_requested = False
  snapshot_requested = False

  viewer = SimpleImageViewer()
  img_to_show = [img_convert(env.observation)]
  
  if args.with_target is not None:
      img_to_show.append(img_convert(env.target_observation))

  if args.with_overhead_map:
      img_to_show.append(env.get_overhead_map_img())

  final_img = stitch_images(img_to_show)

  print(final_img.shape)

  viewer.imshow(final_img)
  viewer.window.on_key_press = key_press

  print("Use arrow keys to move the agent.")
  print("Press R to reset agent\'s location.")
  print("Press S to save the snapshot of the current observation.")
  print("Press Q to quit.")

  rollout(env)

  print("Goodbye.")
