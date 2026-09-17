
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
