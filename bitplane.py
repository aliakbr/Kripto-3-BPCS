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
        list = []
        for i in range(row):
            for j in range(col):
                rgb_values = imgArray[i][j]
                bin_str = ''
                for val in rgb_values:
                    bin_str += '{0:08b}'.format(val)
                list.append(bin_str)
        # Trimming if images is not divisible by 8x8
        self.len_unused_pixels = len(list) % 64
        return list

    def sliceToBlocks(self, binArray):
        """
            Slice binary array to 8x8 blocks images
            input :
                binArray    : binary Array
            output :
                8x8 images in 1d array
        """
        sliced_list = []
        i = 0
        while i < len(binArray) - self.len_unused_pixels:
            sliced_list.append(binArray[i:i+64])
            i += 64
        self.unused_pixels = binArray[i:]
        return sliced_list

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
        blocks_concat = []
        for block in blocks:
            blocks_concat += block

        image_data = []
        i = 0
        j = 0
        for x, block in enumerate(blocks_concat):
            r = int(block[:8], 2)
            g = int(block[8:16], 2)
            b = int(block[16:24], 2)
            image_data.append((i, j ,(r, g, b)))
            j += 1
            if (j == self.size[0]):
                i += 1
                j = 0
        return image_data

    def dataToImage(self, rgb_data, image_file_output):
        """
            Create RGB data from 8x8 blocks binary string
        """
        WIDTH = self.size[0]
        HEIGTH = self.size[1]
        img = Image.new('RGB', (WIDTH, HEIGTH))
        img_data = img.load()
        for x, y, color in rgb_data:
            img_data[y,x] = color
        if self.format_file == "jpg":
            format_file = "JPEG"
        else:
            format_file = self.format_file
        img.save(image_file_output)
