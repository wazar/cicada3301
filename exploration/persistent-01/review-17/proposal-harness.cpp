#include <array>
#include <vector>
#include <random>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
using namespace std;
struct Parts { double lm=0,em=0; double total()const{return lm+em;} };
int main(int argc,char**argv){
 if(argc!=4&&argc!=5)return 2;
 ifstream mf(argv[1]),cf(argv[2]);array<double,17>uni;vector<double>tri(17*17*17);
 for(auto&v:uni)mf>>v;for(auto&v:tri)mf>>v;
 int n,cut;cf>>n>>cut;if(!cf||n<2||cut<2||cut>n)return 3;
 vector<int>c(n);for(auto&v:c){cf>>v;if(v<0||v>=29)return 3;}if(!mf||!cf)return 3;
 auto score=[&](const array<int,29>&m){
  array<int,17> bins{};for(auto a:m){if(a<0||a>=17)throw runtime_error("bad label");bins[a]++;}
  for(auto k:bins)if(!k)throw runtime_error("not surjective");
  array<double,18> normal{},repeat{},different{};
  for(int k=1;k<=17;k++){normal[k]=-log(double(k));repeat[k]=log(.17/double(k));different[k]=k==1?0:log(1./k+.83/(k*(k-1.)));}
  Parts out;
  for(int i=0;i<cut;i++){
   int a=m[c[i]],k=bins[a];out.lm+=i<2?uni[a]:tri[(m[c[i-2]]*17+m[c[i-1]])*17+a];
   out.em+=(i==0||k==1||m[c[i-1]]!=a)?normal[k]:(c[i-1]==c[i]?repeat[k]:different[k]);
  }return out;
 };
 cout<<setprecision(17)<<"[";
 if(argc==5){ifstream maps(argv[4]);array<int,29>m;int j=0;while(maps>>m[0]){for(int r=1;r<29;r++)if(!(maps>>m[r]))return 4;auto s=score(m);if(j++)cout<<",";cout<<"{\"lm\":"<<s.lm<<",\"emission\":"<<s.em<<",\"joint\":"<<s.total()<<"}";}cout<<"]\n";return 0;}
 mt19937_64 rng(stoull(argv[3]));uniform_real_distribution<double>U(0,1);vector<double>w;for(auto p:uni)w.push_back(exp(p));discrete_distribution<int>label(w.begin(),w.end());
 for(int rep=0;rep<1;rep++){
  array<int,29>m;array<int,17>counts{};for(int i=0;i<29;i++)m[i]=i<17?i:label(rng);shuffle(m.begin(),m.end(),rng);for(auto l:m)counts[l]++;
  auto initial=m;auto parts=score(m);double s=parts.total(),best=s;auto bm=m;int accepted=0,valid=0,best_iteration=-1;
  for(int k=0;k<200;k++){
   auto z=m;int a=rng()%29,b=rng()%28;if(b>=a)b++;bool sw=U(rng)<.5;int old=m[a],ne=-1;
   if(sw){if(m[a]==m[b])continue;swap(z[a],z[b]);}
   else {if(counts[old]<=1)continue;ne=rng()%16;if(ne>=old)ne++;z[a]=ne;}
   valid++;double ns=score(z).total(),T=3*pow(.05/3.,double(k)/4999);
   double draw=ns>=s?-1:U(rng);bool take=ns>=s||draw<exp((ns-s)/T);cerr<<setprecision(17)<<k<<" "<<a<<" "<<b<<" "<<sw<<" "<<ne<<" "<<s<<" "<<ns<<" "<<T<<" "<<draw<<" "<<take<<"\n";if(take){m=z;s=ns;accepted++;if(!sw){counts[old]--;counts[ne]++;}if(s>best){best=s;bm=m;best_iteration=k;}}
  }
  array<int,17> actual_counts{};for(auto label:m)actual_counts[label]++;if(actual_counts!=counts)return 9;
  auto final=score(bm);if(rep)cout<<",";
  cout<<"{\"restart\":"<<rep<<",\"score\":"<<best<<",\"lm\":"<<final.lm<<",\"emission\":"<<final.em<<",\"accepted\":"<<accepted<<",\"valid_proposals\":"<<valid<<",\"nominal_proposals\":5000,\"best_iteration\":"<<best_iteration<<",\"initial_map\":[";
  for(int r=0;r<29;r++){if(r)cout<<",";cout<<initial[r];}cout<<"],\"map\":[";for(int r=0;r<29;r++){if(r)cout<<",";cout<<bm[r];}cout<<"]}";
 }cout<<"]\n";return 0;
}
