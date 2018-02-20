from bpcs import BPCS

alg = BPCS()
treshold=0.4
alg.encrypt("testcase/lena.bmp", "testcase/frootlyrics.txt", "output.bmp", sequential=False, threshold=treshold)
print("===output===")
print(alg.decrypt("output.bmp", sequential=False, threshold=treshold))
