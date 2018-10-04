This README is to understand how to use the Code provided in this folder. 
The order to use it is as following: 

0- To have before running the code: 
	(1) Have the NHL hockey dataset already working 
	(2) Have the tables for the AD-Tree in your sql-server as I explain in the thesis
	    For that, you can run file '0BuildStategraphTable.py' with name = state_graph_2 in the variable to create the proper database
1- Run the 1build_graph.py (minor changes might be needed), which uses:
	-  ad_tree.py, ad_node.py, graph_writer.py and db_functions.py
   This will create the Ad.tree		
2- Run the 2load_graph.py: It is a query that will put all tables together for the MDP. 
   The csv file created is stored in "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
   It is called state_graph.csv	
3- Run C:\Users\Carles\Desktop\MasterThesis\CodeThesis\EvalCode\3value_iteration.R 
      () It uses C MDP code implementation from library Rcpp from R. It canbe found in C:\Users\Carles\Desktop\MasterThesis\CodeThesis\EvalCode\value_iteration
      The csv file created is stored in "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
      It is called q_table.csv
4- Run 4MDPValuesToSQLTable. It creates a table with all joining with the play_by_play_events 
	DataSet called q_fulltable in the SQL server	
5- Run 5MDPTeamIdPlayedId. It adds the variables PlayerId and TeamAwayId and TeamHomeId to the q_fullplacetable	as well as MDP variables
6- Run 6JoiningFunctions. It creates 3 tables with time-series metrics: Value, Time, +/- 
    It saves the three pd.Dataframe into path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
    #               path + 'PlayerValMatrix.csv'
    #               path + 'PlayerbyTimeValMatrix.csv' 
    #               path + 'PlusMinusMatrix.csv'      
7- Run 7.0CleaningDatasets. It puts in a nice way the tables from before, it removes inconsistencies:
				(e.g. Players whose time played in a match is 0 cannot have a valuation different than 0)
          It creates 4 Datasets.csv in a nice way: 
		  #CDataset.csv: Valuation per match of Players
                  #TimeDataset.csv: Valuation/TimePlayed per match (in hours) 
                  #PMDataset.csv: PlusMinus measure from Markov per match
                  #PlusMinusTimeDataset.csv:PlusMinus measure from Markov/TimePlayed per match (in hours) 
	pathto find the Datasets = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
8. Running 7.1PlottingEvaluationPlayers:
	It stores in C:\Users\Carles\Desktop\MasterThesis\ResultsPhotos
	Different Plots and interesting grpahics and Tables from the Dataset 	
	It uses the ScrappingSalariesNHL to create plots and use the salary, +/- and NHL metrics in totalcomparison
9. Running '7.2Accuracy of Metrics' creates tables for the different accuracy metrics for different models in the diffrent datasets 
         by subsetting all Players with more than 30 Games Played and 
         selecting their first 25, and forecasting their next 5 with arima models 
10. 7.3TimeseriesModelling gives you an idea of which are the models arima models chosen for different players 
	each one taking into account how many matches he has played (put in ranges)