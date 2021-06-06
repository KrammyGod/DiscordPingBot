from PIL import Image, ImageDraw

def convert_pixels(filename):
    img = Image.open(filename)
    
    pixels = list(img.getdata())
    if (isinstance(pixels[0], tuple)):
        # RGB, convert to lists
        pixels = [list(rgb_pixel[0:3]) for rgb_pixel in pixels]
    else:
        # grayscale, spoof RGB
        pixels = [[pixel,pixel,pixel] for pixel in pixels]
    
    width, height = img.size
    
    return [pixels, width, height]


def save_image(pixels, width, height, filename=None):
    if isinstance(pixels[0],list):
        img = Image.new('RGB',(width,height))
        p = [tuple(pixel) for pixel in pixels]
        p = tuple(p)
    else:
        img = Image.new('L', (width,height))
        pixels = [min(int(abs(p)),255) for p in pixels]
        p = tuple(pixels)
    
    img.putdata(p)
    
    if filename != None:
        img.save(filename)


def get_coord_rgb(img, x, y, width, height):
    # Note: returns None if given coord is out of bounds.
    if (x < 0 or x >= width) or (y < 0 or y >= height):
        return
    
    return img[y*width + x]


def grayscale(rgb_img):
    new_img = []
    for rgb in rgb_img:
        total = 0
        total += rgb[0]*0.3
        total += rgb[1]*0.59
        total += rgb[2]*0.11
        new_img.append(round(total))

    return new_img


def extract_image_segment(img, width, height, centre_coordinate, N):
    start_row = centre_coordinate[1] - (N // 2)
    end_row = start_row + N
    start_col = centre_coordinate[0] - (N // 2)
    end_col = start_col + N
    new_img = []
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            new_img.append(get_coord_rgb(img, col, row, width, height))
    
    return new_img


def modify(img, width, height, kernel):
    # NxN window
    N = len(kernel)
    new_img = []
    for y in range(height):
        for x in range(width):
            segment = extract_image_segment(img, width, height, [x, y], N)
            total = 0
            if not (None in segment):
                # Go through the NxN kernel
                for row in range(N):
                    for col in range(N):
                        total += segment[row*N + col] * kernel[row][col]
            new_img.append(round(total))

    return new_img


# Only for specific kernels work well
def modify_colour(img, org_img, width, height, kernel):
    # NxN window
    N = len(kernel)
    new_img = []
    for y in range(height):
        for x in range(width):
            segment = extract_image_segment(img, width, height, [x, y], N)
            total = 0
            if not (None in segment):
                # Go through the NxN kernel
                for row in range(N):
                    for col in range(N):
                        total += segment[row*N + col] * kernel[row][col]
            change = total - get_coord_rgb(img, x, y, width, height)
            org_img[y*width + x][0] += round(total * 0.3)
            org_img[y*width + x][1] += round(total * 0.59)
            org_img[y*width + x][2] += round(total * 0.11)

    return org_img
