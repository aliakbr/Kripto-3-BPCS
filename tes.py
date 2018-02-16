from bitplane import BitPlaneProcessing

bp_processor = BitPlaneProcessing()
a = bp_processor.getBinArrayTrueColor("tes.jpg")
sliced_a = bp_processor.sliceToBlocks(a)
bit_plane_array = []
for a in sliced_a:
    for i in range(24):
        bit_plane_array.append(bp_processor.generateBitplaneArray(a, i))
print (bit_plane_array[0])
