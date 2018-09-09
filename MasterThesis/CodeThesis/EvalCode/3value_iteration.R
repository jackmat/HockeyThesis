library(Rcpp)

#Load data
states <- read.csv(file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/state_graph.csv", header=TRUE)
colnames(states) <- c("NodeId", "Occurrence", "ChildId", "ChildOccurrence", "RewardGoal", "RewardWin", "Team", "PlayerId")
sourceCpp("C:/Users/Carles/Desktop/MasterThesis/CodeThesis/EvalCode/value_iteration/value_iteration_f.cpp")
# states <- states[,2:9] # When stored, an index was created which is now eliminated 

#value iteration
value_iteration <- function(states, n, c) {
  #Init variables
  unique_states <- subset(states, !duplicated(NodeId))
  nr_of_states <- nrow(unique_states)
  s_ids <- unique_states[,"NodeId"]
  s_occ <- unique_states[,"Occurrence"]
  r_w <- unique_states[,"RewardWin"]
  r_g <- unique_states[,"RewardGoal"]
  q <- value_iteration_f(states, n, c, nr_of_states, r_w, r_g, s_occ, s_ids)
  return(q)
}

system.time(q <- value_iteration(states, 100000, 0.0001))
write.csv(q, file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/q_table.csv")
write.csv(q, file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/q_table2.csv")

##NodeId, expected_goals, probability_next_home_goal, probability_next_away_goal
Dataset<-read.csv(file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/q_table2.csv")
#head(Dataset)
z<-Dataset
head(z,10)
a<-z$V3/(z$V3+z$V4)
b<-z$V4/(z$V3+z$V4)
z$V3<-a
z$V4<-b
write.csv(z, file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/q_table_norm.csv")
write.csv(z, file="C:/Users/Carles/Desktop/MasterThesis/CodeThesis/q_table2_norm.csv")

