#include <cmath>
#include <random>
#include <algorithm>
#include <cstdint>
extern "C" {
double objective(const int* C,const int* g,const double* lf){
 int tab[289]={0},rows[17]={0};double em=0;
 for(int x=0;x<29;x++)for(int y=0;y<29;y++){int n=C[x*29+y];if(!n)continue;int a=g[x],b=g[y];tab[a*17+b]+=n;rows[a]+=n;if(b<12)em+=n*std::log(a!=b?.5:(x==y?.085:.915));}
 double s=em;for(int a=0;a<17;a++){s+=lf[16]-lf[rows[a]+16];for(int b=0;b<17;b++)s+=lf[tab[a*17+b]];}return s;
}
void fit(const int*C,unsigned long long seed,int*out,double*scores,long long*counts){
 int n=0;for(int i=0;i<841;i++)n+=C[i];double*lf=new double[n+18];for(int i=0;i<n+18;i++)lf[i]=std::lgamma(i+1.0);std::mt19937_64 rng(seed);std::uniform_real_distribution<double> u(0,1);std::uniform_int_distribution<int> pick(0,28);
 for(int s=0;s<4;s++){int g[29],best[29];for(int i=0;i<24;i++)g[i]=i/2;for(int i=24;i<29;i++)g[i]=12+i-24;std::shuffle(g,g+29,rng);double cur=objective(C,g,lf),top=cur;std::copy(g,g+29,best);long long valid=0,accepted=0;
 for(int t=0;t<1500;t++){int a=pick(rng),b=pick(rng);if(g[a]==g[b])continue;valid++;std::swap(g[a],g[b]);double v=objective(C,g,lf),temp=2*std::pow(.01,t/1499.);if(v>=cur||u(rng)<std::exp((v-cur)/temp)){cur=v;accepted++;if(v>top){top=v;std::copy(g,g+29,best);}}else std::swap(g[a],g[b]);}
 std::copy(best,best+29,out+s*29);scores[s]=top;counts[2*s]=valid;counts[2*s+1]=accepted;
 }delete[]lf;
}
}
