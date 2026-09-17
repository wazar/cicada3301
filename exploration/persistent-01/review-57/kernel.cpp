#define main archived_search_main
#include "../worker-s/s17_engine.cpp"
#undef main
static double independent(const array<int,29>& m) {
 int a=29,b=29;double z=0;
 for(int t:tokens){int c=t==29?29:m[t];z+=lm[900*a+30*b+c];a=b;b=c;}
 return z;
}
int main(){
 lm.resize(27000);for(int i=0;i<27000;i++)lm[i]=-1.-((i*137LL+11)%30001)/731.;
 mt19937 gen(570017);int checks=0;double worst=0;
 for(int n=0;n<=40;n++)for(int trial=0;trial<4;trial++){
  tokens.clear();for(auto &v:positions)v.clear();
  for(int j=0;j<n;j++){int x=trial==0?29:trial==1?0:gen()%30;tokens.push_back(x);if(x<29)positions[x].push_back(j);}
  array<int,29> m;iota(m.begin(),m.end(),0);shuffle(m.begin(),m.end(),gen);
  for(int a=0;a<29;a++)for(int b=a+1;b<29;b++){
   auto before=m;double s=independent(m),d=delta(m,a,b,affected(a,b));if(m!=before)return 2;
   swap(m[a],m[b]);double want=independent(m)-s;swap(m[a],m[b]);double err=abs(d-want);worst=max(worst,err);if(err>1e-9)return 3;checks++;
  }
 }
 cout<<"{\"checks\":"<<checks<<",\"max_error\":"<<setprecision(17)<<worst<<"}\n";
}
