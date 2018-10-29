import MySQLdb
import csv
import pandas as pd
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"


def main():
    # =============================================================================
    #     ### Description: (1) It merges the 3 tables created of nodes, 
    #                       rewards and edges into ones   
    #                      (2) It saves as a csv file in the path + state_graph.csv
    #                     
    # =============================================================================

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
                    n.Team,
                    n.PlayerId
                FROM nodes n
                LEFT JOIN edges e
                    ON n.NodeId = e.FromId
                JOIN rewards r
                    ON n.NodeId = r.NodeId
                ORDER by n.NodeId ASC"""
    #results =  pd.read_sql_query(query, state_graph_db)
    #results.to_csv(path+"state_graph.csv")
    cursor.execute(query)
    results = cursor.fetchall()
    with open(path+"state_graph.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(results)
    state_graph_db.close()

if __name__ == "__main__":
    main()