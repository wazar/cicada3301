#include <algorithm>
#include <array>
#include <cmath>
#include <ctime>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <numeric>
#include <random>
#include <vector>
using namespace std;
vector<double> lm; vector<int> tokens; array<vector<int>,29> positions;
int mapped(int i,const array<int,29>&m){return i<0?29:(tokens[i]==29?29:m[tokens[i]]);}
double term(int i,const array<int,29>&m){return lm[(mapped(i-2,m)*30+mapped(i-1,m))*30+mapped(i,m)];}
double score(const array<int,29>&m){double s=0;for(int i=0;i<(int)tokens.size();i++)s+=term(i,m);return s;}
vector<int> affected(int a,int b){vector<int> v;for(int c:{a,b})for(int p:positions[c])for(int i=p;i<min(p+3,(int)tokens.size());i++)v.push_back(i);sort(v.begin(),v.end());v.erase(unique(v.begin(),v.end()),v.end());return v;}
double delta(array<int,29>&m,int a,int b,const vector<int>&v){double d=0;for(int i:v)d-=term(i,m);swap(m[a],m[b]);for(int i:v)d+=term(i,m);swap(m[a],m[b]);return d;}
void arr(const array<int,29>&m){cout<<"[";for(int i=0;i<29;i++){if(i)cout<<",";cout<<m[i];}cout<<"]";}
int main(int argc,char**argv){
 ifstream mod(argv[1],ios::binary);lm.resize(27000);mod.read((char*)lm.data(),27000*sizeof(double));if(mod.gcount()!=27000*sizeof(double))return 3;
 ifstream in(argv[2]);int n;unsigned long long seed;time_t deadline;in>>n>>seed>>deadline;array<int,29> freq;for(int&i:freq)in>>i;tokens.resize(n);for(int&i:tokens)in>>i;for(int i=0;i<n;i++)if(tokens[i]!=29)positions[tokens[i]].push_back(i);
 mt19937_64 rng(seed);uniform_real_distribution<double> unif(0.,1.);uniform_int_distribution<int> pick29(0,28),pick28(0,27);array<array<vector<int>,29>,29> aff;for(int a=0;a<29;a++)for(int b=a+1;b<29;b++)aff[a][b]=affected(a,b);
 cout<<setprecision(17)<<"{\"seed\":"<<seed<<",\"probes\":[";
 for(int t=0;t<32;t++){array<int,29> m; iota(m.begin(),m.end(),0);shuffle(m.begin(),m.end(),rng);int a=pick29(rng),b=pick28(rng);if(b>=a)b++;if(a>b)swap(a,b);double old=score(m),d=delta(m,a,b,aff[a][b]);if(t)cout<<",";cout<<"{\"map\":";arr(m);cout<<",\"a\":"<<a<<",\"b\":"<<b<<",\"before\":"<<old<<",\"delta\":"<<d;swap(m[a],m[b]);double after=score(m);if(abs(after-old-d)>1e-8)return 4;cout<<",\"after\":"<<after<<"}";}
 cout<<"],\"restarts\":[";
 for(int r=0;r<24;r++){
  if(time(nullptr)>=deadline||ifstream(argv[3]).good())return 124;
  array<int,29> m; iota(m.begin(),m.end(),0);if(r==0)m=freq;else shuffle(m.begin(),m.end(),rng);array<int,29> initial=m,best=m;double s=score(m),bs=s;int accepted=0,evals=0;
  for(int it=0;it<30000;it++){
   if(it%1000==0){if(time(nullptr)>=deadline||ifstream(argv[3]).good())return 124;if(abs(score(m)-s)>1e-7)return 5;}
   int a=pick29(rng),b=pick28(rng);if(b>=a)b++;if(a>b)swap(a,b);double d=delta(m,a,b,aff[a][b]);evals++;double temp=4*exp(log(.05/4)*it/29999.);
   if(d>=0||unif(rng)<exp(d/temp)){swap(m[a],m[b]);s+=d;accepted++;if(s>bs){bs=s;best=m;}}
  }
  m=best;s=score(m);int sweeps=0;bool local=false;
  for(int pass=0;pass<10;pass++){double bd=1e-12;int ba=-1,bb=-1;for(int a=0;a<29;a++)for(int b=a+1;b<29;b++){double d=delta(m,a,b,aff[a][b]);evals++;if(d>bd){bd=d;ba=a;bb=b;}}sweeps++;if(ba<0){local=true;break;}swap(m[ba],m[bb]);s+=bd;}
  double exact=score(m);if(abs(exact-s)>1e-7)return 6;
  if(r)cout<<",";cout<<"{\"restart\":"<<r<<",\"initial\":";arr(initial);cout<<",\"map\":";arr(m);cout<<",\"score\":"<<exact<<",\"accepted_sa\":"<<accepted<<",\"evaluations\":"<<evals<<",\"hill_sweeps\":"<<sweeps<<",\"local_optimum\":"<<(local?"true":"false")<<"}";cout.flush();
 }
 cout<<"]}\n";return 0;
}
