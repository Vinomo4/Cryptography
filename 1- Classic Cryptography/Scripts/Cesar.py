# **CESAR ENCRYPTION**

# LIBRARIES
import os
from collections import Counter
import time
#-------------------------------------------------------------------------------
# GLOBAL VARIABLES

# Index of the smallest alphabetic character present in our original text.
# In this case, the "A" character.
ll_idx = ord('A')
#-------------------------------------
# Index of the smallest alphanumeric character present in our original text.
# In this case, the last originally encoded English character.
ul_idx = 127
#-------------------------------------
# Path of the folder that contains the clean texts.
ct_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Clean texts"
# Path of the folder that contains the encrypted texts.
ec_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Encrypted Text"
# Path of the folder that will contain the decrypted files
w_path = "/home/vinomo/Desktop/Q7/Cripto/Lab 1/Decrypted Text"
#-------------------------------------------------------------------------------

#AUXILIAR FUNCTIONS

# Function that reads the encrypted file and calculates the necessary shift to
# restablish all the characters to alphanumeric characters.
def read_and_shift():
    # Firstly, we read the encrypted text file.
    with open (ec_path +"/Encrypted1.txt","r",encoding='utf-8-sig') as myfile:
        encrypted = myfile.read()

    # Afterwards, we will compute the maximum value of a character in the text and the minimum in order to obtain the shift.
    min_val = float('inf')
    max_val = 0

    for character in encrypted:
        c_val = ord(character)
        if c_val > ul_idx:
            min_val = min(c_val,min_val)
            max_val = max(c_val,max_val)

    # Once those values are found, the necessary shift is computed.
    shift = (min_val-ll_idx)

    return encrypted,shift
#-------------------------------------
# Function that shifts the alphabetic characters "key" positions, as well as
# shifts them.
def substitution (text,key,shift, type):
    if type == 1:
        return ''.join(
            chr((ord(char) - ll_idx - key - shift) % 26 + ll_idx) if ord(char) > ul_idx else char
            for char in text)
    else:
        return ''.join(
            chr((ord(char) - ll_idx - key - shift) % 26 + ll_idx) if char.isalpha() else char
            for char in text)

#-------------------------------------
# Function that compares a decoded text among all the original files, checking
# if is equal to one of them, returning the respective index in that case or
# "-1" otherwise
def comparison (dec_txt_prototype):
    for idx,filename in enumerate(sorted(os.listdir(ct_path))):
        with open (ct_path+"/"+filename,"r",encoding='utf-8-sig') as clean_file:
            cf_text = clean_file.read().upper() + "\n"
        if dec_txt_prototype == cf_text: return idx+1
    return -1
#-------------------------------------
# Function that writes the decrypted file (with the name read as input) into the
# "decrypted text" folder.
def write_decrypted(filename, dec_txt):
    f = open(w_path+"/"+filename,"w")
    f.write(dec_txt)
    f.close()
#-------------------------------------------------------------------------------
# PRINCIPAL FUNCTIONS

# Function that using brute force (tries all the possible values for the key),
# in this case [0,25], finds the index of the clean text that matches the
# encrypted one and returns the decrypted text.
def brute_force():
    encrypted,shift = read_and_shift()
    for key in range(26):
        pos_dec_txt = substitution(encrypted,key,shift,1)
        pos_idx = comparison(pos_dec_txt)
        if pos_idx != -1: return pos_idx, pos_dec_txt
    return -1,"No matching text was found" # Nimport timeo original text matches the encrypted one (For our case, this cannot happen)
#-------------------------------------
def stat_mthd():
    #First, the shift to the alphabetical characters is performed.
    encrypted,shift = read_and_shift()
    shifted_txt = substitution(encrypted,0,shift,1)
    # The frequency of the characters in the encrypted file is computed.
    ec_txt_freq = sorted(list(Counter(shifted_txt).items()), key = lambda x: -x[1])
    # Then, the frequency of each alphabetical character is computed for each of
    # the clean files.
    for idx,filename in enumerate(sorted(os.listdir(ct_path))):
        with open (ct_path+"/"+filename,"r",encoding='utf-8-sig') as clean_file:
            cf_txt = clean_file.read().upper() + "\n"
        cf_txt_freq = sorted(list(Counter(cf_txt).items()), key = lambda x: -x[1])
        # Now, we compare both histograms to find two files with the same
        # character frequency. When found, the key is computed focusing on the
        # most common character of the encrypted file.
        if all (a[1] == b[1] for a,b in zip(ec_txt_freq,cf_txt_freq)):
            aux = 0
            while not ec_txt_freq[aux][0].isalpha(): aux+=1
            most_common_ec = ec_txt_freq[aux][0]
            for letter,_ in cf_txt_freq:
                # We try the keys but following the most frequent order.
                if letter.isalpha():
                    key = ord(most_common_ec) - ord(letter)
                    pos_dec_txt = substitution(shifted_txt,key,0,2)
                    if pos_dec_txt == cf_txt: return idx+1, pos_dec_txt
    return -1,"No matching text was found"
#-------------------------------------------------------------------------------
def main():
    method = int(input("Please select the desired method: 1- Brute force 2- Statistical \n"))
    start_time = time.time()
    if method == 1:
        og_idx, dec_txt = brute_force()
        write_decrypted("Cesar_Brute_Force.txt",dec_txt)
    else:
        og_idx, dec_txt = stat_mthd()
        write_decrypted("Cesar_Statistical.txt",dec_txt)
    print("The Index of the original file is ",og_idx,".\nThe time of execution has been ","{:.5f}".format(time.time()-start_time)," ms.", sep ="")
    print("The decoded files can be found at the 'Decrypted Text' folder!")
main()
