import os
import sys
import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
import json

usage = '%s scene_name' % sys.argv[0]
if len(sys.argv) != 2:
    print usage
    exit(1)

print sys.argv[1]

def vis_grid_occ_con(grid_occ, grid_con):
    m = grid_occ.shape[0]
    n = grid_occ.shape[1]
    for i in range(3*m):
        for j in range(n):
            ii = i / 3
            cur_id = grid_occ[ii, j]
            if cur_id >= 0:
                if i % 3 == 0:
                    out = ' '
                    if grid_con[cur_id, 3]:
                        out = '|'
                    print '  %s  ' % out,
                elif i % 3 == 1:
                    out1 = ' '
                    if grid_con[cur_id, 2]:
                        out1 = '-'
                    out2 = ' '
                    if grid_con[cur_id, 0]:
                        out2 = '-'
                    print '%s%3d%s' % (out1, cur_id, out2),
                else:
                    out = ' '
                    if grid_con[cur_id, 1]:
                        out = '|'
                    print '  %s  ' % out,
            else:
                print ' '*5,
        print
    print


input_file = os.path.join('../datasets/adobeindoornav_dataset', sys.argv[1], 'grid_occ.npy')

fin = open(input_file, 'r')
grid_id = np.load(fin)
fin.close()

input_file = os.path.join('../datasets/adobeindoornav_dataset', sys.argv[1], 'grid_connect.npy')

fin = open(input_file, 'r')
grid_connect = np.load(fin)
fin.close()

vis_grid_occ_con(grid_id, grid_connect)
