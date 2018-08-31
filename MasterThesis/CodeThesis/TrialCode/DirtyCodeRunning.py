# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 17:31:10 2018

@author: Carles
"""

import MySQLdb
import time

global db_connection, db_cursor    


            

def eventType(case):    
    # =============================================================================
    #     ### Description: Choosing which table to reference in case of a Specific event
    #     ### Args:
    #     #     case: a characther variable containing from the Eventtype column
    #     ###Return:
    #     #     it returns TeamId, TableName, ExternalIdName to reference inside the function
    #                     
    # =============================================================================

    if case == "FACEOFF" :
    	TeamId = "FaceoffWinningTeamId"
    	TableName = "event_faceoff"
    	ExternalIdName = "FaceoffId"
    	return TeamId, TableName, ExternalIdName
    
    elif case == "HIT" :
    	TeamId = "HittingTeamId"
    	TableName = "Event_Hit"
    	ExternalIdName = "HitId"
    	return TeamId, TableName, ExternalIdName
    
    elif  case == "GOAL" :
    	TeamId = "ScoringTeamId"
    	TableName = "Event_Goal"
    	ExternalIdName = "GoalId"
    	return TeamId, TableName, ExternalIdName
    elif case == "SHOT" :
    	TeamId = "ShotByTeamId"
    	TableName = "Event_Shot"
    	ExternalIdName = "ShotId"
    	return TeamId, TableName, ExternalIdName
    elif case == "MISSED SHOT" :
    	TeamId = "MissTeamId"
    	TableName = "Event_Missed_Shot"
    	ExternalIdName = "MissId"
    	return TeamId, TableName, ExternalIdName
    elif case == "BLOCKED SHOT" :
    	TeamId = "BlockTeamId"
    	TableName = "Event_Blocked_Shot"
    	ExternalIdName = "BlockId"
    	return TeamId, TableName, ExternalIdName
    elif case =="GIVEAWAY" :
    	TeamId = "GiveawayTeamId"
    	TableName = "Event_Giveaway"
    	ExternalIdName = "GiveawayId"
    	return TeamId, TableName, ExternalIdName
    elif case == "TAKEAWAY" :
    	TeamId = "TakeawayTeamId"
    	TableName = "Event_Takeaway"
    	ExternalIdName = "TakeawayId"
    	return TeamId, TableName, ExternalIdName
    elif case == "PENALTY" :
    	TeamId = "TeamPenaltyId"
    	TableName = "event_penalty"
    	ExternalIdName = "PenaltyId"
    	return TeamId, TableName, ExternalIdName
    else:
    	print("")
    	TeamId, TableName, ExternalIdName = "", "",""
    	return TeamId, TableName, ExternalIdName


def AwayHomewriting(Res, eventType):
    # =============================================================================
    #     ### Description: Choosing which table to reference in case of a Specific event
    #     ### Args:
    #     #     Res : a vector wih the following columns: AwayTeamId, HomeTeamId, ", TeamId ," 
    #     #     eventType: character variable  coming from EventType column
    #     ###Return:
    #     #     it returns a string of eventType with either "Home" or "Away" associated
    #                     
    # =============================================================================

    if(Res[0][0] == Res[0][2]): # if AwayTeamId == TeamId:
        eventType = "AWAY:" + eventType
        
    elif (Res[0][1] == Res[0][2]): # if HomeTeamId == TeamId:
        eventType = "HOME:" + eventType
    else:
        eventType = "UNSPECIFIED:" + eventType;
        
    return eventType    

def indexing(event):
    # =============================================================================
    #     ### Description: ## It creates the table to work in from sratch
    #     ### Args:
    #     #     event: a charachter variable giving an event from the column EventType
    #     ###Return:
    #     #     It Adds as index in SQL the the id of each table according to eventType function
    # =============================================================================

    TeamId, TableName, ExternalIdName = eventType(event)
    if TableName != "":
        query = "ALTER TABLE "+ TableName + " ADD INDEX ( "+ ExternalIdName + ")"
        db_cursor.execute(query)
    pass



def updateGD(Id):
    # =============================================================================
    #     ### Description:  It updates the value GD column from table to play_by_play_eventsfiltered
    #        to Goal Differential, being + numbers that home Wins and negative that Away Wins
    #        Warning usage: ONLY USABLE IF "EventTypeContext" column different than NULL
    #     ### Args:
    #     #     Id: Id type is a tuple of one number being a long type (e.g. (2013020001L,))
    #     ###Return:
    #     #     None
    # =============================================================================

    start = time.time()
    
#    Id = int(Id[0])
    GD = 0
    db_cursor.execute(""" SELECT EventTypeContext, UniqueId, EventNumber
                      FROM play_by_play_eventsfiltered 
                      WHERE GameId = %s  
                      ORDER BY EventNumber ASC
                      """, ((Id),))
    EventTypeContextvar = db_cursor.fetchall()
        
    
    for tup in range(len(EventTypeContextvar)):
        Eventtype = EventTypeContextvar[tup][0] 
        UniqueId = int(EventTypeContextvar[tup][1]) 
        
        if Eventtype == "AWAY:GOAL":
            GD = GD - 1
        elif Eventtype == "HOME:GOAL":
            GD = GD + 1
        else:
            pass
        query = "".join([
                        "UPDATE play_by_play_eventsfiltered ",
                        "SET GD = ", str(GD) , 
                       " WHERE play_by_play_eventsfiltered.UniqueId = " , str(UniqueId)])
        db_cursor.execute(query)        
    db_connection.commit()   
    print("Time: "+str(time.time() - start))
    pass     

def updatecontextZone(Id):
    # =============================================================================
    #     ### Description:  It updates the value of "Zone" and "EventTypeContext" columns from 
    #                       table  play_by_play_eventsfiltered to ManPower Differential, 
    #                       being + numbers that home has more players and negative viceversa for Away Team
    #     ### Args:
    #     #     Id: Id type is a tuple of one number being a long type (e.g. (2013020001L,))
    #     ###Return:
    #     #     None
    # =============================================================================

    start = time.time()
    
#    Id = int(Id[0])
     
    db_cursor.execute(""" SELECT GameId, EventType, ExternalEventId, EventNumber, UniqueId  
                      FROM play_by_play_eventsfiltered 
                      WHERE GameId = %s  
                      ORDER BY EventNumber ASC
                      """, ((Id),))
    byGameId = db_cursor.fetchall()
    for tup in range(len(byGameId)):
        TeamId, TableName, ExternalIdName = eventType(byGameId[tup][1]) #Eventtype column being 1 
        externalEventId = int(byGameId[tup][2]) #ExternalEventId column being 2
        eventNumber = int(byGameId[tup][3])
        UniqueId = int(byGameId[tup][4])
        if TeamId == "":
            EventContext = byGameId[tup][1]
            Zone = "NULL"
        else:
            db_cursor.execute("".join([" SELECT AwayTeamId, HomeTeamId, ", TeamId ,
                                      " , Zone FROM  ", TableName , "  WHERE ",  
                                      ExternalIdName," = ", str(externalEventId)]))
            Res = db_cursor.fetchall()                      
            EventContext = AwayHomewriting(Res, byGameId[tup][1])
            Zone= Res[0][3]
        query = "".join([
                    "UPDATE play_by_play_eventsfiltered ",
                    " SET Zone = '", str(Zone) ,"' ,", 
                        "EventTypeContext  = '", str(EventContext) ,"'",
                   " WHERE play_by_play_eventsfiltered.UniqueId = " , str(UniqueId)])

        db_cursor.execute(query)        
    db_connection.commit()
            
    print("Time: "+str(time.time() - start))
    pass



def UpdateMD():
    # =============================================================================
    #     ### Description:  It updates the value of "MD" ManPower Differntial
    #                       #                       being + numbers that home has more players and negative viceversa for Away Team
    #     ### Args:
    #     #     None
    #     ###Return:
    #     #     None
    # =============================================================================

    queryMD = """  
            UPDATE play_by_play_eventsfiltered 
            SET MD = (
                 SELECT i.MD
                 FROM ( SELECT tab1.UniqueId,      
                      IF(tab1.HomePlayer1 is null, 0, 1) + IF(tab1.HomePlayer2 is null, 0, 1) + IF(tab1.HomePlayer3 is null, 0, 1) + IF(tab1.HomePlayer4 is null, 0, 1) + IF(tab1.HomePlayer5 is null, 0, 1) + IF(tab1.HomePlayer6 is null, 0, 1) + IF(tab1.HomePlayer7 is null, 0, 1) + IF(tab1.HomePlayer8 is null, 0, 1) + IF(tab1.HomePlayer9 is null, 0, 1) -
                      IF(tab1.AwayPlayer1 is null, 0, 1) - IF(tab1.AwayPlayer2 is null, 0, 1) - IF(tab1.AwayPlayer3 is null, 0, 1) - IF(tab1.AwayPlayer4 is null, 0, 1) - IF(tab1.AwayPlayer5 is null, 0, 1) - IF(tab1.AwayPlayer6 is null, 0, 1) - IF(tab1.AwayPlayer7 is null, 0, 1) - IF(tab1.AwayPlayer8 is null, 0, 1) - IF(tab1.AwayPlayer9 is null, 0, 1)  AS MD
            FROM
                 (SELECT * FROM play_by_play_eventsfiltered ) tab1 ) i
            WHERE play_by_play_eventsfiltered.UniqueId = i.UniqueId)
        
        """
    db_cursor.execute(queryMD)
    db_connection.commit()
    pass

## Running queries 3 and 4
def ContextVariablesCreation():
# =============================================================================
#     ###INDEXING
#    query = """            
#     Select DISTINCT(EventType)
#     FROM
#         play_by_play_eventsfiltered
#     WHERE
#       GameId >= 2007020001
#             """
#     db_cursor.execute(query)
#     DistinctEvents= db_cursor.fetchall()                   
#     [indexing(DistinctEvents[indEvent][0]) for indEvent in range(len(DistinctEvents))]
# 
# =============================================================================

    
    query = """            
                Select DISTINCT(GameId)
                FROM
                    play_by_play_eventsfiltered
                        """
                        
    db_cursor.execute(query)
    diffGameId = db_cursor.fetchall() ##Selecting different GameID
    ###Manipulation of data
    left = diffGameId
    leftlist= map(list, left)
    leftlist2= [val[0] for val in leftlist]
    numleft = map(int, leftlist2)
    ####
    
    counter = len(numleft)
    iterlength = len(numleft)
    

    ############ (3) updatecontextZone(id)
    print("Context and Zone starting to be calculated")
    for indexdiff in range(iterlength):    
        ### For each distinct GameId
        Idcurrent = numleft[indexdiff] #Store current GameId
        updatecontextZone(Idcurrent)
        counter -= 1
        print(counter)
    ########## (4) updateGD(id)
    counter = len(numleft)
    iterlength = len(numleft)
    print("GD starting to be calculated")
    for indexdiff in range(iterlength):    
        ### For each distinct GameId
        Idcurrent= numleft[indexdiff] #Store current GameId
        updateGD(Idcurrent)
        counter -= 1
        print(counter)
    ###########################
    print("MD starting to be calculated")
    UpdateMD()
    pass    


######### Zone None Cleaning
def ZoneBugsSolver():
    query = """ UPDATE play_by_play_eventsfiltered 
                SET Zone = 'offensive'
                WHERE play_by_play_eventsfiltered.GameId = 2013020617 AND 
                play_by_play_eventsfiltered.ExternalEventId = 3531  
                """
    db_cursor.execute(query)        
    db_connection.commit()   
    
    ZoneBugs = [0, 10,11,12,13,14,15,17,18,24,25,26,29,30,38,42,47,48,5,6,63,65,67, 8467412]
    for indexZoneBugs in range(len(ZoneBugs)): 
        print(ZoneBugs[indexZoneBugs])
        queryZone = "".join(["SELECT GameId, EventType, ExternalEventId, EventNumber FROM play_by_play_eventsfiltered WHERE Zone = '", str(ZoneBugs[indexZoneBugs]),"'"])                
        db_cursor.execute(queryZone)
        Data = db_cursor.fetchall()   
        for tup in range(len(Data)):
            TeamId, TableName, ExternalIdName = eventType(Data[tup][1]) #Eventtype column being 1 
            externalEventId = int(Data[tup][2]) #ExternalEventId column being 2
            EventNumber = int(Data[tup][3])
            if TeamId == "":
                Zone = "NULL"        
            else:
                myquery = "".join([" SELECT GameId, AwayTeamId, HomeTeamId, ", TeamId ,
                                          ", Zone FROM  ", TableName , "  WHERE ",
                                          ExternalIdName," = ", str(externalEventId), 
                                          " AND EventNumber  = ", str(EventNumber)])
                db_cursor.execute(myquery)
                Res = db_cursor.fetchall()
                
                Zone= Res[0][4]
                            ### Manual Checking of mistakes in the Big Database
                if Zone == None:
                    Zone = "NULL"
                elif Zone == 'offensive':
                    Zone = "offensive"
                elif int(Zone) in [10,11,12,13,14,15,17,18,24,25,26,29,30,38,42,47,48,5,6,63,65,67]:    
                    Zone = "offensive"
                elif int(Zone) in [0,8467412]:
                    Zone = "NULL"    
                print(Zone)    
            query = "".join([
                        "UPDATE play_by_play_eventsfiltered ",
                        " SET Zone = '", Zone ,"' ",
                       " WHERE play_by_play_eventsfiltered.GameId = " , str(int(Data[tup][0])), 
                       " AND play_by_play_eventsfiltered.EventNumber = ", str(EventNumber)])
            db_cursor.execute(query)        
            print(tup)    
        db_connection.commit()
    pass

ZoneBugsSolver()
def ZoneCorrections():
    ### Passing None and unspecified to NULL        
    updateZone= """
    UPDATE play_by_play_eventsfiltered
    SET   Zone = 'NULL'
    WHERE Zone = 'None' OR Zone = 'unspecified'
    """
    db_cursor.execute(updateZone)
    db_connection.commit()
    pass
ZoneCorrections()
# =============================================================================
# =============================================================================
# db_cursor.execute("set innodb_lock_wait_timeout=100")
# db_cursor.execute("show variables like 'innodb_lock_wait_timeout'")
# db_cursor.fetchall()
# db_cursor.execute("show full processlist")
# db_cursor.execute("kill ")
# db_cursor.fetchall()
# 
# =============================================================================
# =============================================================================

def MdCorrections():
        
    updateMD= """
    UPDATE play_by_play_eventsfiltered
    SET   MD = 0
    WHERE MD > 3 
    AND (EventType = 'PERIOD START' OR EventType = 'PERIOD END' OR 
         EventType = 'GAME END' OR EventType = 'EARLY INTERMISSION END'
         OR EventType = 'GAME OFF')
    """
    db_cursor.execute(updateMD)
    db_connection.commit()
    
    updateMD= """
    UPDATE play_by_play_eventsfiltered
    SET   MD = 0
    WHERE MD <- 3 
    AND (EventType = 'PERIOD START' OR EventType = 'PERIOD END' OR 
         EventType = 'GAME END' OR EventType = 'EARLY INTERMISSION END'
         OR EventType = 'GAME OFF')
    """
    db_cursor.execute(updateMD)
    db_connection.commit()
    print("Error EventType changed. Proceding To do MDcorrections2()")
    MDcorrections2()
    pass
def MDcorrections2():
    ## Changing MD to the previous one
    query= """
    SELECT DISTINCT GameId, ExternalEventId, EventNumber, UniqueId FROM play_by_play_eventsfiltered WHERE MD> 3 OR MD < -3"""
    db_cursor.execute(query)
    Res = db_cursor.fetchall()
    for tup in range(len(Res)):
        GameId = int(Res[tup][0])
        EventNumber = int(Res[tup][2])
        UniqueId = int(Res[tup][3])
        querysearch = "".join(["SELECT MD FROM play_by_play_eventsfiltered", 
                               " WHERE GameId = " , str(GameId), 
                    " AND EventNumber = ", str(EventNumber-1)])
        db_cursor.execute(querysearch)
        MDres = db_cursor.fetchall()
        if MDres ==():
            MD = 0 
        else: 
            MD = int(MDres[0][0])
        
        query = "".join([
                        "UPDATE play_by_play_eventsfiltered ",
                        " SET MD = ", str(MD) , 
                       " WHERE UniqueId = " , str(UniqueId)])
        db_cursor.execute(query)
        print(tup)        
    db_connection.commit()
    pass

MdCorrections()


# =============================================================================
# db_cursor.execute("ALTER TABLE workcontextevents add column TeamId int")
# db_cursor.execute("ALTER TABLE workcontextevents add column PlayerId int")
# =============================================================================

====================================================

    
    



    
#    Id = int(Id[0])
def PlayerIdUpdate(Id):
    
    start = time.time()
    db_cursor.execute(""" SELECT GameId, EventType, ExternalEventId, EventNumber, EventTypeContext, UniqueId  
                      FROM workcontextevents 
                      WHERE GameId = %s  
                      ORDER BY EventNumber ASC
                      """, ((Id),))
    byGameId = db_cursor.fetchall()
    for tup in range(len(byGameId)):
        externalEventId = int(byGameId[tup][2]) #ExternalEventId column being 2
        eventNumber = int(byGameId[tup][3])
        eventTypeContext =byGameId[tup][4]
        UniqueId = int(byGameId[tup][5])
        PlayerId= None
        PlayerColumnId = None
         
        if byGameId[tup][1] in ['GIVEAWAY','HIT', 'MISSED SHOT', 'PENALTY', 'TAKEAWAY']:
            PlayerTableId ='PlayerId'
        elif eventTypeContext == "AWAY:FACEOFF":
            PlayerColumnId='AwayPlayerId'
        elif eventTypeContext == "HOME:FACEOFF":
            PlayerColumnId='HomePlayerId'    
        elif byGameId[tup][1] == 'GOAL':            
            PlayerColumnId='GoalScorerId'
        elif byGameId[tup][1] == 'SHOT':            
            PlayerColumnId='ShootingPlayerId'
        else: 
            pass
        if PlayerColumnId != None:
            TeamId, TableName, ExternalIdName = eventType(byGameId[tup][1]) #Eventtype column being 1 
            db_cursor.execute("".join([" SELECT ", PlayerColumnId,
                                      " FROM  ", TableName , "  WHERE ",  
                                      ExternalIdName," = ", str(externalEventId)]))
            PlayerIdtup = db_cursor.fetchall()                      
            PlayerId = PlayerIdtup[0][0]
         
            
            query = "".join([
                        "UPDATE workcontextevents ",
                        " SET PlayerId = '", str(PlayerId), "' ",
                       " WHERE workcontextevents.UniqueId = " , str(UniqueId)])
            db_cursor.execute(query)
        else: 
            pass
    db_connection.commit()
            
    print("Time: "+str(time.time() - start))
    pass


query = """            
                Select DISTINCT(GameId)
                FROM
                    workcontextevents
                        """
                        
db_cursor.execute(query)
diffGameId = db_cursor.fetchall() ##Selecting different GameID
###Manipulation of data
left = diffGameId
leftlist= map(list, left)
leftlist2= [val[0] for val in leftlist]
numleft = map(int, leftlist2)
####

counter = len(numleft)
iterlength = len(numleft)
for indexdiff in range(iterlength):    
    ### For each distinct GameId
    Idcurrent = numleft[indexdiff] #Store current GameId
    PlayerIdUpdate(Idcurrent)
    counter -= 1
    print(counter)