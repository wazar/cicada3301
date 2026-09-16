#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jpeglib.h"
extern void jpeg_gen_optimal_table(j_compress_ptr,JHUFF_TBL *,long *);
int main(int argc,char**argv){
 if(argc!=4)return 2;FILE *in=fopen(argv[2],"rb"),*out=fopen(argv[3],"wb");if(!in||!out)return 3;
 struct jpeg_compress_struct enc;struct jpeg_error_mgr ce;enc.err=jpeg_std_error(&ce);jpeg_create_compress(&enc);
 if(!strcmp(argv[1],"hist")){long f[257]={0};for(int i=0;i<256;i++)if(fscanf(in,"%ld",&f[i])!=1)return 4;JHUFF_TBL h;memset(&h,0,sizeof(h));jpeg_gen_optimal_table(&enc,&h,f);int n=0;for(int i=1;i<=16;i++){fputc(h.bits[i],out);n+=h.bits[i];}fwrite(h.huffval,1,n,out);fclose(in);fclose(out);jpeg_destroy_compress(&enc);return 0;}
 struct jpeg_decompress_struct dec;struct jpeg_error_mgr de;dec.err=jpeg_std_error(&de);jpeg_create_decompress(&dec);jpeg_stdio_src(&dec,in);jpeg_read_header(&dec,TRUE);jvirt_barray_ptr *a=jpeg_read_coefficients(&dec);jpeg_stdio_dest(&enc,out);jpeg_copy_critical_parameters(&dec,&enc);
 for(int c=0;c<dec.num_components;c++){enc.comp_info[c].dc_tbl_no=dec.comp_info[c].dc_tbl_no;enc.comp_info[c].ac_tbl_no=dec.comp_info[c].ac_tbl_no;}
 for(int k=0;k<NUM_HUFF_TBLS;k++){if(dec.dc_huff_tbl_ptrs[k]){if(!enc.dc_huff_tbl_ptrs[k])enc.dc_huff_tbl_ptrs[k]=jpeg_alloc_huff_table((j_common_ptr)&enc);memcpy(enc.dc_huff_tbl_ptrs[k],dec.dc_huff_tbl_ptrs[k],sizeof(JHUFF_TBL));}if(dec.ac_huff_tbl_ptrs[k]){if(!enc.ac_huff_tbl_ptrs[k])enc.ac_huff_tbl_ptrs[k]=jpeg_alloc_huff_table((j_common_ptr)&enc);memcpy(enc.ac_huff_tbl_ptrs[k],dec.ac_huff_tbl_ptrs[k],sizeof(JHUFF_TBL));}}
 if(!strcmp(argv[1],"opt"))enc.optimize_coding=TRUE;
 else if(!strcmp(argv[1],"perm")){enc.optimize_coding=FALSE;int done=0;for(int cl=0;cl<2&&!done;cl++)for(int k=0;k<NUM_HUFF_TBLS&&!done;k++){JHUFF_TBL *h=cl?enc.ac_huff_tbl_ptrs[k]:enc.dc_huff_tbl_ptrs[k];if(!h)continue;int pos=0;for(int len=1;len<=16;len++){if(h->bits[len]>=2){int x=h->huffval[pos],y=h->huffval[pos+1];h->huffval[pos]=y;h->huffval[pos+1]=x;h->sent_table=FALSE;fprintf(stderr,"{\"class\":%d,\"table\":%d,\"length\":%d,\"symbols\":[%d,%d]}\n",cl,k,len,x,y);done=1;break;}pos+=h->bits[len];}}if(!done)return 5;}
 else return 2;
 jpeg_write_coefficients(&enc,a);jpeg_finish_compress(&enc);jpeg_destroy_compress(&enc);jpeg_finish_decompress(&dec);jpeg_destroy_decompress(&dec);fclose(in);fclose(out);return 0;
}
