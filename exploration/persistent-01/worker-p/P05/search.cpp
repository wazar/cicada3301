#include <array>
#include <vector>
#include <random>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>
using namespace std;
int main(int argc,char**argv){
 if(argc!=4)return 2;ifstream mf(argv[1]),cf(argv[2]);array<double,17> uni;vector<double> tri(17*17*17);for(auto&v:uni)mf>>v;for(auto&v:tri)mf>>v;int n,cut;cf>>n>>cut;vector<int> c(n);for(auto&v:c)cf>>v;if(!mf||!cf)return 3;
 mt19937_64 rng(stoull(argv[3]));uniform_real_distribution<double>U(0,1);vector<double>w;for(auto p:uni)w.push_back(exp(p));discrete_distribution<int> label(w.begin(),w.end());
 auto score=[&](const array<int,29>&m){double s=uni[m[c[0]]]+uni[m[c[1]]];for(int i=2;i<cut;i++)s+=tri[(m[c[i-2]]*17+m[c[i-1]])*17+m[c[i]]];return s;};
 cout<<setprecision(17)<<"[";
 for(int rep=0;rep<8;rep++){
  array<int,29>m;array<int,17>counts{};for(int i=0;i<29;i++)m[i]=i<17?i:label(rng);shuffle(m.begin(),m.end(),rng);for(auto l:m)counts[l]++;double s=score(m),best=s;auto bm=m;int accepted=0,valid=0;
  for(int k=0;k<5000;k++){
   auto z=m;int a=rng()%29,b=rng()%28;if(b>=a)b++;bool sw=U(rng)<.5;int old=m[a],ne=-1;
   if(sw){if(m[a]==m[b])continue;swap(z[a],z[b]);}
   else {if(counts[old]<=1)continue;ne=rng()%16;if(ne>=old)ne++;z[a]=ne;}
   valid++;double ns=score(z),T=3*pow(.05/3.,double(k)/4999);if(ns>=s||U(rng)<exp((ns-s)/T)){m=z;s=ns;accepted++;if(!sw){counts[old]--;counts[ne]++;}if(s>best){best=s;bm=m;}}
  }
  if(rep)cout<<",";cout<<"{\"restart\":"<<rep<<",\"score\":"<<best<<",\"accepted\":"<<accepted<<",\"valid_proposals\":"<<valid<<",\"map\":[";for(int r=0;r<29;r++){if(r)cout<<",";cout<<bm[r];}cout<<"]}";
 }
 cout<<"]\n";return 0;
}
