# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 12:46:21 2018

@author: Carles
"""
import numpy as np
import pandas as pd
import MySQLdb

def main():
    d= MySQLdb.connect(host = '127.0.0.1',
                                port = 3306, 
                                db='nhl', 
                                user='root', 
                                passwd='')
    
    c= d.cursor()
    Alltables= IndexByTeamSeason(2007,d,c)


def IndexByTeamSeason(seasonyear,d,c):
    # Variable where it is store a list of tables order by TeamId -1 (normal indexing in python)
    
    Alltables = []
    
    ## (1) Selecting distinct ids of Teams
    ##      For each team: 
    ##          Select the ids by season
    ##          Put index from 1 to n
    

    query = """SELECT DISTINCT TeamId 
    FROM Plays_In 
    where GameId LIKE '{0}'
    ORDER BY TeamId ASC
    """.format(str(seasonyear)+'%')
    c.execute(query) 
    TeamIds= c.fetchall()
    
    
    for Id in TeamIds:
        IdTeam = Id[0]
        query2= """
        SELECT GameId , Venue 
        FROM Plays_in 
        WHERE TeamId = {0} 
        AND GameId LIKE '{1}'
        ORDER BY GameId ASC
        """.format(IdTeam, str(seasonyear)+'%')

        c.execute(query2) 
        res= c.fetchall()
        listGames = ([int(i[0]) for i in res])
        n=len(res)
        Totalarray= []
        for i in range(n):
            GameIndex = res[i][0] 
            Venue  = res[i][1]
            ######LEFT to set it to some table
            playersarray= UniqueplayersperMatch(GameIndex, Venue, d)
            Totalarray = np.union1d(Totalarray, playersarray)
        Totalarray = Totalarray.astype(int).astype(str).tolist()    
        columnnames = ['GameId', 'CountGame']+Totalarray
        zeromatrix = np.zeros([n,len(Totalarray)])
        data = np.column_stack((np.column_stack((listGames,range(n))), zeromatrix))
        
        d1 = pd.DataFrame(data, columns = columnnames)            
        Alltables.append(d1)
    return Alltables


def UniqueplayersperMatch(GameId, Venue, d):
    query = """
    SELECT i.newCol
    FROM
    (SELECT distinct {1}Player1 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player2 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player3 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player4 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player5 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player6 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player7 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player8 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
     UNION
    SELECT distinct {1}Player9 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    ) i
    WHERE i.newCol is not null""".format(GameId,Venue) 
    return pd.read_sql_query(query, d).values

