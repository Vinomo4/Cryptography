# **SECRET KEY CRYPTOGRAPHY**

# LIBRARIES
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
import filetype
#-------------------------------------------------------------------------------

# AUXILIAR FUNCTIONS

def read_data():
    '''
    Function that reads the key and the encrypted files needed to perform this exercice.
    '''
    with open('./Encrypted/2021_09_30_10_54_25_victor.novelle.key','rb') as file:
        key = file.read()
    with open('./Encrypted/2021_09_30_10_54_25_victor.novelle.enc','rb') as file:
        enc1 = file.read()
    with open('./Encrypted/2021_09_30_10_54_25_victor.novelle.puerta_trasera.enc','rb') as file:
        enc2 = file.read()

    return key,enc1,enc2

def write_results(file,filename, kind):
    '''
    Function that stores the decrypted files with the correct name and format.
    '''
    # Path to store the result.
    store_path = "./Decrypted/"
    # Obtaining the file extension.
    ext = "."+ str(kind.extension)
    with open(store_path+filename+ext, "wb") as f:
        f.write(file)
#-------------------------------------------------------------------------------

# MAIN FUNCTIONS

def decrypt_1(key,enc):
    '''
    Function that given a key and an encrypted file, test the different AES operation method
    to decypher it. The first 16 bytes of the file are used as IV if needed.
    '''
    # Selecting the first 128 bits as nonce from the encripted text.
    iv = enc[:16]
    # List of all the different operation methods for AES.
    modes = [AES.MODE_ECB,AES.MODE_CBC,AES.MODE_CFB,AES.MODE_OFB]
    mode_names = ["ECB","CBC","CFB","OFB"]
    for i,mode in enumerate(modes):
        if i != 0:
            cipher = AES.new(key,mode,iv)
        else: cipher = AES.new(key,mode)
        # Decrypting with the selected method.
        plaintext = cipher.decrypt(enc[16:])
        # Testing if the decrypted file has some known extension.
        kind = filetype.guess(plaintext)
        # Testing if the decrypted text has some file structure.
        if kind is not None:
             # Unpadding the file.
            try:
                plaintext = unpad(plaintext,16)
            except ValueError:
                pass
            else:
                print("-"*10+"SECTION 1"+"-"*10)
                print("The file has been decrypted with " +str(mode_names[i]) +" operation mode and has ."+str(kind.extension)+" extension.")
                print("The file can be found in the Decrypted folder.")
                write_results(plaintext,"test_"+str(mode_names[i]),kind)
                break

def decrypt_2(enc):
    '''
    Function that given an encrypted file using AES in CBC mode,
    performs brute search to find the key. Notice that this brute search is
    pruned as we have information about the procedure for the key generation.
    '''
    # As for all the characters used in the K_i their initial bit is 0, we have to test 2^14 values.
    # First, we generate al the 2^7 bit combinations.
    for i in range(128):
        for j in range(128):
            preMasterKey = i.to_bytes(1,"big")*8 + j.to_bytes(1,"big")*8
            H = SHA256.new(data = preMasterKey).digest()
            # The first 128 bits of H are the AES key and the laters the initial IV vector.
            cipher = AES.new(H[:16],AES.MODE_CBC,H[16:])
            plaintext = cipher.decrypt(enc)
            kind = filetype.guess(plaintext)
            # Testing if the decrypted text has some file structure.
            if kind is not None:
                 # Unpadding the file.
                try:
                    plaintext = unpad(plaintext,16)
                except ValueError:
                    pass
                else:
                    print("-"*10+"SECTION 2"+"-"*10)
                    print("The file has been decrypted with 0x" +str(H[:16].hex()) +" as key and 0x"+str(H[16:].hex())+" IV vector.")
                    print("The file can be found in the Decrypted folder.")
                    write_results(plaintext,"backdoor",kind)
                    break
        else:
            continue
        break

def main():
    key,enc1,enc2 = read_data()
    decrypt_1(key,enc1)
    decrypt_2(enc2)
main()
