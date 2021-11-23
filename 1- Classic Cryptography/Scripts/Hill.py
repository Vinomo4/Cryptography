# **HILL ENCRYPTION**

# LIBRARIES
import os
from collections import Counter
import math
from sympy import *
import time
import re
import numpy as np
#-------------------------------------------------------------------------------
# GLOBAL VARIABLES

# Index of the smallest alphabetic character present in our original text.
# In this case, the "A" character.
ll_idx = ord('A')
#-------------------------------------
# Path of the folder that contains the clean texts.
ct_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Clean texts"
# Path of the folder that contains the encrypted texts.
ec_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Encrypted Text"
# Path of the folder that will contain the decrypted files
w_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Decrypted Text"
# Path of the folder that contains the auxiliar files.
aux_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Auxiliar"
#-------------------------------------------------------------------------------

# AUXILIAR FUNCTIONS

# Function that checks if a Matrix has inverse module 26.
def check_inverse(matrix):
    return math.gcd(matrix.det(),26) == 1
#-------------------------------------
# Function that converts a given string into a list with their respective
# letter indexes.
def convert_to_numbers(string):
    return [ord(c) - ll_idx for c in string]
#-------------------------------------
#Function that converts a given list of integers into their respective string.
def convert_to_letters(l_num):
    return ''.join(chr(ll_idx + x) for x in l_num)
#-------------------------------------
# Function that compares a decoded text among all the original files, checking
# if is equal to one of them, returning the respective index in that case or
# "-1" otherwise
def comparison (dec_txt_prototype):
    for idx,filename in enumerate(sorted(os.listdir(ct_path))):
        with open (ct_path+"/"+filename,"r",encoding='utf-8-sig') as clean_file:
            cf_text = clean_file.read().upper()
        cf_text = re.sub("[^a-z]", "", cf_text, 0, re.IGNORECASE | re.MULTILINE).upper()
        if dec_txt_prototype == cf_text: return idx+1
    return -1
#-------------------------------------
# Function that writes the decrypted file (with the name read as input) into the
# "decrypted text" folder.
def write_decrypted(filename, dec_txt):
    f = open(w_path+"/"+filename,"w")
    f.write(dec_txt)
    f.close()
#-------------------------------------
'''
#Function that given the 3 most common trigrams of our text, generates te 3
# column vectors necessary for obtaining the parameters of the H matrix.
def generate_evaluation_vects(mf_trig):
    s = len(mf_trig)
    return [[mf_trig[0][i],mf_trig[1][i],mf_trig[2][i]] for i in range(s)]
'''
#-------------------------------------------------------------------------------
# PRINCIPAL FUNCTIONS
def decode(h_matrix,ec_trig):
    # In order to decode our original message, we only need to invert the H
    # matrix and multiply our encripted message splitting the text every 3 chars.
    h_matrix_inv = h_matrix.inv_mod(26)
    dc_trigrams = [h_matrix_inv*Matrix(x)%26 for x in ec_trig]
    dc_trigrams = [convert_to_letters(list(x)) for x in dc_trigrams]
    return ''.join(dc_trigrams)
#-------------------------------------
def hill(mf_trig,eng_trig,ec_trig):
    # In order to perform the decypering operation, we need to try the most
    # frequent english trigrams untill we find a matrix that it's invertible
    # mod 26. Once its found, we can compute the values of the parameters of
    # the Hill matrix.Then, if it's invertible, we can decyper the text that is
    # provided as input.
    s = len(eng_trig)
    ec_trig = [convert_to_numbers(x) for x in ec_trig]
    '''
    mf_trig = [convert_to_numbers(x) for x in mf_trig]
    ev_list = generate_evaluation_vects(mf_trig)
    '''
    ev_list = [[23,1,14],[19,8,5],[10,25,24]]
    for i in range(s):
        for j in range(i+1,s):
            for k in range(j+1,s):
                tested_tri = [convert_to_numbers(eng_trig[i]),convert_to_numbers(eng_trig[j]),convert_to_numbers(eng_trig[k])]
                tested_m = Matrix(tested_tri)
                if check_inverse(tested_m):
                    tested_m_inv = tested_m.inv_mod(26)
                    parameters = [(tested_m_inv*Matrix(x)%26).tolist() for x in ev_list]
                    parameters = Matrix([[e[0] for e in c] for c in parameters])
                    if check_inverse(parameters):
                        dec_txt_prototype = decode(parameters,ec_trig)
                        pos_idx  = comparison(dec_txt_prototype)
                        if pos_idx != -1:
                            return pos_idx, dec_txt_prototype
#-------------------------------------
def main():
    with open (ec_path +"/a.txt","r",encoding='utf-8-sig') as myfile:
        encrypted = myfile.read()
    # First, we wil obtain all the trigrams present on our text.
    ec_trig = [encrypted[i:i+3] for i in np.arange(0,len(encrypted)-2,3)]
    # Next we will compute the frequency of each trigram in order to obtain the 3 most common ones.
    ec_trig_freq = sorted(list(Counter(ec_trig).items()), key = lambda x: -x[1])
    mf_trig = ec_trig[:3]
    # Then, we will load the most frequent English trigrams.
    with open (aux_path +"/ENG_trigrams_mod.txt","r",encoding='utf-8-sig') as myfile:
        eng_trig = myfile.read().replace("\n","").split(",")
    # And now, we find the values of the coefficients used in the encoding.
    og_idx,dec_txt = hill(mf_trig,eng_trig,ec_trig)
    write_decrypted("Hill.txt",dec_txt)
    print("The Index of the original file is",og_idx)
    print("The decoded files can be found at the 'Decrypted Text' folder!")
main()
