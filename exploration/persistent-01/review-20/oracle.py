from fractions import Fraction
# Known-plaintext forward event tree. Each terminal includes acceptance or exhaustion.
def forward(plain,previous,key,start=0):
 pending=[(start,Fraction(1),[],[])];out=[]
 while pending:
  j,prob,invalid,repeated=pending.pop()
  if j==len(key):out.append({'output':None,'after':j,'prob':prob,'invalid':invalid,'repeated':repeated});continue
  v=plain^key[j]
  if v>=29:
   pending.append((j+1,prob,invalid+[j],repeated));continue
  if v==previous:
   out.append({'output':v,'after':j+1,'prob':prob*Fraction(17,100),'invalid':invalid,'repeated':repeated})
   pending.append((j+1,prob*Fraction(83,100),invalid,repeated+[j]))
  else:out.append({'output':v,'after':j+1,'prob':prob,'invalid':invalid,'repeated':repeated})
 return out
# Inverse by acceptance-position enumeration; earlier trials must be invalid or repeated.
def inverse(output,previous,key,start=0):
 out=[]
 for a in range(start,len(key)):
  plain=output^key[a]
  if plain>=29:continue
  weight=Fraction(17,100) if output==previous else Fraction(1);invalid=[];repeated=[]
  for j in range(start,a):
   v=plain^key[j]
   if v>=29:invalid.append(j)
   elif v==previous:weight*=Fraction(83,100);repeated.append(j)
   else:break
  else:out.append({'plain':plain,'after':a+1,'prob':weight,'invalid':invalid,'repeated':repeated})
 return out
