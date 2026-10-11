def risks(features,files):
 have={x['name'] for x in features}; paths=' '.join(f['path'].lower() for f in files); checks=[('Testing','Testing','High'),('Documentation','readme','Medium'),('Configuration','Environment Variables','Medium'),('Error Handling','Error Handling','Medium'),('Scalability','docker','Medium')]; out=[]
 for label,signal,level in checks:
  ok=(signal in have) if signal in {'Testing','Environment Variables','Error Handling'} else signal in paths
  out.append({'area':label,'level':'Low' if ok else level,'reason':'Relevant practices were detected.' if ok else f'Limited evidence of {label.lower()} practices was detected.'})
 return out
