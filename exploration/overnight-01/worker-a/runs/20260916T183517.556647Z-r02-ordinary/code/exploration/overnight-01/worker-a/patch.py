from pathlib import Path
p=Path(__file__).with_name('search.py');s=p.read_text().replace("p['original_page']<=54","p['original_page']<=55")
s=s.replace("ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();t=time.monotonic();q=Score();ps=pages();keys=recipes();stage=O/a.stage;stage.mkdir(exist_ok=True)","ap.add_argument('--seconds',type=int,default=780);ap.add_argument('--page55',action='store_true');a=ap.parse_args();t=time.monotonic();q=Score();ps=[p for p in pages() if (p['original_page']==55 if a.page55 else p['original_page']!=55)];keys=recipes();stage=O/(a.stage+('-p55' if a.page55 else ''));stage.mkdir(exist_ok=True)")
p.write_text(s)
