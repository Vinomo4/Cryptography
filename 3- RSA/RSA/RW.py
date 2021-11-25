# **RON WAS WRONG, WHIT IS RIGHT**

# LIBRARIES
from Crypto.PublicKey import RSA
import os
import math
import sympy
#-------------------------------------------------------------------------------
# Filepaths
public_path = "./RSA_RW/" # Folder containing all the public documents from my colleagues.
my_info_path = "./My_info/" # Folder where my public key and encrypted files are stored.
my_private_path = "./My_private_info/" # Folder where my deduced private keys will be stored.
decrypted_path = "./Decrypted/" # Folder where my decrypted files will be stored.
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    # First, I will read my public key.
    with open(my_info_path+"victor.novelle_pubkeyRSA_RW.pem",'r') as f:
        my_public_key = RSA.import_key(f.read())

    # Next, we will iterate through all the other public keys until we find one that shares a factor with mine.
    found = False
    factor1 = 0
    while not found:
        for filename in os.listdir(public_path):
            # Reading only the public keys.
            if filename.split(".")[-1] == "pem":
                with open(public_path+filename,'r') as f:
                    public_key = RSA.import_key(f.read())
                # Computing the GCD between the modules.
                gcd =  math.gcd(public_key.n,my_public_key.n)
                # We share a factor.
                if gcd > 1 and gcd != my_public_key.n:
                    # Its value is stored and the search is stopped.
                    factor1 = gcd
                    found = True

    # The second factor is obtained.
    factor2 = my_public_key.n // factor1

    # Now,  we have e,n,p and q. In order to decript our file, we just need to find d (private exponent) and reverse the steps.

    # First, the selection of the necessary variables from the Public Key is executed.
    publicExponent = my_public_key.e
    modulus = my_public_key.n
    Phimodulus = (factor1-1) * (factor2-1)

    # Then, we compute d.
    privateExponent = int(sympy.gcdex(publicExponent,Phimodulus)[0])
    if privateExponent < 0:
        privateExponent += Phimodulus

    # Now that we have all the components, we can create the private key.
    # Following Crypto.PublicKey.RSA.construct documentation:
    # https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html

    privateKey = RSA.construct((modulus,publicExponent,privateExponent,factor1,factor2))

    with open(my_private_path+"victor.novelle_privkeyRSA_RW.pem",'wb') as f:
        f.write(privateKey.export_key())

    # Now, we proceed to decript the original file, first obtaining the key encrypted with RSA and then decrypting the AES.

    os.system("openssl rsautl -decrypt -in "+my_info_path+"victor.novelle_RSA_RW.enc -out "+decrypted_path+"AES_key_RW.txt -inkey " +my_private_path+"victor.novelle_privkeyRSA_RW.pem")

    os.system("openssl enc -d -aes-128-cbc -pbkdf2 -kfile "+decrypted_path+"AES_key_RW.txt -in "+my_info_path+"victor.novelle_AES_RW.enc -out "+decrypted_path+"/og_file_RW.png")

    print("Files decrypted!")
