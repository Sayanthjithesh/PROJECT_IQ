def score(files,tech,features,arch):
 names={f['name'] for f in features}; paths=' '.join(f['path'].lower() for f in files)
 complexity=min(20,4+len(tech['languages'])*3+len(tech['technologies']))
 completeness=min(25,len(names)*2)
 professional=min(20,(4 if 'README' in paths else 0)+(5 if 'Testing' in names else 0)+(4 if 'Docker' in names else 0)+(4 if 'Environment Variables' in names else 0)+(3 if 'Error Handling' in names else 0))
 value=min(15,5+(5 if 'Dashboard' in names else 0)+(5 if ('Machine Learning' in names or 'Prediction' in names) else 0))
 differentiation=min(10,4+len(tech['technologies'])//3)
 deployment=min(10,(5 if 'Docker' in names else 0)+(3 if any(x in paths for x in ['deploy','vercel','render']) else 0)+(2 if 'REST API' in names else 0))
 cats={'Technical Complexity':complexity,'Feature Completeness':completeness,'Professional Practices':professional,'Real World Value':value,'Differentiation':differentiation,'Deployment and Scalability':deployment}; total=sum(cats.values())
 maturity='Beginner' if total<=35 else 'Developing' if total<=65 else 'Intermediate' if total<=80 else 'Advanced' if total<=90 else 'Professional'
 return {'categories':cats,'total':total,'maturity':maturity}
