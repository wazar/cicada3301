from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET,unittest
from parse_inputs import ALPHABET,parse,ROOT,OUT,sha
class ParserTests(unittest.TestCase):
 def test_hand(self):
  p=parse('ᚠ-ᚢ/ᚦ.% %ᛠ/');self.assertEqual([x['indices'] for x in p],[[0,1,2],[28]]);self.assertEqual(p[0]['source_char_positions'],[0,2,4]);self.assertEqual(p[1]['stream_start'],3)
 def test_mutation(self): self.assertNotEqual(parse('ᚠᚢ')[0]['indices'],parse('ᚠᚦ')[0]['indices'])
 def test_boundaries(self):
  x=parse('ᚠ/ᚢ%ᚦ');self.assertEqual(len(x),2);self.assertEqual(len(x[0]['lines']),2);self.assertEqual(x[0]['lines'][1]['rune_start'],1)
def main():
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ParserTests));assert r.wasSuccessful()
 data=json.loads((OUT/'dataset.json').read_text()); K=[i for p in data['pages'] for i in p['indices']]
 def indices(s): return [ALPHABET.index(c) for c in s if c in ALPHABET]
 order=['p0-2','p3-7','p8-14','p15-22','p23-26','p27-32','p33-39','p40-53','p54-55','p56_an_end','p57_parable']
 files=[ROOT/f'liber-primus/data/sources/relikd_{s}.txt' for s in order]
 R=sum([indices(p.read_text()) for p in files],[])
 tp=ROOT/'liber-primus/data/sources/rtkd_master.txt';T=indices(tp.read_text()); starts=[i for i in range(len(T)-23) if T[i:i+24]==K[:24]];assert len(starts)==1
 table=(OUT/'sources/relikd-README.md').read_text().split('Gematria Primus (reversed)')[1].split('```')[0]
 entries=re.findall(r'(\d+)\s+([ᚠ-ᛠᛡ])\s+(\d+)\s+([A-Z/]+)',table)
 observed={28-int(n):c for n,c,prime,tr in entries};assert len(observed)==29;assert ''.join(observed[i] for i in range(29))==ALPHABET
 xml=ET.parse(OUT/'sources/archive-files.xml'); archived={f.attrib['name']:f.findtext('sha1') for f in xml.findall('file')}
 rows=[]
 for n in range(58):
  p=ROOT/f'liber-primus/data/relikd/p{n}.jpg' if n<56 else OUT/f'sources/{n}.jpg'
  actual=hashlib.sha1(p.read_bytes()).hexdigest();expected=archived[f'{n}.jpg'];rows.append(dict(original_page=n,source=str(p.relative_to(ROOT)),sha256=sha(p),sha1=actual,archive_sha1=expected,match=actual==expected))
 result=dict(parser_tests=3,alphabet_separate_source='sources/relikd-README.md reversed table; all29 match; related community source, not independent glyph ground truth',transcriptions=dict(krisyotam=len(K),relikd=len(R),rtkd_prefix_runes=starts[0],rtkd_suffix=len(T[starts[0]:]),K_equals_R=K==R,K_equals_T_suffix=K==T[starts[0]:]),source_hashes={str(p.relative_to(ROOT)):sha(p) for p in files+[tp]},image_archive_comparison=rows)
 (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(transcriptions=result['transcriptions'],alphabet_entries=len(observed),image_sha1_matches=sum(x['match'] for x in rows),image_count=len(rows)),indent=2))
if __name__=='__main__':main()
