library(dplyr)

WrittenSeason <- 2007
RegMatches <- 82
pathtoSaveFiles<- "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/CleanDatasets/"

main<- function(Season = WrittenSeason, RegularMatches = RegMatches, savepath= pathtoSaveFiles){
  ## 0. Reading Matrices and establishing Game Counter
  path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
  
  
  PlayerValMatrix <- read.csv(paste0(path, Season, "PlayerValMatrix", ".csv"),
                              sep = ",", dec = ".", header = TRUE)
  PlayerValMatrix$CountGame <- 1:nrow(PlayerValMatrix)
  PlayerbyTimeValMatrix <- read.csv(paste0(path, Season, "PlayerbyTimeValMatrix", ".csv"),
                                    sep = ",", dec = ".", header = TRUE)
  PlayerbyTimeValMatrix$CountGame <- 1:nrow(PlayerbyTimeValMatrix)
  
  PlusMinusMatrix <- read.csv(paste0(path, Season, "PlusMinusMatrix", ".csv"),
                              sep = ",", dec = ".", header = TRUE)
  PlusMinusMatrix$CountGame <- 1:nrow(PlusMinusMatrix)
  
  Dataset<-JoinPlayersValuesIntoOneCol(myData = PlayerValMatrix) # WARNING IS OKAY
  SecTimeDataset<-JoinPlayersValuesIntoOneCol(myData = PlayerbyTimeValMatrix)# WARNING IS OKAY
  PlusMinusDataset<-JoinPlayersValuesIntoOneCol(myData = PlusMinusMatrix)# WARNING IS OKAY
  # ## Checking for whether 0 in one side correspond to 0 in the other matrix
  # ## The idea is that if valuation is 0, it means that player has not played in the game, 
  # #  and therefore the time played should be 0
  ##(1) For Valuation Dataset
  WrongIndexInValDataset<-EvaluatedTimeVsValue(ValMat = Dataset, TimeMat = SecTimeDataset)
  CDataset<-DfCorrection(Dataset, WrongIndexInValDataset)  
  DatasetbyTime<-  CDataset[,2:ncol(CDataset)]/SecTimeDataset[,2:ncol(SecTimeDataset)]*3600 ## Val/h

  DatasetbyTime[is.na(DatasetbyTime)] <- 0
  TimeDataset<-data.frame(CountGame = 1:RegularMatches, DatasetbyTime)
  colnames(TimeDataset)<- colnames(CDataset)
  
  TimeDataset[sapply(TimeDataset,is.infinite)] <- 0
  CDataset[sapply(TimeDataset,is.infinite)] <- 0  
  ##(2) For +/- Dataset
  WrongIndexInPlusMinDataset<-EvaluatedTimeVsValue(ValMat = PlusMinusDataset, TimeMat = SecTimeDataset)
  PMDataset<-DfCorrection(PlusMinusDataset, WrongIndexInValDataset)  
  PlusMinusbyTime<-  PMDataset[,2:ncol(PMDataset)]/SecTimeDataset[,2:ncol(SecTimeDataset)]*3600 ## Val/h
  PlusMinusbyTime[is.na(PlusMinusbyTime)] <- 0
  PlusMinusTimeDataset<-data.frame(CountGame = 1:RegularMatches, PlusMinusbyTime)
  colnames(PlusMinusTimeDataset)<- colnames(PMDataset)
  
  PMDataset[sapply(TimeDataset,is.infinite)] <- 0
  PlusMinusTimeDataset[sapply(TimeDataset,is.infinite)] <- 0

  #CDataset, TimeDataset, PMDataset, PlusMinusTimeDataset are the important Datasets Cleaned
  write.csv(CDataset, paste0(savepath, Season, "CDataset.csv"))
  write.csv(TimeDataset, paste0(savepath, Season, "TimeDataset.csv"))
  write.csv(PMDataset, paste0(savepath, Season,"PMDataset.csv"))
  write.csv(PlusMinusTimeDataset, paste0(savepath, Season,"PlusMinusTimeDataset.csv"))
  write.csv(SecTimeDataset, paste0(savepath, Season,"SecTimeDataset.csv"))
}

JoinRepeatedPlayers<- function(Data){
  
  # Getting the subset of only Players wit more than one column appear
  # This is due to the facvt that the might have played in more than one team
  columnNames<- colnames(Data)
  UniquePlayers<-substr(columnNames, 1,8) 
  Mytab<-as.data.frame(table(UniquePlayers))
  RepeatedPlayers<- filter(Mytab, Freq>1)
  
  #Creating a Data.frame to store results
  Res<- matrix(nrow=RegMatches,
               ncol= length(RepeatedPlayers$UniquePlayers))
  Res<- as.data.frame(Res)
  colnames(Res) <-as.character(RepeatedPlayers$UniquePlayers)
  
  for(i in 1:nrow(RepeatedPlayers)){
    Smallframe <-select(Data, 
                        contains(as.character(RepeatedPlayers[i,1])))# change first 1 for i
    Res[,i]<-apply(Smallframe, 1, Choosedif0)
    if(class(Res[,i])!="numeric"){
      print(paste0(RepeatedPlayers[i,1], " in iteration ",i))
    }
  }  
  eliminateRep<- as.character(RepeatedPlayers$UniquePlayers)
  RemoveRep <- select(Data, -contains("_")) %>% select(-one_of(eliminateRep))
  ## The warning is OK
  EndData<-cbind(RemoveRep, Res)
  colnames(EndData)[2:length(colnames(EndData))]<- 
    substr(colnames(EndData)[2:length(colnames(EndData))],2,8)
  
  
  return(EndData)  
}

Choosedif0<-function(x){
  #### It takes a vector of two numbers and 
  #### It gives out the one different to 0 if possible
  col1<- as.numeric(x[1])
  col2<- as.numeric(x[2])
  if(length(x)==3){
    col3 <- as.numeric(x[3])
  }
  else{col3<- rep(0, length(col1))}
  if(col1==0 & col2==0 & col3==0){return(as.numeric(0))}
  else if(col1!=0 & col2==0 & col3 == 0){return(col1)}
  else if(col2!=0 & col1==0 & col3 == 0){return(col2)}
  else if(col1==0 & col2==0 & col3 != 0){return(col3)}
  
  else{return(max(c(col1,col2, col3)))}
}


JoinPlayersValuesIntoOneCol<- function(myData){
  n<-length(colnames(myData))
  Datas <- myData[,2:n] # dropoutCols<- c("X")
  FilteredFrame<- Datas %>%
    filter(CountGame <=RegMatches) %>% 
    select(-contains("GameId"))
  FilteredFrame[mapply(is.infinite, FilteredFrame)] <- NA ### TO REMOVE IF SO
  FilteredFrame[is.na(FilteredFrame)] <- 0
  Dataset<- JoinRepeatedPlayers(Data = FilteredFrame)
  return(Dataset)
}


DfCorrection<- function(Data, vecindexes= WrongIndexInValDataset){
  ## Correction in the Dataset for the indexes passed set to 0
  if(length(vecindexes)==0){return(Data)}
  else{
    for(i in 1:length(vecindexes)){
      Indexes<- unlist(strsplit(vecindexes[1], ","))
      row<- as.numeric(Indexes[1])
      column<- as.numeric(Indexes[2])
      Data[row, column]<-0
      
      return(Data)  
    }}}
EvaluatedTimeVsValue<- function(ValMat, TimeMat){
  # It returns the indexes of the matrix in ValMat that should be 0 in a string
  WRONGVALUATIONindex <- integer(0)
  for( i in 2:ncol(ValMat)){
    Vec1<-TimeMat[,i]
    Vec2<-ValMat[,i]
    index<-which(Vec1==0)
    which(Vec2[index]!=0)
    Condition<-identical(Vec2[index],rep(0,length(index)))
    
    # checking incoherences on time 
    if(Condition==TRUE){ 
      
    }else{WRONGVALUATIONindex<-c(WRONGVALUATIONindex,paste0(which(Vec2[index]!=0),",",i))
    }
  }
  return(WRONGVALUATIONindex)
}

suppressWarnings(main())
# There is one warning related to a join of columns where more than the joined columns are supplied
# No problem