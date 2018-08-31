# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 12:44:20 2018

@author: Carles
"""
def fetch_all_from_db(nhl_db, cursor, query):
    cursor.execute(query)
    return cursor.fetchall()