from __future__ import print_function
from datetime import timedelta
from texttable import Texttable

class ADNode:
    def __init__(self):
        self.type = ""
        self.name = ""
        self.node_id = 0
        self.visited = False
        self.count = 0
        self.occurence = 0
        self.value = 0
        self.zone = ""
        self.team = ""
        self.player_id = 0
        self.period = 0
        self.md = ""
        self.gd = 0
        self.reward_goal = 0
        self.reward_win = 0
        self.event_time = timedelta(0, 0, 0)
        self.away_count = 0
        self.home_count = 0
        self.children = []
        self.parent = None

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type    

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_node_id(self, id):
        self.node_id = id

    def get_node_id(self):
        return self.node_id

    def mark_as_visited(self):
        self.visited = True

    def mark_as_unvisited(self):
        self.visited = False

    def has_been_visited(self):
        return self.visited    

    def set_zone(self, zone):
        self.zone = zone

    def get_zone(self):  
        return self.zone

    def set_team(self, team):
        self.team = team

    def get_team(self):
        return self.team    

    def set_player_id(self, pid):
        self.player_id = pid

    def get_player_id(self):
        return self.player_id     

    def set_period(self, p):
        self.period = p

    def get_period(self):
        return self.period

    def set_manpower_diff(self, md):
        self.md = md

    def get_manpower_diff(self):
        return self.md

    def set_goal_diff(self, gd):
        self.gd = gd

    def get_goal_diff(self):
        return self.gd

    def set_event_time(self, time):
        self.event_time = time

    def increment_count(self):
        self.count += 1
    
    def increment_occurence(self):
        self.occurence += 1

    def get_occurence(self):
        return self.occurence    

    def add_child(self, node):
        self.children.append(node)

    def get_children(self):
        return self.children    

    def find_child(self, node):
        for child in self.children:
            if child.compare_node(node):
                return child
        return None        

    def compare_node(self, node):
        if self.type != node.get_type():
            return False
        if self.type == "terminal" or node.get_type() == "terminal":
            if self.team == node.get_team():
                return True
            return False
        if self.type == "event" or node.get_type() == "event":
            if (self.name != node.get_name() or self.team != node.get_team() or
                self.zone != node.get_zone()):
                return False
        if self.gd != node.get_goal_diff():
            return False
        if self.md != node.get_manpower_diff():
            return False
        if self.period != node.get_period():
            return False
        return True

    def set_parent(self, node):
        self.parent = node

    def get_parent(self):
        return self.parent   

    def print_node(self):
        table = []
        table_header = ["Node id", "Period", "MD", "GD", "Event time", "Event", "Parent id", "Child id", "Occ"]
        table.append(table_header)
        parent_id = 0
        if not self.parent:
            parent_id = -1
        else:
            parent_id = self.parent.get_node_id()
        action = ""
        if self.team == "":
            action = self.name
        elif self.get_type() == "terminal":
            action = "{0}({1})".format(self.name, self.team)   
        else:
            action = "{0}({1}, {2}, {3})".format(self.name, self.team, self.player_id, self.zone)
        child_id = 0
        if not self.children:
            child_id = -1
        else:
            child_id = self.children[0].get_node_id()         
        table.append([self.node_id, self.period, self.md, self.gd, self.event_time, action, parent_id, child_id, self.occurence])
        t = Texttable()
        t.add_rows(table)
        return t.draw()    

    def print_node_simple(self):
        parent_id = 0
        if not self.parent:
            parent_id = -1
        else:
            parent_id = self.parent.get_node_id()
        action = ""
        if self.team == "":
            action = self.name
        elif self.get_type() == "terminal":
            action = "{0}({1})".format(self.name, self.team)   
        else:
            action = "{0}({1}, {2}, {3})".format(self.name, self.team, self.player_id, self.zone) 
        res = ("|| Nid: {0} P: {1} MD: {2} GD: {3} ET: {4} E: {5} Pid: {6} O: {7} ||"
            .format(self.node_id, self.period, self.md, self.gd, self.event_time, action, parent_id, self.occurence))
        return res          
