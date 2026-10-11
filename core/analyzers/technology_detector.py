import re
TECH={'Python':(['.py'],['import ','from ']),'JavaScript':(['.js','.jsx'],['import ','require(']),'TypeScript':(['.ts','.tsx'],['import ']),'HTML':(['.html'],[]),'CSS':(['.css'],[])}
LIBS={'Streamlit':'streamlit','FastAPI':'fastapi','Flask':'flask','React':'react','Pandas':'pandas','NumPy':'numpy','Scikit-learn':'sklearn','TensorFlow':'tensorflow','PyTorch':'torch','SQLAlchemy':'sqlalchemy','Plotly':'plotly','Docker':'docker'}
def detect(files):
 langs=set(); tech=set(); evidence={}
 for f in files:
  for k,(ext,_) in TECH.items():
   if f['suffix'] in ext: langs.add(k)
  txt=f['text'].lower()
  for name,key in LIBS.items():
   if key in txt or key in f['path'].lower(): tech.add(name); evidence.setdefault(name,[]).append(f['path'])
 return {'languages':sorted(langs),'technologies':sorted(tech),'evidence':evidence}
