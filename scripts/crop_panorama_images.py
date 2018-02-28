import numpy as np
from PanoramaImageViewer.panorama_image_cropper import crop_panorama_image
import os
import sys
import argparse
import scipy.misc as misc
import math

parser = argparse.ArgumentParser()
parser.add_argument("scene_name", type=str, help="scene name")
parser.add_argument('--front_theta', type=float, default=180.0, help='front_theta [default: 180.0]')
parser.add_argument('--res_x', type=int, default=512, help='res_x [default: 512]')
parser.add_argument('--res_y', type=int, default=512, help='res_y [default: 512]')
parser.add_argument('--fov', type=float, default=60.0, help='fov [default: 60.0]')
parser.add_argument('--theta_jitter', type=float, default=0.0, help='theta_jitter [default: 0.0]')
parser.add_argument('--phi_jitter', type=float, default=0.0, help='phi_jitter [default: 0.0]')
parser.add_argument('--gaussian_noise_sigma', type=float, default=0.0, help='phi_jitter [default: 0.0 out of 255]')
parser.add_argument('--number_jitter', type=int, default=1, help='number of images/jitters for every location [default: 1]')
parser.add_argument('--output_suffix', type=str, default='cropped_rgb_images', help='output directory suffix [default: cropped_rgb_images]')
args = parser.parse_args()

input_dir = os.path.join('../datasets/adobeindoornav_dataset', args.scene_name, 'panorama_images')
output_dir = os.path.join('../datasets/adobeindoornav_dataset', args.scene_name, 'panorama_images_'+args.output_suffix)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)
else:
    print '%s folder exists! Please check and delete it!' % output_dir
    exit(1)

item_list = [item for item in os.listdir(input_dir) if item.endswith('_0.jpg')]

def theta_norm(theta):
    return (theta + 180) % 360 - 180

i = 0
for item in item_list:
    print '[%d/%d] Loading image: %s ' % (i, len(item_list), os.path.join(input_dir, item))
    img = misc.imread(os.path.join(input_dir, item))
    fn = item.split('.')[0]
    if '_' in fn:
        fn = fn.split('_')[0]

    print fn

    # front
    for j in range(args.number_jitter):
        theta_jitter_random = np.clip(np.random.randn(), -1, 1) * args.theta_jitter + args.front_theta
        phi_jitter_random = np.clip(np.random.randn(), -1, 1) * args.phi_jitter
        out_img = crop_panorama_image(img, theta_norm(theta_jitter_random), phi_jitter_random, args.res_x, args.res_y, args.fov)
        rand_img = np.int32(np.random.randn(out_img.shape[0], out_img.shape[1], out_img.shape[2]) * args.gaussian_noise_sigma)
        out_img = np.clip(rand_img + out_img, 0, 255)
        misc.imsave(os.path.join(output_dir, fn+'_0_'+str(j)+'.png'), out_img)

    # left
    for j in range(args.number_jitter):
        theta_jitter_random = np.clip(np.random.randn(), -1, 1) * args.theta_jitter + args.front_theta - 90.0
        phi_jitter_random = np.clip(np.random.randn(), -1, 1) * args.phi_jitter
        out_img = crop_panorama_image(img, theta_norm(theta_jitter_random), phi_jitter_random, args.res_x, args.res_y, args.fov)
        rand_img = np.int32(np.random.randn(out_img.shape[0], out_img.shape[1], out_img.shape[2]) * args.gaussian_noise_sigma)
        out_img = np.clip(rand_img + out_img, 0, 255)
        misc.imsave(os.path.join(output_dir, fn+'_270_'+str(j)+'.png'), out_img)

    # right
    for j in range(args.number_jitter):
        theta_jitter_random = np.clip(np.random.randn(), -1, 1) * args.theta_jitter + args.front_theta + 90.0
        phi_jitter_random = np.clip(np.random.randn(), -1, 1) * args.phi_jitter
        out_img = crop_panorama_image(img, theta_norm(theta_jitter_random), phi_jitter_random, args.res_x, args.res_y, args.fov)
        rand_img = np.int32(np.random.randn(out_img.shape[0], out_img.shape[1], out_img.shape[2]) * args.gaussian_noise_sigma)
        out_img = np.clip(rand_img + out_img, 0, 255)
        misc.imsave(os.path.join(output_dir, fn+'_90_'+str(j)+'.png'), out_img)

    # back
    for j in range(args.number_jitter):
        theta_jitter_random = np.clip(np.random.randn(), -1, 1) * args.theta_jitter + args.front_theta + 180.0
        phi_jitter_random = np.clip(np.random.randn(), -1, 1) * args.phi_jitter
        out_img = crop_panorama_image(img, theta_norm(theta_jitter_random), phi_jitter_random, args.res_x, args.res_y, args.fov)
        rand_img = np.int32(np.random.randn(out_img.shape[0], out_img.shape[1], out_img.shape[2]) * args.gaussian_noise_sigma)
        out_img = np.clip(rand_img + out_img, 0, 255)
        misc.imsave(os.path.join(output_dir, fn+'_180_'+str(j)+'.png'), out_img)

    i += 1

