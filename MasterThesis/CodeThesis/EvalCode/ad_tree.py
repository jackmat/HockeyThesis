from __future__ import print_function

from ad_node import ADNode
import Queue

class ADTree:
    def __init__(self, db_writer):
        self.num_nodes = 1
        self.leaves = []
        self.added_leaf_last = False
        self.root = ADNode()
        self.root.set_type("root")
        self.root.set_name("root")
        self.root.set_node_id(self.num_nodes)
        self.current_node = self.root
        self.previous_node = None
        self.db_writer = db_writer
        self.db_writer.write_node(self.root)

    def get_root(self):
        return self.root

    def get_num_nodes(self):
        return self.num_nodes

    def add_event(self, game_id, md, gd, period, event_type, event_nr, zone, team, player_id, event_time):
        new_node = ADNode()
        new_node.set_type("event")
        new_node.set_manpower_diff(md)
        new_node.set_goal_diff(gd)
        new_node.set_period(period)
        new_node.set_name(event_type)
        new_node.set_zone(zone)
        new_node.set_team(team)
        new_node.set_player_id(player_id)
        new_node.set_event_time(event_time)
        current_node = self.current_node
        previous_node = self.previous_node
        if current_node.get_type() == "root":
            self.db_writer.increment_node_occurrence(self.root.get_node_id())
            current_node.increment_occurence()
            # if not self.root.has_been_visited():
            #    self.root.mark_as_visited()
            # TODO increment all counts
            # create new state node
            state_node = ADNode()
            state_node.set_type("state")
            state_node.set_manpower_diff(md)
            state_node.set_goal_diff(gd)
            state_node.set_period(period)
            state_node.set_name("state")
            # see if there is any state with same context
            next_node = current_node.find_child(state_node)
            if next_node == None:
                self.num_nodes += 1
                state_node.set_node_id(self.num_nodes)
                self.db_writer.write_node(state_node)
                current_node.add_child(state_node)
                state_node.set_parent(current_node)
                next_node = state_node
                self.db_writer.write_edge(current_node, next_node)
            self.db_writer.increment_edge_occurence(current_node, next_node)
            current_node = next_node
            # need to link leaf to new state
            if self.added_leaf_last:
                next_node = previous_node.find_child(current_node)
                if next_node == None:
                    previous_node.add_child(current_node)
                    self.db_writer.write_edge(previous_node, current_node)
                self.db_writer.increment_edge_occurence(previous_node, current_node)
                self.added_leaf_last = False
            self.db_writer.increment_node_occurrence(current_node.get_node_id())
            current_node.increment_occurence()
            # if not current_node.has_been_visited():
            #    current_node.mark_as_visited()
            # TODO increment all counts

        # inject shot event before goal
        if event_type == "goal":
            shot_node = ADNode()
            shot_node.set_type("event")
            shot_node.set_manpower_diff(md)
            shot_node.set_goal_diff(gd)
            shot_node.set_period(period)
            shot_node.set_name("shot")
            shot_node.set_zone(zone)
            shot_node.set_team(team)
            shot_node.set_player_id(player_id)
            shot_node.set_event_time(event_time)

            next_node = current_node.find_child(shot_node)
            if next_node == None:
                self.num_nodes += 1
                shot_node.set_node_id(self.num_nodes)
                self.db_writer.write_node(shot_node)
                current_node.add_child(shot_node)
                shot_node.set_parent(current_node)
                next_node = shot_node
                self.db_writer.write_edge(current_node, next_node)
            self.db_writer.increment_edge_occurence(current_node, next_node)
            previous_node = current_node
            current_node = next_node
            self.db_writer.increment_node_occurrence(current_node.get_node_id())
            current_node.increment_occurence()
            # if not current_node.has_been_visited():
            #    current_node.mark_as_visited()
            # TODO increment all counts
            self.db_writer.write_node_info(game_id, event_nr, previous_node, current_node)

        next_node = current_node.find_child(new_node)
        if next_node == None:
            self.num_nodes += 1
            new_node.set_node_id(self.num_nodes)
            self.db_writer.write_node(new_node)
            current_node.add_child(new_node)
            new_node.set_parent(current_node)
            next_node = new_node
            self.db_writer.write_edge(current_node, next_node)
        self.db_writer.increment_edge_occurence(current_node, next_node)
        previous_node = current_node
        current_node = next_node
        self.db_writer.increment_node_occurrence(current_node.get_node_id())
        current_node.increment_occurence()
        if event_type != "goal":
            self.db_writer.write_node_info(game_id, event_nr, previous_node, current_node)  
        # if not current_node.has_been_visited():
        #    current_node.mark_as_visited()
        # TODO increment all counts
        self.current_node = current_node
        self.previous_node = previous_node

    def add_leaf_event(self):
        in_leaves = False
        #this does nothing
        for leaf in self.leaves:
            if leaf.compare_node(self.current_node):
                in_leaves = True
        if not in_leaves:
            self.leaves.append(self.current_node)
        self.added_leaf_last = True
        self.previous_node = self.current_node
        self.current_node = self.root

    def add_winner_event(self, winner, gd):
        current_node = self.current_node
        previous_node = self.previous_node
        new_node = ADNode()
        new_node.set_type("terminal")
        if not winner:
            new_node.set_name("tie")
        else:
            new_node.set_name("winner")
            new_node.set_team(winner)
        new_node.set_goal_diff(gd)
        next_node = current_node.find_child(new_node)
        if next_node == None:
            self.num_nodes += 1
            new_node.set_node_id(self.num_nodes)
            self.db_writer.write_node(new_node)
            current_node.add_child(new_node)
            new_node.set_parent(current_node)
            self.db_writer.write_edge(current_node, new_node)
            previous_node = current_node
            current_node = new_node
        else:
            previous_node = current_node
            current_node = next_node
        self.db_writer.increment_edge_occurence(previous_node, current_node)
        current_node.increment_count()  # ?
        self.db_writer.increment_node_occurrence(current_node.get_node_id())
        current_node.increment_occurence()
        # if not current_node.has_been_visited:
        #    current_node.mark_as_visited()
        # increment all counts
        #self.current_node = current_node
        #self.previous_node = previous_node
        self.current_node = self.root
        self.previous_node = None
        self.added_leaf_last = False

    def print_tree_to_file(self):
        q = Queue.Queue()
        q.enqueue(self.root)
        self.root.mark_as_visited()
        while(not q.isEmpty()):
            level = False
            v = q.dequeue()
            for child in v.get_children():
                if not child.has_been_visited():
                    with open("adtree.txt", "a") as text_file:
                        print(child.print_node(), file=text_file)
                    q.enqueue(child)
                    child.mark_as_visited()
                    level = True
            if level:
                with open("adtree.txt", "a") as text_file:
                    print("\n" + "#"*100 + "\n", file=text_file)

