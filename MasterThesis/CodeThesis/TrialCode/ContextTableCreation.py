# -*- coding: utf-8 -*-
"""
Created on Mon May 21 22:59:08 2018

@author: Carles
"""

import MySQLdb
import time
import warnings

class SQLContextTableCreation(object):
    
    def __init__(self):
    # =============================================================================
    #     ### Args:
    #     #    None
    #     ###Return:
    #     # db_connection:  Connexion to MySQLdb for the dataset nhl
    #     # db_cursor: db_cursor being part of the conexion from db_connection
    #      #                
    # =============================================================================
        #Creating a list of variables,  that are basic for the usage of SQL
        self.db_connection = ""
        self.db_cursor = ""
        
        #### Initialization of the variables
        
        self.SQLConnection()

    def SQLConnection(self, var ="init"):
        # =============================================================================
        #     ### Description: Initialize/ Close MySQLdb Connection
        #     ### Args:
        #     #     var: If var = "close", connection is closed
        #     ###Return:
        #     # self.db_connection:  Connexion to MySQLdb for the dataset nhl
        #     # self.db_cursor: db_cursor being part of the conexion from db_connection
        #                     
        # =============================================================================
        
        if var == "close":
            print("connection close")
            
            self.db_connection= self.db_connection.close()
            pass
        else:
            self.db_connection = MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306, 
                                    db='nhl', 
                                    user='root', 
                                    passwd='')
        
            self.db_cursor = self.db_connection.cursor()
            print("connexion stablished")
            pass
         
    def CreateTable_play_by_play_eventsfiltered(self):
        # =============================================================================
        #     ### Description: ## It creates the table to work in from sratch
        #     ### Args:
        #     #     None
        #     ###Return:
        #     #     None                   
        # =============================================================================
    
        #self.db_cursor.execute("DROP TABLE play_by_play_eventsfiltered")
        query =   """
            CREATE TABLE play_by_play_eventsfiltered
                SELECT * 
            FROM
                play_by_play_events
            WHERE
              GameId >= 2007020001
            """   
        self.db_cursor.execute(query)
        
        ## Adding indexes
        self.db_cursor.execute("ALTER TABLE play_by_play_eventsfiltered ADD INDEX (EventNumber)")
        self.db_cursor.execute("ALTER TABLE play_by_play_eventsfiltered ADD INDEX (GameId)")

        ## Adding Zone, EventTypeContext, MD= ManPower differential , GD = Goal differential
        #1
        queryZone = """ALTER TABLE play_by_play_eventsfiltered
            ADD Zone varchar(255)"""
        self.db_cursor.execute(queryZone)
        #2
        queryEventTypeContext = """ALTER TABLE play_by_play_eventsfiltered
            ADD EventTypeContext varchar(255)"""
        self.db_cursor.execute(queryEventTypeContext)
        #3
        queryMD= """ALTER TABLE
          play_by_play_eventsfiltered
          ADD  MD int"""
        self.db_cursor.execute(queryMD)
        
        #4
        queryGD= """ALTER TABLE
          play_by_play_eventsfiltered
          ADD  GD int"""
        self.db_cursor.execute(queryGD)
        print("variables Adding Zone, EventTypeContext, MD= ManPower differential , GD = Goal differential to table play_by_play_eventsfiltered")
        pass

    def eventType(self,case):    
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
    
    
    def AwayHomewriting(self, Res, eventType):
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
            warnings.warn(
            "UNSPECIFIED HAS BEEN RETURNED, CHECK ",
            PendingDeprecationWarning
            )
        return eventType    
    
    def indexing(self, event):
        # =============================================================================
        #     ### Description: ## It creates the table to work in from sratch
        #     ### Args:
        #     #     event: a charachter variable giving an event from the column EventType
        #     ###Return:
        #     #     It Adds as index in SQL the the id of each table according to eventType function
        # =============================================================================
    
        TeamId, TableName, ExternalIdName = self.eventType(event)
        if TableName != "":
            query = "ALTER TABLE "+ TableName + " ADD INDEX ( "+ ExternalIdName + ")"
            self.db_cursor.execute(query)
        pass
    
    def updateGD(self, Id):
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
        
        Id = int(Id[0])
        GD = 0
        self.db_cursor.execute(""" SELECT EventTypeContext, ExternalEventId
                          FROM play_by_play_eventsfiltered 
                          WHERE GameId = %s  
                          ORDER BY EventNumber ASC
                          """, ((Id),))
        EventTypeContextvar = self.db_cursor.fetchall()
    
        for tup in range(len(EventTypeContextvar)):
            
            if EventTypeContextvar[tup][0] == "AWAY:GOAL":
                GD = GD - 1
            elif EventTypeContextvar[tup][0] == "HOME:GOAL":
                GD = GD + 1
            else:
                pass
            query = "".join([
                            "UPDATE play_by_play_eventsfiltered ",
                            "SET GD = ", str(GD) , 
                           " WHERE play_by_play_eventsfiltered.GameId = " , str(Id), " AND ",
                             "play_by_play_eventsfiltered.ExternalEventId = ", str(EventTypeContextvar[tup][1])])
            self.db_cursor.execute(query)        
        self.db_connection.commit()   
        print("Time: "+str(time.time() - start))
        pass     
    
    def updatecontextZone(self, Id):
        # =============================================================================
        #     ### Description:  It updates the value of "Zone" and "EventTypeContext" columns from 
        #                       table  play_by_play_eventsfiltered Adding who does the action on "EventTypeContext"
        #                        for Away or Home team
        #     ### Args:
        #     #     Id: Id type is a tuple of one number being a long type (e.g. (2013020001L,))
        #     ###Return:
        #     #     None
        # =============================================================================
    
        start = time.time()
        
        Id = int(Id[0])   
         
        self.db_cursor.execute(""" SELECT GameId, EventType, ExternalEventId, EventNumber  
                          FROM play_by_play_eventsfiltered 
                          WHERE GameId = %s  
                          ORDER BY EventNumber ASC
                          """, ((Id),))
        byGameId = self.db_cursor.fetchall()
        for tup in range(len(byGameId)):
            TeamId, TableName, ExternalIdName = self.eventType(byGameId[tup][1]) #Eventtype column being 1 
            externalEventId = int(byGameId[tup][2]) #ExternalEventId column being 2
            eventNumber = int(byGameId[tup][3])
            if TeamId == "":
                EventContext = byGameId[tup][1]
                Zone = "NULL"
            else:
                self.db_cursor.execute("".join([" SELECT AwayTeamId, HomeTeamId, ", TeamId ,
                                          " , Zone FROM  ", TableName , "  WHERE ",  
                                          ExternalIdName," = ", str(externalEventId)]))
                Res = self.db_cursor.fetchall()                      
                EventContext = self.AwayHomewriting(Res, byGameId[tup][1])
                Zone= Res[0][3]
            query = "".join([
                        "UPDATE play_by_play_eventsfiltered ",
                        " SET Zone = '", str(Zone) ,"' ,", 
                            "EventTypeContext  = '", str(EventContext) ,"'",
                       " WHERE play_by_play_eventsfiltered.GameId = " , str(Id), " AND ",
                         "play_by_play_eventsfiltered.ExternalEventId = ", str(externalEventId),
                        " AND play_by_play_eventsfiltered.EventNumber = ", str(eventNumber)])

            self.db_cursor.execute(query)        
        self.db_connection.commit()
                
        print("Time: "+str(time.time() - start))
        pass
    
    def UpdateMD(self):
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
                     FROM ( SELECT tab1.GameId, tab1.EventNumber,      
                          IF(tab1.HomePlayer1 is null, 0, 1) + IF(tab1.HomePlayer2 is null, 0, 1) + IF(tab1.HomePlayer3 is null, 0, 1) + IF(tab1.HomePlayer4 is null, 0, 1) + IF(tab1.HomePlayer5 is null, 0, 1) + IF(tab1.HomePlayer6 is null, 0, 1) + IF(tab1.HomePlayer7 is null, 0, 1) + IF(tab1.HomePlayer8 is null, 0, 1) + IF(tab1.HomePlayer9 is null, 0, 1) -
                          IF(tab1.AwayPlayer1 is null, 0, 1) - IF(tab1.AwayPlayer2 is null, 0, 1) - IF(tab1.AwayPlayer3 is null, 0, 1) - IF(tab1.AwayPlayer4 is null, 0, 1) - IF(tab1.AwayPlayer5 is null, 0, 1) - IF(tab1.AwayPlayer6 is null, 0, 1) - IF(tab1.AwayPlayer7 is null, 0, 1) - IF(tab1.AwayPlayer8 is null, 0, 1) - IF(tab1.AwayPlayer9 is null, 0, 1)  AS MD
                FROM
                     (SELECT * FROM play_by_play_eventsfiltered ) tab1 ) i
                WHERE play_by_play_eventsfiltered.GameId = i.GameId AND
                     play_by_play_eventsfiltered.EventNumber = i.EventNumber)
            
            """
        self.db_cursor.execute(queryMD)
        self.db_connection.commit()
        pass
        
    def ZoneBugsSolver(self):
        ZoneBugs = ['None',0, 10,11,12,13,14,15,17,18,24,25,26,29,30,38,42,47,48,5,6,63,65,67, 8467412]
        for indexZoneBugs in range(len(ZoneBugs)): 
            print(ZoneBugs[indexZoneBugs])
            queryZone = "".join(["SELECT GameId, EventType, ExternalEventId, EventNumber FROM play_by_play_eventsfiltered WHERE Zone = '", str(ZoneBugs[indexZoneBugs]),"'"])                
            self.db_cursor.execute(queryZone)
            Data = self.db_cursor.fetchall()   
            for tup in range(len(Data)):
                TeamId, TableName, ExternalIdName = self.eventType(Data[tup][1]) #Eventtype column being 1 
                externalEventId = int(Data[tup][2]) #ExternalEventId column being 2
                EventNumber = int(Data[tup][3])
                if TeamId == "":
                    Zone = "NULL"        
                else:
                    myquery = "".join([" SELECT GameId, AwayTeamId, HomeTeamId, ", TeamId ,
                                              ", Zone FROM  ", TableName , "  WHERE ",
                                              ExternalIdName," = ", str(externalEventId), 
                                              " AND EventNumber  = ", str(EventNumber)])
                    self.db_cursor.execute(myquery)
                    Res = self.db_cursor.fetchall()
                    
                    Zone= Res[0][4]
                                ### Manual Checking of mistakes in the Big Database
                    if Zone == None:
                        Zone = "NULL"
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
                self.db_cursor.execute(query)        
                print(tup)    
            self.db_connection.commit()
        pass
