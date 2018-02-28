import os
import sys
import argparse
import progressbar
import h5py
import numpy as np
import scipy.misc as misc
import json

data_folder = '../datasets/adobeindoornav_dataset'

parser = argparse.ArgumentParser()
parser.add_argument('scene_name', type=str, help='Input Scene Name')
parser.add_argument('--data_dir', type=str, default='panorama_images_cropped_rgb_images', help='input data folder [default: panorama_images_cropped_rgb_images]')
parser.add_argument('--num_imgs_per_loc', type=int, default=1, help='number of images per location [default: 1]')
args = parser.parse_args()

img_channel_num = 3

# load scene info
occ_input_file = os.path.join(data_folder, args.scene_name, 'grid_occ.npy')
connect_input_file = os.path.join(data_folder, args.scene_name, 'grid_connect.npy')

fin = open(occ_input_file, 'r')
grid_id = np.load(fin)
fin.close()

fin = open(connect_input_file, 'r')
grid_connect = np.load(fin)
fin.close()

num_loc = np.max(grid_id) + 1
print 'Total locations: ', num_loc

assert(num_loc == grid_connect.shape[0])
assert(grid_connect.shape[1] == 4)

output_dir = os.path.join('../data', args.data_dir)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

output_h5_file = os.path.join(output_dir, args.scene_name + '.h5')
output_valid_locs_file = os.path.join(output_dir, args.scene_name + '.locs.json')

# open h5 file
h5_fout = h5py.File(output_h5_file)

# load all images
img = misc.imread(os.path.join(data_folder, args.scene_name, args.data_dir, '0_0_0.png'))
print img.dtype

img_size_x = img.shape[0]
img_size_y = img.shape[1]

print 'Loading the images'
observation = np.zeros((num_loc*4, args.num_imgs_per_loc, img_size_x, img_size_y, 3), dtype=np.uint8)

missing_locs_list = []
valid_locs_list = []

bar = progressbar.ProgressBar()
for i in bar(range(num_loc)):
    target_filename = os.path.join(data_folder, args.scene_name, args.data_dir, str(i) + '_0_0.png')

    if not os.path.exists(target_filename):
        missing_locs_list.append(i)
        continue

    valid_locs_list.append(i)

    for j in range(args.num_imgs_per_loc):
        img0 = misc.imread(os.path.join(data_folder, args.scene_name, args.data_dir, str(i) + '_0_'+str(j)+'.png'))
        img1 = misc.imread(os.path.join(data_folder, args.scene_name, args.data_dir, str(i) + '_90_'+str(j)+'.png'))
        img2 = misc.imread(os.path.join(data_folder, args.scene_name, args.data_dir, str(i) + '_180_'+str(j)+'.png'))
        img3 = misc.imread(os.path.join(data_folder, args.scene_name, args.data_dir, str(i) + '_270_'+str(j)+'.png'))

        observation[i*4, j] = img0
        observation[i*4+1, j] = img1
        observation[i*4+2, j] = img2
        observation[i*4+3, j] = img3

with open(output_valid_locs_file, 'w') as fout:
    json.dump(valid_locs_list, fout)

# generate the graph
location = np.zeros((num_loc*4, 2), dtype=np.int32)
rotation = np.zeros((num_loc*4), dtype=np.int32)

print 'Generating location, graph and rotation arrays'
graph = np.ones((num_loc*4, 4), dtype=np.int32) * -1
for i in range(grid_id.shape[0]):
    for j in range(grid_id.shape[1]):
        if grid_id[i, j] >= 0 and grid_id[i, j] not in missing_locs_list:
            cur_id = grid_id[i, j]

            location[4*cur_id: 4*cur_id+4, 0] = i
            location[4*cur_id: 4*cur_id+4, 1] = j

            rotation[4*cur_id] = 0
            rotation[4*cur_id+1] = 90
            rotation[4*cur_id+2] = 180
            rotation[4*cur_id+3] = 270

            if grid_connect[cur_id, 0] and grid_id[i, j+1] not in missing_locs_list:
                graph[4*cur_id, 0] = 4*grid_id[i, j+1]
            graph[4*cur_id, 1] = 4*cur_id+1
            if grid_connect[cur_id, 2]  and grid_id[i, j-1] not in missing_locs_list:
                graph[4*cur_id, 3] = 4*grid_id[i, j-1]
            graph[4*cur_id, 2] = 4*cur_id+3

            if grid_connect[cur_id, 1] and grid_id[i+1, j] not in missing_locs_list: 
                graph[4*cur_id+1, 0] = 4*grid_id[i+1, j]+1
            graph[4*cur_id+1, 1] = 4*cur_id+2
            if grid_connect[cur_id, 3] and grid_id[i-1, j] not in missing_locs_list: 
                graph[4*cur_id+1, 3] = 4*grid_id[i-1, j]+1
            graph[4*cur_id+1, 2] = 4*cur_id

            if grid_connect[cur_id, 0] and grid_id[i, j+1] not in missing_locs_list: 
                graph[4*cur_id+2, 3] = 4*grid_id[i, j+1]+2
            graph[4*cur_id+2, 1] = 4*cur_id+3
            if grid_connect[cur_id, 2] and grid_id[i, j-1] not in missing_locs_list: 
                graph[4*cur_id+2, 0] = 4*grid_id[i, j-1]+2
            graph[4*cur_id+2, 2] = 4*cur_id+1

            if grid_connect[cur_id, 1] and grid_id[i+1, j] not in missing_locs_list: 
                graph[4*cur_id+3, 3] = 4*grid_id[i+1, j]+3
            graph[4*cur_id+3, 1] = 4*cur_id
            if grid_connect[cur_id, 3] and grid_id[i-1, j] not in missing_locs_list: 
                graph[4*cur_id+3, 0] = 4*grid_id[i-1, j]+3
            graph[4*cur_id+3, 2] = 4*cur_id+2

# dump data to hdf5 file
print 'Saving to hdf5 file'
h5_fout.create_dataset('observation', data=observation, compression='gzip', compression_opts=4, dtype=np.uint8)
h5_fout.create_dataset('location', data=location, compression='gzip', compression_opts=1, dtype=np.int32)
h5_fout.create_dataset('rotation', data=rotation, compression='gzip', compression_opts=1, dtype=np.int32)
h5_fout.create_dataset('graph', data=graph, compression='gzip', compression_opts=1, dtype=np.int32)

h5_fout.close()
print 'Hdf5 dumped and closed! Good bye!'
