"""
    Class script for bitplane image processing
"""

import numpy as np
from PIL import Image


class BitPlaneProcessing:
    """
        Class to process image in bitplane
    """
    def __init__(self):
        self.unused_pixels = 0
        self.img_file = ""
        self.ALPHA_TRESHOLD = 0.3
        self.size = (0, 0)
        self.format_file = ""
        self.width_border = 0
        self.height_border = 0

    def getBinArrayTrueColor(self, img_file):
        """
            Return list of binary representation of pixel
        """
        self.img_file = img_file
        img = Image.open(img_file)
        imgArray = np.array(img)
        row, col, channel = imgArray.shape
        self.format_file = img_file.split(".")[1]
        self.size = (col, row)
        matrix = [['0' for x in range(col)] for y in range(row)]
        self.true_rgb_values = [[(0, 0, 0) for x in range(col)] for y in range(row)]
        for i in range(row):
            for j in range(col):
                rgb_values = imgArray[i][j]
                bin_str = ''
                for val in rgb_values:
                    bin_str += '{0:08b}'.format(val)
                matrix[i][j] = bin_str
                r, g ,b = rgb_values
                r = int(r)
                g = int(g)
                b = int(b)
                self.true_rgb_values[i][j] = (r, g, b)
        return matrix

    def sliceToBlocks(self, binMatrix):
        """
            Slice binary array to 8x8 blocks images
            input :
                binArray    : binary Array
            output :
                8x8 images in 1d array
        """
        blocks = []
        w, h = self.size
        i = 0
        j = 0
        while (i + 8 < h):
            j = 0
            while (j + 8 < w):
                block = []
                for x in range(8):
                    block += binMatrix[i+x][j:j+8]
                blocks.append(block)
                j += 8
            i += 8
        self.height_border = i
        self.width_border = j
        return blocks

    def sliceStringToBlocks(self, input_str):
        output = []
        i = 0
        while (i < len(input_str)):
            output.append(input_str[i:i+64])
            i += 64
        return output

    def generateBitplaneArray(self, binArray, bit_pos):
        """
            Generate bitplane from desirable bit position
            return a binary image (matrix of value 1 or 0)
            0 <= bit_pos <= 23
        """
        bitPlaneOutput = []
        for i in range(len(binArray)):
            bitPlaneOutput += binArray[i][bit_pos]
        return ''.join(bitPlaneOutput)

    def calculateComplexity(self, binArray):
        """
            Calculate a complexity of blocks of images
            input :
                 binary string of binary 8x8 blocks
            output :
                complexity
        """
        count = 0
        for i in range(8):
            for j in range(8):
                if (binArray[i*8 + j] == '1'):
                    if (i - 1 >= 0):
                        if (binArray[i*8 + j] != binArray[(i-1)*8 + j]):
                            count += 1
                    if (j - 1 >= 0):
                        if (binArray[i*8 + j] != binArray[i*8 + (j-1)]):
                            count += 1
                    if (i + 1 < 8):
                        if (binArray[i*8 + j] != binArray[(i+1)*8 + j]):
                            count += 1
                    if (j + 1 < 8):
                        if (binArray[i*8 + j] != binArray[i*8 + (j+1)]):
                            count += 1
        return (count/112)

    def calculateMaxDataSize(self, img_file):
        """
            Calculate maximum size of data that can be hide by the images
            input :
                Image file name
            output :
                Number of bits that can be hid
        """
        img_bin_ar = self.getBinArrayTrueColor("tes.jpg")
        blocks = self.sliceToBlocks(img_bin_ar)
        count = 0

        for block in blocks:
            for i in range(24):
                bit_plane = self.generateBitplaneArray(block, i)
                if self.calculateComplexity(bit_plane) > self.ALPHA_TRESHOLD:
                    count += 1
        return (count-1)*64/8 # -1 for message saving bitplane

    def bitplaneToBlocks(self, bitplanes):
        """
            Return blocks of image from bitplanes
        """
        blocks = []
        i = 0
        while (i < len(bitplanes)):
            bitplane_block = bitplanes[i:i+24]
            block = [''.join(i) for i in zip(*bitplane_block)]
            blocks.append(block)
            i += 24
        return blocks

    def blocksToRGBData(self, blocks):
        """
            Blocks binary to RGB data
        """
        w, h = self.size
        image_data = []
        # Insert blocks data
        x_start, y_start = 0, 0
        for i, block in enumerate(blocks):
            for j, pixel in enumerate(block):
                r = int(pixel[:8], 2)
                g = int(pixel[8:16], 2)
                b = int(pixel[16:24], 2)
                x = x_start + (j // 8)
                y = y_start + (j % 8)
                image_data.append((x, y ,(r, g, b)))
            y_start += 8
            if (y_start >= self.width_border):
                x_start += 8
                y_start = 0

        # Insert unused pixels
        i = self.height_border
        while (i < h):
            j = 0
            while (j < w):
                image_data.append((i, j, self.true_rgb_values[i][j]))
                j += 1
            i += 1

        i = 0
        while (i < h):
            j = self.width_border
            while (j < w):
                image_data.append((i, j, self.true_rgb_values[i][j]))
                j += 1
            i += 1

        i = self.height_border
        while (i < h):
            j = self.width_border
            while (j < w):
                image_data.append((i, j, self.true_rgb_values[i][j]))
                j += 1
            i += 1

        return image_data

    def dataToImage(self, rgb_data, image_file_output):
        """
           Save RGB Data to Image
        """
        img = Image.new(mode="RGB", size=self.size)
        img_data = img.load()
        rgb_data = sorted(rgb_data, key=lambda x: (x[1],x[0]))
        for x, y, color in rgb_data:
            img_data[y,x] = color
        img.save(image_file_output)

    def conjugate_bitplane(self, P):
        W = ''.join(['1' for i in range(64)])
        B = ''.join(['0' for i in range(64)])
        Wc = ''.join(['01' for i in range(32)])
        Bc = ''.join(['10' for i in range(32)])
        def _xor(a, b):
            return '0' if a == b else '1'
        _P = ""
        for i, c in enumerate(P):
            _P += _xor(c, Wc[i])
        return _P
