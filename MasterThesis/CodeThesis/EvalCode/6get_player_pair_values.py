import sys
import MySQLdb
import time
from datetime import timedelta
from db_functions import fetch_all_from_db, write_to_db
from itertools import combinations
from sort_pair import sort_pair

ACTION_EVENTS = "('FACEOFF', 'SHOT', 'MISSED SHOT', 'BLOCKED SHOT', 'TAKEAWAY', 'GIVEAWAY', 'HIT', 'GOAL', 'PENALTY')"
START_YEAR = 2007020001
TOIT = 1 #time on ice together

def main():
    nhl_db = MySQLdb.connect(
        host="localhost", user="root", passwd="", db="nhl")
    cursor = nhl_db.cursor()
    state_graph_db = MySQLdb.connect(
        host="localhost", user="root", passwd="", db="state_graph")
    cursor_sg = state_graph_db.cursor()
    vi_db = MySQLdb.connect(
        host="localhost", user="root", passwd="", db="valueiteration")
    cursor_vi = vi_db.cursor()
    query = "DROP TABLE IF EXISTS player_pair_valuations_influence;"
    write_to_db(vi_db, cursor_vi, query)
    query = """ CREATE TABLE valueiteration.player_pair_valuations_influence (
                GameId INT, 
                Player1Id INT,
                Player1TOI TIME,
                NrOfActionsPlayer1 INT,
                Player2Id INT,
                Player2TOI TIME,
                NrOfActionsPlayer2 INT,
                AbsPairAis DOUBLE,
                AbsP1Ais DOUBLE,
                AbsP2Ais DOUBLE,
                PairTOI TIME,
                NrOfActionsTogether INT); """
    write_to_db(vi_db, cursor_vi, query)
    query = """ALTER TABLE valueiteration.player_pair_valuations_influence 
            ADD INDEX ( GameId, Player1Id, Player2Id );"""
    write_to_db(vi_db, cursor_vi, query)
    query = """SELECT DISTINCT GameId FROM play_by_play_events 
            WHERE GameId >= {0}
            ORDER BY GameId DESC""".format(START_YEAR)
    results = fetch_all_from_db(nhl_db, cursor, query)
    print("Number of games: {0}".format(len(results)))
    nr_of_games = 0
    start = time.time()
    for row in results:
        game_id = row[0]
        print("Getting player valuations for game = {0}".format(row[0]))
        event_numbers = []
        event_types = []
        event_ids = []
        event_times = []
        home_players_on_ice = []
        away_players_on_ice = []
        query = """SELECT * FROM `play_by_play_events`   
			WHERE GameId = {0} AND EventType IN {1}  
            ORDER BY EventNumber ASC
			""".format(game_id, ACTION_EVENTS)
        result = fetch_all_from_db(nhl_db, cursor, query)
        for res in result:
            home_players_on_ice.append(get_players(res, True, nhl_db, cursor))
            away_players_on_ice.append(get_players(res, False, nhl_db, cursor))
            event_numbers.append(res[4])
            event_times.append(res[6])
            event_types.append(res[7])
            event_ids.append(res[8])
        from_node_ids = []
        to_node_ids = []
        #loop through player actions and get 
        #corresponding edges to calculate impact
        for i in range(0, len(event_numbers)):
            query = """SELECT * FROM `node_info`   
                WHERE GameId = {0} and EventNumber = {1}
                """.format(game_id, event_numbers[i])
            result = fetch_all_from_db(state_graph_db, cursor_sg, query)
            from_node_ids.append(result[0][2])
            to_node_ids.append(result[0][3])
        #get action values
        action_values = []
        for i in range(0, len(event_numbers)):
            from_id = from_node_ids[i]
            to_id = to_node_ids[i]
            query = """ SELECT * FROM q_table
                    WHERE NodeId = {0} """.format(from_id)
            result = fetch_all_from_db(vi_db, cursor_vi, query)
            from_id_value = result[0][1]
            query = """ SELECT * FROM q_table
                    WHERE NodeId = {0} """.format(to_id)
            result = fetch_all_from_db(vi_db, cursor_vi, query)
            to_id_value = result[0][1]
            # impact = Q(S*a) - Q(s)
            action_values.append(to_id_value - from_id_value)
        #get player ids
        player_ids = []
        for i in range(0, len(event_numbers)):
            event_type = event_types[i]
            event_id = event_ids[i]
            player_id = get_player_id(event_type, event_id, game_id, nhl_db, cursor)
            if player_id == 0:
                print("""faulty player id! game_id: {0}, event_id: {1} 
                        """.format(game_id, event_id))
            player_ids.append(player_id)
        #get all unique player pairs >= TOIT 
        player_pairs = get_player_pairs(player_ids, home_players_on_ice, away_players_on_ice, event_times)
        #get times that players are on the ice
        player_times = get_player_times(player_pairs, home_players_on_ice, away_players_on_ice, event_times)
        #get player pair values
        player_pair_values, action_counts = get_pair_values(player_pairs, player_ids, home_players_on_ice,
                                            away_players_on_ice, action_values, player_times)
        #write player pair values
        for i in range(0, len(player_pairs)):
            query = """ INSERT IGNORE INTO player_pair_valuations_influence
                        VALUES ({0}, {1}, '{2}', {3}, {4}, '{5}', {6}, {7}, {8}, {9}, '{10}', {11})
                        """.format(game_id, player_pairs[i][0], player_times[i][1], action_counts[i][0], 
                        player_pairs[i][1], player_times[i][3], action_counts[i][1], player_pair_values[i][0],
                        player_pair_values[i][1], player_pair_values[i][2], player_pairs[i][2], action_counts[i][2])
            write_to_db(vi_db, cursor_vi, query)
        nr_of_games += 1
        print("Games processed: {0}".format(nr_of_games))
    end = time.time()
    print("Time elapsed: {0}".format(end - start))
    nhl_db.close()
    state_graph_db.close()
    vi_db.close()

def get_player_id(event_type, event_id, game_id, db, c):
    player_id = 0
    if event_type == "BLOCKED SHOT":
        query = """ SELECT PlayerId FROM event_blocked_shot 
                    WHERE GameId = {0} AND BlockId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]
    elif event_type == "FACEOFF":
        query = """ SELECT * FROM event_faceoff 
                    WHERE GameId = {0} AND FaceoffId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:    
            team_winning_id = result[0][8]
            if team_winning_id == result[0][2]: #awayteam
                player_id = result[0][11]
            elif team_winning_id == result[0][3]: #hometeam
                player_id = result[0][13]
    elif event_type == "GIVEAWAY":
        query = """ SELECT PlayerId FROM event_giveaway
                    WHERE GameId = {0} AND GiveawayId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]
    elif event_type == "GOAL":
        query = """ SELECT GoalScorerId FROM event_goal
                    WHERE GameId = {0} AND GoalId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]
    elif event_type == "HIT":
        query = """ SELECT PlayerId FROM event_hit
                    WHERE GameId = {0} AND HitId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result and result[0][0] != None:
            player_id = result[0][0]
    elif event_type == "MISSED SHOT":
        query = """ SELECT PlayerId FROM event_missed_shot
                    WHERE GameId = {0} AND MissId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]
    elif event_type == "PENALTY":
        query = """ SELECT PlayerId FROM event_penalty
                    WHERE GameId = {0} AND PenaltyId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result and result[0][0] != None:
            player_id = result[0][0]
    elif event_type == "SHOT":
        query = """ SELECT ShootingPlayerId FROM event_shot
                    WHERE GameId = {0} AND ShotId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]
    elif event_type == "TAKEAWAY":
        query = """ SELECT PlayerId FROM event_takeaway
                    WHERE GameId = {0} AND TakeawayId = {1} 
                """.format(game_id, event_id)
        result = fetch_all_from_db(db, c, query)
        if result:
            player_id = result[0][0]         
    return player_id

def get_players(result, home, db, c):
    players = []
    query = "SELECT SkaterId FROM Skater WHERE "
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
        return []
    results = fetch_all_from_db(db, c, query + ";")
    for res in results:
        players.append(res[0])
    return players

#get unique players that plays in the same team
def get_player_pairs(player_ids, players_home, players_away, event_times):
    threshold = timedelta(minutes=TOIT)
    unique_players = list(set(player_ids))
    player_pairs = []
    for pair in combinations(unique_players, 2):
        #need sorting to avoid pairs appearing twice
        sorted_pair = pair
        if pair[0] > pair[1]:
            new_sorted = (pair[1], pair[0])
            sorted_pair = new_sorted
        player_1 = sorted_pair[0]
        player_2 = sorted_pair[1]
        pair_total_time = timedelta(0, 0, 0)
        current_event_time = timedelta(0, 0, 0)
        on_ice = False
        for i in range(0, len(event_times)):
            if ((player_1 in players_home[i] and player_2 in players_home[i]) or
                (player_1 in players_away[i] and player_2 in players_away[i])):
                if not on_ice:
                    current_event_time = event_times[i]
                    on_ice = True
                else:
                    if event_times[i] != timedelta(0):
                        pair_total_time += event_times[i] - current_event_time
                    current_event_time = event_times[i]            
            else:
                current_event_time = timedelta(0, 0, 0)
                on_ice = False
        if pair_total_time >= threshold:
            player_pairs.append([player_1, player_2, pair_total_time])
    return player_pairs

def get_pair_values(player_pairs, player_ids, players_home, players_away, action_values, player_times):
    pair_values = []
    action_counts = []
    for p in range(0,len(player_pairs)):
        #the different pair values
        value = 0
        value_per_minute = 0
        value_p1 = 0
        value_p2 = 0
        #local variables
        player_1 = player_pairs[p][0]
        player_2 = player_pairs[p][1]
        together_value = 0
        player_1_values = 0
        player_2_values = 0
        p1_counts = 0
        p2_counts = 0
        together_counts = 0
        for i in range(0, len(action_values)):
            #both on ice
            if ((player_1 in players_home[i] and player_2 in players_home[i]) or
                (player_1 in players_away[i] and player_2 in players_away[i])):
                #if player_1 == player_ids[i] or player_2 == player_ids[i]:
                    together_value += action_values[i]
                    together_counts += 1
            #else get individual values    
            else: 
                if player_1 in players_home[i] and player_2 not in players_home[i]:
                    #if player_1 == player_ids[i]:
                        player_1_values += action_values[i]
                        p1_counts += 1
                elif player_1 in players_away[i] and player_2 not in players_away[i]:
                    #if player_1 == player_ids[i]:
                        player_1_values += action_values[i]
                        p1_counts += 1
                elif player_2 in players_home[i] and player_1 not in players_home[i]:
                    #if player_2 == player_ids[i]:
                        player_2_values += action_values[i]
                        p2_counts += 1
                elif player_2 in players_away[i] and player_1 not in players_away[i]:
                    #if player_2 == player_ids[i]:
                        player_2_values += action_values[i]
                        p2_counts += 1
        #absolute values
        p1_abs = abs(player_1_values)
        p2_abs = abs(player_2_values)
        together_abs = abs(together_value)
        #divide with time on ice (minutes)
        time_p1 = player_times[p][1]
        time_p2 = player_times[p][3]
        time_together = player_pairs[p][2]
        final_p1 = 0
        final_p2 = 0
        #because time could be zero but not the values
        if time_p1 > timedelta(0):
            final_p1 = p1_abs/time_to_decimal_minutes(time_p1)
        if time_p2 > timedelta(0):
            final_p2 = p2_abs/time_to_decimal_minutes(time_p2)
        final_together = together_abs/time_to_decimal_minutes(time_together)
        if not p1_abs and not p2_abs:
           value = together_abs
           value_per_minute = 'Null'
        else:
            value = together_abs/(p1_abs + p2_abs)
            if not final_p1 and not final_p2:
                value_per_minute = 'Null'
            else:
                value_per_minute = final_together/(final_p1 + final_p2)
        if p1_abs:
            value_p1 = together_abs/p1_abs
        else:
            value_p1 = 'Null'
        if p2_abs:
            value_p2 = together_abs/p2_abs
        else:
            value_p2 = 'Null'
        pair_values.append([together_abs,p1_abs,p2_abs])
        action_counts.append([p1_counts, p2_counts, together_counts])
    return pair_values, action_counts

#get player times for when player 1 is on the ice and NOT player 2, vise versa
def get_player_times(player_pairs, players_home, players_away, event_times):
    player_times = []
    for pair in player_pairs:
        player_1 = pair[0]
        player_2 = pair[1]
        p1_total_time = timedelta(0, 0, 0)
        p2_total_time = timedelta(0, 0, 0)
        p1_current_time = timedelta(0, 0, 0)
        p2_current_time = timedelta(0, 0, 0)
        p1_on_ice = False
        p2_on_ice = False
        for i in range(0, len(event_times)):
            #player 1
            if ((player_1 in players_home[i] or player_1 in players_away[i]) and
                not (player_2 in players_home[i] or player_2 in players_away[i])):
                if not p1_on_ice:
                    p1_current_time = event_times[i]
                    p1_on_ice = True
                else:
                    if event_times[i] != timedelta(0):
                        p1_total_time += event_times[i] - p1_current_time
                    p1_current_time = event_times[i]
            else:
                p1_current_time = timedelta(0, 0, 0)
                p1_on_ice = False
            #player 2
            if ((player_2 in players_home[i] or player_2 in players_away[i]) and
                not (player_1 in players_home[i] or player_1 in players_away[i])):
                if not p2_on_ice:
                    p2_current_time = event_times[i]
                    p2_on_ice = True
                else:
                    if event_times[i] != timedelta(0):
                        p2_total_time += event_times[i] - p2_current_time
                    p2_current_time = event_times[i]
            else:
                p2_current_time = timedelta(0, 0, 0)
                p2_on_ice = False
        #print("p1: {0}, t1: {1}, p2: {2}, t2: {3}".format(player_1, p1_total_time, player_2, p2_total_time))
        player_times.append([player_1, p1_total_time, player_2, p2_total_time])
    return player_times

def time_to_decimal_minutes(time):
    return time.seconds // 60 + ((time.seconds % 60) / 60)

if __name__ == "__main__":
    main() 