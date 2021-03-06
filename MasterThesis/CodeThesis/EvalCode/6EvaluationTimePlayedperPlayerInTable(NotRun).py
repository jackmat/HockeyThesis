# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 12:46:21 2018

@author: Carles
"""
import numpy as np
import pandas as pd
import MySQLdb
import datetime
ACTION_EVENTS = "('FACEOFF', 'SHOT', 'MISSED SHOT', 'BLOCKED SHOT', 'TAKEAWAY', 'GIVEAWAY', 'HIT', 'GOAL', 'PENALTY')"
from __future__ import division
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"

def main():
    # =============================================================================
    #     ### Description:   (1) Opens MySQLdb connection
    #                        (2) Creates the season tables for
    #                               Value, Time, with ones (to multiply and get the first values back)
    #                        (3) For each distinct teamId in the table: 
    #                               Calculates time Players play per match
    #                               Calculates valuation of players per match
    #                        (4) Everything is put in one big pd.Dataframe
    #                        (5) Metrics created: 
    #                               Value/Time*60 per match (Valuation/ min)
    #                               Value per match
    #
    #     ### Args:
    #    ###Return:
    #     #     It saves the two pd.Dataframe metrics into
    #               path + 'PlayerValMatrix.csv'
    #               path + 'PlayerbyTimeValMatrix.csv' 
    #                     
    # =============================================================================

    d= MySQLdb.connect(host = '127.0.0.1',
                                port = 3306, 
                                db='nhl', 
                                user='root', 
                                passwd='')
    
    c= d.cursor()
    for Season in range(2007,2015):
        print(Season)
        PlayerValueMat= IndexByTeamSeason(Season,d,c)
        print("Value Matrix created")
        PlayerTimePlayer= IndexByTeamSeason(Season,d,c)
        print("Time Matrix created")
        PlusMinus= IndexByTeamSeason(Season,d,c)
        print("PlusMinus Matrix created")

        query = """SELECT DISTINCT TeamId 
            FROM Plays_in 
            WHERE  GameId LIKE '{0}%'        ORDER BY TeamId ASC
            """.format(Season)
            
        c.execute(query)
        results = c.fetchall()
        RangeTeam = [int(i[0]) for i in results]
        for team in range(len(PlayerValueMat)):
            print("doing iteration "+ str(team) + " out of "+str(len(RangeTeam)))

            Team = RangeTeam[team]

#            TimeMat = PlayerTimePlayer[team] #change 0 to team
#            ValueMat = PlayerValueMat[team]
            PlusMinMat = PlusMinus[team] 
#            PlayerTimePlayer[team] = TimePlayed(Team = Team, pandasframe = TimeMat, c =c ,d = d) #Storing timeplayedby macth
#            PlayerValueMat[team] = EvaluationPlayers(Team = Team , pandasframe = ValueMat, c =c ,d = d)
            PlusMinus[team] = PlusMinusFun(Team = Team , pandasframe = PlusMinMat, c =c ,d = d)            
            
        #(1) Creating Markovian +/- metric for valuation of 
        PlusMinMatrix = JoinListpdMatrices(PlusMinus)
        #(2) Val (This one is already PlayerValueMat)
#        ValMat = JoinListpdMatrices(PlayerValueMat)
        #(3) Fulljoin of matrices by counter for both metrics
#        ValbySecMat = JoinListpdMatrices(PlayerTimePlayer) # Changed ValbySec for just        
        
        #(4) Store it to pass it to R 
#        ValMat.to_csv(path + str(Season)+'PlayerValMatrix.csv')
#        ValbySecMat.to_csv(path +str(Season)+ 'PlayerbyTimeValMatrix.csv') 
        PlusMinMatrix.to_csv(path +str(Season)+ 'PlusMinusMatrix.csv')
        #(5) Plot it in R
        
def IndexByTeamSeason(seasonyear,d,c, Matzero = True):
    # =============================================================================
    #     ### Description:   Selecting distinct ids of Teams
    #                          For each team: 
    #                             Select the ids of the players by season and the matches played
    #                             Put index from 1 to n as a counter table
    #                             Create an empty np.zeros(matrix) or np.ones
    #     ### Args:
    #     #     seasonyear: integer value. Only 2007-2014 years are accepted
    #     #     Matzero: if True, np.zeroMatrix is created, else, np.ones(matrix)
    #     #     c: cursor
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns a pd.Dataframe with Players by team and Season with  
    #           0 value by default
    #                     
    # =============================================================================

    Alltables = []
       

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
        if Matzero != True:
            zeromatrix =np.ones([n,len(Totalarray)])
        data = np.column_stack((np.column_stack((listGames,range(n))), zeromatrix))
        
        d1 = pd.DataFrame(data, columns = columnnames, index = listGames)            
        Alltables.append(d1)
    return Alltables

def PlusMinusFun(Team, pandasframe, c,d):
    ### 
    # =============================================================================
    #     ### Description: For each match in the pd.Dataframe, select players and GameId, eventnum, typeEvent, EventTime
    #                       and calculate the valuation of that player inside the team
    #     ### Args:
    #     #     Team: the team Id. If it is not correct for the matrix, problems will arise
    #     #     pandasframe: pd.Dataframe of columns[Match,Counter, id_players...]
    #     #     c: cursor
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same pandasframe matrix with the values of each player 
    #                     
    # =============================================================================

    Matches = pandasframe.GameId.values   
    Mat = pandasframe
    for match in range(len(Matches)):
        PrevVal = 0
        CurVal= 0
        CurEventType = ''
        PrevEventType = ''
#match = 0        
        MatchId = int(Matches[match]) # change for match
        Index = match
# =============================================================================
#         if Index >0:
#             break;
# =============================================================================
        query = """SELECT Venue FROM `plays_in` WHERE 
        GameId = {0} AND TeamId = {1}""".format(MatchId, Team)
        c.execute(query)
        try:
            result = c.fetchall()
            Venue = result[0][0].lower()
        except IndexError:
            print(MatchId, result, query, Team)
            break
        query = """SELECT EventNumber
                    FROM q_fulltable
                    WHERE GameId  = {0}
                    ORDER BY EventNumber
        """.format(MatchId)        
        c.execute(query)
        EventIndex = c.fetchall()
        for i in range(len(EventIndex)):
#i = 0            
            EventNumber =  EventIndex [i][0]
#            print(MatchId, EventNumber)
            if i >0: 
                PrevVal = CurVal 
                PrevEventType = CurEventType                       
            query = """
                    SELECT EventType, PlayerId, Prob_next_{0}_goal
                    FROM q_fulltable
                    WHERE GameId = {1}
                    AND EventNumber = {2}
            """.format(Venue, MatchId, EventNumber)
            c.execute(query)
            result = c.fetchall()
            CurEventType = result[0][0]
            PlayerId = result[0][1]
            CurVal = result[0][2]
            if CurEventType in ACTION_EVENTS:
                PlayersPlayed = UniqueplayersperEvent(MatchId, Venue, d, EventNumber).astype(str).tolist()
                if PlayersPlayed != []:
                    PlayersPlayed2 = [item for sublist in PlayersPlayed for item in sublist]

                    if str(PlayerId) in list(Mat.columns):                 
                        DiffValue = (CurVal-PrevVal)
#                        print(DiffValue)
                        if (CurEventType =='FACEOFF' and PrevEventType == 'PERIOD END'):
                            DiffValue = 0
                        Mat.loc[pandasframe.index[Index], PlayersPlayed2] += DiffValue             
    return Mat
    
def TimePlayed(Team, pandasframe,c,d ):
    ### For each match, select players and GameId, eventnum, typeEvent, EventTime
    # =============================================================================
    #     ### Description: For each match in the pd.Dataframe, select players and GameId, eventnum, typeEvent, EventTime
    #                       and calculate the time that player inside the team
    #     ### Args:
    #     #     Team: the team Id. If it is not correct for the matrix, problems will arise
    #     #     pandasframe: pd.Dataframe of columns[Match,Counter, id_players...]
    #     #     c: cursor
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same pandasframe matrix with the time played by each player(in seconds)
    #           The format is just np.float
    #                     
    # =============================================================================

    Matches = pandasframe.GameId.values   
    PrevTime = datetime.timedelta(0,0)
    CurrentTime= datetime.timedelta(0,0)
    CurEventType =''
    PrevEventType =''
    Mat = pandasframe
    for match in range(len(Matches)):
        
        MatchId = int(Matches[match]) # change for match
        Index = match
        query = """SELECT Venue FROM `plays_in` WHERE 
        GameId = {0} AND TeamId = {1}""".format(MatchId, Team)
        c.execute(query)
        try:
            result = c.fetchall()
            Venue = result[0][0]
        except IndexError:
            print(MatchId, Team, result)
            break;
        query = """SELECT EventNumber
                    FROM q_fulltable
                    WHERE GameId  = {0}
                    ORDER BY EventNumber
        """.format(MatchId)        
        c.execute(query)
        EventIndex = c.fetchall()
        for i in range(len(EventIndex)):
            EventNumber =  EventIndex [i][0]
            if i >0: 
                PrevTime = CurrentTime
                PrevEventType = CurEventType
                
            else: 
                PrevTime = datetime.timedelta(0,0)
            PlayersPlayed = UniqueplayersperEvent(MatchId, Venue, d, EventNumber).astype(str).tolist()
            if PlayersPlayed != []:
                PlayersPlayed2 = [item for sublist in PlayersPlayed for item in sublist]
            query = """SELECT EventTime, EventType
            FROM q_fulltable
            WHERE GameId = {0}
            AND EventNumber = {1}
            """.format(MatchId, EventNumber)
            c.execute(query)
            result = c.fetchall()
            if result ==():
                print(str(MatchId)+ "with eventnumber = " +str(EventNumber) + "non existing")
                pass 
            else: 
                CurrentTime = result[0][0]
                CurEventType = result[0][1]
                if CurEventType == 'PERIOD START':
                    PrevTime = datetime.timedelta(0,0)
                    CurrentTime = datetime.timedelta(0,0)
    #                    print(PrevTime)
                if PlayersPlayed != []:    
                    DiffTime = (CurrentTime-PrevTime).total_seconds()
                    if (CurEventType =='FACEOFF' and PrevEventType == 'PERIOD END'):
                        DiffTime = 0
                    if DiffTime<0:
                        print(MatchId, EventNumber, DiffTime, CurrentTime, PrevTime, CurEventType, PrevEventType)
                        DiffTime = 0
                        print("Difftime solved to 0")
                    if DiffTime>350:
                        print(MatchId, EventNumber, DiffTime, CurrentTime, PrevTime, CurEventType, PrevEventType)
                        DiffTime = 0
                        print("Difftime solved to 0")
                    Mat.loc[pandasframe.index[Index], PlayersPlayed2] += DiffTime

    return Mat                





def EvaluationPlayers(Team, pandasframe,c,d ):
    ### 
    # =============================================================================
    #     ### Description: For each match in the pd.Dataframe, select players and GameId, eventnum, typeEvent, EventTime
    #                       and calculate the valuation of that player inside the team
    #     ### Args:
    #     #     Team: the team Id. If it is not correct for the matrix, problems will arise
    #     #     pandasframe: pd.Dataframe of columns[Match,Counter, id_players...]
    #     #     c: cursor
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same pandasframe matrix with the values of each player 
    #                     
    # =============================================================================

    Matches = pandasframe.GameId.values   
    Mat = pandasframe
    for match in range(len(Matches)):
        PrevVal = 0
        CurVal= 0
        CurEventType = ''
        PrevEventType = ''
        MatchId = int(Matches[match]) # change for match
        Index = match
# =============================================================================
#         if Index >0:
#             break;
# =============================================================================
        query = """SELECT Venue FROM `plays_in` WHERE 
        GameId = {0} AND TeamId = {1}""".format(MatchId, Team)
        c.execute(query)
        try:
            result = c.fetchall()
            Venue = result[0][0].lower()
        except IndexError:
            print(MatchId, result, query, Team)
            break
        query = """SELECT EventNumber
                    FROM q_fulltable
                    WHERE GameId  = {0}
                    ORDER BY EventNumber
        """.format(MatchId)        
        c.execute(query)
        EventIndex = c.fetchall()
        for i in range(len(EventIndex)):
            EventNumber =  EventIndex [i][0]
#            print(MatchId, EventNumber)
            if i >0: 
                PrevVal = CurVal 
                PrevEventType = CurEventType                       
            query = """
                    SELECT EventType, PlayerId, Prob_next_{0}_goal
                    FROM q_fulltable
                    WHERE GameId = {1}
                    AND EventNumber = {2}
            """.format(Venue, MatchId, EventNumber)
            c.execute(query)
            result = c.fetchall()
            CurEventType = result[0][0]
            PlayerId = result[0][1]
            CurVal = result[0][2]
            if CurEventType in ACTION_EVENTS:
                if PlayerId != '':
                    if str(PlayerId) in list(Mat.columns):                 
                        DiffValue = (CurVal-PrevVal)
#                        print(DiffValue)
                        if (CurEventType =='FACEOFF' and PrevEventType == 'PERIOD END'):
                            DiffValue = 0
                        Mat.loc[pandasframe.index[Index], str(PlayerId)] += DiffValue             
    return Mat                

def JoinListpdMatrices(pdMatList, jointype= 'outer'):
    # =============================================================================
    #     ### Description: Returning a pd.Dataframe from a list of Dataframes 
    #                       with one same column being '1' using merge iteratively
    #     ### Args:
    #     #     pdMatLst: a list of pd.Dataframes. 
    #                      (important: Dataframes must have the same column name '1' to work, although that can be reespecified)
    #     #    jointype: argument say how do you want to join the different Dataframes.
    #                    must be either ‘left’, ‘right’, ‘outer’, ‘inner’    
    #    ###Return:
    #     #     it returns  Returning a pd.Dataframe from a list of Dataframes 
    #                     
    # =============================================================================
    TotalMerge = ''
    for i in range(len(pdMatList)):
        if i==0:
            TotalMerge = pdMatList[i]
            
        if i >0:        
            MatExtracted = pdMatList[i]
            TotalMerge= TotalMerge.merge(MatExtracted, left_on= 'CountGame', right_on= 'CountGame', how = jointype)
    return TotalMerge
def UniqueplayersperEvent(GameId, Venue, d, eventnumber):
    ### 
    # =============================================================================
    #     ### Description: It returns the GameId Unique Id players of a 
    #          specific match, event and team
    #     ### Args:
    #     #     GameId: integer number that refers to an IdMatch
    #     #     Venue: 'Away' or 'Home'. It affects the columns to choose
    #     #     event_number: integer number that refers to a specific event
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same pandasframe matrix with the values of each player 
    #                     
    # =============================================================================
    query = """
    SELECT i.newCol AS Players
    FROM
    (SELECT distinct {1}Player1 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player2 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player3 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player4 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player5 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player6 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player7 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player8 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
     UNION
    SELECT distinct {1}Player9 AS newCol
                    FROM q_fulltable
                    WHERE GameId = {0}
                    AND EventNumber = {2}
                    ) i
    WHERE i.newCol is not null""".format(GameId,Venue, eventnumber) 
    return pd.read_sql_query(query, d).values    
def UniqueplayersperMatch(GameId, Venue, d):
    # =============================================================================
    #     ### Description: It returns the GameId Unique Id players of a specific match and team
    #     ### Args:
    #     #     GameId: integer number that refers to an IdMatch
    #     #     Venue: 'Away' or 'Home'. It affects the columns to choose
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same pandasframe matrix with the values of each player 
    #                     
    # =============================================================================

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


if __name__ == "__main__":
    main()