from __future__ import division
import sys
import MySQLdb

class GraphWriter:
    def __init__(self):
        #self.graph_db = MySQLdb.connect(host="localhost", user="root", passwd="", db="state_graph")
        self.graph_db = MySQLdb.connect(host = '127.0.0.1',
                                        port = 3306,
                                    user="root", 
                                    passwd="", 
                                    db="state_graph_2")
        self.cursor = self.graph_db.cursor()
        self.drop_it_like_its_hot("nodes")
        self.drop_it_like_its_hot("edges")
        self.drop_it_like_its_hot("rewards")
        self.drop_it_like_its_hot("node_info")

    def write_node(self, node):
        self.write_reward(node)
        query = """ INSERT IGNORE INTO `nodes`
                    VALUES({0}, '{1}', '{2}', {3}, '{4}', {5}, '{6}', {7}, '{8}', {9})
                """.format(node.get_node_id(), node.get_type(), node.get_name(),
                            node.get_goal_diff(), node.get_manpower_diff(), node.get_period(),
                            node.get_team(), node.get_player_id(), node.get_zone(), 0)
        self.write_to_db(query)

    def write_node_info(self, game_id, event_nr, previous, current):
        query = """ INSERT IGNORE INTO `node_info`
                    VALUES({0}, {1}, {2}, {3})
                """.format(game_id, event_nr, previous.get_node_id(), current.get_node_id())
        self.write_to_db(query)

    def write_edge(self, from_node, to_node):
        query = """ INSERT IGNORE INTO `edges`
                    VALUES({0}, {1}, {2})
                """.format(from_node.get_node_id(), to_node.get_node_id(), 0)
        self.write_to_db(query)

    def write_reward(self, node):
        reward_goal = 0.0
        reward_win = 0.0
        if node.get_name() == "goal":
            if node.get_team() == "home":
                reward_goal = 1.0
            elif node.get_team() == "away":
                reward_goal = -1.0
        elif node.get_name() == "winner":
            if node.get_team() == "home":
                reward_win = 1.0
            elif node.get_team() == "away":
                reward_win = -1.0
        query = """ INSERT IGNORE INTO `rewards`
                            VALUES({0}, {1}, {2})
                """.format(node.get_node_id(), reward_goal, reward_win)
        self.write_to_db(query)

    def increment_node_occurrence(self, node_id):
        query = """ UPDATE `nodes`
				    SET Occurrence = Occurrence + 1
				    WHERE NodeId = {0} 
                """.format(node_id)
        self.write_to_db(query)

    def increment_edge_occurence(self, from_node, to_node):
        query = """ UPDATE `edges`
                    SET Occurrence = Occurrence + 1
                    WHERE FromId = {0} AND ToId = {1}
                """.format(from_node.get_node_id(), to_node.get_node_id())                
        self.write_to_db(query)

    def write_to_db(self, q):
        try:
            self.cursor.execute(q)
            self.graph_db.commit()
        except:
            print("Error: could not write to db")
            self.graph_db.close()
            sys.exit()

    def drop_it_like_its_hot(self, table):
        try: 
            q = "TRUNCATE TABLE {0}".format(table)
            self.cursor.execute(q)
            self.graph_db.commit()
        except:
            print("Error: could not truncate table in db")
            self.graph_db.close()
            sys.exit()

    def close_db(self):
        self.graph_db.close()     