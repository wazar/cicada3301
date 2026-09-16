import os,sys,json,random,time,hashlib,importlib.util,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'liber-primus'))
import verify_solution as oracle
sk=oracle.sk
# Fresh authored prose: fixture independent of inherited solved text and plants.
TEXT=('A SMALL BOAT WAS WAITING BY THE RIVER WHEN THE CHILDREN CAME DOWN FROM THE HOUSE. '
'THEY CARRIED BREAD AND WATER FOR THE LONG JOURNEY THROUGH THE HILLS. THE OLD MAN TOLD THEM '
'TO FOLLOW THE PATH UNTIL THEY FOUND A BRIDGE AND THEN TO TURN TOWARDS THE MORNING SUN. '
'AT NIGHT THEY SAT BESIDE THE FIRE AND SPOKE ABOUT THE FRIENDS THEY HAD LEFT BEHIND. ')
TOKENS=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
def encode(t):
    t=t.upper().replace('V','U').replace('K','C').replace('Q','C').replace('Z','S'); out=[]
    while t:
        tok=next((s for s in sorted(TOKENS,key=len,reverse=True) if t.startswith(s)),None)
        if tok is None:
            if t[0].isalpha(): raise ValueError(t)
            t=t[1:];continue
        out.append(TOKENS.index(tok)); t=t[len(tok):]
    return out

def encrypt(p,key,seed,supp=.83,step=1,start=0):
    rng=random.Random(seed); c=[]; used=[]; j=start
    for x in p:
        while True:
            y=(x+key[j])%29
            if c and y==c[-1] and rng.random()<supp: j+=step
            else: break
        c.append(y);used.append(j);j+=1
    return c,used,j

def handchecks():
    assert encrypt([2,3,4],[1,0,2,5,8,9],1,1) == ([3,5,9],[0,2,3],4)
    assert encrypt([2,3,4],[1,0,2,5,8,9],1,1,2) == ([3,8,12],[0,3,4],5)
    assert encrypt([28,1],[2,28],1,0) == ([1,0],[0,1],2)
    assert encode('FUTHORC')==[0,1,2,3,4,5]
    assert encode(TEXT)==sk.eng_to_idx(TEXT)
    return True

def select(cs,key,truth=None):
    rows=[]
    for page,c in enumerate(cs):
        choices=[]
        for mode in ['rigid','beam']:
            for sign in [-1,1]:
                d=(sk.rigid_decode(c,key,sign=sign,o=0) if mode=='rigid' else sk.beam_decode(c,key,sign=sign,o=0,beam_w=400,max_skip=3))
                r={'mode':mode,'sign':sign,'score':d['score']}
                if truth is not None:
                    p=truth[page];r.update(recovery=sum(a==b for a,b in zip(p,d['plain_idx']))/len(p),exact=d['plain_idx']==p,alignment_length=len(d['plain_idx']))
                choices.append(r)
        rows.append({'page':page,'choices':choices,'best':max(choices,key=lambda r:r['score'])})
    scores=[r['best']['score'] for r in rows]
    return {'rows':rows,'best':max(scores),'second':sorted(scores,reverse=True)[1],'english_accept':sum(s>=-5.5 for s in scores)>=2}

def plant(L,seed,construction='reset',register='english'):
    p=encode(TEXT if register=='english' else ''.join(c for c in TEXT if c not in 'AEIOU'))
    p=(p*5); ps=[p[:L],p[L:2*L]]
    rng=random.Random(seed);key=[rng.randrange(29) for _ in range(2048)]
    cs=[];uses=[];start=0
    for i,pg in enumerate(ps):
        c,u,end=encrypt(pg,key,seed+10000+i,step=2 if construction=='skip2' else 1,start=start)
        cs.append(c);uses.append(u)
        if construction=='continuous':start=end
    return ps,key,cs,uses

def pilot():
    t=time.monotonic();handchecks(); rows=[]
    for L in [60,120]:
        p,k,c,u=plant(L,51001)
        for label,key in [('correct',k),('wrong',[random.Random(8+i).randrange(29) for i in range(2048)])]:
            s=time.monotonic();rows.append({'L':L,'label':label,'elapsed':time.monotonic()-s,'result':select(c,key,p)})
            rows[-1]['elapsed']=time.monotonic()-s
    return {'handchecks':True,'elapsed':time.monotonic()-t,'rows':rows}
if __name__=='__main__':
    result=pilot();(OUT/'pilot.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
