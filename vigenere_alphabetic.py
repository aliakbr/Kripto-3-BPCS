"""
    Script for alphabetic vigenere
"""
import re

ASCII_BASE = 97

def is_alphabet(character):
    """
        Return true if the character is alphabet in lowercase
        and return false otherwise
    """
    return (ord(character) >= 97 and ord(character) <= 122)

def padd_key(key, plaintext):
    """
        Input :
            key : Key of the vigenere algorithm
            plaintext : Plain Text
        Output :
            string of padded key
    """
    pad_len = len(plaintext) - len(key)
    j = 0  #index of plain_text
    i = 0 #index of key
    output = ""
    while j < len(plaintext):
        if is_alphabet(plaintext[j]):
            output += key[i]
            i += 1
            if (i == len(key)):
                i = 0
        j += 1
    return output


class Vigenere_Cypher:
    """
        Vigenere Alphabetic Class
    """
    def encrypt(self, key, plaintext):
        """
            This function will return ciphertext of the plain Text
            Input :
                key : Key string
                plaintext : Plain Text
            Output :
                string of encrypted string
        """
        output = ""
        plaintext = re.sub(r'[^a-zA-Z]',r'', plaintext)
        key = key.lower()
        plaintext = plaintext.lower()
        padded_key = padd_key(key, plaintext)
        for i in range(len(plaintext)):
            enc_ascii = ((ord(plaintext[i]) + ord(padded_key[i]) - 2*ASCII_BASE) % 26) + ASCII_BASE
            output += chr(enc_ascii)
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
        output = ""
        encrypted = re.sub(r'[^a-zA-Z]',r'', encrypted)
        encrypted = encrypted.lower()
        key = key.lower()
        padded_key = padd_key(key, encrypted)
        for i in range(len(encrypted)):
            dec_ascii = ((ord(encrypted[i]) - ord(padded_key[i])) % 26) + ASCII_BASE
            output += chr(dec_ascii)
        return output
