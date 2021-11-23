# **HILL AUXILIAR ENCRYPTION**

# LIBRARIES
import os
from collections import Counter
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
#-------------------------------------------------------------------------------

#AUXILIAR FUNCTIONS

def main():
    # This code outputs the values of the first 10 encoded trygrams and their
    # respective original value. They could be used to build and M matrix and
    # thus the H matrix. Notice that the original file HAS to be known for
    # using this auxiliar.
    with open (ec_path +"/Encrypted3.txt","r",encoding='utf-8-sig') as myfile:
        encrypted = myfile.read()
    ec_trigrams = [encrypted[i:i+3] for i in np.arange(0,len(encrypted)-2,3)]
    with open (ct_path+"/wells_22.txt","r",encoding='utf-8-sig') as myfile:
        clean = myfile.read()
    caps = re.sub("[^a-z]", "", clean, 0, re.IGNORECASE | re.MULTILINE).upper()
    clean_trigrams = [caps[i:i+3] for i in np.arange(0,len(encrypted)-2,3)]
    for i in range (min(10,len(ec_trigrams))):
        print([ord(x)-ll_idx for x in ec_trigrams[i]],"->",[ord(x)-ll_idx for x in clean_trigrams[i]])
main()
