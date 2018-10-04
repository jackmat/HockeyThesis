# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 12:52:46 2018

@author: Carles
"""
import MySQLdb

name = "state_graph"
def StateTableCreation(name):
    con = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3306,
        user="root", passwd="")
    cursor = con.cursor()
    sql = "DROP DATABASE IF EXISTS "+name
    cursor.execute(sql)
    con.commit()
    sql = 'CREATE DATABASE '+ name
    cursor.execute(sql)
    print("Table " +name + " created")
    con = MySQLdb.connect(
            host = '127.0.0.1',
            port = 3306,
            user="root", passwd="",
            db = name)
    cursor = con.cursor()

    edgessql = '''CREATE TABLE edges (
           FromId int(11),
           ToId int(11),
           Occurrence int(11)
           ) 
           '''
    print("Table edges created")

    cursor.execute(edgessql)
    con.commit()
    sql = "ALTER TABLE `edges` ADD INDEX (ToId)"
    cursor.execute(sql)
    print("Index created")
    sql = "ALTER TABLE `edges` ADD INDEX (FromId)"
    cursor.execute(sql)

    nodessql = '''CREATE TABLE nodes (
           NodeId int(11),
           NamesID VARCHAR(20) ,
           EventTypeId VARCHAR(20),
           GD int(11),
           MD int(11),
           Period int(11),
           TeamId VARCHAR(20),
           PlayerId VARCHAR(20),
           Zone VARCHAR(20),
           Occurence int(11)) 
           '''
    
    cursor.execute(nodessql)
    con.commit()
    sql = "ALTER TABLE `nodes` ADD INDEX (NodeId)"
    cursor.execute(sql)
    
    print("Table nodes created")
    node_infosql = '''CREATE TABLE node_info(
           GameId int(11),
           EventNumber int(11) ,
           previous int(11),
           current int(11) 
           ) 
           '''
    
    cursor.execute(node_infosql)
    print("Table node_info created")
    
    rewardssql = '''CREATE TABLE rewards(
           NodeId int(11),
           RewardGoal int(11),
           RewardWin int(11)
           ) 
           '''
    
    cursor.execute(rewardssql)
    print("Table rewards created")
    con.commit()
    pass

StateTableCreation(name= name)