import sympy
import hashlib
from ecpy.curves import Curve,Point

Qx = 0xe8502cd0d24ea2b192aab6730fcfa0b457e5c2c07cae6e55914aa69467faa5f8
Qy = 0xb03f46ac2352b4483b6464fbeacde9e4fb8f10a7f4e823ba95296eefca72bb83
signature = 0x30450220289fd4913d2387e36533ee782f4a8e2119541c263ca9b52be308874fccbc718402210081d3ab3d7bc402ef7cd93c65224f25db2689939dd2d0f0d26ffc2ced5b8f43ed
f1 = 0x289fd4913d2387e36533ee782f4a8e2119541c263ca9b52be308874fccbc7184
f2 = 0x0081d3ab3d7bc402ef7cd93c65224f25db2689939dd2d0f0d26ffc2ced5b8f43ed

# P-256
curve = Curve.get_curve('secp256r1')
G = curve.generator
wikipedia_publickey = Point(Qx,Qy,curve)
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b


def check_point(x,y):
    return pow(y,2,p) == (pow(x,3,p) - 3*x + b)%p


# a) comprobar que el orden es un numero primo.
print("The order of the curve is prime" if sympy.isprime(n) else "The order of the curve isn't prime")

# b) Comprobando que la clave publica es un punto de la curva.
print("The public key is a point of the curve" if check_point(Qx,Qy) else "The public key isn't a point of the curve")
# This can also be checked using the following line.
#print("The public key is a point of the curve" if curve.is_on_curve(wikipedia_publickey)else "The public key isn't a point of the curve")

# c) Calcular el orden del punto P.

# Hecho con Suge Math. Fotografia en el discord canal Cripto.

# d) Comprobar firma

# Construccion del mensaje

preamble = 64*'20' +''.join(format(ord(c),'x') for c in 'TLS 1.3, server CertificateVerify')+'00'

with open("./Message/message.bin","rb") as f:
    message384 = hashlib.sha384(f.read())
message = preamble+message384.hexdigest()
message = hashlib.sha256(bytes.fromhex(message)).hexdigest()

print("The message is:",message)

# Converting the message to numeric.
message = int(message,16)

# Verificacion del mensaje
w1 = message * pow(f2,-1,n) % n
w2 = f1 * pow(f2,-1,n) % n

E = w1 * G + w2 * wikipedia_publickey

print("The signature is verifified" if E.x == f1 else "The signature isn't verified")
