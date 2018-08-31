This README is to understand how to use the Code provided in this folder. 
The order to use it is as following: 

0- To have before running the code: 
	(1) Have the NHL hockey dataset already working 
	(2) Have the tables for the AD-Tree in your sql-server as I explain in the thesis
1- Run the build_graph.py (minor changes might be needed), which uses:
	-  ad_tree.py, ad_node.py, graph_writer.py and db_functions.py
   This will create the Ad.tree		
2- Run the load_graph.py: It is a query that will put all tables together for the MDP. 
   The csv file created is stored in C:\Users\Carles\Desktop\HockeyThesis\ThesisHockeyMDP\Code
   It is called state_graph.csv	
3- Run C:\Users\Carles\Desktop\HockeyThesis\ThesisHockeyMDP\Code\EvalCode\value_iteration\value_iteration.R 
      () It uses C MDP code implementation from library Rcpp from R
      The csv file created is stored in C:\Users\Carles\Desktop\HockeyThesis\ThesisHockeyMDP\Code
      It is called q_table.csv
4- Run MDPValuesToSQLTable. It creates a table with all joining with the play_by_play_events 
	DataSet called q_fulltable in the SQL server	
5- Run MDPTeamIdPlayedId. It adds the variables PlayerId and TeamAwayId and TeamHomeId to the q_fullplacetable	