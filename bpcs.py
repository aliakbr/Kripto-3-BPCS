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
        threshold=0.3,
        encrypted=True):
        print ("Initialize encryption ...")
        bp = BitPlaneProcessing(threshold)
        vigenere = Vigenere_Ascii()

        # Calculate bitplanes that can be used
        max_bitplanes = bp.calculateMaxDataSize(img_file)
        max_size_conj_map = bp.calculateMaxDataSize(img_file) * 0.1
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
        bin_name = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_file)
        while len(bin_name) % 64 != 0:
            bin_name += dummy_binary
        bin_name += ''.join('{0:08b}'.format(ord(x), 'b') for x in '\x00\x00\x00\x00\x00\x00\x00\x00') # partition as end of file name
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
        if (max_bitplanes - max_size_conj_map) < (msg_blocks_size  + nm_size):
            print ("Your file/filename is too big ... can't embed message")
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
        for idx, (no, bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and (i < msg_blocks_size):
                count += 1
                if count < (max_size_conj_map+2): # 2 bitplane to store conjugation map info
                    # First complex plane is reserved for conjugation map
                    conj_idx.append((no, idx))
                    bitplanes_used.append(no)
                    default_conj_bitplanes.append(bitplane)
                    continue
                else:
                    if nm < nm_size:
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
                    conj_map.append(count)
                encrypted_bitplanes.append((no, encrypted_bitplane))
                bitplanes_used.append(no)
            else:
                encrypted_bitplanes.append((no, bitplane))

        # Creating conjugation map
        print('Creating conjugation map...')
        print ("Conjugation Map : {} bitplane".format(len(conj_map)))
        bin_conj = ''.join('{0:016b}'.format(x, 'b') for x in conj_map)
        while len(bin_conj) % 64 != 0:
            bin_conj += dummy_binary
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
            else:
                if (conj_input_counter < conj_map_len):
                    encrypted_bitplane = ''.join(input_conj[conj_input_counter])
                    conj_input_counter += 1
                else:
                    encrypted_bitplane = default_conj_bitplanes[x]
            encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
            if encrypted_complexity <= bp.alpha_threshold:
                encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
                encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
            encrypted_bitplanes.insert(conj_idx[x][1], (conj_idx[x][0], encrypted_bitplane))

        encrypted_bitplanes.sort(key=lambda x: x[0])
        encrypted_bitplanes = [x[1] for x in encrypted_bitplanes]

        print('Save bitplanes as image...')
        # Save bitplanes as image
        blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
        if cgc:
            reversed_blocks_encrypted = bp.reverse_CGC(blocks_encrypted)
            blocks_encrypted = bp.bitplaneToBlocks(reversed_blocks_encrypted)

        print('Calculate PSNR...')
        bitplanes_after = bp.create_bitplanes(blocks_encrypted)
        bitplanes_after = [bitplane[0] for bitplane in bitplanes_after]
        psnr = bp.calculate_psnr(bitplanes_ori, bitplanes_after)

        print('Accumulate blocks to form image...')
        img_data = bp.blocksToRGBData(blocks_encrypted)
        bp.dataToImage(img_data, output_file)
        return psnr

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
        max_size_conj_map = bp.calculateMaxDataSize(img_file) * 0.1
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
        i = 0
        conj_map = []
        output = ""
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
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.alpha_threshold:
                if header < (max_size_conj_map + 2):
                    if header == 0:
                        # Read block size of conjugation map
                        bitplane = bp.conjugate_bitplane(bitplane)
                        conj_map_block_len = int(bitplane, 2)
                    elif header == 1:
                        # Read size of conjugation map
                        bitplane = bp.conjugate_bitplane(bitplane)
                        conj_map_len = int(bitplane, 2)
                    else:
                        if (conj_map_counter < conj_map_block_len):
                            bitplane = bp.conjugate_bitplane(bitplane)
                            k = 0
                            print (len(bitplane))
                            while (k < len(bitplane)):
                                idx = int(bitplane[k:k+16], 2)
                                if (len(conj_map) < conj_map_len):
                                    conj_map.append(idx)
                                k += 16
                            conj_map_counter += 1
                else:
                    if file_name[-8:] != '\x00\x00\x00\x00\x00\x00\x00\x00':
                        if header in conj_map:
                            bitplane = bp.conjugate_bitplane(bitplane)
                        j = 0
                        while (j < len(bitplane)):
                            kar = chr(int(bitplane[j:j+8], 2))
                            file_name += kar
                            j += 8
                    else:
                        if header in conj_map:
                            bitplane = bp.conjugate_bitplane(bitplane)
                        if msg_checker == 0:
                            block_len = int(bitplane, 2)
                            msg_checker += 1
                        else:
                            msg_len = int(bitplane, 2)
                            header += 1
                            break
                header += 1

        file_name = file_name.strip('\x00').strip()
        count = 0
        print ('Conjugation idx : {}'.format(conj_map))
        print ('File name       : {}'.format(file_name))
        print ('Message usage : {} bitplanes'.format(block_len))
        print ('Message length  : {} B'.format(msg_len))
        bitplanes_used = []
        for no, (bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and i != block_len:
                if count >= header:
                    if count in conj_map:
                        bitplane = bp.conjugate_bitplane(bitplane)
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        if (len(output) < msg_len):
                            output += kar
                        j += 8
                    i += 1
                    bitplanes_used.append(no)
                count += 1

        print('Bitplanes Used For Message:', bitplanes_used)
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
        # array_of_bytes = []
        # with open(filename, 'rb') as f:
        #     byte = f.read(1)
        #     while byte:
        #         array_of_bytes.append(byte)
        #         byte = f.read(1)
        #
        # temp = [int(x[0]) for x in array_of_bytes]
        # return ''.join(chr(x) for x in temp)
        plaintext = []
        with open(filename,'rb') as f1:
            while True:
                b = f1.read(1)
                if b:
                    plaintext.append(chr(ord(b)))
                else: break
        return plaintext

    def write_byte_string(self, filename, output):
        # array_of_bytes = [ord(x) for x in output]
        # with open(filename, 'wb') as f:
        #     f.write(bytearray(array_of_bytes))
        # return output
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
