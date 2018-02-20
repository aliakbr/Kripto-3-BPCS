"""
    Class to do BPCS algorithm
"""
from bitplane import BitPlaneProcessing
from vigenere_ascii import Vigenere_Ascii
from PIL import Image
import numpy as np
import math
import random
import pickle

class BPCS:
    def encrypt(self, img_file, input_file, output_file,
        key='default',
        sequential=True,
        cgc=False,
        threshold=0.3,
        encrypted=True):
        print ("Initialize encryption ...")
        bp = BitPlaneProcessing(threshold)
        vigenere = Vigenere_Ascii()

        # Calculate bitplanes that can be used
        max_bitplanes = bp.calculateMaxDataSize(img_file)
        max_size_conj_map = int(bp.calculateMaxDataSize(img_file) * 0.1)
        print ("Maximum bitplanes :",max_bitplanes)
        print ("Maximum conjugation maps:",max_size_conj_map)

        # Create bitplanes of image img_file
        img_bin_ar = bp.getBinArrayTrueColor(img_file)
        blocks = bp.sliceToBlocks(img_bin_ar)
        if cgc:
            bitplanes_comp = bp.create_bitplanes_CGC(blocks)
        else:
            bitplanes_comp = bp.create_bitplanes(blocks)
        bitplanes_ori = [bitplane[0] for bitplane in bitplanes_comp]

        # Split input into 8x8 blocks
        dummy_binary = "00000000"

        # File Name
        print ("Calculating bitplanes usage ..")
        filename_size = len(input_file)
        bin_name = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_file)
        while len(bin_name) % 64 != 0:
            bin_name += dummy_binary
        input_name = bp.sliceStringToBlocks(bin_name)
        nm_size = len(input_name)

        input_text = self.read_byte_string(input_file)
        if encrypted:
            input_text = vigenere.encrypt(key, input_text)
        msg_size = len(input_text)
        bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
        while len(bin_input) % 64 != 0:
            bin_input += dummy_binary
        input_blocks = bp.sliceStringToBlocks(bin_input)
        msg_blocks_size = len(input_blocks)
        usage = msg_blocks_size  + nm_size + 6 + ((msg_blocks_size // 64) + 1)
        if (max_bitplanes - max_size_conj_map) < (usage):
            print ("Over payload can't embed message")
            return 0
        else:
            print ("Filename usage : {} bitplanes".format(nm_size))
            print ("Message usage : {} bitplanes".format(msg_blocks_size))

        # Inserting message
        encrypted_bitplanes = []
        conj_map = []
        conj_idx = []
        i = -2
        nm = 0
        count = -1
        for idx, (bitplane, complexity) in enumerate(bitplanes_comp):
            bitplanes_comp[idx] = (idx, bitplane, complexity)

        if not sequential:
            random.seed(self.get_seed(key))
            random.shuffle(bitplanes_comp)

        print ("Creating encrypted bitplane and insert message...")
        bitplanes_used = []
        bitplanes_used_msg = []
        default_conj_bitplanes = []
        offset = 0
        f = 0
        for idx, (no, bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and (i < msg_blocks_size):
                count += 1
                if count < (max_size_conj_map + 3): # 2 bitplane to store conjugation map info
                    # First complex plane is reserved for conjugation map
                    conj_idx.append((no, idx))
                    bitplanes_used.append(no)
                    default_conj_bitplanes.append(bitplane)
                    continue
                else:
                    if nm < nm_size:
                        if (f == 0):
                            encrypted_bitplane = ''.join('{0:064b}'.format(filename_size))
                            offset = idx
                            f += 1
                        else:
                            # Second complex plane is reserved for file name
                            encrypted_bitplane = ''.join(input_name[nm])
                            nm += 1
                    else:
                        if i == -2:
                            # Change first bit plane to save bitplanes used length
                            encrypted_bitplane = ''.join('{0:064b}'.format(msg_blocks_size))
                        elif i == -1:
                            # Change second bit plane to save length of message in byte
                            encrypted_bitplane = ''.join('{0:064b}'.format(msg_size))
                        else:
                            encrypted_bitplane = ''.join(input_blocks[i])
                            bitplanes_used_msg.append(no)
                        i += 1
                encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                if encrypted_complexity <= bp.alpha_threshold:
                    encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
                    conj_map.append("1")
                else:
                    conj_map.append("0")
                encrypted_bitplanes.append((no, encrypted_bitplane))
                bitplanes_used.append(no)
            else:
                encrypted_bitplanes.append((no, bitplane))

        # Creating conjugation map
        print('Creating conjugation map...')
        print (conj_map)
        bin_conj = ''.join(conj_map)
        while len(bin_conj) % 64 != 0:
            bin_conj += "0"
        input_conj = bp.sliceStringToBlocks(bin_conj)
        conj_map_len = len(input_conj)
        print ("Conjugation Map Bitplanes usage :", conj_map_len)

        # Insert conjugation map bitplanes
        print('Inserting conjugation map...')
        conj_input_counter = 0
        for x in range(len(conj_idx)):
            if (x == 0):
                encrypted_bitplane = ''.join('{0:064b}'.format(conj_map_len))
            elif (x == 1):
                encrypted_bitplane = ''.join('{0:064b}'.format(len(conj_map)))
            elif (x == 2):
                encrypted_bitplane = ''.join('{0:064b}'.format(offset))
            else:
                if (conj_input_counter < conj_map_len):
                    encrypted_bitplane = ''.join(input_conj[conj_input_counter])
                    conj_input_counter += 1
                else:
                    encrypted_bitplane = default_conj_bitplanes[x]
            encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
            encrypted_bitplanes.insert(conj_idx[x][1], (conj_idx[x][0], encrypted_bitplane))

        encrypted_bitplanes.sort(key=lambda x: x[0])
        encrypted_bitplanes = [x[1] for x in encrypted_bitplanes]

        print('Save bitplanes as image...')
        # Save bitplanes as image
        blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
        if cgc:
            reversed_blocks_encrypted = bp.reverse_CGC(blocks_encrypted)
            blocks_encrypted = bp.bitplaneToBlocks(reversed_blocks_encrypted)

        print('Calculate bitplanes after...')
        bitplanes_after = bp.create_bitplanes(blocks_encrypted)
        bitplanes_after = [bitplane[0] for bitplane in bitplanes_after]

        print('Accumulate blocks to form image...')
        img_data = bp.blocksToRGBData(blocks_encrypted)
        bp.dataToImage(img_data, output_file)
        return True

    def decrypt(self, img_file,
        key='default',
        sequential=True,
        cgc=False,
        threshold=0.3,
        encrypted=True):
        bp = BitPlaneProcessing(threshold)
        vigenere = Vigenere_Ascii()

        print ("Initializing decryption .....")
        max_bitplanes = bp.calculateMaxDataSize(img_file)
        max_size_conj_map = int(bp.calculateMaxDataSize(img_file) * 0.1)
        print ("Maximum bitplanes :",max_bitplanes)
        print ("Maximum conjugation maps:",max_size_conj_map)

        # Create bitplanes of image img_file
        img_bin_ar = bp.getBinArrayTrueColor(img_file)
        blocks = bp.sliceToBlocks(img_bin_ar)
        if cgc:
            bitplanes_comp = bp.create_bitplanes_CGC(blocks)
        else:
            bitplanes_comp = bp.create_bitplanes(blocks)

        header = 0
        conj_map = []
        file_name = ""
        msg_len = 0

        if not sequential:
            random.seed(self.get_seed(key))
            random.shuffle(bitplanes_comp)

        print ("Decrypting file header ...")
        msg_checker = 0
        conj_map_block_len = 0
        conj_map_counter = 0
        conj_map_len = 0
        offset = 0
        filename_size = 0
        f = 0
        offset = max_size_conj_map + 3
        i_conj = 0
        for i, (bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold:
                if i < offset:
                    if header == 0:
                        # Read block size of conjugation map
                        bitplane = bp.conjugate_bitplane(bitplane)
                        conj_map_block_len = int(bitplane, 2)
                    elif header == 1:
                        # Read size of conjugation map
                        bitplane = bp.conjugate_bitplane(bitplane)
                        conj_map_len = int(bitplane, 2)
                    elif header == 2:
                        # Read size of conjugation map
                        bitplane = bp.conjugate_bitplane(bitplane)
                        offset = int(bitplane, 2)
                    else:
                        if (conj_map_counter < conj_map_block_len):
                            bitplane = bp.conjugate_bitplane(bitplane)
                            k = 0
                            while (k < len(bitplane)):
                                if (len(conj_map) < conj_map_len):
                                    conj_map.append(bitplane[k])
                                k += 1
                            conj_map_counter += 1
                else:
                    if (len(file_name) == 0) or (len(file_name) < filename_size):
                        if conj_map[i_conj] == "1":
                            bitplane = bp.conjugate_bitplane(bitplane)
                        i_conj += 1
                        if (f == 0):
                            # Read filename header
                            filename_size = int(bitplane, 2)
                            f += 1
                        else:
                            # Read filename
                            j = 0
                            while (j < len(bitplane)):
                                kar = chr(int(bitplane[j:j+8], 2))
                                if len(file_name) < filename_size:
                                    file_name += kar
                                j += 8
                    else:
                        if conj_map[i_conj] == "1":
                            bitplane = bp.conjugate_bitplane(bitplane)
                        i_conj += 1
                        if msg_checker == 0:
                            block_len = int(bitplane, 2)
                            msg_checker += 1
                        else:
                            msg_len = int(bitplane, 2)
                            header += 1
                            break
                header += 1
        print (i_conj)
        print (len(conj_map))
        file_name = file_name.strip('\x00').strip()
        print ('Conjugation idx : {}'.format(conj_map))
        print ('Offset idx : {}'.format(offset))
        print ('File name       : {}'.format(file_name))
        print ('Message usage : {} bitplanes'.format(block_len))
        print ('Message length  : {} B'.format(msg_len))

        bitplanes_used = []
        count = 0
        i = 0
        output = ""
        for no, (bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and i != block_len:
                if count >= header:
                    if conj_map[i_conj] == "1":
                        bitplane = bp.conjugate_bitplane(bitplane)
                    i_conj += 1
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        if (len(output) < msg_len):
                            output += kar
                        j += 8
                    i += 1
                    bitplanes_used.append(no)
                count += 1

        # print('Bitplanes Used For Message:', bitplanes_used)
        if encrypted:
            output = vigenere.decrypt(key, output)
        self.write_byte_string(file_name, output)
        return file_name

    def get_seed(self, key):
        seed = 0
        for c in key:
            seed += ord(c)
        return seed

    def read_byte_string(self, filename):
        plaintext = []
        with open(filename,'rb') as f1:
            while True:
                b = f1.read(1)
                if b:
                    plaintext.append(chr(ord(b)))
                else: break
        return plaintext

    def write_byte_string(self, filename, output):
        list_hex = [hex(ord(c)).split('x')[-1] for c in output]
        for i, c in enumerate(list_hex):
            if len(c) == 1:
                list_hex[i] = '0'+c
        hex_string = ' '.join(list_hex)
        bytes_result = bytes.fromhex(hex_string)
        with open(filename, 'wb') as f:
            f.write(bytes_result)

    def vigenere_encrypt(self, vigenere, input_file):
        """
            Input :
                file name
            Output :
                list of char of byte
        """
        plaintext = []
        with open(input_file,'rb') as f1:
            while True:
                b = f1.read(1)
                if b:
                    plaintext.append(chr(ord(b)))
                else: break
        return (vigenere.encrypt(plaintext))

    def vigenere_decrypt(self, vigenere, encrypted):
        """
            Input :
                list of char of byte [chr(ord(b))]
            Output :
                bytes of file
        """
        result = vigenere.decrypt(encrypted)
        list_hex = [hex(ord(c)).split('x')[-1] for c in result]
        for i, c in enumerate(list_hex):
            if len(c) == 1:
                list_hex[i] = '0'+c
        hex_string = ' '.join(list_hex)
        bytes_result = bytes.fromhex(hex_string)
        with open(savefile, 'wb') as f:
            f.write(bytes_result)


    def calculate_psnr(self, filename_x, filename_y):
        # Precondition: Both files have the same dimensions
        img_x = Image.open(filename_x).convert("RGB")
        img_y = Image.open(filename_y).convert("RGB")
        img_x = np.array(img_x)
        img_y = np.array(img_y)

        row, col, channel = img_x.shape
        sum = [0, 0, 0] # [r, g, b]
        for i in range(row):
            for j in range(col):
                for k in range(len(img_x[i][j])):
                    if img_x[i][j][k] != img_y[i][j][k]:
                        sum[k] += 1

        avg = [x / (row * col) for x in sum]
        rms = [math.sqrt(x) for x in avg]
        psnr = [20 * math.log10(256 / x) for x in rms]
        return np.average(psnr)
