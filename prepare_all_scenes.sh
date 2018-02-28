#!/bin/bash

if [ ! -d datasets/adobeindoornav_dataset ]; then
    echo "Please make sure you have downloaded the data and put it under datasets/adobeindoornav_dataset first!"
    exit 1
fi

if [ -d data/panorama_images_cropped_rgb_images ]; then
    echo "It seems that you have run this bash before. Please check and delete folder data/panorama_images_cropped_rgb_images"
    exit 1
fi

# crop images
cd scripts
echo "Cropping regular images from 360 images..."
bash run_crop_all_scenes_without_jitters.sh
echo "Finished."

# gen h5
echo "Generating h5 files..."
bash run_gen_visu_h5_without_jitters.sh
echo "Finished."

# visu
cd ..
echo "Data is ready! Please run "
echo "\n\t\t cd visu && python keyboard_agent.py [scene_name]"
echo "\n to visualize the scene [scene_name]"
echo "\n For example, run "
echo "\n\t\t cd visu && python keyboard_agent.py et12-kitchen"
echo "\n to visualize the et12-kitchen scene."
