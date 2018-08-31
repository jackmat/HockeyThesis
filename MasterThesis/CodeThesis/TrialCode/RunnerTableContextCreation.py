# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 15:18:49 2018

@author: Carles
"""
import sys
path = "C:/Users/Carles/Desktop/HockeyThesis/ThesisHockeyMDP/Code/EvaluatedCode"
sys.path.append(path)
from ContextTableCreation import SQLContextTableCreation


def ContextTableCreation(num):
    # =============================================================================
    #### Description- Args - Returns
    #       # Working Functions
    #       # 0. Initialize var = SQLContextTableCreation()
    #       # (1). CreateTable_play_by_play_eventsfiltered  to create the tables
    #       #     For the calculations to go faster, use function indexing(events) for the events table that you want to put SQL indexes in
    #       # (2) Adding indexes in the main table manually
    #       # (3) updatecontextZone(id)
    #       # (4) updateGD(id)
    #       # (5) updateMD
    ##### Args:
    #       # num = list containing int numbers 1 to 5. Result of the numbers explained in description
    # =============================================================================
    
    ##Specifically
    ### 0. Initialize var = SQLContextTableCreation()
    
    
    TableCreation = SQLContextTableCreation()
    if 1 in num:
    # (1). CreateTable_play_by_play_eventsfiltered  to create the tables
        TableCreation.CreateTable_play_by_play_eventsfiltered()
        print("Table Created")
            # Adding indexes in the main table manually
        query = "ALTER TABLE play_by_play_eventsfiltered ADD INDEX ( ExternalEventId)"
        TableCreation.db_cursor.execute(query)
        print("Indexing done")
    
    if 2 in num:
    # (2). For the calculations to go faster, use function indexing(events) for the events table that you want to put SQL indexes in
    #### Indexing distinct variable types to make ADD INDEX()
        query = """            
            Select DISTINCT(EventType)
            FROM
                play_by_play_events
            WHERE
              GameId >= 2007020001
                    """
        TableCreation.db_cursor.execute(query)
        DistinctEvents= TableCreation.db_cursor.fetchall()                   
        [TableCreation.indexing(DistinctEvents[indEvent][0]) for indEvent in range(len(DistinctEvents))]
        
        
    if 3 in num or 4 in num:
    # General code for 3 and 4
        query = """            
            Select DISTINCT(GameId)
            FROM
                play_by_play_eventsfiltered
                    """
                    
        TableCreation.db_cursor.execute(query)
        diffGameId = TableCreation.db_cursor.fetchall() ##Selecting different GameID
        
        
        counter = len(diffGameId)
        iterlength = len(diffGameId)
    
    if 3 in num:
        # (3) updatecontextZone(id)
        for indexdiff in range(iterlength):    
            ### For each distinct GameId
            Idcurrent= diffGameId[indexdiff] #Store current GameId
            TableCreation.updatecontextZone(Idcurrent)
            counter -= 1
            print(counter)
    
    if 4 in num:    
        # (4) updateGD(id)
        for indexdiff in range(iterlength):    
            ### For each distinct GameId
            Idcurrent= diffGameId[indexdiff] #Store current GameId
            TableCreation.updateGD(Idcurrent)
            counter -= 1
            print(counter)
    if 5 in num: 
        # (5) updateMD
        TableCreation.UpdateMD()
    print("Work finalized")
    TableCreation.SQLConnection(var = "close")
    pass
    

### number of processes to operate
mylist = [1,2]
ContextTableCreation(mylist)