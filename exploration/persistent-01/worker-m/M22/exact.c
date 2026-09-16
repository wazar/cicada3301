#include <math.h>
#include <stdint.h>
// exact state=(consumed key phase,last two LM tokens); fixed length score denominator
// At most3*900 states. Sparse active lists avoid full-state work per rune.
double fixed(const int *c,const int *ends,int n,const int *key,int period,const double *lm){
 double a[2700],b[2700];int ai[2700],bi[2700],an=1,bn;for(int i=0;i<2700;i++){a[i]=-INFINITY;b[i]=-INFINITY;}a[899]=0;ai[0]=899;
 for(int i=0;i<n;i++){
  bn=0;
  for(int t=0;t<an;t++){
   int state=ai[t],phase=state/900,ctx=state%900,last=ctx%30;
   for(int literal=0;literal<=(c[i]==0);literal++){
    int r=literal?0:(c[i]-key[phase]+29)%29;int nextphase=literal?phase:(phase+1)%period;
    double val=a[state]+lm[ctx*30+r];int nextctx=last*30+r;
    if(ends[i]){val+=lm[nextctx*30+29];nextctx=r*30+29;}
    int ns=nextphase*900+nextctx;if(b[ns]==-INFINITY)bi[bn++]=ns;if(val>b[ns])b[ns]=val;
   }
  }
  for(int t=0;t<an;t++)a[ai[t]]=-INFINITY;
  for(int t=0;t<bn;t++){int s=bi[t];a[s]=b[s];b[s]=-INFINITY;ai[t]=s;}an=bn;
 }
 double best=-INFINITY;for(int t=0;t<an;t++)if(a[ai[t]]>best)best=a[ai[t]];
 int denom=n;for(int i=0;i<n;i++)denom+=ends[i];return best/denom;
}
void scan(const int*c,const int*ends,int n,int period,const double*lm,double*out){int count=1;for(int i=0;i<period;i++)count*=29;for(int code=0;code<count;code++){int key[3],x=code;for(int j=period-1;j>=0;j--){key[j]=x%29;x/=29;}out[code]=fixed(c,ends,n,key,period,lm);}}
