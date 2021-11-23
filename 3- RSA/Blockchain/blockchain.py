# **BLOCKCHAIN**

# LIBRARIES
import sympy
import math
import random
import hashlib
import pickle
import time
import numpy as np
from prettytable import PrettyTable
import csv
#-------------------------------------------------------------------------------
# Filepaths
generated_path = "./Chains/" # Folder where the generated blockchains will be stored.
test_path =  "./Test/" # Folder where the files provided for testing the code are stored.
time_path = "./Time comparisons/" # Folder where the time tables will be stored.
#-------------------------------------------------------------------------------

class rsa_key:
    def __init__(self,bits_modulo=2048,e=2**16+1):
        '''
        Genera una clau RSA (de 2048 bits i amb exponent públic 2**16+1 per defecte)
        '''

        # Number of bits that p and q should have.
        self.num_bits = bits_modulo//2

        self.publicExponent = e # e
        self.primeP = self.find_prime(first = False) # p
        self.primeQ = self.find_prime(first = True) # q
        self.modulus = (self.primeP) * (self.primeQ) # n
        self.Phimodulus = (self.primeP-1) * (self.primeQ-1)

        # To find the private exponent, we will use the Bezout's identity.

        self.privateExponent = int(sympy.gcdex(self.publicExponent,self.Phimodulus)[0]) # d
        if self.privateExponent < 0:
            self.privateExponent += self.Phimodulus

        self.privateExponentModulusPhiP = self.privateExponent % (self.primeP-1) # d mod (p-1)
        self.privateExponentModulusPhiQ = self.privateExponent % (self.primeQ-1) # d mod (q-1)

        self.inverseQModulusP = int(sympy.gcdex(self.primeQ,self.primeP)[0]) # q'
        self.q_qapos = self.primeQ * self.inverseQModulusP # q*q'


    def find_prime(self, first):
        '''
        Objective:
            - Find a random prime number (p) of 1024 bits that gcd(p-1,e) = 1.
        Input
            - first: Boolean indicating wheather the number we are searching is the first of
                     the two prime factors used by RSA.
        Output:
            - The prime itself.
        '''
        # Establishing the upper and lower limits for the search.
        upp_lim = 2**self.num_bits-1
        low_lim = 2**(self.num_bits-1)+1
        while True:
            # First we select a random prime between 2^1023 +1 and 2^1024 -1
            aux_p = sympy.randprime(low_lim,upp_lim)
            # Then, we check if the possible p value minus 1 and e are co-primes.
            if math.gcd(aux_p-1,self.publicExponent) == 1:
                # We found a correct p value and the search is stopped.
                if (first and aux_p != self.primeP) or not first : return aux_p

    def sign(self,message):
        '''
        retorma un enter que és la signatura de "message" feta amb la clau RSA fent servir el TXR
        '''
        # For this signature, we will use Fermat's little theorem to speed up things.
        # m^d mod(n) = m^dp mod(p) * q*q' + m^dq mod(q) * p*p'
        message_p = message % self.primeP
        message_q = message % self.primeQ
        first_term = pow(message_p, self.privateExponentModulusPhiP, self.primeP)
        second_term = pow(message_q, self.privateExponentModulusPhiQ, self.primeQ)
        return first_term * self.q_qapos + second_term * (1-self.q_qapos)

    def sign_slow(self,message):
        '''
        retorma un enter que és la signatura de "message" feta amb la clau RSA sense fer servir el TXR
        '''
        return pow(message,self.privateExponent,self.modulus)


class rsa_public_key:
    def __init__(self, rsa_key):
        '''
        genera la clau pública RSA asociada a la clau RSA "rsa_key"
        '''
        self.publicExponent = rsa_key.publicExponent
        self.modulus = rsa_key.modulus
    def verify(self, message, signature):
        '''
        retorna el booleà True si "signature" es correspon amb una
        signatura de "message" feta amb la clau RSA associada a la clau
        pública RSA.
        En qualsevol altre cas retorma el booleà False
        '''
        return pow(signature,self.publicExponent,self.modulus) == message

class transaction:
    def __init__(self, message, RSAkey):
        '''
        genera una transacció signant "message" amb la clau "RSAkey"
        '''
        self.public_key = rsa_public_key(RSAkey)
        self.message = message
        self.signature = RSAkey.sign(message)
    def verify(self):
        '''
        retorna el booleà True si "signature" es correspon amb una
        signatura de "message" feta amb la clau pública "public_key".
        En qualsevol altre cas retorma el booleà False
        '''
        return self.public_key.verify(self.message,self.signature)


def check_hash(hash):
    '''
    Function that checks if a hash fulfils the requested condition.
    '''
    return hash < 2**240

def compute_hash(block,seed):
    '''
    Function that computes a possible hash for a block.
    It may not be valid.
    '''
    input = str(block.previous_block_hash)
    input = input+str(block.transaction.public_key.publicExponent)
    input = input+str(block.transaction.public_key.modulus)
    input = input+str(block.transaction.message)
    input = input+str(block.transaction.signature)
    input = input+str(seed)
    h=int(hashlib.sha256(input.encode()).hexdigest(),16)
    return h

def find_valid_hash(block):
    '''
    Function that modifies the seed value until finding a correct hash value.
    '''
    found = False
    while not found:
        seed = random.randint(0,2**256)
        h = compute_hash(block,seed)
        if check_hash(h): found = True
    return seed,h

class block:
    def __init__(self):
        '''
        crea un bloc (no necesàriament vàlid)
        '''
        # The initialitzation in this case is not relevant.
        self.block_hash = None
        self.previous_block_hash = None
        self.transaction = None
        self.seed = None

    def genesis(self,transaction):
        '''
        genera el primer bloc d’una cadena amb la transacció "transaction" que es caracteritza per:
        - previous_block_hash=0
        - ser vàlid
        '''
        assert transaction.verify() == True
        self.transaction = transaction
        self.previous_block_hash = 0
        # This function finds both the block hash and the seed parameters.
        self.seed,self.block_hash = find_valid_hash(self)
        return self

    def next_block(self, transaction):
        '''
        genera el següent block vàlid amb la transacció "transaction"
        '''
        # Ensuring the provided transaction is valid.
        assert transaction.verify() == True
        # In this function, an existent block computes the next one.
        # First, we create a new block, initializing the parameters properly.
        new_b = block()
        new_b.previous_block_hash = self.block_hash
        new_b.transaction = transaction
        new_b.seed, new_b.block_hash = find_valid_hash(new_b)
        return new_b

    def verify_block(self):
        '''
        Verifica si un bloc és vàlid:
        -Comprova que el hash del bloc anterior cumpleix las condicions exigides
        -Comprova la transacció del bloc és vàlida
        -Comprova que el hash del bloc cumpleix las condicions exigides
        Si totes les comprovacions són correctes retorna el booleà True.
        En qualsevol altre cas retorma el booleà False
        '''
        # Conditions for a block to not be valid.
        # Invalid transaction
        if not self.transaction.verify():
            print("Invalid transaction")
            return False
        # The block hash is different from the one obtained by computing the value or
        # the hash value is > 2**240.
        if compute_hash(self,self.seed) != self.block_hash or not check_hash(self.block_hash):
            print("Invalid seed")
            return False
        # The previous block hash exceeds 2**240.
        if not check_hash(self.previous_block_hash):
            print("Hash doesn't fulfill the 'proof of work' condition")
            return False
        # All the conditions are fulfiled.
        return True

class block_chain:
    def __init__(self,transaction):
        '''
        genera una cadena de blocs que és una llista de blocs,
        el primer bloc és un bloc "genesis" generat amb la transacció "transaction"
        '''
        self.list_of_blocks = [block().genesis(transaction)]
    def add_block(self,transaction):
        '''
        afegeix a la llista de blocs un nou bloc vàlid generat amb la transacció "transaction"
        '''
        block = self.list_of_blocks[-1].next_block(transaction)
        self.list_of_blocks.append(block)

    def verify(self):
        '''
        verifica si la cadena de blocs és vàlida:
        - Comprova que tots el blocs són vàlids
        - Comprova que el primer bloc és un bloc "genesis"
        - Comprova que per cada bloc de la cadena el següent és el correcte
        Si totes les comprovacions són correctes retorna el booleà True.
        En qualsevol altre cas retorma el booleà False i fins a quin bloc la cadena és válida
        '''
        gen = self.list_of_blocks[0]
        if gen.previous_block_hash != 0 or not gen.verify_block():
            print("Genesis rejected")
            return False,0
        for i in range(1,len(self.list_of_blocks)):
            b = self.list_of_blocks[i]
            if not b.verify_block():
                print("Verification rejected")
                return False,i

            if i != len(self.list_of_blocks)-1:
                if self.list_of_blocks[i].block_hash != self.list_of_blocks[i+1].previous_block_hash:
                    print("Chain assertion rejected")
                    return False, i
        return True,None

def generate_block_chain(n_blocks, n_valid_blocks,file):
    '''
    Generates a random blockchain with the specified
    n_blocks and stores the object in the file path.
    Input:
        -n_blocks: Number of total blocks of the chain.
        -n_valid_blocks: Number of valid blocks of the chain.
        - file: Filepath where the chain will be stored +
                name of the file.
    '''
    rsa = rsa_key()
    trans = transaction(random.randint(0,2**256),rsa)
    blck_ch = block_chain(trans)
    for i in range(n_valid_blocks-1):
        print(i+1)
        rsa = rsa_key()
        trans = transaction(random.randint(0,2**256),rsa)
        blck_ch.add_block(trans)

    # Ensuring that the generated blockchain is correct.
    assert blck_ch.verify() == True
    print("Correct block chain")

    file += ".pickle"
    with open(file, 'wb') as file:
        pickle.dump(blck_ch, file)

def read_blockchain(filename):
    '''
    Reads a .pickle file that contains a blockchain.
    '''
    with open(filename, 'rb') as f:
        blockchain = pickle.load(f)
    return blockchain

def generate_time_table(filename):
    '''
    Function that evaluates the time difference between using slow vs. fast signature in RSA.
    '''
    header = ["Key length (bits)","Without CRT (s)","With CRT (s)"] # Header of the table.
    rows = [] # List where the execution times will be stored.
    for i in range(4):
        bits = 512*(2**i) # Number of bits of the modulo.
        rsa = rsa_key(bits_modulo = bits)
        # Generating the messages.
        messages = [random.getrandbits(256) for _ in range(100)]
        for j in range(10):
            aux_time_slow = []
            aux_time_fast = []
            time_i = time.time()
            for message in messages:
                rsa.sign_slow(message)
            time_f = time.time()
            for message in messages:
                rsa.sign(message)
            aux_time_fast.append(time.time()-time_f)
            aux_time_slow.append(time_f - time_i)
        rows.append([str(bits),round(np.mean(aux_time_slow),4),round(np.mean(aux_time_fast),4)])
    # Creating the table
    table = PrettyTable()
    # Adding the column names
    table.field_names = header
    # Adding rows to the table
    table.add_rows(rows)
    # Writing in .txt format.
    with open(time_path+filename+'.txt', 'w') as f:
        f.write("Average execution time to sign 100 messages")
        f.write(str(table))
    # Writing in .csv format
    with open(time_path+filename+'.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(header)
        # Write multiple rows
        writer.writerows(rows)
    # Printing in terminal
    print("Average execution time to sign 100 messages:")
    print(str(table))

def main():
    #generate_block_chain(100,100,generated_path + "valid_blockchain")
    generate_time_table("timetable")
main()
