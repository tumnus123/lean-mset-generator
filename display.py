# display.py
#---------------
#
#

from PIL import Image

def display_iter_array(iter_array, min_iter, max_iter, img_width, img_height):
    img = Image.new('RGB', (img_width, img_height))

    # convert iter_array to RGB_array
    RGB_array = []
    for val in iter_array:
        RGB_array.append(get_pixel_color(min_iter, max_iter, val))

    img.putdata(RGB_array)
    img.save('output_imgs\pil_image.png')

def get_pixel_color(min_iter, max_iter, this_iter, alg='normalized_grayscale'):
    if alg=='normalized_grayscale':
        norm_iter = int(((this_iter - min_iter) / (max_iter - min_iter)) * 255.0)
        RGB_tuple = (norm_iter, norm_iter, norm_iter)

    return(RGB_tuple)
