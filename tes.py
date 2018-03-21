from bpcs import BPCS

alg = BPCS()
treshold=0.3
a = alg.encrypt("testcase/lena.bmp", "testcase/tes1.txt", "output1.bmp", sequential=False, threshold=treshold)
if (a != False):
    print("===output===")
    print(alg.decrypt("output1.bmp", sequential=False, threshold=treshold))
