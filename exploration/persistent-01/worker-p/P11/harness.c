/* Independently authored driver. Third-party implementations linked separately. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "jpeglib.h"
FILE *bitloadfile(FILE *);short inject(short);int bitendload(void);
FILE *bitsavefile(FILE *);void exject(short);void sinkstate(void);
static int zz[64]={0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63};
int main(int argc,char**argv){
 if(argc<4)return 2;
 FILE *in=fopen(argv[2],"rb"),*out=fopen(argv[3],"wb");if(!in||!out)return 3;
 if(!strcmp(argv[1],"sink")){bitsavefile(out);int16_t x;while(fread(&x,2,1,in)==1)exject(x);sinkstate();fclose(in);return 0;}
 if(argc!=5)return 2;FILE *payload=fopen(argv[4],"rb");if(!payload||!bitloadfile(payload))return 4;
 if(!strcmp(argv[1],"inject")){int16_t x;while(fread(&x,2,1,in)==1){x=inject(x);fwrite(&x,2,1,out);}fclose(in);fclose(out);fprintf(stderr,"{\"complete\":%d}\n",bitendload());return bitendload()?0:5;}
 if(strcmp(argv[1],"jpeg"))return 2;
 struct jpeg_decompress_struct dec;struct jpeg_error_mgr de;dec.err=jpeg_std_error(&de);jpeg_create_decompress(&dec);jpeg_stdio_src(&dec,in);jpeg_read_header(&dec,TRUE);jvirt_barray_ptr *a=jpeg_read_coefficients(&dec);
 /* This control path deliberately requires MCU-aligned dimensions. */
 if(dec.image_width%(8*dec.max_h_samp_factor)||dec.image_height%(8*dec.max_v_samp_factor))return 6;
 for(unsigned my=0;my<dec.image_height/(8*dec.max_v_samp_factor);my++)for(unsigned mx=0;mx<dec.image_width/(8*dec.max_h_samp_factor);mx++)for(int ci=0;ci<dec.num_components;ci++){
  jpeg_component_info *c=&dec.comp_info[ci];for(int y=0;y<c->v_samp_factor;y++){JBLOCKARRAY row=(*dec.mem->access_virt_barray)((j_common_ptr)&dec,a[ci],my*c->v_samp_factor+y,1,TRUE);for(int x=0;x<c->h_samp_factor;x++)for(int k=0;k<64;k++){JCOEF *v=&row[0][mx*c->h_samp_factor+x][zz[k]];*v=inject(*v);}}
 }
 struct jpeg_compress_struct enc;struct jpeg_error_mgr ce;enc.err=jpeg_std_error(&ce);jpeg_create_compress(&enc);jpeg_stdio_dest(&enc,out);jpeg_copy_critical_parameters(&dec,&enc);jpeg_write_coefficients(&enc,a);jpeg_finish_compress(&enc);jpeg_destroy_compress(&enc);jpeg_finish_decompress(&dec);jpeg_destroy_decompress(&dec);fclose(in);fclose(out);fprintf(stderr,"{\"complete\":%d}\n",bitendload());return bitendload()?0:5;
}
