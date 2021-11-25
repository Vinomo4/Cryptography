# **PSEUDO RSA**

# LIBRARIES
from Crypto.PublicKey import RSA
import os
import math
import sympy
#-------------------------------------------------------------------------------
# Filepaths
my_info_path = "./My_info/" # Folder where my public key and encrypted files are stored.
my_private_path = "./My_private_info/" # Folder where my deduced private keys will be stored.
decrypted_path = "./Decrypted/" # Folder where my decrypted files will be stored.
#-------------------------------------------------------------------------------

def second_degree(a,b,c):
    '''
    Objective:
        - Find the solutions of a second degree polynomic equation.
    Input:
        - a,b,c: coefficients of the equation
    Output:
        - The two results (integers).
    '''
    inside_sqrt = b**2 - 4*a*c
    res1 = (-b + math.isqrt(inside_sqrt))//(2*a)
    res2 = (-b - math.isqrt(inside_sqrt)) //(2*a)
    return res1,res2


def main():
    # First, I will read my public key.
    with open(my_info_path+"victor.novelle_pubkeyRSA_pseudo.pem",'r') as f:
        my_public_key = RSA.import_key(f.read())

    # Extract the modulus.
    modulus = my_public_key.n

    # Then,we obtain the number of bits and extract B.
    block_size = modulus.bit_length()//4

    B = int(bin(modulus)[3*block_size +2:],2)
    carry = 0

    found = False

    # rxs and r+s computation.
    while not found:
        A = int(bin(modulus)[2:block_size+2],2)
        A -= carry # We substract de carry-
        C = int(bin(modulus)[block_size+2:3*block_size+2],2)
        C += (1<<(2*block_size))*carry # And add it to the middle section.
        AB = rs = (A << block_size) + B # rs
        BA = (B << block_size) + A
        # Finding r + s
        r_s =  math.isqrt(C-BA+2*AB)
        if r_s**2 == C-BA+2*AB: found = True
        else: carry+= 1
        assert carry < 3

    # Now we can solve the second degree equation.
    r,s = second_degree(1,-r_s,rs)

    # Now, we can compute p and q and thus, decrypt the files.

    p = (r << block_size) + s
    q = (s << block_size) + r

    # First, the selection of the necessary variables from the Public Key is executed.
    publicExponent = my_public_key.e
    modulus = my_public_key.n
    Phimodulus = (p-1) * (q-1)

    # Then, we compute d.
    privateExponent = int(sympy.gcdex(publicExponent,Phimodulus)[0])
    if privateExponent < 0:
        privateExponent += Phimodulus

    # Now that we have all the components, we can create the private key.
    # Following Crypto.PublicKey.RSA.construct documentation:
    # https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html

    privateKey = RSA.construct((modulus,publicExponent,privateExponent,p,q))

    with open(my_private_path+"victor.novelle_privkeyRSA_pseudo.pem",'wb') as f:
        f.write(privateKey.export_key())

    # Now, we proceed to decript the original file, first obtaining the key encrypted with RSA and then decrypting the AES.

    os.system("openssl rsautl -decrypt -in "+my_info_path+"victor.novelle_RSA_pseudo.enc -out "+decrypted_path+"/AES_key_pseudo.txt -inkey "+my_private_path+"victor.novelle_privkeyRSA_pseudo.pem")

    os.system("openssl enc -d -aes-128-cbc -pbkdf2 -kfile "+decrypted_path+"/AES_key_pseudo.txt -in "+my_info_path+"victor.novelle_AES_pseudo.enc -out "+decrypted_path+"/og_file_pseudo.jpeg")

    print("Files decrypted!")

main()
