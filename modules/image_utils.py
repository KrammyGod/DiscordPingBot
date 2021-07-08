from PIL import Image, ImageDraw

def convert_pixels(filename):
    """
    (str) -> list
    
    Load an image using PIL.Image and extract and return
    the pixels, width, and height as a list.
    """
    img = Image.open(filename)
    
    pixels = list(img.getdata())
    # Size of 3000x2500 pixel image
    # Larger images takes too much memory, will not convert into pixels
    if len(pixels) > 7500000:
        return [None, None, None]

    if (isinstance(pixels[0], tuple)):
        # RGB, convert to lists
        pixels = [list(i[0:3]) for i in pixels]
    else:
        # grayscale, spoof RGB
        pixels = [[pixel,pixel,pixel] for pixel in pixels]
    
    width, height = img.size
    
    return [pixels, width, height]


def save_image(pixels, width, height, filename=None):
    """
    (list, int, int, list, str) -> None
    
    Display a list of pixels as an image. If filename given,
    save generated image to file.
    """
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
    '''
    (list, int, int, int, int) -> int
    '''
    # Note: returns None if given coord is out of bounds.
    if (x < 0 or x >= width) or (y < 0 or y >= height):
        return
    
    return img[y*width + x]


def grayscale(rgb_img):
    """
    (list) -> list
    
    Function converts an image of RGB pixels to grayscale.
    Input list is a nested list of RGB pixels.
    
    The intensity of a grayscale pixel is computed from the intensities of
    RGB pixels using the following equation
    
        grayscale intensity = 0.3 * R + 0.59 * G + 0.11 * B
    
    where R, G, and B are the intensities of the R, G, and B components of the
    RGB pixel. The grayscale intensity should be rounded to the nearest
    integer.
    """
    
    new_img = []
    for rgb in rgb_img:
        total = 0
        total += rgb[0]*0.3
        total += rgb[1]*0.59
        total += rgb[2]*0.11
        new_img.append(round(total))

    return new_img


def extract_image_segment(img, width, height, centre_coordinate, N):
    """
    (list, int, int, list, int) -> list
    
    Extracts a 2-dimensional NxN segment of a image centred around
    a given coordinate. The segment is returned as a list of pixels from the
    segment.
    
    img is a list of grayscale pixel values
    width is the width of the image
    height is the height of the image
    centre_coordinate is a two-element list defining a pixel coordinate
    N is the height and width of the segment to extract from the image
    
    """
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
    """
    (list, int, int, list) -> list
    
    Apply the kernel filter defined within the two-dimensional list kernel to 
    image defined by the pixels in img and its width and height.
    
    img is a 1 dimensional list of grayscale pixels
    width is the width of the image
    height is the height of the image
    kernel is a 2 dimensional list defining a NxN filter kernel, n must be an odd integer
    
    The function returns the list of pixels from the filtered image
    """

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


def modify_colour(img, org_img, width, height, kernel):
    """
    (list, int, int, list) -> list
    
    Apply the kernel filter defined within the two-dimensional list kernel to 
    image defined by the pixels in img and its width and height.
    
    img is a 1 dimensional list of grayscale pixels
    width is the width of the image
    height is the height of the image
    kernel is a 2 dimensional list defining a NxN filter kernel, n must be an odd integer
    
    The function returns the list of pixels from the filtered image
    """

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
