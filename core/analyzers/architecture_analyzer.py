def infer(files,tech):
 paths=[f['path'].lower() for f in files]; layers=[]
 if any(x in ' '.join(paths) for x in ['frontend','components','pages']) or 'React' in tech['technologies']: layers.append('Presentation Layer')
 if any(x in ' '.join(paths) for x in ['api','routes','app.py','main.py']) or any(x in tech['technologies'] for x in ['FastAPI','Flask']): layers.append('Application / API Layer')
 if any(x in ' '.join(paths) for x in ['service','services','core']): layers.append('Service / Intelligence Layer')
 if any(x in tech['technologies'] for x in ['Scikit-learn','TensorFlow','PyTorch']): layers.append('ML / AI Layer')
 if 'Database' in ' '.join(paths) or 'SQLAlchemy' in tech['technologies']: layers.append('Data Layer')
 if not layers: layers=['Application Layer','Business Logic','Data / File Layer']
 recommended=['Presentation Layer','Application / API Layer','Service / Intelligence Layer','Data Layer']
 return {'current':layers,'recommended':recommended,'gaps':[x for x in recommended if x not in layers]}
