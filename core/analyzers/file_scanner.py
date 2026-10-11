from pathlib import Path
IGNORE={'node_modules','.git','venv','.venv','__pycache__','dist','build','.next'}
TEXT_EXT={'.py','.js','.jsx','.ts','.tsx','.html','.css','.md','.txt','.json','.yml','.yaml','.toml','.sql'}
def scan(root):
 root=Path(root); files=[]
 for p in root.rglob('*'):
  if any(x in IGNORE for x in p.parts) or not p.is_file() or p.suffix.lower() not in TEXT_EXT: continue
  try: files.append({'path':str(p.relative_to(root)),'suffix':p.suffix.lower(),'size':p.stat().st_size,'text':p.read_text(errors='ignore')[:200000]})
  except: pass
 return files
