from bpcs import BPCS

alg = BPCS()
treshold=0.5
alg.encrypt("testcase/lena.bmp", "testcase/tes1.txt", "output1.bmp", sequential=True, threshold=treshold)
print("===output===")
print(alg.decrypt("output1.bmp", sequential=True, threshold=treshold))
