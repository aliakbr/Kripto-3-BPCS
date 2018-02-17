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
        dummy_binary = "00001010"
        
        # File Name
        bin_name = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_file)
        while len(bin_name) % 64 != 0:
            bin_name += dummy_binary
        input_name = bp.sliceStringToBlocks(bin_name)
        
        # File Body
        with open(input_file, "r") as f:
            input_text = f.read()
        bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
        while len(bin_input) % 64 != 0:
            bin_input += dummy_binary
        input_blocks = bp.sliceStringToBlocks(bin_input)
        msg_size = len(input_blocks)
        print (msg_size)
        
        # Inserting message
        encrypted_bitplanes = []
        i = 0
        count = 0
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.ALPHA_TRESHOLD and (i < msg_size):
                if count == 0:
                    # First complex plane is reserved for file name
                    encrypted_bitplane = ''.join(input_name)
                    count += 1
                elif count == 1:
                    # Change first bit plane to save message length
                    encrypted_bitplane = ''.join('{0:064b}'.format(msg_size))
                    count += 1
                else:
                    encrypted_bitplane = ''.join(input_blocks[i])
                    i += 1
                encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                if encrypted_complexity <= bp.ALPHA_TRESHOLD:
                    encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
                    encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                print ("Encrypted : {}".format(encrypted_bitplane))
                encrypted_bitplanes.append(encrypted_bitplane)
            else:
                encrypted_bitplanes.append(bitplane)
        
        # Save bitplanes as image
        blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
        img_data = bp.blocksToRGBData(blocks_encrypted)
        bp.dataToImage(img_data, output_file)

    def decrypt(self, img_file):
        # Create bitplanes of image img_file
        img_bin_ar = bp.getBinArrayTrueColor(img_file)
        blocks = bp.sliceToBlocks(img_bin_ar)
        bitplanes_comp = []
        for block in blocks:
            for i in range(24):
                bitplane = bp.generateBitplaneArray(block, i)
                complexity = bp.calculateComplexity(bitplane)
                bitplanes_comp.append((bitplane, complexity))

        count = 0
        i = 0
        output = ""
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.ALPHA_TRESHOLD:
                bitplane = bp.conjugate_bitplane(bitplane)
                msg_len = int(bitplane, 2)
                break

        print (msg_len)
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.ALPHA_TRESHOLD and i != msg_len:
                if count == 0:
                    count += 1
                else:
                    j = 0
                    print (bitplane)
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        output += kar
                        j += 8
                    i += 1
        return output
