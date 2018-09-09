# install.packages("RMySQL")
library(RMySQL)
mydb <- dbConnect(MySQL(), user='root', 
                  password='', 
                  dbname='state_graph_2', host='127.0.0.1')

rs = dbSendQuery(mydb, "select * from nodes")
nodes = fetch(rs, n=-1)

rs = dbSendQuery(mydb, "select * from node_info")
NodeInfo = fetch(rs, n=-1)

rs = dbSendQuery(mydb, "select * from edges")
edges = fetch(rs, n=-1)

rs = dbSendQuery(mydb, "select * from rewards")
rewards = fetch(rs, n=-1)

library(dplyr)
Data <- nodes %>% select('NodeId','Occurrence', 'TeamId', 'PlayerId') %>%
            left_join(edges, by = c("NodeId" = "FromId")) %>%
          left_join(rewards, by = c("NodeId" = "NodeId")) 

Data<- Data[,c(1,2,5,6,7,8,3,4)]  
colnames(Data)<-  c("NodeId", "Occurrence",   
         "ChildId", "ChildOccurrence",
         "RewardGoal", "RewardWin","Team", "PlayerId")

head(Data)

sort(unique(Data$ChildId), decreasing = T)
Data %>% filter(ChildId < 9)
