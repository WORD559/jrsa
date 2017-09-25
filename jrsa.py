##Basic RSA implementation in Python
#Quite slow, especially for the very large keys, but it works
#UPDATE: Not as slow! Now uses Chinese Remainder Theorem to speed up decryption
#        Also uses exponentiation by squaring to speed up encryption
#        Generating two primes and all the maths that goes with making your keys
#is still pretty slow, though. I need a faster way to do that.
#Drastic speedup by using miller-rabin primality test!
#Apparently it doesn't work properly when the keys get huge.

import random
import decimal

def is_prime(num,tests=10):
    if num == 1:
        return (num,False)
    if num % 2 == 0:
        return (num,False)
    for i in range(tests):
        if pow(random.randrange(1,num),(num-1),num) != 1:
            return (num,False)
    return (num,True)

def millerrabin(num,tests=10,threshold=1,fermat=False):
    if num == 1:
        return (num,False)
    if (num == 2) or (num==3):
        return (num,True)
    if num % 2 == 0:
        return (num,False)
    def test(num,s,d,fermat):
        a = random.randrange(2,num-1)
        test = pow(a,d,num)
        if test == 1:
            return True
        else:
            for i in range(s):
                test = pow(a,(2**i)*d,num)
                if test == num-1:
                    return True
            if fermat:
                if pow(a,num-1,num) == 1:
                    return True
        return False
    d = num-1
    s = 0
    
    while d%2 == 0:
        s+=1
        d>>=1
    prime = 0.
    for _ in range(tests):
        if test(num,s,d,fermat):
            prime += 1
    return (num,prime/tests >= threshold)
    
    
    
def gcd(x,y):
    while y:
        x,y = y, x%y
    return x
    
def random_prime(lower,upper,tests=10,threshold=1):
    count = 1
    num = random.randrange(lower,upper+1)
    if num % 2 == 0:
        num+=1
    print "Testing "+str(count)
    #num, prime = is_prime(num,tests)
    num,prime = millerrabin(num,tests,threshold)
    while not prime:
        count += 1
        print "Testing "+str(count)
        #num, prime = is_prime(num+2,tests)#is_prime(random.randrange(lower,upper+1),tests)
        num,prime = millerrabin(num+2,tests)
    print "Prime found!",num
    return num
    
def generate_keypair(lower,upper,tests=10,threshold=1,set_primes=None,chinese=True,use_Decimal=True):
    if isinstance(set_primes,(list,tuple)) and len(set_primes) == 2:
        p,q = set_primes
    else:
        p,q = random_prime(lower,upper,tests,threshold),random_prime(lower,upper,tests,threshold)
    n = p*q
    m = (p-1)*(q-1)
    e = 3
    while gcd(e,m) != 1:
        e+=1
    i = 1
    test = (1 + 1*m)%e
    d = (1 + 1*m)/e
    while test != 0:
        i+=1
        test = (1 + i*m)%e
        d = (1 + i*m)/e
    if not chinese:
        return ({"e":e,"n":n},{"e":int(d),"n":n})
    if not use_Decimal:
        dp = d%(p-1)
        dq = d%(q-1)
        qinv = (q**(-1)) % p
    else:
        tp = decimal.Decimal(p)
        tq = decimal.Decimal(q)
        dp = d%(p-1)
        dq = d%(q-1)
        qinv = (tq**(-1)) % tp
    return ({"e":e,"n":n},{"e":int(d),"n":n,"p":p,"q":q,"dp":int(dp),
                           "dq":int(dq),"qinv":qinv})
    
def encrypt(number,public):
    return pow(number,public["e"],public["n"])
    
def decrypt(number,private):
    return pow(number,public["e"],public["n"])

def chinese_decrypt(number,private,squares=True):
    if squares:
        m1 = square_method(number,private["dp"],private["p"])
    else:
        m1 = number**private["dp"] % private["p"]
    print "Got m1"
    if squares:
        m2 = square_method(number,private["dq"],private["q"])
    else:
        m2 = number**private["dq"] % private["q"]
    print "Got m2"
    h = (private["qinv"]*(m1-m2)) % private["p"]
    print "Got h"
    return int(m2+h*private["q"])

def square_encrypt(number,key):
    binary = bin(key["e"])[2:]
    powers = []
    for k in range(1,len(binary)+1):
        if binary[-k] == "1":
            powers.append(k-1)
    vals = [number]
    for k in range(1,powers[-1]+1):
        vals.append((vals[-1]*vals[-1])%key["n"])
    x = 1
    for val in range(len(vals)):
        if val in powers:
            x*=vals[val]
    return x%key["n"]

def square_method(number,exponent,n):
    binary = bin(exponent)[2:]
    powers = []
    for k in range(1,len(binary)+1):
        if binary[-k] == "1":
            powers.append(k-1)
    vals = [number]
    for k in range(1,powers[-1]+1):
        vals.append((vals[-1]*vals[-1])%n)
    x = 1
    for val in range(len(vals)):
        if val in powers:
            x*=vals[val]
    return x%n
