"""
    Class script for bitplane image processing
"""

import numpy as np
from PIL import Image

DUMMY_BYTES_STRING = "111111111111111111111111"

class BitPlaneProcessing:
    """
        Class to process image in bitplane
    """
    def getBinArrayTrueColor(self, img_file):
        """
            Return list of binary representation of pixel
        """
        img = Image.open(img_file)
        imgArray = np.array(img)
        row, col, channel = imgArray.shape
        list = []
        for i in range(row):
            for j in range(col):
                rgb_values = imgArray[i][j]
                bin_str = ''
                for val in rgb_values:
                    bin_str += '{0:08b}'.format(val)
                list.append(bin_str)
        # Padding the list with dummy bytes
        if len(list) % 64 != 0:
            for i in range(64 - (len(list) % 64)):
                list.append(DUMMY_BYTES_STRING)
        return list

    def sliceToBlocks(self, binArray):
        """
            Slice binary array to 8x8 blocks images
            input :
                binArray    : binaryArray
                blocks      : desirable blocks
        """
        sliced_list = []
        i = 0
        while i < len(binArray):
            sliced_list.append(binArray[i:i+64])
            i += 64
        return sliced_list

    def generateBitplaneArray(self, binArray, bit_pos):
        """
            Generate bitplane from desirable bit position
            return a binary image (matrix of value 1 or 0)
            0 <= bit_pos <= 23
        """
        bitPlaneOutput = []
        for i in range(len(binArray)):
            reversed_bin = binArray[i][::-1]
            bitPlaneOutput += reversed_bin[bit_pos]
        return bitPlaneOutput
