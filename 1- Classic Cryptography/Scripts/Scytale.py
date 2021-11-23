# **SCYTALE ENCRYPTION**

# LIBRARIES
import os
from collections import Counter
from math import ceil
import time
#-------------------------------------------------------------------------------
# GLOBAL VARIABLES

# Path of the folder that contains the clean texts.
ct_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Clean texts"
# Path of the folder that contains the encrypted texts.
ec_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Encrypted Text"
# Path of the folder that will contain the decripted files
w_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Decrypted Text"
#-------------------------------------------------------------------------------

# AUXILIAR FUNCTIONS

# Function that writes the decrypted file (with the name read as input) into the
# "decrypted text" folder.
def write_decrypted(filename, dec_txt):
    f = open(w_path+"/"+filename,"w")
    f.write(dec_txt)
    f.close()
#-------------------------------------------------------------------------------
# PRINCIPAL FUNCTIONS

# The reasoning behind this function is the following:
# In order to perform the scytale encoding, the text is written each character
# into a column, making change of row when arriving to the end. Then, the text is
# read column-wise. Thus, if we write the encripted text by columns using the same
# number of rows used for encriptation, we will recover the original matrix and thus,
# reading it row-wise we will retrieve the original message.
def scytale(text,n_rows):
    size = len(text)
    n_cols = size//n_rows
    auxiliar_matrix = [['' for j in range (n_cols)] for i in range (n_rows)]

    txt_idx = 0
    for j in range(n_cols):
        for i in range(n_rows):
            auxiliar_matrix[i][j] = text[txt_idx] # Writting the message column-wise.
            txt_idx += 1
    msg = ""
    for i in range(n_rows):
        for j in range(n_cols):
            msg += auxiliar_matrix[i][j] # Reading the message row-wise.
    return msg

# Function that reads the encrypted text and performs brute-force search on the
# row parameter in ordert to decode an Scytale encrypted file.
def read_and_permute():
    # Firstly, we read the encrypted text file.
    with open (ec_path +"/Encrypted2.txt","r",encoding='utf-8-sig') as myfile:
        encrypted = myfile.read()
    found = False
    i = 1
    while not found:
        pos_dec = scytale(encrypted,i)
        if "Wells" in pos_dec: # Word that appears in all the clean files.
            found = True
        i += 1
    return i-1,pos_dec
#-------------------------------------------------------------------------------
def main():
    start_time = time.time()
    rows,dec_txt = read_and_permute()
    write_decrypted("Scytale.txt",dec_txt)
    print("The number of rows of the Scytale is",rows,".\nThe time of execution has been ","{:.5f}".format(time.time()-start_time)," ms.", sep ="")
    print("The decoded files can be found at the 'Decrypted Text' folder!")
main()
