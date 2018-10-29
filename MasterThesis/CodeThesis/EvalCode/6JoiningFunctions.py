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
    #                               +/-, Value, Time, 
    #                        (3) For each distinct teamId in the table: 
    #                               Calculates time Players play per match
    #                               Calculates valuation of players per match
    #                        (4) Everything is put in one big pd.Dataframe
    #                        (5) Metrics created: 
    #                               Time per match (sec)
    #                               Value per match
    #                               PlusMinus Markov metric per match
    #
    #     ### Args:
    #    ###Return:
    #     #     It saves the two pd.Dataframe metrics into
    #               path + 'PlayerValMatrix.csv'
    #               path + 'PlayerbyTimeValMatrix.csv' 
    #               path + 'PlusMinusMatrix.csv'      
    # =============================================================================

    d= MySQLdb.connect(host = '127.0.0.1',
                                port = 3306, 
                                db='nhl', 
                                user='root', 
                                passwd='')
    
    c= d.cursor()
    
    
    for Season in range(2007,2015):
        print(Season)
#    Season = 2007
        PlayerValueMat = IndexByTeamSeason(Season,d,c)
        print("Value Matrix created")
        PlayerTimePlayer = IndexByTeamSeason(Season,d,c)
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
#team=0            

            Team = RangeTeam[team]

            TimeMat = PlayerTimePlayer[team] #change 0 to team
            ValueMat = PlayerValueMat[team]
            PlusMinMat = PlusMinus[team] 
            PlayerValueMat[team], PlusMinus[team],  PlayerTimePlayer[team] = ValuePlusMinusTimeFunc(Team = Team , 
                          pandasframe = ValueMat,
                          pandasframe2 = PlusMinMat,
                          pandasframe3 = TimeMat,
                          c = c ,
                          d = d)
        #### Fulljoin of matrices by counter for both metrics    
        #(1) Plus/min Matrix
        PlusMinMatrix = JoinListpdMatrices(PlusMinus)
        #(2) Val (This one is already PlayerValueMat)
        ValMat = JoinListpdMatrices(PlayerValueMat)
        #(3) Time played by each player
        PlayedTimePerMatch = JoinListpdMatrices(PlayerTimePlayer)        
        
        #(4) Store it to pass it to R 
        ValMat.to_csv(path + str(Season)+'PlayerValMatrix.csv')
        PlayedTimePerMatch.to_csv(path +str(Season)+ 'PlayerbyTimeValMatrix.csv') 
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

def ValuePlusMinusTimeFunc(Team, pandasframe, pandasframe2, pandasframe3, c,d):
    ### 
    # =============================================================================
    #     ### Description: For each match in the pd.Dataframe, select players and GameId, eventnum, typeEvent, EventTime
    #                       and calculate the (1) valuation of that player inside the team 
    #                                         (2) plus minus metric for that team
    #                                         (3) Time played by player in each match
    #     ### Args:
    #     #     Team: the team Id. If it is not correct for the matrix, problems will arise
    #     #     pandasframe: pd.Dataframe of columns[Match,Counter, id_players...] for the calculation  of Individual Valuation
    #     #     pandasframe2: pd.Dataframe of columns[Match,Counter, id_players...] for the calculation  of collective plus minus Valuation
    #     #     pandasframe3: pd.Dataframe of columns[Match,Counter, id_players...] for the calculation  of Time played by player  
    #     #     c: cursor
    #     #     d: db_connection
    #                    
    #    ###Return:
    #     #     It returns the same 3 pandasframe matrix with the values of each player 
    #                     
    # =============================================================================

    d_state_graph = MySQLdb.connect(host = '127.0.0.1',
                                port = 3306, 
                                db='state_graph_2', 
                                user='root', 
                                passwd='')
    c_state_graph= d_state_graph.cursor()
    
    Matches = pandasframe.GameId.values   
    Mat = pandasframe
    Mat2 = pandasframe2
    Mat3 = pandasframe3
    for match in range(len(Matches)):
        PrevTime = datetime.timedelta(0,0)
        CurrentTime= datetime.timedelta(0,0)
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
#i = 2            
            EventNumber =  EventIndex [i][0]
#            print(MatchId, EventNumber)
            if i >0: 
                PrevTime = CurrentTime                
                PrevEventType = CurEventType
            else: 
                PrevTime = datetime.timedelta(0,0)
            PlayersPlayed = UniqueplayersperEvent(MatchId, Venue, d, EventNumber).astype(str).tolist()
            if PlayersPlayed != []:
                PlayersPlayed2 = [item for sublist in PlayersPlayed for item in sublist]
    
                       
            query = """
                    SELECT EventType, PlayerId, EventTime
                    FROM q_fulltable
                    WHERE GameId = {1}
                    AND EventNumber = {2}
            """.format(Venue, MatchId, EventNumber)
            c.execute(query)
            result = c.fetchall()
            CurEventType = result[0][0]
            PlayerId = result[0][1]
            CurrentTime = result[0][2]
            ### Calculation of Matrices for time (Mat3)
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
                if DiffTime>350:
                    print(MatchId, EventNumber, DiffTime, CurrentTime, PrevTime, CurEventType, PrevEventType)
                    DiffTime = 0
                Mat3.loc[pandasframe3.index[Index], PlayersPlayed2] += DiffTime

            # If CurEventType in Action_Events:
            ### select probability of next Event performed (by another player)
            ###### if next event is an action as well,  my action has an effect, therefore impact and so DiffValue
            ###### else  DiffValue = 0
            ### Calculation of Matrices for Value and PlusMins (Mat, Mat2)
            if CurEventType in ACTION_EVENTS:
                if PlayerId != '':
                    query = """SELECT * FROM `node_info`   
                            WHERE GameId = {0} and EventNumber = {1}
                            """.format(MatchId, EventNumber)
                    c_state_graph.execute(query)
                    result = c_state_graph.fetchall()
                    From_id = result[0][2]
                    To_id = result[0][3]
                    
                    query = """ SELECT * FROM q_table
                    WHERE NodeId = {0} """.format(From_id)
                    c.execute(query)
                    myres = c.fetchall()
                    
################################################## Need to check in this part the number
                    if Venue == "home":
                        from_id_value = myres[0][2]
                        
                        query = """ SELECT * FROM q_table
                                WHERE NodeId = {0} """.format(To_id)
                        c.execute(query)
                        result = c.fetchall()
                        to_id_value = result[0][2]
                    elif Venue == "away":
                        from_id_value = myres[0][3]
                        
                        query = """ SELECT * FROM q_table
                                WHERE NodeId = {0} """.format(To_id)
                        c.execute(query)
                        result = c.fetchall()
                        to_id_value = result[0][3]
                    else:
                        print(query, Venue)
                        break;
                        
                    # impact = Q(S*a) - Q(s)
                    action_values = to_id_value - from_id_value
                    try:
                        Mat.loc[pandasframe.index[Index], str(PlayerId)] += action_values # This is Player Val
                        Mat2.loc[pandasframe2.index[Index], PlayersPlayed2] += action_values # This is PlusMinus
                    except KeyError:
                        print(MatchId, EventNumber ,PlayerId, action_values, PlayerId, PlayersPlayed2, "problem!")
                        break

                    
# =============================================================================
#                     FromId, ToId = NodeSelectionFromStateGraph(GameId= MatchId,
#                                               EventNumber= EventNumber,
#                                               c = c_state_graph,
#                                               d=d_state_graph , 
#                                               NodeId = NodeId)
#                     PostVal, PostActionType = NextProbability(NodeId = ToId, 
#                                                               Venue =  Venue,
#                                                               c=c,
#                                                               d=d)
#                     
#                     if str(PlayerId) in list(Mat.columns):                 
#                         if PostActionType in ACTION_EVENTS:
#                             DiffValue = (PostVal - CurVal)
#                         else: 
#                             DiffValue = 0
#                         
#                         Mat.loc[pandasframe.index[Index], str(PlayerId)] += DiffValue # This is Player Val
#                         Mat2.loc[pandasframe2.index[Index], PlayersPlayed2] += DiffValue # This is PlusMinus
#     return Mat, Mat2, Mat3
# =============================================================================
    
# =============================================================================
# def NodeSelectionFromStateGraph(c_state ,d_state, GameId, EventNumber):
#     query="""
#                     SELECT FromId, ToId
#                     FROM edges, node_info
#                     WHERE 
#                     current = FromId
#                     AND GameId = {0}
#                     AND EventNumber = {1}
#                 """.format(GameId, EventNumber)
#     c_state_graph.execute(query)
#     result = c_state_graph.fetchall()
#     try:
#         FromId = result[0][0]
#         NextNode = result[0][1]
#     except IndexError:
#         print(result, GameId, EventNumber, query)
#     return(result)
# 
# =============================================================================
def NodeSelectionFromStateGraph(c_state ,d_state, GameId, EventNumber):
    query="""
                    SELECT ToId
                    FROM node_info, edges
                    WHERE 
                    current = FromId
                    AND GameId = {0}
                    AND EventNumber = {1}
                """.format(GameId, EventNumber)
    c_state_graph.execute(query)
    result = c_state_graph.fetchall()
    try:
        FromId = result[0][0]
        NextNode = result[0][1]
    except IndexError:
        print(result, GameId, EventNumber, query)
    return(result)
                
# =============================================================================
# NodeSelectionFromStateGraph(c_state =c_state_graph, 
#                         d_state = d_state_graph,
#                         GameId = 2007020005,
#                         EventNumber = 2)
# 
# =============================================================================
def NextProbability(NodeId, c,d, Venue ):
    query = """
                    SELECT Prob_next_{0}_goal, EventType
                    FROM q_fulltable
                    WHERE NodeId = {1}
            """.format(Venue, NodeId)
    c.execute(query)
    result = c.fetchall()
    try:
        NextVal = result[0][0]
        PostActionType = result[0][1]
    except IndexError:
        print(NodeId, result, query, Venue)
    return(NextVal, PostActionType)
    
    
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