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
Boolean <- FALSE #Changing to TRUE if wanting to work with non-zero Data (reccommended)
NameVar <-""
NTOP<- 944
Season<-2007
SalariesCalc <- FALSE # Changing to True when scrapped Data is on the varible Salaries2007
loadpath<-"C:/Users/Carles/Desktop/MasterThesis/CodeThesis/CleanDatasets/" 
RegularMatches<-82
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"

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

myquantile<- function(Data, probs){
  # Function that calculates quantiles without taking into account values equals to 0
  DATA<- Data[Data!=0]
  return(quantile(DATA, probs = probs))
}
Plottingdiffmeasures<-function(Data, Season){
  ggplot(Data)+ geom_point()
  ggplot(Data, aes(x = Salary, y = value)) + 
    geom_point(aes(color = variable #, group = P
    ),show.legend = TRUE) +
    labs(subtitle="Metrics comparsion", 
         y="Valuation by Player", 
         x="Salary (in Million of dollars)", 
         title=paste0("Player's valuation on ",Season)#, 
         #caption = "Source: Carles Illustration"
    )
}
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
  MeanData<-apply(Data, 1, myquantile, probs = c(0.05, 0.25, 0.5, 0.75,0.95))
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
    myData_melted<-myData_melted[ !myData_melted$value==0,] 
    myTime_melted<-myTime_melted[ !myTime_melted$value==0,]
    myPlusMinus_melted<-myPlusMinus_melted[ !myPlusMinus_melted$value==0,] 
    PlusMinusTime_melted<-PlusMinusTime_melted[ !PlusMinusTime_melted$value==0,]
  }
  #Adding Variable to know which measure they are
  Valmelted<-cbind(myData_melted, Dat="Val")
  Valtimemelted<-cbind(myTime_melted, Dat="Val/h")
  PMValmelted<-cbind(myPlusMinus_melted, Dat="+/- Val")
  PlusMinusTimemelted<-cbind(PlusMinusTime_melted, Dat="+/- Val/h")
  
  # Putting them all together in Datasetdiff0
  Datasetdiff0<- rbind(Valmelted, Valtimemelted,PMValmelted,PlusMinusTimemelted) 
  quantiles<-quantile(Datasetdiff0$value, probs = c(0.025,0.975))
  hist1<-ggplot(Datasetdiff0, aes(x= value))+
    facet_grid(.~Dat, scales = "free") +
    scale_fill_gradient("Count", low = "green", high = "red")+
    labs(subtitle="Distribution of the 95% of the matches (Non- outliers shown)", 
         y="Frequency", 
         x="Player's valuation per match", 
         title= paste0("Distribution of player's valuation for ", Season,"-",Season+1)
         #caption = "Source: Carles Illustration"
    )+
    geom_histogram(aes(x = value, 
                       y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..], 
                       fill = (..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]),
                   bins = 20, stat= "bin")+
    xlim(c(quantiles[1],quantiles[2])) 
  boxplot1<-ggplot(Datasetdiff0, aes(x ="", y=value))+ 
    facet_grid(.~Dat)+ coord_cartesian(ylim = c(-3, 4))+
    labs(subtitle=paste0("Box plot distritbution (Outliers not shown)"), 
           y="Valuation range", 
           x="", 
           title= paste0("Players Valuation for ", Season,"-",Season+1)#, 
           #caption = "Source: Carles Illustration"
    )+
    geom_boxplot(outlier.shape=NA,
                 outlier.size=NA, notch=F)
    

####################### Time Series Evaluation  
  MeanVal <- MyQuantileApplication(Data= CDataset, DatVar = "Val")
  TimeVal <- MyQuantileApplication(Data= TimeDataset, DatVar = "Val/h")
  PlusMinVal <- MyQuantileApplication(Data= PMDataset, DatVar = "+/- Val")
  TimePlusMinVal <- MyQuantileApplication(Data= PlusMinusTimeDataset, DatVar = "+/- Val/h")
  
  totuData<- rbind(MeanVal, TimeVal, PlusMinVal, TimePlusMinVal)
  meanmelted<- melt(totuData, id.vars = c("counter", "Dat"))
  scatterplot2<-ggplot(meanmelted, aes(x= counter, y = value))+ 
    facet_grid(.~Dat)+
    labs(subtitle="Quantile analysis of player's performances for each match", 
         y="Valuation", 
         x="Nº of regular season Match", 
         title= paste0("Quantile Player's performance per match in ", Season,"-",Season+1)#, 
         #caption = "Source: Carles Illustration"
    )+    geom_line(aes(color = variable))   # add quantile values at x=0.5

  
  #  CDataset, TimeDataset, PMDataset, PlusMinusTimeDataset
  
### Getting the name for the top N players

TopPlayers<-TopCols(CDataset, NTOP)
TopDataset <- subset(CDataset, select = c("CountGame",TopPlayers))
PlayerId <- TopPlayers
query = paste0("SELECT PlayerName FROM `player` WHERE PlayerId IN (", paste(PlayerId,collapse=","),")")
topNAMES <- QueryMySQL(mydb= mydb, query = query)
SeasonVar<- SeasonCompletename(Season = Season)

################### Checking that time played in different matches and GP from Stats are the same

GPquery = paste0("SELECT player.PlayerName, i.PlayerId, sum(i.GP) AS GP from player, (SELECT  DISTINCT team, PlayerId ,GP FROM `player_career_stats` WHERE Season = '",SeasonVar,"' AND SeasonType = 'Regular Season')i  WHERE i.PlayerId = player.PlayerId GROUP by PlayerId")
GPPlayer<- QueryMySQL(mydb= mydb, GPquery)
GPPlayers<-GPPlayer[!duplicated(GPPlayer),] #removing duplicated rows
SecTableGP<-colSums(SecTimeDataset[,2:ncol(SecTimeDataset)] != 0)
mynames<-as.numeric(as.character(names(SecTableGP)))
SecTableGP<-data.frame(PlayerId=mynames,
                       GPsec=unlist(SecTableGP,use.names = F))

CompareGP<-left_join(SecTableGP, GPPlayers, by = "PlayerId")
# BESTSCORESPAPER2013<-c("Jason Spezza", "Jonathan Toews","Joe Pavelski", "Marian Hossa",
#                    "Patrick Sharp", "Sidney Crosby" , "Claude Giroux" ,"Tyler Seguin")


totPath <- paste0("C:/Users/Carles/Desktop/MasterThesis/CodeThesis/EvalCode/", 
                  "scrappingSalariesNHL.R")
source(totPath)
Seasonyear<- Season+1 # 2008 stands for 2007-2008 and so on
if(SalariesCalc ==FALSE){
SalariesCalc <- TRUE
Salaries2007<-main(Seasonyear)}
#Only taking into account full data
GeneralTable<-topNAMES%>%
  mutate(TotVal = apply(CDataset[,2:ncol(CDataset)],2,sum))%>%
  mutate(TotValh = apply(TimeDataset[,2:ncol(TimeDataset)],2,sum))%>%
  mutate(TotPMVal = apply(PMDataset[,2:ncol(PMDataset)],2,sum))%>%
  mutate(TotPMValh = apply(PlusMinusTimeDataset[,2:ncol(PlusMinusTimeDataset)],2,sum))%>%
  left_join(Salaries2007, by = c("PlayerName"= "Player"))%>%
  left_join(CompareGP, by = "PlayerName")%>% 
  select(PlayerName,P, Age, Salary, GPsec, G,GA, PlusMin,NHL, TotVal,TotPMVal, TotValh,TotPMValh)%>%
  filter(GPsec != 0)%>%
  dplyr::rename(GP = GPsec)%>%
  mutate(ByMatchVal = TotVal/GP)%>%
  mutate(ByMatchPMVal = TotPMVal/GP)%>%
  mutate(ByMatchValh = TotValh/GP)%>%
  mutate(ByMatchPMValh = TotPMValh/GP)%>%
  mutate(ByMatchPlusMin= PlusMin/GP)%>%
  mutate(ByMatchNHL= NHL/GP)%>%
  mutate_if(is.numeric, round ,2)%>% 
  filter(TotValh!=Inf)%>%
  filter(TotValh!=-Inf)


NamesCol<-colnames(GeneralTable)[8:length(colnames(GeneralTable))]
for( i in 1:length(NamesCol)){
  colarrange<- NamesCol[i]
  TopplayersbyMetric<-GeneralTable%>% 
    arrange(desc(eval(parse(text =colarrange))))  %>% 
    head(10)
  TableNames<- paste0(Season, " Top 10 Players order by metric performance ", colarrange)  
  
  png(filename = paste0(TableNames,".pdf",
                        width=nrow(TopplayersbyMetric)*10,
                        height=ncol(TopplayersbyMetric)*10)) 
  grid.table(TopplayersbyMetric) 
  dev.off() 
  
  print(xtable(TopplayersbyMetric, type = "latex"), file = paste0(FilepathSrotingPlots,TableNames,'.tex'))
  write.table(TopplayersbyMetric, paste0(FilepathSrotingPlots,TableNames,".csv"))
  
}

#hist(Table$GPsec-Table$GP.y,breaks = 100)


tableresData <- melt(GeneralTable, id.vars = colnames(GeneralTable)[1:7])

scatterplot4<- Plottingdiffmeasures(tableresData%>% filter(grepl("ByMatch",variable)),Season = Season)
scatterplot5<- Plottingdiffmeasures(tableresData%>% filter(!grepl("ByMatch",variable)),Season = Season)
scatterplot891011<-function(Data, Season, scaled ="Scaled", type = "by Games Played"){
  p<-ggplot2::ggplot(Data)+
  facet_grid(variable~., scales = "free")+        
  geom_point(aes(x =Salary, y = value))+
  theme_bw()+
  labs(subtitle=paste0(scaled," ",type  ,"Regression of Metrics Valuation~Salary"), 
         y="Valuation", 
         x="Salary (in $M)", 
         title= paste0("Metrics regression for ", Season,"-",Season+1)#, 
         #caption = "Source: Carles Illustration"
  )
  
  return(p)
}

colnames(GeneralTable)
ind<-c(8:19)
normtableres<-data.frame(cbind(Salary =GeneralTable$Salary, apply(GeneralTable[,ind],2,scale)))
norm_tableresData <- reshape2::melt(normtableres, id.vars = "Salary")
scatterplot6<- Plottingdiffmeasures(norm_tableresData%>% filter(grepl("ByMatch",variable)), Season = Season)
scatterplot7<- Plottingdiffmeasures(norm_tableresData%>% filter(!grepl("ByMatch",variable)), Season = Season)

scatterplot8 <- scatterplot891011(tableresData%>% filter(grepl("ByMatch",variable)),
                                  Season = Season, 
                                  type = "by Games Played",
                                  scaled = ""  )
scatterplot9 <- scatterplot891011(tableresData%>% filter(!grepl("ByMatch",variable)),
                                  Season = Season,
                                  type = "by Season",
                                  scaled = ""  )
scatterplot10<- scatterplot891011(norm_tableresData%>% filter(grepl("ByMatch",variable)),
                                  Season = Season,
                                  type = "by Games Played",
                                  scaled = "Scaled" )

scatterplot11<- scatterplot891011(norm_tableresData%>% filter(!grepl("ByMatch",variable)),
                                  Season = Season,
                                  type = "by Season",
                                  scaled = "Scaled"  )



listPlots<- list()
listPlots[[1]]<-boxplot1 # CHangning the date only to written once
listPlots[[2]]<-hist1
listPlots[[3]]<-scatterplot2 # Chage the title removing 2007
listPlots[[4]]<-scatterplot4
listPlots[[5]]<-scatterplot5
listPlots[[6]]<-scatterplot6
listPlots[[7]]<-scatterplot7
listPlots[[8]]<-scatterplot8
listPlots[[9]]<-scatterplot9
listPlots[[10]]<-scatterplot10
listPlots[[11]]<-scatterplot11

NamePlots<- c(paste0(Season,NameVar," Box summary of players Evaluation for all matches in ", Season),
            paste0(Season,NameVar," Histogram distribution from 0.05 to 0.95 quantiles of players Evaluation for all matches in 2007"),
            paste0(Season,NameVar," Scatterplot of all of players Evaluation for all matches in ",Season, "with quantiles c(0.05,0.25,0.5,0.75,0.95)"),
            paste0(Season,NameVar," Non-scaled comparison byMatch metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " Non-scaled comparison Total metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " scaled comparison byMatch metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " scaled comparison Total metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " Non-Scaled separated regression By match metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " Non-Scaled separated regression Total metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " Scaled separated regression By match metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " Scaled separated regression Total metrics to Salary all players in ", Season),
            paste0(Season,NameVar,  " GeneralTableWithMetrics"))  
              # Can I say it has a higher impact than the other measures on salary ?
FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"

for( i in 1:length(listPlots)){
  totname<-paste0(FilepathSrotingPlots,NamePlots[i],'.png')
  ggsave(plot= listPlots[[i]], file = totname,  device = 'png', limitsize = FALSE)
  # make plot
}


#Table meaning:
# Games Played(GP), Goals(G), Goals Assisted(GA), +/-, NHL Points (G+Assists)

print(xtable(GeneralTable, type = "latex"), file = paste0(FilepathSrotingPlots,NamePlots[8],'.tex'))
write.table(GeneralTable, paste0(FilepathSrotingPlots,NamePlots[12],".csv"))
# }
# main()

