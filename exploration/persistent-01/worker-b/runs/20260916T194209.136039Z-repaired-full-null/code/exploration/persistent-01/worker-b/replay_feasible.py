import importlib.util,pathlib
OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('repair',OUT/'feasible.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
m.b.old.decode=m.decode
# Separate directory tag while keeping original runner's IDs/model and exact seeded null procedure.
original_save=m.b.save
m.b.save=lambda name,x:original_save('repaired-'+name,x)
original_gzip=m.b.gzip.open
m.b.gzip.open=lambda name,*args,**kwargs:original_gzip(pathlib.Path(name).with_name('repaired-'+pathlib.Path(name).name),*args,**kwargs)
if __name__=='__main__':m.b.main()
