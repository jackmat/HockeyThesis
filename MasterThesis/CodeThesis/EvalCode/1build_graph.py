from __future__ import print_function
import sys
import MySQLdb
import time
import sys
path = "C:\Users\Carles\Desktop\MasterThesis\CodeThesis\EvalCode"
sys.path.append(path)




from ad_tree import ADTree
from graph_writer import GraphWriter
from db_functions import fetch_all_from_db
import cProfile, pstats, StringIO

ACTION_EVENTS = "('FACEOFF', 'SHOT', 'MISSED SHOT', 'BLOCKED SHOT', 'TAKEAWAY', 'GIVEAWAY', 'HIT', 'GOAL', 'PENALTY')"
START_END_EVENTS = "('PERIOD START', 'PERIOD END', 'EARLY INTERMISSION START', 'STOPPAGE', 'SHOOTOUT COMPLETED', 'GAME END', 'GAME OFF', 'EARLY INTERMISSION END')"
end_events = ["stoppage", "goal", "shootout completed", "penalty", "early intermission end", "period end"]
START_YEAR = 2007020001

def main():
    graph_writer = GraphWriter()
    tree = ADTree(graph_writer)
    nhl_db = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3306,
         user="root", passwd="", db="nhl")
    cursor = nhl_db.cursor()
    query = """SELECT DISTINCT GameId FROM play_by_play_eventsfiltered 
            WHERE GameId >= {0}""".format(START_YEAR)
    results = fetch_all_from_db(nhl_db, cursor, query)
    nr_of_games = 0
    print("Number of games: {0}".format(len(results)))
    start = time.time()
    for row in results:
        add_events_to_tree(row[0], tree, nhl_db, cursor)
        nr_of_games += 1
        print("Games processed: {0}".format(nr_of_games))
    end = time.time()
    print("Time elapsed: {0}".format(end - start))    
    nhl_db.close()
    graph_writer.close_db()

def game_winner(game_id, db, c):
    query = """SELECT Result FROM `Plays_In`
			WHERE GameId = {0} AND Venue = 'Home'
            """.format(game_id)
    result = fetch_all_from_db(db, c, query)
    game_result = result[0][0]
    if game_result == 1:
        return "home"
    elif game_result == -1:
        return "away"
    else:
        return ""

def get_num_players(result, home, db, c):
    count = 0
    query = "SELECT COUNT(*) AS NumSkaters FROM Skater WHERE "
    num_players = 0
    for i in range(0, 8):
        player_id = 0
        if home:
            player_id = result[18 + i]    
        else:
            player_id = result[9 + i]
        if player_id:
            num_players += 1
            if i == 0:
                query += "SkaterId = {0}".format(player_id)
                continue
            query += " OR SkaterId = {0}".format(player_id)
    if num_players == 0:
        return 0
    results = fetch_all_from_db(db, c, query + ";")
    if results:
        count = results[0][0]
    else: 
        return -1
    return count

def get_table_info(event_type):
    team_id = ""
    table_name = ""
    external_id_name = "" 
    if event_type == "FACEOFF" :
        team_id = "FaceoffWinningTeamId"
        table_name = "event_faceoff"
        external_id_name = "FaceoffId"
    elif event_type == "HIT":
        team_id = "HittingTeamId"
        table_name = "Event_Hit"
        external_id_name = "HitId"
    elif event_type == "GOAL" :
        team_id = "ScoringTeamId"
        table_name = "Event_Goal"
        external_id_name = "GoalId"
    elif event_type == "SHOT" :
        team_id = "ShotByTeamId"
        table_name = "Event_Shot"
        external_id_name = "ShotId"
    elif event_type == "MISSED SHOT":
        team_id = "MissTeamId"
        table_name = "Event_Missed_Shot"
        external_id_name = "MissId"
    elif event_type == "BLOCKED SHOT":
        team_id = "BlockTeamId"
        table_name = "Event_Blocked_Shot"
        external_id_name = "BlockId"
    elif event_type == "GIVEAWAY":
        team_id = "GiveawayTeamId"
        table_name = "Event_Giveaway"
        external_id_name = "GiveawayId"
    elif event_type == "TAKEAWAY":
        team_id = "TakeawayTeamId"
        table_name = "Event_Takeaway"
        external_id_name = "TakeawayId"
    elif event_type == "PENALTY":
        team_id = "TeamPenaltyId"
        table_name = "event_penalty"
        external_id_name = "PenaltyId"
    return team_id, table_name, external_id_name

def add_events_to_tree(game_id, tree, db, c):
    pr = cProfile.Profile()
    pr.enable()  # 
    print("Processing Game: {0}".format(game_id))
    query = """SELECT * FROM `play_by_play_eventsfiltered`   
			WHERE GameId = {0} and (EventType IN {1} or EventType IN {2})
			ORDER BY EventNumber ASC
			""".format(game_id, ACTION_EVENTS, START_END_EVENTS)
    results = fetch_all_from_db(db, c, query)
    gd = 0
    for row in results:
        nr_of_home_skaters = get_num_players(row, True, db, c)
        nr_of_away_skaters = get_num_players(row, False, db, c)
        if nr_of_home_skaters < 0 or nr_of_away_skaters < 0:
            print("could not fetch nr of players")
            print(game_id)
            print(row[4])
            db.close()
            sys.exit()
        md = nr_of_home_skaters - nr_of_away_skaters
        event = row[7]
        event_type = event.lower()
        event_id = row[8]
        game_id = row[0]
        event_nr = row[4]
        period = row[5]
        event_time = row[6]
        player_id = 0
        team_id, table_name, external_id_name = get_table_info(event)
        zone = ""
        team = ""
        if team_id:     
            query = """SELECT AwayTeamId, HomeTeamId, {0}, Zone FROM {1}
                        WHERE {2} = {3};
                        """.format(team_id, table_name, external_id_name, event_id)
            result = fetch_all_from_db(db, c, query)
            if result[0][0] == result[0][2]: #awayteam
                team = "away"
            elif result[0][1] == result[0][2]: #hometeam
                team = "home"
            zone = result[0][3]
        #create new ADnode
        tree.add_event(game_id, md, gd, period, event_type, event_nr, zone, team, player_id, event_time)
        # Update goal differential
        if event_type == "goal" and team == "away":
            gd -= 1
        elif event_type == "goal" and team == "home":
            gd += 1
        # append state if it is a end marker
        if event_type in end_events:
            tree.add_leaf_event()
    #Game is over
    winner = game_winner(game_id, db, c)
    tree.add_winner_event(winner, gd)
    pr.disable()  # end profiling
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


if __name__ == "__main__":
    main() 

    

