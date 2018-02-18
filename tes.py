# from bitplane import BitPlaneProcessing
#
# bp = BitPlaneProcessing()
# # a = bp.getBinArrayTrueColor("tes.jpg")
# # sliced_a = bp.sliceToBlocks(a)
# # bit_planes = []
# # for a in sliced_a:
# #     for i in range(24):
# #         bit_planes.append(bp.generateBitplaneArray(a, i))
# #
# # bit_planes_comp = []
# # for bit_plane in bit_planes:
# #     bit_planes_comp.append((bit_plane, bp.calculateComplexity(bit_plane)))
# #
# # print (bit_planes_comp)
# print (bp.calculateMaxDataSize("tes.jpg"))

## Inserting
from bpcs import BPCS
##
alg = BPCS()
alg.encrypt("gray.png", "inp.txt", "output.png", sequential=False)
print("===output===")
print(alg.decrypt("output.png", sequential=False))
# Create bitplanes of image img_file
#from PIL import Image
#import numpy as np
#from bitplane import BitPlaneProcessing
#img_file = "tes.jpg"
#input_file = "input.txt"
#output_file = "output.png"
#output_file1 = "output1.png"
#bp = BitPlaneProcessing()
#img_bin_ar = bp.getBinArrayTrueColor(img_file)
#blocks = bp.sliceToBlocks(img_bin_ar)
#img = Image.open(img_file)
#imgArray = np.array(img)
#r, g ,b = imgArray[0][0]
#r = int(r)
#g = int(g)
#b = int(b)
#col1 = (r,g,b)
#a = blocks[0][0]
#r = int(a[:8], 2)
#g = int(a[8:16], 2)
#b = int(a[16:24], 2)
#col = (r, g, b)
#b = []
#for i in range(8):
#    for j in range(8):
#        b.append(img_bin_ar[i][j])
#
#bitplanes_comp = []
#bitplanes = []
#for block in blocks:
#    for i in range(24):
#        bitplane = bp.generateBitplaneArray(block, i)
#        complexity = bp.calculateComplexity(bitplane)
#        bitplanes_comp.append((bitplane, complexity))
#        bitplanes.append(bitplane)
#
#blocks_1 = bp.bitplaneToBlocks(bitplanes)
#img_data = bp.blocksToRGBData(blocks_1)
#img_data1 = bp.blocksToRGBData(blocks)
#bp.dataToImage(img_data, output_file)
#bp.dataToImage(img_data, output_file1)
#
#img = Image.open(output_file1)
#imgArray = np.array(img)
#img_bin_ar1 = bp.getBinArrayTrueColor(output_file)
#img_bin_ar2 = bp.getBinArrayTrueColor(output_file1)
#blocks = bp.sliceToBlocks(img_bin_ar)
#bitplanes_comp1 = []
#bitplanes1 = []
#for block in blocks:
#    for i in range(24):
#        bitplane = bp.generateBitplaneArray(block, i)
#        complexity = bp.calculateComplexity(bitplane)
#        bitplanes_comp1.append((bitplane, complexity))
#        bitplanes1.append(bitplane)
#
#
#
## Split input into 8x8 blocks
#with open(input_file, "r") as f:
#    input_text = f.read()
#bin_input = ''.join('{0:08b}'.format(ord(x), 'b') for x in input_text)
#dummy_binary = "00001010"
#while len(bin_input) % 64 != 0:
#    bin_input += dummy_binary
#input_blocks = bp.sliceStringToBlocks(bin_input)
#msg_size = len(input_blocks)
#
## Inserting message
#encrypted_bitplanes = []
#i = 0
#count = 0
#for bitplane, complexity in bitplanes_comp:
#    if complexity > bp.ALPHA_TRESHOLD and (i < msg_size):
#        if count == 0:
#            # Change first bit plane to save message length
#            encrypted_bitplane = ''.join('{0:064b}'.format(msg_size))
#            count += 1
#        else:
#            encrypted_bitplane = ''.join(input_blocks[i])
#            i += 1
#        encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
#        if encrypted_complexity <= bp.ALPHA_TRESHOLD:
#            encrypted_bitplane = bp.conjugate_bitplane(encrypted_bitplane)
#            encrypted_complexity = bp.calculateComplexity(encrypted_bitplane)
#        encrypted_bitplanes.append(encrypted_bitplane)
#    else:
#        encrypted_bitplanes.append(bitplane)
#
## Save bitplanes as image
#blocks_encrypted = bp.bitplaneToBlocks(encrypted_bitplanes)
#img_data = bp.blocksToRGBData(blocks_encrypted)
#bp.dataToImage(img_data, output_file)
