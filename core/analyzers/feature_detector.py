RULES={'Authentication':['login','register','password','jwt','oauth'],'Database':['sqlite','sqlalchemy','postgres','mysql','mongodb'],'CRUD':['create','update','delete','insert into'],'REST API':['fastapi','flask','@app.get','@router.'],'Dashboard':['dashboard','st.metric','plotly','chart'],'Machine Learning':['sklearn','tensorflow','torch','predict(','fit('],'Prediction':['predict(','predict_proba'],'Data Visualization':['plotly','matplotlib','seaborn','st.chart'],'File Upload':['file_uploader','uploadfile','multipart'],'Testing':['pytest','unittest','test_'],'Docker':['dockerfile','docker-compose'],'Environment Variables':['dotenv','os.getenv','.env'],'Error Handling':['try:','except','raise ']}
def detect(files):
 out=[]
 for feat,signals in RULES.items():
  hits=[]
  for f in files:
   t=(f['path']+' '+f['text']).lower()
   if any(s.lower() in t for s in signals): hits.append(f['path'])
  if hits:
   conf=min(98,55+len(set(hits))*10)
   out.append({'name':feat,'confidence':conf,'files':sorted(set(hits))[:8],'evidence':f"Detected {len(set(hits))} relevant file(s)."})
 return out
