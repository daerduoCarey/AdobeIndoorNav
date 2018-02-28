import os
from subprocess import call

list_fn = os.path.join('../splits/all_scenes_list.txt')

with open(list_fn, 'r') as fin:
    items = fin.readlines()

indir = '~/projects/indoor_nav/turtlebot_dataset/data'

for item in items:
    scene_name = item.rstrip()

    cmd = 'cp %s %s' % (os.path.join(indir, scene_name+'_targets.txt'), \
            os.path.join('landmark_targets', scene_name+'.txt'))
    print cmd
    #call(cmd, shell=True)

    cmd = 'cp %s %s' % (os.path.join(indir, scene_name+'_sift_selected_targets.txt'), \
            os.path.join('featureful_targets', scene_name+'.txt'))
    print cmd
    call(cmd, shell=True)
