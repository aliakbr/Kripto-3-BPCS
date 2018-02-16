"""
    Class to do BPCS algorithm
"""
from bitplane import BitPlaneProcessing
bp = BitPlaneProcessing()

class BPCS:
    def encrypt(self, img_file, input_file, output_file):
        # Create bitplanes of image img_file
        img_bin_ar = bp.getBinArrayTrueColor(img_file)
        blocks = bp.sliceToBlocks(img_bin_ar)
        bitplanes_comp = []
        for block in blocks:
            for i in range(24):
                bitplane = bp.generateBitplaneArray(block, i)
                complexity = bp.calculateComplexity(bitplane)
                bitplanes_comp.append((bitplane, complexity))

        # Split input into 8x8 blocks
        with open(input_file, "r") as f:
            input_text = f.read()
        bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
        dummy_binary = "00001010"
        while len(bin_input) % 64 != 0:
            bin_input += dummy_binary
        input_blocks = bp.sliceToBlocks(bin_input)
        msg_size = len(input_blocks)

        # Inserting message
        encrypted_bitplanes = []
        i = 0
        count = 0
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.ALPHA_TRESHOLD and (i != len(input_blocks)):
                if count == 0:
                    # Change first bit plane to save message length
                    msg_len = ''.join('{0:064b}'.format(msg_size))
                    encrypted_bitplane = msg_len
                    encrypted_bitplanes.append(encrypted_bitplane)
                    count += 1
                else:
                    encrypted_bitplanes.append(input_blocks[i])
                    i += 1
            else:
                encrypted_bitplanes.append(''.join(bitplane))
        blocks = bp.bitplaneToBlocks(encrypted_bitplanes)
        img_data = bp.blocksToRGBData(blocks)
        print (img_data)
        bp.dataToImage(img_data, output_file)
