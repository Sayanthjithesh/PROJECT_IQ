def predict(feature):
 f=feature.lower(); bonus=8 if any(x in f for x in ['chat','ai','ml','predict']) else 5
 return {'portfolio_value':bonus,'technical_complexity':min(10,bonus-1),'user_value':min(10,bonus),'recommendation':'Recommended' if bonus>=6 else 'Consider based on project goal','prerequisites':['Clear user need','Integration plan','Testing strategy'],'note':'All impact values are estimates generated from rule-based heuristics.'}
