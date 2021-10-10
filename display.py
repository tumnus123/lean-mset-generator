# display.py
#---------------
#
#

from PIL import Image

def display_iter_array(pixel_array, min_z, max_z, img_width, img_height):
    img = Image.new('RGB', (img_width, img_height))

    # convert iter_array to RGB_array
    RGB_array = []
    for px in pixel_array:
        RGB_array.append(get_pixel_color(min_z, max_z, px.output_z))

    img.putdata(RGB_array)
    img.save('output_imgs\pil_image.png')

def get_pixel_color(min_z, max_z, this_z, alg='normalized_grayscale'):
    if alg=='normalized_grayscale':
        norm_z = int(((this_z - min_z) / (max_z - min_z)) * 255.0)
        RGB_tuple = (norm_z, norm_z, norm_z)

    if alg=='raw_z':
        RGB_tuple = (this_z, this_z, this_z)

    return(RGB_tuple)
