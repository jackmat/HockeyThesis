# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 16:29:14 2018

@author: Carles
"""

import MySQLdb
import pandas as pd
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"


def main():
    # =============================================================================
    #     ### Description:   (1) Opens MySQLdb connection
    #                        (2) It reads a q_table in a specified path create by MDP value_iteration
    #                               it puts name to its colums
    #                        (3) It merges online play_by_play_events with the MDP file
    #                        (4) It creates a Table Called q_fulltable in the server with all Data
    #                            Variables Prob_next_home_goal and Prob_next_away_goal created
    #     ### Args:
    #    ###Return:
    #     #     Variables Prob_next_home_goal and Prob_next_away_goal created
    #                     
    # =============================================================================

    state_graph_db = MySQLdb.connect(host = '127.0.0.1',
                                        port = 3306,
                                    user="root", 
                                    passwd="", 
                                    db="state_graph_2")
                          
    cursor = state_graph_db.cursor()
    qtable= pd.read_csv(path+"q_table.csv")
    
    ## Establishing column names
    qtable.columns = ["NodeId","GeneralIndex", "expected_goals", "probability_next_home_goal", "probability_next_away_goal"]
    ## Writing table iteration
    Node_info= pd.read_sql_query("SELECT * FROM node_info", state_graph_db )
    ## Passing it to Node_info which stores the reference to each NodeId being current
    Data2 = pd.merge(Node_info, qtable, how='left', left_on=['current'], right_on=['NodeId'])
    
    # Joining also Data from nodes
    Nodes= pd.read_sql_query("SELECT * FROM nodes", state_graph_db )
    Data3 = pd.merge(Data2, Nodes, how='left', left_on=['NodeId'], right_on=['NodeId'])
    FullData= Data3[['GameId', 'EventNumber', 'NodeId','expected_goals',
                   'probability_next_home_goal',  'probability_next_away_goal',
                   'EventType','GD','MD','Period','TeamId','PlayerId','Zone']]
    list(FullData.columns) 
    # ['GameId','EventNumber','NodeId','expected_goals',
    #  'probability_next_home_goal', 'probability_next_away_goal','EventType', 'GD','MD','Period',
    # 'TeamId','PlayerId', 'Zone']
    state_graph_db.close()
    # TableCreation()
    
    
    FullDataVal = FullData.values 
    
    nhl= MySQLdb.connect(host = '127.0.0.1',
                                        port = 3306,
                                    user="root", 
                                    passwd="", 
                                    db="nhl")
                          
    cursor = nhl.cursor()
    totlen = int(FullDataVal.shape[0])
    counter = 0
    FullDataVal[:,0]= FullDataVal[:,0].astype(int).astype(str)
    FullDataVal[:,1]= FullDataVal[:,1].astype(int).astype(str)
    FullDataVal[:,2]= FullDataVal[:,2].astype(int).astype(str)
    FullDataVal[:,3]= FullDataVal[:,3].astype(float).astype(str)
    FullDataVal[:,4]= FullDataVal[:,4].astype(float).astype(str)
    FullDataVal[:,5]= FullDataVal[:,5].astype(float).astype(str)
    FullDataVal[:,6]= FullDataVal[:,6].astype(str)
    FullDataVal[:,7]= FullDataVal[:,7].astype(int).astype(str)
    FullDataVal[:,8]= FullDataVal[:,8].astype(int).astype(str)
    FullDataVal[:,10]= FullDataVal[:,10].astype(str)
    FullDataVal[:,12]= FullDataVal[:,12].astype(str)

    for row in FullDataVal:
        GameId = row[0]
        EventNumber = row[1]
        NodeId= row[2]
        expected_goals = row[3]
        probability_next_home_goal =row[4]
        probability_next_away_goal = row[5]
# =============================================================================
#         if float(row[4])>0:
#             if float(row[5])>0:
#                 probability_next_home_goal =  str(float(row[4])/(float(row[4])+float(row[5])))
#         else:
#             probability_next_home_goal = str(0)
#         if float(row[5])>0:
#             if float(row[4])>0:
#                 probability_next_away_goal = str(float(row[5])/(float(row[4])+float(row[5])))
#         else:
#             probability_next_away_goal = str(0)
#             
# =============================================================================
        EventType_y= row[6]
        GD= row[7]
        MD = row[8]
        Team = row[10]
        Zone = row[12]
        query = "".join(["""UPDATE q_fulltable    
                SET NodeId = """, NodeId,
                    ", ExpGoals = ",expected_goals, 
                    ", Prob_next_home_goal = ", probability_next_home_goal,
                    ", Prob_next_away_goal = ", probability_next_away_goal,
 #                   ", Event = '", EventType_y,"'",
 #                   ", GD = ", GD, 
 #                   ", MD = ", MD,
 #                   ", Zone = '", Zone,"'",    
 #                   ", Team = '", Team,"'",     
                " WHERE GameId = " ,GameId,
                " AND EventNumber = ",EventNumber]) 
        cursor.execute(query)
        counter += 1
        if counter % 10000 == 0:
            nhl.commit()    
        print(totlen-counter)
        if counter == totlen: 
            nhl.commit()    
    nhl.commit()        
    print("Dataset filled")
def TableCreation():
    
    nhl= MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306,
                                    user="root", 
                                    passwd="", 
                                    db="nhl")
                          
    cursor = nhl.cursor()

    query = """DROP TABLE  IF EXISTS q_fulltable;
        CREATE TABLE q_fulltable 
        SELECT * FROM `play_by_play_events` WHERE GameId >= 2007020001
    """
    cursor.execute(query)
    cursor.fetchall()    
    ##GD, MD, Period = PeriodNumber already there
    ## Creating extra TeamId, PlayerId to store players IDs
    query = """
    ALTER TABLE q_fulltable 
    ADD COLUMN MD INT,
    ADD COLUMN GD INT, ADD Zone VARCHAR(20),
    ADD COLUMN Event VARCHAR(20),ADD PlayerId INT,
    ADD COLUMN Team VARCHAR(20), ADD NodeId INT,
    ADD COLUMN ExpGoals FLOAT,
    ADD COLUMN Prob_next_home_goal FLOAT,
    ADD COLUMN Prob_next_away_goal FLOAT,
    ADD COLUMN TeamIdHome INT,
    ADD COLUMN TeamIdAway INT
    """
    cursor.execute(query)    
    cursor.fetchall()
    
# =============================================================================
#     query = """
#     ALTER TABLE q_fulltable ADD INDEX GameId, 
#     ADD INDEX EventNumber
#     """
#     cursor.execute(query)    
#     cursor.fetchall()
#     
# =============================================================================
    print("Table Created")    
    nhl.close()
    pass

if __name__ == "__main__":
    main()