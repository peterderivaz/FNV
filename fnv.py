# http://isthe.com/chongo/tech/comp/fnv/

def egcd(a, b):
    """Returns 1/a mod b."""
    x, y, u, v, bb = 0, 1, 1, 0, b
    while b != 0:
        q = a // b
        a, b = b, a % b
        x, u = u - q * x, x
        y, v = v - q * y, y
    return u if u > 0 else u + bb

from collections import defaultdict

def fnv_collision(N=64, mode=0, numsections=8,alt=False):
    """Searches for shortest string with N-bit FNV hash==0.

    Mode=0 means any bytes allowed
    Mode=1 means non-null ascii string [0x01 - 0x7f]
    Mode=2 means printable ascii string = [0x20 - 0x7e]
    Mode=3 means alphanumeric [0x30 - 0x39, 0x41 - 0x5a, 0x60 - 0x7a]

    If numsections is >1 then it splits the search into this many sections.
    This reduces memory use by numsections but increases computation time by numsections"""
    global t
    t=0
    off={32:2166136261,64:14695981039346656037}[N]
    off2=0
    p={32:16777619,64:1099511628211}[N]
    M=2**N
    e=egcd(p,M)
    if alt:
        off=off*e%M
    mask=M-1
    numbytes=2
    go=True
    if mode==0:
        allowed_symbols=range(256)
    elif mode==1:
        allowed_symbols=range(1,0x80)
    elif mode==2:
        allowed_symbols=range(0x20,0x7f)
    elif mode==3:
        allowed_symbols=range(0x30,0x39+1)+range(0x41,0x5a+1)+range(0x60,0x7a+1)
    else:
        raise ValueError
    mask2=numsections-1
    while go:
        numbytes=numbytes+1
        numbytes_minus_1=numbytes-1 # Skip the middle byte as this is inferred
        front=numbytes_minus_1//2 # Build set with this many symbols
        back=numbytes_minus_1-front  # Iterate over this many symbols

        for section in range(numsections):
            if not go: break
            # First generate a set
            print 'Make set',section,numbytes
            S=[p*off%M]
            for s in range(front):
                S2=set()
                for x in allowed_symbols:
                    if s==0 and (x&mask2)!=section: continue
                    print s,front,x,len(S2)
                    for a in S:   
                        y=p*(a^x)&mask
                        if s==(front-1):
                            y2=y>>8
                            #if (y2&mask2)==section:
                            S2.add(y2)
                        else:
                            S2.add(y)
                S=S2
            print front,back,len(S)
            print 'Check back'
            # Now iterate over the back symbols
            Dback=defaultdict(set)
            def f(D,S,symbols,s,n,mult,debug=False):
                global t
                if n==0:
                    y=s>>8
                    if y in S:
                        D[y].add((s,tuple(symbols)))
                        print len(D),s
                    return
                for x in allowed_symbols:
                    if debug:
                        print x
                    y=(mult*(s^x))&mask
                    f(D,S,symbols+[x],y,n-1,mult,False)
            f(Dback,S,[],p*off2%M,back,e,True)
            if not len(Dback): continue
            print numbytes,len(Dback),'found'
            # Now rescan from front and record interesting positions
            Dfront=defaultdict(set)
            f(Dfront,Dback,[],p*off%M,front,p)
            # Now check any answers
            print 'checking...',len(Dfront),len(Dback)
            for a,a_S in Dfront.items():
                b_S = Dback[a]
                for a_s,a_syms in a_S:
                    for b_s,b_syms in b_S:
                        mid=a_s^b_s
                        if mid in allowed_symbols:
                            t+=1
                            print 'sol',t,map(hex,a_syms),hex(mid),map(hex,b_syms[::-1])
                            go=False
import time
t0=time.time()     
fnv_collision(32,0,1)
print time.time()-t0

# non-null ascii string [0x01 - 0x7f]
# printable ascii string = [0x20 - 0x7e]
# alphanumeric [0x30 - 0x39, 0x41 - 0x5a, 0x60 - 0x7a]

# When find a match, may wish to record interesting final values (in D[x>>8]=x, then run first step again
# Or could store all of these in the first step anyway?  Would then allow finer check of any potential matches.
# Could perhaps store stack trace of found byte values?
#
# May want to run in sections i.e. &mask2 == section?
# Takes longer, but less memory
#
# No collisions even with 8 bytes!
#
# In first stage, could use a bloom filter to narrow down possibilities...
# Would be much more memory efficient!
# Can probably handle at most 64 million entries at the moment (=>64 sections for 9 byte test...)
# Probably better to simply cut down the range explored for the first symbol
# Can then do full test on all final symbols, this should make the set generation much faster.

# fnv_collision(64,0,1,alt=True)
# sol 1 ['0xd5', '0x6b', '0xb9'] 0x53L ['0x42', '0x87', '0x8', '0x36']

# fnv_collision(64,0,64)
# 2 hours
# sol 1 ['0xf8', '0x71', '0x2', '0xca'] 0x6cL ['0x6d', '0xa5', '0xae', '0xfc']
# sol 2 ['0x26', '0xec', '0x1b', '0x56'] 0x5eL ['0xb8', '0x5d', '0x5e', '0x39']
# sol 3 ['0x1f', '0x5f', '0xc2', '0xb2'] 0x3bL ['0x75', '0xfb', '0x7c', '0x92']
# sol 4 ['0x58', '0x21', '0xf5', '0xa2'] 0xe1L ['0x1', '0x9d', '0x80', '0xe0']
#
# fnv_collision(64,1,8)
# 10 hours!
# sol 1 ['0x40', '0x61', '0x13', '0x53'] 0x2aL ['0x14', '0x45', '0x2b', '0x40', '0x68']
# sol 2 ['0x10', '0x17', '0x34', '0x7c'] 0x28L ['0x61', '0x38', '0x72', '0x64', '0x4d']
# sol 3 ['0x20', '0x65', '0x5b', '0x68'] 0x4aL ['0x25', '0x9', '0x34', '0x6c', '0x21']
# sol 4 ['0x60', '0x9', '0x50', '0x68'] 0x4bL ['0x21', '0x4f', '0x5b', '0x1f', '0x73']

