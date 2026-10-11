from core.analyzers.file_scanner import scan
from core.analyzers.technology_detector import detect as technologies
from core.analyzers.feature_detector import detect as features
from core.analyzers.architecture_analyzer import infer
from core.intelligence.scoring_engine import score
from core.intelligence.gap_analyzer import gaps
from core.intelligence.risk_analyzer import risks
from pathlib import Path

def analyze(root,project_name=None):
 files=scan(root); tech=technologies(files); feats=features(files); arch=infer(files,tech); sc=score(files,tech,feats,arch)
 name=project_name or Path(root).name
 domain='AI/ML' if any(x in tech['technologies'] for x in ['Scikit-learn','TensorFlow','PyTorch']) else ('Data Analytics' if 'Pandas' in tech['technologies'] else 'Web Application')
 return {'project':{'name':name,'domain':domain,'type':'Software Application','file_count':len(files)},'technologies':tech,'features':feats,'architecture':arch,'score':sc,'recommendations':gaps(feats,domain),'risks':risks(feats,files)}
