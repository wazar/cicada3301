from pathlib import Path
import shutil,hashlib,json,subprocess,difflib
B=Path('exploration/persistent-01/worker-s'); O=B/'S15'; O.mkdir(exist_ok=True)
P=Path('exploration/persistent-01/worker-p/private-P28/resurrecting-open-source-projects-outguess-24810e1/src'); S=O/'source'
assert not Path('exploration/persistent-01/STOP').exists()
shutil.copytree(P,S,dirs_exist_ok=True)
files=['outguess.c','jpeg-6b-steg/jdcoefct.c']; manifest=[]
for f in files:
 p=S/f; old=p.read_text();manifest.append({'file':f,'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if f=='outguess.c':
  target='\t\ttmp |= (TEST_BIT(bitmap->bitmap, i) ? 1 : 0) << where;'
  new='''        { static FILE *s15f = NULL; int pair[2];
          if (!s15f && getenv("S15_SELECT")) s15f=fopen(getenv("S15_SELECT"),"wb");
          pair[0]=i; pair[1]=TEST_BIT(bitmap->bitmap,i)?1:0;
          if(s15f) fwrite(pair,sizeof(int),2,s15f);
        }
'''+target
 else:
  target='\t\tfor (k = 0; k < DCTSIZE2; k++)\n\t\t  steg_use_bit((JCOEF) (*block)[k]);'
  new='''        for (k = 0; k < DCTSIZE2; k++) {
          unsigned short s15v=(JCOEF)(*block)[k];
          if ((s15v & 1) != s15v) {
            static FILE *s15f=NULL; int row[9];
            if(!s15f && getenv("S15_MAP")) s15f=fopen(getenv("S15_MAP"),"wb");
            row[0]=compptr->component_index;
            row[1]=MCU_col_num*compptr->MCU_width+xindex;
            row[2]=cinfo->input_iMCU_row*compptr->v_samp_factor+yoffset+yindex;
            row[3]=k; row[4]=(JCOEF)(*block)[k];
            row[5]=compptr->h_samp_factor;row[6]=compptr->v_samp_factor;
            row[7]=cinfo->max_h_samp_factor;row[8]=cinfo->max_v_samp_factor;
            if(s15f) fwrite(row,sizeof(int),9,s15f);
          }
          steg_use_bit((JCOEF) (*block)[k]);
        }'''
 assert old.count(target)==1
 p.write_text(old.replace(target,new));manifest[-1]['instrumented_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 (O/(Path(f).name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),p.read_text().splitlines(True),fromfile=f,tofile=f+'-trace')))
# Independent random-access array traversal, linked against unmodified library.
reader=r'''
#include <stdio.h>
#include <stdlib.h>
#include "jpeglib.h"
int main(int argc,char **argv){
 struct jpeg_decompress_struct c; struct jpeg_error_mgr e; FILE *f=fopen(argv[1],"rb"),*o=fopen(argv[2],"wb"); int ci,x,y,k;
 c.err=jpeg_std_error(&e);jpeg_create_decompress(&c);jpeg_stdio_src(&c,f);jpeg_read_header(&c,TRUE);
 jvirt_barray_ptr *a=jpeg_read_coefficients(&c);
 for(ci=0;ci<c.num_components;ci++) {jpeg_component_info *p=&c.comp_info[ci];
 for(y=0;y<p->height_in_blocks;y++){JBLOCKARRAY r=(*c.mem->access_virt_barray)((j_common_ptr)&c,a[ci],y,1,FALSE);
 for(x=0;x<p->width_in_blocks;x++)for(k=0;k<64;k++){unsigned short v=r[0][x][k];if((v&1)!=v){
 int z[9]={ci,x,y,k,(JCOEF)r[0][x][k],p->h_samp_factor,p->v_samp_factor,c.max_h_samp_factor,c.max_v_samp_factor};fwrite(z,sizeof(int),9,o);
 }}}} fclose(o);jpeg_destroy_decompress(&c);fclose(f);return 0;
}
/* Bundled library references callbacks even though coefficient API never calls them. */
short steg_use_bit(unsigned short v){return v;} void steg_set_bit(short *p){} 
'''
(O/'coeff_reader.c').write_text(reader)
cmds=[(['make','-j1','-f','makefile.ansi','CC=cc','CFLAGS=-O2 -DHAVE_STDC_HEADERS','libjpeg.a'],S/'jpeg-6b-steg'),(['cc','-O2','-std=gnu99','-I.','outguess.c','golay.c','arc.c','pnm.c','jpg.c','iterator.c','md5.c','jpeg-6b-steg/libjpeg.a','-lm','-o','outguess'],S),(['cc','-O2','-I'+str(P/'jpeg-6b-steg'),str(O/'coeff_reader.c'),str(P/'jpeg-6b-steg/libjpeg.a'),'-o',str(O/'coeff_reader')],Path('.'))]
rows=[]
for i,(cmd,cwd) in enumerate(cmds):
 r=subprocess.run(cmd,cwd=cwd,capture_output=True,timeout=240);(O/f'build{i}.stdout').write_bytes(r.stdout);(O/f'build{i}.stderr').write_bytes(r.stderr);rows.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode});assert r.returncode==0,r.stderr.decode()
(O/'build.json').write_text(json.dumps({'files':manifest,'commands':rows,'original_binary_sha256':hashlib.sha256((P/'outguess').read_bytes()).hexdigest(),'trace_binary_sha256':hashlib.sha256((S/'outguess').read_bytes()).hexdigest()},indent=2));print('PASS build')
