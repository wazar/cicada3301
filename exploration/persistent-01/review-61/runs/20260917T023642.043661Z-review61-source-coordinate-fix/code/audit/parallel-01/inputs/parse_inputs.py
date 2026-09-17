"""Independent standard-library parser; no inherited imports. Frozen v1 export."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ALPHABET='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(txt):
    pages=[]; offset=0; raw_offset=0
    for region,seg in enumerate(txt.split('%')):
        lines=[]; seq=[]; pos=[]; seps=[]; line_start=0
        for li,line in enumerate(seg.split('/')):
            vals=[]; positions=[]
            for ci,ch in enumerate(line):
                absolute=raw_offset+line_start+ci
                if ch in ALPHABET:
                    vals.append(ALPHABET.index(ch)); positions.append(absolute)
                elif not ch.isspace():
                    seps.append(dict(character=ch,source_char=absolute,rune_gap=len(seq)+len(vals),source_line=li))
            if vals:
                lines.append(dict(source_line=li,rune_start=len(seq),rune_end=len(seq)+len(vals),indices=vals,source_char_positions=positions,raw=line))
            seq.extend(vals); pos.extend(positions); line_start+=len(line)+1
        if seq:
            segment=len(pages); original=segment if segment<50 else segment+1
            pages.append(dict(segment_id=segment,source_region_id=region,original_page=original,original_filename=f'{original}.jpg',stream_start=offset,stream_end=offset+len(seq),rune_count=len(seq),indices=seq,source_char_positions=pos,lines=lines,non_rune_tokens=seps))
            offset+=len(seq)
        raw_offset+=len(seg)+1
    return pages

def main():
    src=ROOT/'liber-primus/data/krisyotam_runes.txt'; pages=parse(src.read_text())
    stream=[v for p in pages[:-2] for v in p['indices']]
    data=dict(version='parallel-01-inputs-v1',source=str(src.relative_to(ROOT)),source_sha256=sha(src),parser_sha256=sha(Path(__file__)),alphabet=ALPHABET,positions='zero based; end offsets exclusive; source character offsets count Unicode code points',line_definition='Slash-delimited transcription lines; source newlines retained in raw. These are not certified image-typographic line boundaries.',pages=pages,unsolved=dict(segment_ids=list(range(55)),rune_count=len(stream),sha256_comma_joined_indices=hashlib.sha256(','.join(map(str,stream)).encode()).hexdigest()))
    mapping=[]
    for p in range(58):
        pg=next((x for x in pages if x['original_page']==p),None)
        path=ROOT/f'liber-primus/data/relikd/p{p}.jpg'
        row=dict(original_page=p,original_filename=f'{p}.jpg',local_image=str(path.relative_to(ROOT)) if path.exists() else None,image_sha256=sha(path) if path.exists() else None,segment_id=pg['segment_id'] if pg else None,source_region_id=pg['source_region_id'] if pg else None,rune_count=pg['rune_count'] if pg else 0,stream_start=pg['stream_start'] if pg else pages[49]['stream_end'],stream_end=pg['stream_end'] if pg else pages[49]['stream_end'],map_status='R19 map provisionally adopted; targeted image verification recorded separately',non_rune_inventory='All image content outside the transcription is retained by original image reference; ornaments, headings, illustrations and separators have not been exhaustively segmented.',text_region='Source transcription segment; may include headings, excludes untranscribed material')
        mapping.append(row)
    (OUT/'dataset.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (OUT/'page-map.json').write_text(json.dumps(dict(version=data['version'],parser_sha256=data['parser_sha256'],source_sha256=data['source_sha256'],pages=mapping),indent=2)+'\n')
    print(json.dumps(dict(segments=len(pages),lines=sum(len(p['lines']) for p in pages),all_runes=sum(p['rune_count'] for p in pages),unsolved=data['unsolved'],dataset_sha256=sha(OUT/'dataset.json'),page_map_sha256=sha(OUT/'page-map.json')),indent=2))
if __name__=='__main__': main()
