from bpcs import BPCS

alg = BPCS()
treshold=0.5
a = alg.encrypt("testcase/lena.bmp", "testcase/apple.png", "output1.bmp", sequential=True, threshold=treshold)
if (a != False):
    print("===output===")
    print(alg.decrypt("output1.bmp", sequential=True, threshold=treshold))
