"""Small reference ciphers. No inherited modules or scorers; explicit F positions."""
ALPHABET='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
TOKENS='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def indices(text): return [ALPHABET.index(c) for c in text if c in ALPHABET]
def render(arr): return ''.join(TOKENS[i] for i in arr)
def primes(n):
    out=[];v=2
    while len(out)<n:
        if all(v%d for d in range(2,int(v**0.5)+1)):out.append(v)
        v+=1
    return out
def decode(arr, method='plain',key=(),interrupts=(),drop=False):
    result=[];consumed=0;fseen=0
    sequence=[p-1 for p in primes(len(arr))] if method=='totient' else None
    for c in arr:
        if c==0:fseen+=1
        if c==0 and fseen in interrupts:
            if not drop:result.append(0)
            continue
        if method=='plain':p=c
        elif method=='atbash':p=28-c
        elif method=='atbash_shift3':p=(28-c+3)%29
        elif method=='keyed':p=(c-key[consumed%len(key)])%29
        elif method=='totient':p=(c-sequence[consumed])%29
        else:raise ValueError(method)
        result.append(p);consumed+=1
    return result
