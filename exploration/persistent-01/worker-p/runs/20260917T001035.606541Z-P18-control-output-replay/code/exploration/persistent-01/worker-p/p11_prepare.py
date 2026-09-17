import pathlib,re,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];R=pathlib.Path(__file__).parent/'P11';S=ROOT/'exploration/persistent-01/coordinator/jsteg-source/mirror-0.diff';text=S.read_text();assert hashlib.sha256(S.read_bytes()).hexdigest()=='c1f02db0e00b4a9861d1d8830b48112f1d569cb00392740fc72c4e8b35bbfb8b'
for name in ['bitsource.c','bitsource.h','bitsink.c','bitsink.h']:
 chunk=text.split('diff -c -N jpeg-v4/'+name+' ')[1].split('\ndiff -c -N ')[0];source='\n'.join(x[2:] for x in chunk.splitlines() if x.startswith('+ '))+'\n';(R/'private-source'/('original-'+name)).write_text(source)
 if name.endswith('.c'):
  source='#include <stdint.h>\n'+source.replace('unsigned long','uint32_t')
  if name=='bitsource.c':source=source.replace('(((uint32_t) ~0) >> ++shift)','((++shift >= 32) ? UINT32_C(0) : (UINT32_MAX >> shift))').replace('perror(errno);','perror("fstat");')
  else:source+='\nvoid sinkstate(void) { fprintf(stderr,"{\\"rep_width\\":%u,\\"file_size\\":%u,\\"fileindex\\":%u,\\"header_bits\\":%u,\\"buffer_bytes\\":%u,\\"bitindex\\":%d,\\"open\\":%d}\\n",rep_width,file_size,fileindex,curr_special,bufindex,bitindex,outfile!=0); }\n'
 (R/'private-source'/name).write_text(source)
print('Extracted source-derived local-only32bit adaptations')
