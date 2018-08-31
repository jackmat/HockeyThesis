import MySQLdb
import csv
import pandas as pd
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"


def main():
    state_graph_db = MySQLdb.connect(host = '127.0.0.1',
                                        port = 3306,
                                    user="root", 
                                    passwd="", 
                                    db="state_graph_2")
                          
    cursor = state_graph_db.cursor()
    query = """ SELECT n.NodeId, 
                    n.Occurrence, 
                    e.ToId, 
                    e.Occurrence,
                    r.RewardGoal,
                    r.RewardWin,
                    n.TeamId,
                    n.PlayerId
                FROM nodes n
                LEFT JOIN edges e
                    ON n.NodeId = e.FromId
                JOIN rewards r
                    ON n.NodeId = r.NodeId
                ORDER by n.NodeId ASC"""
    results =  pd.read_sql_query(query, state_graph_db)
    results.to_csv(path+"state_graph.csv")


if __name__ == "__main__":
    main()