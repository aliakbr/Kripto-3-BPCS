"""
    Class to do BPCS algorithm
"""
from bitplane import BitPlaneProcessing
from vigenere_ascii import Vigenere_Ascii
import random
import pickle

class BPCS:
    def encrypt(self, img_file, input_file, output_file,
        key='default',
        sequential=True,
        cgc=False,
        threshold=0.3):
        bp = BitPlaneProcessing(threshold)
        vigenere = Vigenere_Ascii()

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

        input_text = self.read_byte_string(input_file)
        input_text = vigenere.encrypt(key, input_text)
        bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
        while len(bin_input) % 64 != 0:
            bin_input += dummy_binary
        input_blocks = bp.sliceStringToBlocks(bin_input)
        msg_size = len(input_blocks)

        # Inserting message
        encrypted_bitplanes = []
        conj_map = ['0']
        conj_idx = 0
        i = 0
        count = -1

        for idx, (bitplane, complexity) in enumerate(bitplanes_comp):
            bitplanes_comp[idx] = (idx, bitplane, complexity)

        if not sequential:
            random.seed(self.get_seed(key))
            random.shuffle(bitplanes_comp)

        bitplanes_used = []
        for idx, (no, bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and (i < msg_size):
                count += 1
                if count == 0:
                    # First complex plane is reserved for conjugation map
                    conj_idx = idx
                    conj_no = no
                    bitplanes_used.append(no)
                    continue
                elif count == 1:
                    # Second complex plane is reserved for file name
                    encrypted_bitplane = ''.join(input_name)
                elif count == 2:
                    # Change first bit plane to save message length
                    encrypted_bitplane = ''.join('{0:064b}'.format(msg_size))
                else:
                    encrypted_bitplane = ''.join(input_blocks[i])
                    i += 1
                encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                if encrypted_complexity <= bp.alpha_threshold:
                    encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
                    encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                    conj_map.append(str(count))
                encrypted_bitplanes.append((no, encrypted_bitplane))
                bitplanes_used.append(no)
            else:
                encrypted_bitplanes.append((no, bitplane))

        print('Bitplanes Used:', bitplanes_used)
        str_conj = '/'.join(conj_map)
        bin_conj = ''.join('{0:08b}'.format(ord(x), 'b') for x in str_conj)
        while len(bin_conj) % 64 != 0:
            bin_conj += dummy_binary
        input_conj = bp.sliceStringToBlocks(bin_conj)
        encrypted_bitplane = bp.conjugate_bitplane(''.join(input_conj))
        encrypted_bitplanes.insert(conj_idx, (conj_no, encrypted_bitplane))

        encrypted_bitplanes.sort(key=lambda x: x[0])
        encrypted_bitplanes = [x[1] for x in encrypted_bitplanes]

        # Save bitplanes as image
        blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
        img_data = bp.blocksToRGBData(blocks_encrypted)
        bp.dataToImage(img_data, output_file)

    def decrypt(self, img_file,
        key='default',
        sequential=True,
        cgc=False,
        threshold=0.3):
        bp = BitPlaneProcessing(threshold)
        vigenere = Vigenere_Ascii()

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
        conj_map = [0]
        output = ""

        if not sequential:
            random.seed(self.get_seed(key))
            random.shuffle(bitplanes_comp)

        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.alpha_threshold:
                if count == 0:
                    msg_conj = ""
                    bitplane = bp.conjugate_bitplane(bitplane)
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        msg_conj += kar
                        j += 8
                    conj_map = msg_conj.strip().split('/')
                    count += 1
                elif count == 1:
                    file_name = ""
                    if count in conj_map:
                        bitplane = bp.conjugate_bitplane(bitplane)
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        file_name += kar
                        j += 8
                    file_name = file_name.strip()
                    count += 1
                else:
                    if count in conj_map:
                        bitplane = bp.conjugate_bitplane(bitplane)
                    msg_len = int(bitplane, 2)
                    break

        count = 0
        print ('Conjugation idx : {}'.format(conj_map))
        print ('File name       : {}'.format(file_name))
        print ('Message length  : {}'.format(msg_len))
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.alpha_threshold and i != msg_len:
                if count <= 2:
                    count += 1
                elif count:
                    if count in conj_map:
                        bitplane = bp.conjugate_bitplane(bitplane)
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        output += kar
                        j += 8
                    i += 1

        output = vigenere.decrypt(key, output)
        self.write_byte_string(file_name, output)
        return file_name

    def get_seed(self, key):
        seed = 0
        for c in key:
            seed += ord(c)
        return seed

    def read_byte_string(self, filename):
        array_of_bytes = []
        with open(filename, 'rb') as f:
            byte = f.read(1)
            while byte:
                array_of_bytes.append(byte)
                byte = f.read(1)

        temp = [int(x[0]) for x in array_of_bytes]
        return ''.join(chr(x) for x in temp)

    def write_byte_string(self, filename, output):
        array_of_bytes = [ord(x) for x in output]
        with open(filename, 'wb') as f:
            f.write(bytearray(array_of_bytes))
        return output
