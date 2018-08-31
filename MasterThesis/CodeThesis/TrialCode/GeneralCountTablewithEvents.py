# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 16:19:11 2018

@author: Carles
"""
import pandas as pd
import MySQLdb
from __future__ import division

db_connection = MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306, 
                                    db='nhl', 
                                    user='root', 
                                    passwd='')
        
db_cursor = db_connection.cursor()

#db_cursor.execute("DROP TABLE workcontextevents")
def Createtable(name):
    # name: a character variable
    query =   "".join(["CREATE TABLE  ", name, " SELECT * FROM play_by_play_eventsfiltered"])      
    print(query)
    db_cursor.execute(query)
    db_cursor.execute("".join(["ALTER TABLE ", name , " ADD INDEX (EventNumber)"]))
    db_cursor.execute("".join(["ALTER TABLE ", name , " ADD INDEX (GameId)"]))
    db_cursor.execute("".join(["ALTER TABLE ", name , " ADD INDEX ( ExternalEventId)"]))
    print("Table Created")
    pass

# Createtable('workcontextevents')
## Giving to workcontextevents a new index unique
# =============================================================================
# db_cursor.execute("""ALTER TABLE workcontextevents DROP UniqueId  """)
# db_cursor.execute("""ALTER TABLE workcontextevents ADD COLUMN  UniqueId  INT AUTO_INCREMENT PRIMARY KEY""")
# db_connection.commit()
# =============================================================================



###################################################
### Calculating Occurrences of EveryState
queryStates1 = """select  MD,  GD, P, Zone, EventTypeContext, SUM(AMOUNT) as Occ
FROM (SELECT GameId, EventNumber, MD,  GD, Zone, PeriodNumber as P, EventTypeContext, 1 AS AMOUNT 
              FROM workcontextevents) tab1
          group by MD,  GD, P, EventTypeContext, Zone"""

OccStates = pd.read_sql_query(queryStates1 , db_connection)                  
numStates =[i for i in range(len(OccStates))]
OccStates['idStates'] = numStates

# =============================================================================
# ## Creating new Dataframe to work with
# db_cursor.execute("""DROP TABLE IdTableEvents """)
# db_cursor.execute("""CREATE TABLE IdTableEvents SELECT GameId, EventNumber, ExternalEventId, MD,  GD, PeriodNumber, EventTypeContext, Zone
#                   FROM workcontextevents""")
# db_cursor.execute("ALTER TABLE IdTableEvents ADD INDEX (EventNumber)")
# db_cursor.execute("ALTER TABLE IdTableEvents ADD INDEX (GameId)")
# db_cursor.execute("ALTER TABLE IdTableEvents ADD INDEX (ExternalEventId)")
# 
db_cursor.execute("ALTER TABLE workcontextevents ADD COLUMN IdContext int")
db_connection.commit()
# 
# =============================================================================
##Updating table Idcontext as unique variable related to states from table OccStates
iterlen = len(OccStates)
for index in range(4964,len(OccStates)):
    MD = OccStates['MD'][index]     
    GD = OccStates['GD'][index]
    PeriodNumber = OccStates['P'][index]
    EventTypeContext = OccStates['EventTypeContext'][index]
    Zone = OccStates['Zone'][index]
    Id = OccStates['idStates'][index]
    query = "".join([" UPDATE workcontextevents",
                     " SET IdContext = ", str(Id),
            " WHERE MD = ", str(MD), " AND GD = " , str(GD), 
            " AND PeriodNumber = " , str(PeriodNumber) , 
            " AND Zone = '" , str(Zone) , "'", 
           " AND EventTypeContext = '", EventTypeContext,"'"])
    db_cursor.execute(query)    
    db_connection.commit()
    print(iterlen-index)
    
##Creating transition matrices    
import numpy as np    
import pandas as pd
AbslolutMat = np.zeros([len(OccStates),len(OccStates)]) 
query = "SELECT GameId, ActionSequence, EventNumber, IdContext FROM workcontextevents"
db_cursor.execute(query)
byGameId = db_cursor.fetchall()


## Doing the transition matrix
for tup in range(len(byGameId)):
    print(len(byGameId)-tup)
    if len(byGameId)-tup<1:
        break
    else:               
        IdContext = int(byGameId[tup][3]) #IdContext column being 1 
        CurrentId = IdContext
        NextId = int(byGameId[tup+1][3])
        AbslolutMat[CurrentId, NextId] +=   1 
        
TransitionMat =  AbslolutMat/np.transpose(OccStates['idStates'].values) ## Try before            



#############Create a tree