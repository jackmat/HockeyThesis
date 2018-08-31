# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 20:29:54 2018

@author: Carles
"""
import os
import sys
path = "C:/Users/Carles/Desktop/HockeyThesis/ThesisHockeyMDP/Code/EvaluatedCode/adtree-py-master/adtree-py-master/src"
sys.path.append(os.path.abspath(path))


import MySQLdb
db_connection = MySQLdb.connect(host = '127.0.0.1',
                                    port = 3306, 
                                    db='nhl', 
                                    user='root', 
                                    passwd='')
        
db_cursor = db_connection.cursor()

query = """SELECT Distinct GameId from workcontextevents order by GameId, EventNumber ASC"""

db_cursor.execute(query)
diffGameId = db_cursor.fetchall() ##Selecting different GameID

for diffGameId in 





###Manipulation of data
left = diffGameId
leftlist= map(list, left)
leftlist2= [val[0] for val in leftlist]
numleft = map(int, leftlist2)


path= "C:/Users/Carles/Desktop/HockeyThesis/ThesisHockeyMDP/Code/EvaluatedCode/java2python-master/java2python"
modules =   [f for f in listdir(path) if isfile(join(path, f))]
modules2 = glob.glob(dirname(modules))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

# =============================================================================
# 
# from os.path import dirname, basename, isfile
# import glob
# import re
# from os import listdir
# from os.path import isfile, join
# 
# modules =   [f for f in listdir(path) if isfile(join(path, f))]
# modules2 = glob.glob(dirname(modules))
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
# 
# import ArrayRecord as Record
# import SparseADTree as ADTree
# import IteratedTreeContingencyTable as ContingencyTable
# 
# arityList = [4, 3, 2, 5]
# recordsTable = [[1, 2, 1, 4], [2, 2, 2, 5], [1, 3, 1, 1], [4, 1, 2, 1],
#                 [2, 2, 1, 4], [4, 3, 2, 5], [3, 1, 1, 1], [1, 1, 2, 5]]
# 
# 
# 
# 
#     
# if __name__ == '__main__':
#     # import the original dataset to the record module
#     Record.initRecord([arityList, recordsTable])
# 
#     # declare that the ADTree module uses ArrayRecord module as dataset
#     ADTree.importModules('ArrayRecord')
# 
#     # declare that the ContingencyTable uses ArrayRecord and SparsADTree modules
#     ContingencyTable.importModules('ArrayRecord', 'SparseADTree')
# 
#     # initialise recordNums containing all numbers in the dataset
#     recordNums = [num for num in range(1, Record.recordsLength+1)]
# 
#     # build an AD-Tree with attribute list starts from the first attribute,
#     # and for all the records
#     adtree = ADTree.ADNode(1, recordNums)
# 
#     # build a contingency table for the first and third attributes
#     contab = ContingencyTable.ContingencyTable([2, 4], adtree)
# 
#     # query for [1, 1], [2, 1], [3, 1] and [4, 1], and print on screen
#     for i in range(4):
#         query = [i+1, 1]
#         count = contab.getCount(query)
#         print('Q:', query, 'C:', count)
#     
#     
# 
# =============================================================================




// Conversion output is limited to 2048 chars
// Share Varycode on Facebook and tweet on Twitter
// to double the limits.

from System import *
from com.mysql.jdbc.Connection import *
from System.Collections.Generic import *
from System.Collections import *
from System.IO import *
from System.sql.DriverManager import *
from System.sql.ResultSet import *
from System.sql.SQLException import *
from System.sql.Statement import *

class BuildTree(object):
	def __init__(self):
		self._currentNode = None
		self._root = None
		self._previousNode = None
		self._con = None
		self._homeGoal = 0
		self._awayGoal = 0
		self._numNodes = 1
		self._numEvents = 1
		self._homeWin = False
		self._leaves = None
		self._addedLeafLast = False
		self._checkManpower = True
		self._checkGoalDiff = True
		self._checkPeriod = False
		self._noLoops = False
		self._onlyPenaltyLoop = False
		self._f = None
		self._fw = None
		self._data_db = "NHL_Final2"
		self._tree_db = "NHL_Sequence_Tree_Full_GD_MD"

	def main(args):
		t1 = System.currentTimeMillis()
		self._root = Node()
		self._root.SetType("Root")
		self._root.SetNodeId(self._numNodes)
		self._root.SetGoalDiff(0)
		self._root.SetManDiff(0)
		self._root.SetPeriod(0)
		self._root.SetZone("Unspecified")
		self._root.SetName("Root")
		self._f = File("BuildingTreeConvergence.csv")
		try:
			self._fw = FileWriter(self._f)
			self._fw.write("NumEvents, NumNodes\n")
		except IOException, e:
			Console.WriteLine("Failed to open file for writing.")
			e.printStackTrace()
			return 
		finally:
		GameIds = BuildTree.GetGameIds()
		if GameIds == None:
			Console.WriteLine("Failed to get GameIds")
			return 
		len = GameIds.size()
		self._leaves = ArrayList[Node]()
		if BuildTree.prepareNodeTable() != 0:
			Console.WriteLine("Failed to prepare node tables.")
			return 
		if BuildTree.writeNodeToTable(self._root) != 0:
			Console.WriteLine("Failed to write root to table.")
			return 
		i = 0
		while i < len:
			self._currentNode = self._root
			self._previousNode = None
			self._addedLeafLast = False
			self._homeGoal = 0
			self._awayGoal = 0
			self._gameId = GameIds.get( i );
			if ( SetWin( gameId ) != 0 )
			{
				System.out.println( "Could not set win." );
				return;
			}
			
			if ( AddEventsToTree( gameId ) != 0 )
			{
				System.out.println( "Failed to add events to tree for GameId = " + GameIds.get( i ) );
				return;
			}
			
			root.MarkUnvisited();
		}
		
		//root.PrintNode(0);
		System.out.println("NumEvents = " + numEvents + ", NumNodes = " + numNodes );
		long t2 = System.currentTimeMillis();
		System.out.println( "Total runtime: " + ((t2-t1)/1000.0) + "seconds" );
		
		try
		{
			fw.write(numEvents + "," + numNodes + "\n");
			fw.close();
		}
		catch (IOException e)
		{
			System.out.println( "Failed to close file." );
			e.printStackTrace();
			return;
		}
	}
	
	private static ArrayList<Integer> GetGameIds()
	{
		ArrayList<Integer> GameIds = new ArrayList<Integer>();
		
		String CONN_STR = "jdbc:mysql://127.0.0.1/";
		try 
		{
			java.lang.Class.forName( "com.mysql.jdbc.Driver" );
		} 
		catch ( Exception ex ) 
		{
			System.out.println( "Unable to load MySQL JDBC driver" );
			return null;
		}
		
		try
		{
			con = (Connection) DriverManager.getConnection( CONN_STR, 
					"root", 
					"root" );











# =============================================================================
# ####################Tree Creation
# import itertools
# import numpy as np
# States = range(8130)
# query_list = np.array(list(itertools.product(States, States)))
# Index = 0 
# Current_ADnode = root()
# 
# 
# def ADCOUNT(ADnode, Querylist, index):
#     If index == size(Querylist): 
#         return Adnode.count
# 
#     varynode = Vary node child of ADnode that corresponds to indexth attribute in Query-list 
#     Next_ADnode = ADNODE child of Varynode that corresponds to indexth value in Query-list
# 
#     If count(Next_ADnode) == 0:
#         return 0
#     If Next_ADnode is a MCV then:
#         Count  =  ADCOUNT(ADdnode, Querylist, index+l)
#         For each s in siblings of Next-ADnode do:
#             Count = Count - ADCOUNT(s, Querylist, index+l)
#         return Count
#    return ADCOUNT(NextADnode, Querylist, index+l)
#         
# query = "ALTER TABLE workcontextevents add ComplexEvent varchar(255)"
# db_cursor.execute(query)
# 
# updateComplexEvent= """
#     UPDATE workcontextevents
#     SET   ComplexEvent = concat(EventTypeContext,'(',Zone,')') 
#         """
#         
# db_cursor.execute(updateComplexEvent)
# db_connection.commit()
# =============================================================================
