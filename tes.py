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

# Inserting
from bpcs import BPCS

alg = BPCS()
alg.encrypt("tes.jpg", "input.txt")
