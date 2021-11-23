# **GF(256)**

# LIBRARIES
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from prettytable import PrettyTable

import csv
#-------------------------------------------------------------------------------
# GLOBAL VARIABLES

# Module polynomial
global m
m = 0b100011101
# AES Module
#m = 0b100011011
# G^1 = x
global x
x = 2
#AES generator
#x = 3
# Aesthetic for plots
plt.style.use("ggplot")
#-------------------------------------------------------------------------------

#AUXILIAR FUNCTIONS

def multiply_by_x(B):
    '''
    Function that mutiplies by our g^1 = x.
    '''
    aux = B << 1
    if aux > 255:
        aux = aux ^ m
    return aux

def execute_tests():
    '''
    Function that ensures that none of the lab notes constraints are violated.
    '''
    # Inverse test.
    assert sum([GF_product_t(i,GF_invers(i)) != 1 for i in range(1,256)]) != 255, "The product of an element with its inverse is not 1."
    # Different multiplication functions test.
    for i in range(1,256):
        for j in range(1,256):
            if GF_product_t(i,j) != GF_product_p(i,j): raise Exception("The table and polynomial multiplication functions" \
            "provide a different result for the same (a,b) pair.")
    # Commutative property.
    for pair in combinations(range(1,256),2):
        if(GF_product_p(pair[0], pair[1]) != GF_product_p(pair[1],pair[0]) or
            GF_product_t(pair[0], pair[1]) != GF_product_t(pair[1],pair[0])): raise Exception("The multiplication is "\
            "not commutative.")
    print("All the tests have been passed!")

def write_test_results(results,extra):
    '''
    Function that stores the obtained results from the ET tests.
    '''
    if not extra:
        folder = "ET_factors/"
        header = ["Factor","GF_product_t ET", "GF_product_p ET"]
        filename = "Time_comparison_factors"
    elif extra == 1:
        folder = "ET_ones/"
        header = ["Number of ones","GF_product_t ET", "GF_product_p ET"]
        filename = "Time_comparison_ones"
        xlab = "Number of ones"
    elif extra == 2:
        folder = "ET_real/"
        header = ["Number of multiplications","GF_product_t ET", "GF_product_p ET"]
        filename = "Time_comparison_real_setup"
        xlab = "Number of multiplications"
    # 1. TXT file with a table.
    x = PrettyTable()
    # Adding the information to the table and writing into a file.
    x.field_names = header
    x.add_rows(results)
    with open('./Outputs/'+folder+filename+'.txt', 'w') as f:
        f.write(str(x))
    # 2. CSV file
    with open('./Outputs/'+folder+filename+'.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(header)
        # Write multiple rows
        writer.writerows(results)
    # 3. PLOT
    if extra > 0:
        t_times = [x[1]*1000 for x in results]
        p_times = [x[2]*1000 for x in results]
        if extra == 1:
            plt.plot(range(17),t_times,label = "GF_product_t")
            plt.plot(range(17),p_times,label = "GF_product_p")
        elif extra == 2:
            plt.plot([1] + list(range(50,1001,50)),t_times,label = "GF_product_t")
            plt.plot([1] + list(range(50,1001,50)),p_times,label = "GF_product_p")
        plt.xlabel(xlab)
        plt.ylabel('Execution time (ms)')
        plt.title('Comparison of ET')
        plt.legend()
        plt.savefig("./Outputs/"+folder+filename+".png",bbox_inches = "tight")
        plt.close()
#-------------------------------------------------------------------------------

# MAIN FUNCTIONS

def GF_product_p(a,b):
    '''
    Function that performs the polynomial multiplication between two given integers
    from GF(256).
    '''
    # First, we check if one of both integers is 0.
    if not a or not b:
        return 0
    # We check if one of the values is the neutral element of the multiplication.
    if a == 1 or b == 1: return max(a,b)
    # First, we initialize our auxiliary value  as a[0]*b.
    aux = a%2*b
    # Then, we iterate for the a bits. If we found one = 1, we perform the polinomial multiplication
    # which consists in applying the multiplication_by_x function as many times as the bit index.
    for i in range(1,8):
        a = a >> 1
        if a%2:
            temp_result = b
            for j in range(i):
                temp_result = multiply_by_x(temp_result)
            aux = aux ^ temp_result
    return aux

def generate_exp_table():
    '''
    Function that generates the 255 numbers different from 0 present on GF(256) using
    the powers of the provided generator.
    '''
    # First, we create an empty table that will be filled.
    exp_table = [0 for i in range(255)]
    exp_table[0] = 1
    exp_table[1] = x
    # Then, we compute the powers.
    for i in range(2,255):
        exp_table[i] = GF_product_p(x,exp_table[i-1])
    return exp_table

def generate_log_table(exp):
    '''
    Function that generates the loarithmic table. In this table, each position
    (which represents an integer of the GF(256) saves the power to which the generator
    has to be raised to achieve that value.
    '''
    log_table = [0 for i in range(255)]
    for i in range(1,256):
        log_table[i-1] = exp.index(i)
    return log_table

def generate_tables():
    '''
    Function that generates both the exponential and logarithmic table and computes their creation time.
    This values are stored as global variables
    '''
    start_time = time.time()
    global exp
    exp = generate_exp_table()
    global log
    log = generate_log_table(exp)
    global time_tables
    time_tables = time.time() - start_time


def GF_product_t(a,b):
    '''
    Function that performs the product between two GF(256) elements using table lookups.
    '''
    # First, we check if one of both integers is 0.
    if not a or not b:
        return 0
    # We check if one of the values is the neutral element of the multiplication.
    if a == 1 or b == 1: return max(a,b)
    # We extract the corresponding exponent of the values.
    t_idx_a = log[a-1]
    t_idx_b = log[b-1]
    # As its a multiplication of g^i*g^j, the result is g^(i+j). As we are in GF(256),we must not forget to compute the module.
    res_idx = (t_idx_a+t_idx_b)%255
    # Lastly, we obtain the final value elevating the generator to the corresponding index using the table.
    return exp[res_idx]

def GF_invers(a):
    '''
    Function that returns the inverse element from the input one on the GF(256).
    '''
    # First we check if the value is 0.
    if not a: return 0
    # We obtain the index to which we have to elevate the generator to obtain the integer.
    t_idx_a = log[a-1]
    # Then, applying the inverse in a GF(256) field only consists in obtaing the value from the
    # exponential table located in the 254-i positon.
    return exp[(255-t_idx_a)%255]


def GF_es_generador(a):
    '''
    Function that checks if the provided integer is a generator of a GF(256).
    '''
    if not a or a == 1: return False
    pos_gen_table = [0 for i in range(255)]
    pos_gen_table[0] = 1
    pos_gen_table[1] = a
    for i in range(2,255):
        pos_gen_table[i] = GF_product_p(a,pos_gen_table[i-1])
    # In order to check that a is a generator in the GF(256), all its different powers
    # module m should be different. To obtain the number of different values, we will use a set.
    if  len(set(pos_gen_table))!= len(pos_gen_table): return False
    # All the powers are different!..
    return True

def time_evaluation_extra_2():
    '''
    Function that compares the performance of the polynomial multiplication against
    the table multiplication. For this extra test, multiple random multiplications are
    perfomed and the execution time depending on the number of products is computed.
    '''
    rows = []
    # Now, we create all the possible pairs of multiplications than can be performed.
    pairs = list(combinations(range(1,256),2))
    # Then, we will select k pairs and perform the multiplications.
    for k in range(0,1001,50):
        if not k : k = 1
        # Selecting the k random multiplications to perform.
        mults = random.choices(pairs,k = k)
        aux_t = []
        aux_p = []
        # To obtain a more reliable value, 1000 function calls will be perfomed and afterwards averaged.
        for i in range(1000):
            t_time = time.time()
            for pair in mults:
                GF_product_t(pair[0],pair[1])
            aux_t.append(time.time() - t_time)
            p_time = time.time()
            for pair in mults:
                GF_product_p(pair[0],pair[1])
            aux_p.append(time.time()-p_time)
        rows.append([str(k),time_tables+np.mean(aux_t),np.mean(aux_p)])
    print("Finished ET test 3")
    write_test_results(rows,2)

def time_evaluation_extra():
    '''
    Function that compares the performance of the polynomial multiplication against
    the table multiplication. For this extra test, the perfomance is compared depending on the number of bits equal to one
    in both elements.
    '''
    rows = []
    # Now, we create all the possible pairs of multiplications than can be performed.
    times_p = [0 for i in range(17)]
    times_t = [0 for i in range(17)]
    num_op= [0 for i in range(17)]
    for a in range(256):
        for b in range(256):
            # Computing the number of ones in the multiplication.
            idx = bin(a)[2:].count('1')+ bin(b)[2:].count('1')
            aux_p = []
            aux_t = []
            for i in range(100):
                t_time = time.time()
                GF_product_t(a,b)
                aux_t.append(time.time()-t_time)
                p_time = time.time()
                GF_product_p(a,b)
                aux_p.append(time.time() - p_time)
            times_t[idx] += np.mean(aux_t)
            times_p[idx] += np.mean(aux_p)
            num_op[idx] +=1
    for i in range(17):
        rows.append([str(i),times_t[i] / num_op[i],times_p[i] / num_op[i]])
    print("Finished ET test 2")
    write_test_results(rows,1)

def time_evaluation():
    '''
    Function that compares the performance of the polynomial multiplication against
    the table multiplication. The tests performed are the ones provided in the lecture notes.
    '''
    # Values to multiplicate.
    multis = [0x02, 0x03, 0x09, 0x0B, 0x0D, 0x0E]
    rows = []
    for mult in multis:
        aux_t = []
        aux_p = []
        # All the "a" values are multiplied and then added.
        for a in range(256):
            aux_2_t = []
            aux_2_p = []
            # To obtain a more reliable value, 1000 function calls will be performed and afterwards averaged.
            for i in range(1000):
                t_time = time.time()
                GF_product_t(a,mult)
                aux_2_t.append(time.time()-t_time)
                p_time = time.time()
                GF_product_p(a,mult)
                aux_2_p.append(time.time()-p_time)
            aux_t.append(np.mean(aux_2_t))
            aux_p.append(np.mean(aux_2_p))
        rows.append([hex(mult),sum(aux_t),sum(aux_p)])
    print("Finished ET test 1")
    write_test_results(rows, 0)


def main():
    # We execute the function in order to obtain the global values.
    generate_tables()
    execute_tests()
    time_evaluation()
    time_evaluation_extra()
    time_evaluation_extra_2()
main()
