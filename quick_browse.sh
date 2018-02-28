#!/bin/bash

DIR=data/panorama_images_cropped_rgb_images_preview
FN=adobeindoornav_et12_kitchen_preview.zip
URL=cs.stanford.edu/~kaichun/adobeindoornav/adobeindoornav_et12_kitchen_preview.zip

if [ ! -d $DIR ]; then
    mkdir -p $DIR
fi

if [ ! -f $DIR/$FN ]; then
    cd $DIR
    wget $URL
    unzip $FN
    cd ../..
fi

cd visu
python keyboard_agent.py et12-kitchen --h5_dir panorama_images_cropped_rgb_images_preview
cd ..
