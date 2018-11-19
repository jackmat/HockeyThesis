### Loading Libraries
library(ggplot2)
library(reshape2)
library(dplyr)
library(tidyr)
library(tidyverse) 
library(broom)
library(gridExtra)
library(kableExtra)
library(xtable)
library(plyr)
library(RMySQL)
library(rlang)


## Environment for graphics
options(scipen=999)  # turn-off scientific notation like 1e+48 NOT SURE WHAT IT DOES
theme_set(theme_bw())  # pre-set the bw theme.


#### Global variables
Boolean <- TRUE #Changing to TRUE if wanting to work with non-zero Data (reccommended)
NameVar <-""
NTOP<- 944
Season<-2007
SalariesCalc <- FALSE # Changing to True when scrapped Data is on the varible Salaries2007
loadpath<-"C:/Users/Carles/Desktop/MasterThesis/CodeThesis/CleanDatasets/" 
RegularMatches<-82
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"

## Loading Datasets
CDataset<-read.csv(paste0(loadpath, Season, "CDataset.csv"),check.names=FALSE)
TimeDataset<-read.csv(paste0(loadpath, Season, "TimeDataset.csv"),check.names=FALSE)
PlusMinusTimeDataset<-read.csv(paste0(loadpath, Season,"PlusMinusTimeDataset.csv"),check.names=FALSE)
PMDataset<-read.csv(paste0(loadpath, Season,"PMDataset.csv"),check.names=FALSE)
SecTimeDataset<-read.csv(paste0(loadpath, Season,"SecTimeDataset.csv"),check.names=FALSE)
CDataset<-CDataset[,2:length(CDataset)]
TimeDataset<-TimeDataset[,2:length(TimeDataset)]
PlusMinusTimeDataset<-PlusMinusTimeDataset[,2:length(PlusMinusTimeDataset)]
PMDataset<-PMDataset[,2:length(PMDataset)]
SecTimeDataset<-SecTimeDataset[,2:length(SecTimeDataset)]


TopCols <- function(Data, topn=3){
  ### It extracts top n players by higher valuation
  mylen<-apply(Data[,2:length(Data)],2, sum)
  lst <- sort(mylen, index.return=TRUE, decreasing=TRUE)
  Topn<-lapply(lst, `[`, lst$x %in% head(unique(lst$x),topn))
  return(names(Topn$x))
}
mydb <- dbConnect(MySQL(), 
                 user='root', 
                 password='', 
                 dbname='nhl', 
                 host='localhost')


QueryMySQL <- function(mydb= mydb, query){
  # Fetching a query to a db
  rs<- dbSendQuery(mydb, query)
  topNAMES = fetch(rs, n= -1)
  return(topNAMES)
}
SeasonCompletename <- function(Season){
  # Returning a specific SeasonName to be be read in nhl database for table player_career_stats 
  return(paste0(Season,"-",Season+1))
}
MyQuantileApplication<-function(Data, DatVar, probs = c(0.05, 0.25, 0.5, 0.75,0.95)){
  # It returns the quantiles without taking into account 0
  MeanData<-apply(Data, 1, quantile, probs = c(0.05, 0.25, 0.5, 0.75,0.95))
  MeaNData<- as.data.frame(t(MeanData))
  uData<- data.frame(MeaNData, counter = 1:nrow(MeaNData), Dat = DatVar)
  colnames(uData)<-c("5%", "25%", "50%","75%", "95%", "counter", "Dat")
  return(uData)
}
  ##################################General Evaluation of the Data ############
  myData_melted <- melt(CDataset, id.vars = 'CountGame')
  myTime_melted<- melt(TimeDataset, id.vars = 'CountGame')
  myPlusMinus_melted<-  melt(PMDataset, id.vars = 'CountGame')
  PlusMinusTime_melted<-  melt(PlusMinusTimeDataset, id.vars = 'CountGame')
    
  # Eliminating from evaluation values exactly 0, which means probably that the player has not played
  if(Boolean == TRUE){
    Boolean <- FALSE
    myData_melted<-myData_melted[ !myTime_melted$value==0,] 
    myPlusMinus_melted<-myPlusMinus_melted[ !myTime_melted$value==0,] 
    PlusMinusTime_melted<-PlusMinusTime_melted[ !myTime_melted$value==0,]
    myTime_melted<-myTime_melted[ !myTime_melted$value==0,]
    }
  #Adding Variable to know which measure they are
  Valmelted<-cbind(myData_melted, Dat="Val")
  Valtimemelted<-cbind(myTime_melted, Dat="Val/h")
  PMValmelted<-cbind(myPlusMinus_melted, Dat="+/- Val")
  PlusMinusTimemelted<-cbind(PlusMinusTime_melted, Dat="+/- Val/h")
  # Putting them all together in Datasetdiff0
  Datasetdiff0<- rbind(Valmelted, Valtimemelted,PMValmelted,PlusMinusTimemelted) 

