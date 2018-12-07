# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 19:23:07 2018

@author: Carles
"""

from os import listdir
from os.path import isfile, join
mypath = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/EvalCode/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

citations = ['csv', 'timedelta','__future__', 'MySQLdb', 'numpy', 
             'pandas', 'Queue','sys','Texttabel', 'time'] 

import csv
from datetime import timedelta
from __future__ import print_function, division
import MySQLdb
import numpy as np
import pandas as pd
import Queue
import sys
from texttable import Texttable
import time
