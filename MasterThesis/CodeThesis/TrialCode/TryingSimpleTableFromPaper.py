# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 15:41:53 2018

@author: Carles
"""

import MySQLdb
db_connection = MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306, 
                                    db='nhl', 
                                    user='root', 
                                    passwd='')
        
db_cursor = db_connection.cursor()

import pandas as pd
queryGoal = """
    SELECT PeriodNumber as P, MD, GD, Zone, COUNT(EventType) AS Goal
    FROM  workcontextevents
    WHERE EventType= 'GOAL'
    Group By P , MD, GD 
    """
queryPenalty = """    
    SELECT PeriodNumber as P, MD, GD, COUNT(EventType) AS Penalty
    FROM  workcontextevents
    WHERE EventType= 'PENALTY'
    Group By P, MD, GD
"""

### THIS ONE IS WRONG !!!
querySequence = """    
    SELECT PeriodNumber AS P, MD, GD, COUNT(Distinct(GameId +''+ ActionSequence )) AS Sequence
    FROM   workcontextevents
    Group  By P, MD, GD
"""



goalRes = pd.read_sql_query(queryGoal, db_connection)                  
penaltyRes = pd.read_sql_query(queryPenalty, db_connection)
sequenceRes = pd.read_sql_query(querySequence, db_connection)
result = pd.concat([goalRes, penaltyRes, sequenceRes], axis=1, join_axes=[goalRes.index])
new_df = pd.merge(goalRes, penaltyRes,   on=['P','MD','GD'])
Data =pd.merge(new_df, sequenceRes,   on=['P','MD','GD'])
