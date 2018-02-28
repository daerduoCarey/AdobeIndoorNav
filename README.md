# AdobeIndoorNav Dataset

![Dataset Overview](https://github.com/daerduoCarey/AdobeIndoorNav/blob/master/images/dataset_overview.png)

**Figure 1. The AdobeIndoorNav Dataset and other 3D scene datasets.** Our dataset supports research on robot visual navigation in real-world scenes. It provides visual inputs given a robot position: (a) the original 3D point cloud reconstruction; (b) the densely sampled locations shown on 2D scene map; (c) four examples RGB images captured by robot camera and their corresponding locations and poses. Sample views from 3D synthetic and real-world recontructed scene datasets: (d) Observation images from two synthetic datasets: [SceneNet RGB-D](https://robotvault.bitbucket.io/scenenet-rgbd.html) and [AI2-THOR](http://ai2thor.allenai.org/); (e) Rendered images from two real-world scene datasets: [Stanford 2D-3D-S](http://buildingparser.stanford.edu/) and [ScanNet](http://www.scan-net.org/).

## About the paper

Arxiv Version: https://arxiv.org/abs/1802.08824

Project Page: https://cs.stanford.edu/~kaichun/adobeindoornav/

Video: https://youtu.be/iqo1ihr_qXI

Contact: kaichun@cs.stanford.edu

## About this repository

This repository contains the AdobeIndoorNav dataset and the relevant codes for visualization. The dataset is proposed and used in the paper [The AdobeIndoorNav Dataset: Towards Deep Reinforcement Learning based Real-world Indoor Robot Visual Navigation](https://arxiv.org/abs/1802.08824) by Kaichun Mo, Haoxiang Li, Zhe Lin, Joon-Young Lee. We design a semi-automatic pipeline to collect a new dataset for robot indoor visual navigation. Our dataset includes 3D reconstruction for real-world scenes as well as densely captured real 2D images from the scenes. It provides high-quality visual inputs with real-world scene complexity to the robot at dense grid locations.


## Dependencies

All the code is tested in Python2.7. Please run the following commands to install the dependencies.

           pip install -r requirements.txt


## The Dataset

Please check the `README.md` under folder `datasets` to download the dataset. 

The first-version dataset contains 24 scenes (i.e. 15 office rooms, 5 conference rooms, 2 open spaces, 1 kitchen, 1 storage room). For each scene, we propose the raw 3D point cloud in `ply` format, the 2D obstacle map and laser-scan map, the ground-truth world graph map and a set of densely captured panoramic 360 images at each observation location.

The dataset splits are in `splits` folder. It contains the train/test split and all scene sub-category splits.

The dataset statistics are in `stats` folder. It contains the sparse landmark location ids (`stats/landmark_targets`) and the dense SIFT-featureful location ids (`stats/landmark_targets`), as introduced in the paper.


## Quick Start

You can run the following command to quickly browse in *et12-kitchen* scene.

            bash quick_browse.sh

To prepare all the 24 scenes for visualization, run the following command. This will take a while. Be patient. Please make sure you have downloaded the dataset and put it under folder `datasets/adobeindoornav_dataset`.

            bash prepare_all_scenes.sh

To prepare the scenes with random camera jitters and visual noises, please run

            bash prepare_all_scenes_with_jitters.sh


## Visualize the Scenes

You need to first crop regular images from the panoramic 360 images. To process each scene, go to `scripts` folder and run

            python crop_panorama_images.py [scene_name]

We also provide the functionality to add camera jitters and random noises to the visual inputs, check the following for more details.

            python crop_panorama_images.py --help

To run batch generation for all 24 scenes, please run

            bash run_crop_all_scenes_without_jitters.sh
            bash run_crop_all_scenes_with_jitters.sh


Then, we dump the data into HDF5 files. To process each scene, go to `scripts` folder and run

            python gen_visu_h5.py [scene_name]

This commands defaults to load the images from `data/panorama_images_cropped_rgb_images` folder and generate one image per location. To load the cropped images from different folder and to load more images per location, use the following

            python gen_visu_h5.py [scene_name] --data_dir [data_dir] --num_imgs_per_loc [num_imgs_per_loc]

To run in batch, please use

            bash run_gen_visu_h5_without_jitters.sh
            bash run_gen_visu_h5_with_jitters.sh

Finally, we are ready to use a keyboard controlled agent to visualze the scene. Go to `visu` folder and run 

            python keyboard_agent.py [scene_name]

Run the following to see more options. You can disable the overhead map, or specify a target observation (shown as red arrow in the map).

            python keyboard_agent.py --help

## Citing this work

If the dataset is useful for your research, please consider cite the following paper:

        @article{Mo18AdobeIndoorNav,
            Author = {Kaichun Mo and Haoxiang Li and Zhe Lin and Joon-Young Lee},
            Title = {The AdobeIndoorNav Dataset: Towards Deep Reinforcement Learning based Real-world Indoor Robot Visual Navigation},
            Year = {2018},
            Eprint = {arXiv:1802.08824},
        }


## License

MIT Licence

