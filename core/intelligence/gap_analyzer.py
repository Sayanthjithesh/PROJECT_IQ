EXPECTED={'AI/ML':['Machine Learning','Prediction','Data Visualization','Testing','Environment Variables'],'Web Application':['Authentication','Database','REST API','Error Handling','Testing'],'Data Analytics':['Data Visualization','Database','Reports','Export']}
def gaps(features,domain='General Software Project'):
 have={x['name'] for x in features}; key='AI/ML' if 'AI' in domain or 'ML' in domain else 'Data Analytics' if 'Data' in domain else 'Web Application'
 missing=[x for x in EXPECTED[key] if x not in have]
 return [{'recommendation':f'Add {x}','priority':'High' if x in missing[:2] else 'Medium','why':f'{x} was not detected and is commonly valuable for this project profile.','impact':'Improves completeness and professional readiness.','skills':'Project-specific implementation','difficulty':'Medium'} for x in missing]
