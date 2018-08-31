# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 11:35:38 2018

@author: Carles
"""

from __future__ import print_function
import sys
import MySQLdb
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/EvalCode"
sys.path.append(path)




ACTION_EVENTS = "('FACEOFF', 'SHOT', 'MISSED SHOT', 'BLOCKED SHOT', 'TAKEAWAY', 'GIVEAWAY', 'HIT', 'GOAL', 'PENALTY')"
START_END_EVENTS = "('PERIOD START', 'PERIOD END', 'EARLY INTERMISSION START', 'STOPPAGE', 'SHOOTOUT COMPLETED', 'GAME END', 'GAME OFF', 'EARLY INTERMISSION END')"
end_events = ["stoppage", "goal", "shootout completed", "penalty", "early intermission end", "period end"]
START_YEAR = 2007020001



def main():
    db_connection = MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306, 
                                    db='nhl', 
                                    user='root', 
                                    passwd='')
        
    db_cursor = db_connection.cursor()

    query = """SELECT DISTINCT GameId FROM q_fulltable 
            WHERE GameId >= {0}""".format(START_YEAR)
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    nr_of_games = 0
    print("Number of games: {0}".format(len(results)))
    for row in results:
        Idmatch = row[0]
        GetPlayerIds(Idmatch, db_connection, db_cursor)
        GetTeamId(Idmatch, db_connection, db_cursor)           
        db_connection.commit()        
        
        nr_of_games += 1
        print("Games processed: {0}".format(nr_of_games))

   
    
def get_table_info(event_type, teamvar):
    team_id = ""
    table_name = ""
    external_id_name = "" 
    PlayerId_col = ""
    if event_type == "FACEOFF" :
        team_id = "FaceoffWinningTeamId"
        table_name = "event_faceoff"
        external_id_name = "FaceoffId"
        PlayerId_col = teamvar.title() +"PlayerId"
    elif event_type == "HIT":
        team_id = "HittingTeamId"
        table_name = "Event_Hit"
        external_id_name = "HitId"
        PlayerId_col = "PlayerId"
    elif event_type == "GOAL" :
        team_id = "ScoringTeamId"
        table_name = "Event_Goal"
        external_id_name = "GoalId"
        PlayerId_col = "GoalScorerId"    
    elif event_type == "SHOT" :
        team_id = "ShotByTeamId"
        table_name = "Event_Shot"
        external_id_name = "ShotId"
        PlayerId_col = "ShootingPlayerId"            
    elif event_type == "MISSED SHOT":
        team_id = "MissTeamId"
        table_name = "Event_Missed_Shot"
        external_id_name = "MissId"
        PlayerId_col = "PlayerId"            
    elif event_type == "BLOCKED SHOT":
        team_id = "BlockTeamId"
        table_name = "Event_Blocked_Shot"
        external_id_name = "BlockId"
        PlayerId_col = "PlayerId"            
    elif event_type == "GIVEAWAY":
        team_id = "GiveawayTeamId"
        table_name = "Event_Giveaway"
        external_id_name = "GiveawayId"
        PlayerId_col = "PlayerId"    

    elif event_type == "TAKEAWAY":
        team_id = "TakeawayTeamId"
        table_name = "Event_Takeaway"
        external_id_name = "TakeawayId"
        PlayerId_col = "PlayerId"    

    elif event_type == "PENALTY":
        team_id = "TeamPenaltyId"
        table_name = "event_penalty"
        external_id_name = "PenaltyId"
        PlayerId_col = "PlayerId"    

    return team_id, table_name, external_id_name, PlayerId_col

# =============================================================================
# import cProfile, pstats, StringIO
# 
# =============================================================================

def GetPlayerIds(IdMatch, d,  c):
# =============================================================================
#     pr = cProfile.Profile()
#     pr.enable()  # 
# =============================================================================
    
    query = """SELECT GameId, EventNumber, EventType, Team FROM q_fulltable   
			WHERE GameId = {0} and (EventType IN {1} or EventType IN {2})
			ORDER BY EventNumber ASC
			""".format(IdMatch, ACTION_EVENTS, START_END_EVENTS)
    c.execute(query)
    res = c.fetchall()
    for row in res:
        GameId = row[0]
        EventNum = row[1]
        event = row[2]
        team = row[3]
        if event in ['FACEOFF', 'SHOT', 'MISSED SHOT', 'BLOCKED SHOT', 'TAKEAWAY', 'GIVEAWAY', 'HIT', 'GOAL', 'PENALTY']:
            team_id, table_name, external_id_name, PlayerIdCol = get_table_info(event, team)
            print(GameId, EventNum, event)
            if event == 'FACEOFF':                    
                if team !="": 
                    
                    query2= """
                     SELECT {0}      
                     FROM  {1}
                     WHERE GameId = {2} AND EventNumber = {3}
                
                """.format(PlayerIdCol, table_name, GameId, EventNum)
#                print(query2)
                c.execute(query2)
                tuppleid = c.fetchall()
                play = tuppleid[0][0]
                if play not in (None,""):
                    query3= """
                    UPDATE q_fulltable
                    SET PlayerId = {0}
                    WHERE GameId = {1} AND EventNumber = {2}
                    """.format(play, GameId, EventNum)
                    c.execute(query3)
                    
#               print(team)
            else:
                query2= """
                     SELECT {0}      
                     FROM  {1}
                     WHERE GameId = {2} AND EventNumber = {3}
                
                """.format(PlayerIdCol, table_name, GameId, EventNum)
#                print(query2)
                c.execute(query2)
                tuppleid = c.fetchall()
                play = tuppleid[0][0]
                if play not in (None,""):
                    query3= """
                    UPDATE q_fulltable
                    SET PlayerId = {0}
                    WHERE GameId = {1} AND EventNumber = {2}
                    """.format(play, GameId, EventNum)
                    c.execute(query3)
                
# =============================================================================
#     pr.disable()  # end profiling
#     s = StringIO.StringIO()
#     sortby = 'cumulative'
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats()
#     print(s.getvalue())
# =============================================================================
    d.commit()
#[GetPlayerIds(i[0], d, c) for i in results]
#GetPlayerIds(results[9200][0], d,c)


def GetTeamId(IdMatch, d,c): 
    
    query = """SELECT TeamId, GameId, Venue FROM `plays_in` WHERE GameId = {0} """.format(IdMatch)
    c.execute(query)
    result = c.fetchall()
    for row in result:
        TeamId = row[0]
        GameId = row[1]
        Venue = row[2]
        if Venue == "Away":
           query = """
                   UPDATE q_fulltable
                      SET TeamIdAway = {0} 
                      WHERE GameId = {1}""".format(TeamId, GameId)
                      
        elif Venue == "Home":
           query = """
                   UPDATE q_fulltable
                      SET TeamIdHome = {0}
                      WHERE GameId = {1}""".format(TeamId, GameId)
        else:
            print("error. Not a Team written")              
            
        c.execute(query) 
        
        

if __name__ == "__main__":
    main()


# =============================================================================
# import pandas as pd
# results= pd.read_sql_query(query, d).values
# pd.read_sql_query("SHOW PROCESSLIST", db_connection)
# db_cursor.execute("kill 32")
# 
# =============================================================================

