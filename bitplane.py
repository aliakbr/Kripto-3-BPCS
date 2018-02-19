"""
    Class script for bitplane image processing
"""

import numpy as np
from PIL import Image


class BitPlaneProcessing:
    """
        Class to process image in bitplane
    """
    def __init__(self, alpha_threshold=0.3):
        self.unused_pixels = 0
        self.img_file = ""
        self.alpha_threshold = alpha_threshold
        self.size = (0, 0)
        self.format_file = ""
        self.width_border = 0
        self.height_border = 0
        self.bits_len = 24
        self.enc_mode = "RGB"

    def getBinArrayTrueColor(self, img_file):
        """
            Return list of binary representation of pixel
        """
        self.img_file = img_file
        img = Image.open(img_file)
        if (img.mode == "RGBA"):
            self.bits_len = 32
            self.enc_mode = "RGBA"
        else:
            self.bits_len = 24
            img = img.convert("RGB")
            self.enc_mode = "RGB"
        imgArray = np.array(img)
        row, col, channel = imgArray.shape
        self.format_file = img_file.split(".")[1]
        self.size = (col, row)
        matrix = [['0' for x in range(col)] for y in range(row)]
        if (self.enc_mode == "RGBA"):
            self.true_rgb_values = [[(0, 0, 0, 0) for x in range(col)] for y in range(row)]
        else:
            self.true_rgb_values = [[(0, 0, 0) for x in range(col)] for y in range(row)]
        for i in range(row):
            for j in range(col):
                rgb_values = imgArray[i][j]
                bin_str = ''
                for val in rgb_values:
                    bin_str += '{0:08b}'.format(val)
                matrix[i][j] = bin_str
                if (self.enc_mode == "RGBA"):
                    r, g ,b, a = rgb_values
                    self.true_rgb_values[i][j] = (int(r), int(g), int(b), int(a))
                else:
                    r, g ,b = rgb_values
                    self.true_rgb_values[i][j] = (int(r), int(g), int(b))
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
            0 <= bit_pos <= 23 or 0 <= bit_pos <= 31
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
                Number of bitplanes
        """
        img_bin_ar = self.getBinArrayTrueColor(img_file)
        blocks = self.sliceToBlocks(img_bin_ar)
        count = 0

        for block in blocks:
            for i in range(self.bits_len):
                bit_plane = self.generateBitplaneArray(block, i)
                if self.calculateComplexity(bit_plane) > self.alpha_threshold:
                    count += 1
        return count

    def create_bitplanes(self, blocks):
        """
            Create list of bitplanes and its complexity
        """
        output = []
        for block in blocks:
            for i in range(self.bits_len):
                bitplane = self.generateBitplaneArray(block, i)
                complexity = self.calculateComplexity(bitplane)
                output.append((bitplane, complexity))
        return output
    
    def xor_bitplane(self, b, bprev):
        """
            XOR 2 bitplanes
        """
        return '{0:064b}'.format(int(b, 2) ^ int(bprev, 2))
    
    def create_bitplanes_CGC(self, blocks):
        """
            Create list of bitplanes and its complexity with CGC
        """
        output = []
        for block in blocks:
            last = ""
            for i in range(self.bits_len):
                bitplane = self.generateBitplaneArray(block, i)
                last = bitplane
                if i != 1:
                    bitplane = self.xor_bitplane(bitplane, last)
                complexity = self.calculateComplexity(bitplane)
                output.append((bitplane, complexity))
        return output
    
    def reverse_CGC(self, blocks):
        """
            Return to PBC from CGC
        """
        output = []
        for block in blocks:
            last = ""
            for i in range(self.bits_len):
                bitplane = self.generateBitplaneArray(block, i)
                if i != 1:
                    bitplane = self.xor_bitplane(bitplane, last)
                complexity = self.calculateComplexity(bitplane)
                last = bitplane
                output.append((bitplane, complexity))
        return output

    def bitplaneToBlocks(self, bitplanes):
        """
            Return blocks of image from bitplanes
        """
        blocks = []
        i = 0
        while (i < len(bitplanes)):
            bitplane_block = bitplanes[i:i+self.bits_len]
            block = [''.join(i) for i in zip(*bitplane_block)]
            blocks.append(block)
            i += self.bits_len
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
                if (self.enc_mode == "RGBA"):
                    a = int(pixel[24:32], 2)
                    image_data.append((x, y ,(r, g, b, a)))
                else:
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
        if (self.enc_mode == "RGB"):
            img = Image.new(mode="RGB", size=self.size)
        else:
            img = Image.new(mode="RGBA", size=self.size)
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
