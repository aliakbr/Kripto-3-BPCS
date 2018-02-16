"""
    Script for extended ascii vigenere
"""

def padd_key(key, seq_input):
    """
        Input :
            key : Key of the vigenere algorithm
            plaintext : list of bytes/char
        Output :
            padded key as sequence of bytes
    """
    pad_len = len(seq_input) - len(key)
    j = 0  #index of key
    output = [c for c in key]
    for i in range(pad_len):
        output += key[j]
        j += 1
        if (j == len(key)):
            j = 0
    return output

class Vigenere_Ascii:
    """
        Vigenere Ascii Class
    """
    def encrypt(self, key, plaintext):
        """
            This function will return ciphertext of the plain ascii Text in char
            Input : Sequence of ASCII bytes
            output : Encrypted sequence of ascii bytes in char
        """
        output = []
        padded_key = padd_key(key, plaintext)
        for i in range(len(plaintext)):
            enc_ascii = (ord(plaintext[i]) + ord(padded_key[i])) % 256
            output.append(chr(enc_ascii))
        return output


    def decrypt(self, key, encrypted):
        """
            This function will return decrypted text
            Input :
                key : Key string
                encrypted_txt : encrypted string
            Output :
                decrypted string
        """
        output = []
        padded_key = padd_key(key, encrypted)
        for i in range(len(encrypted)):
            dec_ascii = (ord(encrypted[i]) - ord(padded_key[i])) % 256
            output.append(chr(dec_ascii))
        return output
