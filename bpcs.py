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

        # Calculate bitplanes used for conjugation map
        num_bitplanes = bp.calculateMaxDataSize(img_file)
        num_conj_map = bp.calculateMaxDataSize(img_file) * 0.1

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
        bin_name = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_file)
        while len(bin_name) % 64 != 0:
            bin_name += dummy_binary
        bin_name += ''.join('{0:08b}'.format(ord(x), 'b') for x in '\x00\x00\x00\x00\x00\x00\x00\x00') # partition as end of file name
        input_name = bp.sliceStringToBlocks(bin_name)
        nm_size = len(input_name)

        input_text = self.read_byte_string(input_file)
        input_text = vigenere.encrypt(key, input_text)
        msg_size = len(input_text)
        bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
        while len(bin_input) % 64 != 0:
            bin_input += dummy_binary
        input_blocks = bp.sliceStringToBlocks(bin_input)
        msg_blocks_size = len(input_blocks)

        # Inserting message
        encrypted_bitplanes = []
        conj_map = ['abc']
        conj_idx = []
        i = -2
        nm = 0
        count = -1

        for idx, (bitplane, complexity) in enumerate(bitplanes_comp):
            bitplanes_comp[idx] = (idx, bitplane, complexity)

        if not sequential:
            random.seed(self.get_seed(key))
            random.shuffle(bitplanes_comp)

        bitplanes_used = []
        bitplanes_used_msg = []
        for idx, (no, bitplane, complexity) in enumerate(bitplanes_comp):
            if complexity > bp.alpha_threshold and (i < msg_blocks_size):
                count += 1
                if count <= 2:
                    # First complex plane is reserved for conjugation map
                    conj_idx.append((no, idx))
                    bitplanes_used.append(no)
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
                    encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
                    conj_map.append(chr(count+97))
                encrypted_bitplanes.append((no, encrypted_bitplane))
                bitplanes_used.append(no)
            else:
                encrypted_bitplanes.append((no, bitplane))

        print('Bitplanes Used:', bitplanes_used)
        print('Bitplanes Used For Message:', bitplanes_used_msg)
        str_conj = '/'.join(conj_map)
        bin_conj = ''.join('{0:08b}'.format(ord(x), 'b') for x in str_conj)
        while len(bin_conj) % 64 != 0:
            bin_conj += dummy_binary
        input_conj = bp.sliceStringToBlocks(bin_conj)
        while len(input_conj) < 3:
            input_conj.append(''.join(['00000000'] * 8))

        # Insert conjugation map bitplanes
        for x in range(len(conj_idx)):
            encrypted_bitplane = bp.conjugate_bitplane(''.join(input_conj[x]))
            encrypted_bitplanes.insert(conj_idx[x][1], (conj_idx[x][0], encrypted_bitplane))

        encrypted_bitplanes.sort(key=lambda x: x[0])
        encrypted_bitplanes = [x[1] for x in encrypted_bitplanes]

        # Save bitplanes as image
        blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
        if cgc:
            reversed_blocks_encrypted = bp.reverse_CGC(blocks_encrypted)
            blocks_encrypted = bp.bitplaneToBlocks(reversed_blocks_encrypted)
            
        bitplanes_after = bp.create_bitplanes(blocks_encrypted)
        bitplanes_after = [bitplane[0] for bitplane in bitplanes_after]
        psnr = bp.calculate_psnr(bitplanes_ori, bitplanes_after)
        print(psnr)
            
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

        msg_checker = 0
        for bitplane, complexity in bitplanes_comp:
            if complexity > bp.alpha_threshold:
                if header <= 2:
                    bitplane = bp.conjugate_bitplane(bitplane)
                    j = 0
                    while (j < len(bitplane)):
                        kar = chr(int(bitplane[j:j+8], 2))
                        if (ord(kar)-97) >= 0:
                            conj_map.append(ord(kar)-97)
                        j += 8
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
        print ('Bitplane used : {}'.format(block_len))
        print ('Message length  : {}'.format(msg_len))
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
