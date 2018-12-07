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
Season<-2008
SalariesCalc <- FALSE # Changing to True when scrapped Data is on the varible Salaries2007
loadpath<-"C:/Users/Carles/Desktop/MasterThesis/CodeThesis/CleanDatasets/" 
RegularMatches<-82
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"

## Loading Datasets
readFile<- function(Season, loadpath){
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
  
  
  return(list(Direct= CDataset, 
              Directh= TimeDataset, 
              Collective = PMDataset,
              Collectiveh = PlusMinusTimeDataset,
              TimeSet = SecTimeDataset))

  }
DataSet2007 <-readFile(Season = 2007, loadpath = loadpath)
DataSet2008 <-readFile(Season = 2008, loadpath = loadpath)

## Melting Datasets and just in selecting only those values in time different than 0 
MeltingData <- function(Data,variab = "CountGame", elim0 = TRUE, Seasonvar){ 
  myData_melted <- melt(Data, id.vars = variab)
    
  if(elim0==TRUE){
    if(Seasonvar == 2007){
      myTime_melted<- melt(DataSet2007[[5]], id.vars = 'CountGame')
      myData_melted<-myData_melted[ !myTime_melted$value==0,]}
    if(Seasonvar == 2008){
      myTime_melted<- melt(DataSet2008[[5]], id.vars = 'CountGame')
      myData_melted<-myData_melted[ !myTime_melted$value==0,]}
    
    else{"No season provided properly (Not 2007 nor 2008)"}
    }
  return(myData_melted)
  }
DataMelted2007<-lapply(DataSet2007, MeltingData, Seasonvar = 2007)
DataMelted2008<-lapply(DataSet2008, MeltingData, Seasonvar = 2008)


Valmelted2007           <-cbind(DataMelted2007[[1]], Dat="Direct", Year = "07-08")
Valtimemelted2007       <-cbind(DataMelted2007[[2]], Dat="Directh", Year = "07-08")
PMValmelted2007         <-cbind(DataMelted2007[[3]], Dat="Collective", Year = "07-08")
PlusMinusTimemelted2007 <-cbind(DataMelted2007[[4]], Dat="Collectiveh", Year = "07-08")

Valmelted2008           <-cbind(DataMelted2008[[1]], Dat="Direct", Year = "08-09")
Valtimemelted2008       <-cbind(DataMelted2008[[2]], Dat="Directh", Year = "08-09")
PMValmelted2008         <-cbind(DataMelted2008[[3]], Dat="Collective", Year = "08-09")
PlusMinusTimemelted2008 <-cbind(DataMelted2008[[4]], Dat="Collectiveh", Year = "08-09")



# Putting them all together in Datasetdiff0
Datasetdiff0<- rbind(Valmelted2007, Valmelted2008,
                     Valtimemelted2007, Valtimemelted2008,
                     PMValmelted2007,PMValmelted2008, 
                     PlusMinusTimemelted2007,PlusMinusTimemelted2008 ) 
quantiles<-quantile(Datasetdiff0$value, probs = c(0.001,0.999))

quantilebyMatch<- Datasetdiff0 %>% group_by(Dat, Year, CountGame)%>% 
  dplyr::summarise('5%' = quantile(value, probs = 0.05),
                   '25%' = quantile(value, probs = 0.25),
                   '50' = quantile(value, probs = 0.5),
                    'mean'= mean(value),
                   '75%'= quantile(value, probs = 0.75),
                   '95%'= quantile(value, probs = 0.95))
quantilemelted<- melt(quantilebyMatch, id.vars = c("Dat", "Year", "CountGame"))
quantilemelted$CountGame<- as.numeric(quantilemelted$CountGame)

colnames(quantilemelted)[4]<- "Quantile"
scatterplot2<-ggplot(quantilemelted, aes(x= CountGame, y = value))+ 
  facet_grid(Dat~Year, scales = "free")+
  labs(#title="Quantile analysis of player's performance per match and year", 
       y="Valuation", 
       x="Nº of regular season Match" 
       #caption = "Source: Carles Illustration"
  )+    geom_line(aes(color = Quantile))+   # add quantile values at x=0.5
  theme(legend.position="right", 
        legend.text=element_text(size=8),
        legend.title=element_text(size=8)
        )+ guides(col = guide_legend(nrow = 6, byrow = TRUE))
scatterplot2


## Calculating the quantiles for the Data selecting from 1% to 99% 
quantiledata<- matrix()
DatVars<-unique(Datasetdiff0$Dat)
yearVars<-unique(Datasetdiff0$Year)
GeneralQuantileTable<-matrix(ncol = 7)
rownames<-integer(0)
counter<-0

for(j in 1:length(DatVars)){
  for(year in 1:length(yearVars)){
    filt<-Datasetdiff0 %>% filter(Dat == DatVars[j]& Year == yearVars[year]) 
    rownames<-c(rownames, paste0(DatVars[j],yearVars[year]))    
    FilteredData<- filt%>% filter(value < quantile(filt$value, 0.999)) %>% 
      filter( value >  quantile(filt$value, 0.001))
    if(counter ==0){
      quantiledata<- FilteredData
      counter<- counter+1
      GeneralQuantileTable<-c(quantile(filt$value, probs = c(0.05,0.25,0.5,0.75,0.95)), mean =mean(filt$value), sd= sd(filt$value))}
    else{quantiledata<-rbind(quantiledata, FilteredData)
          counter <- counter +1
          GeneralQuantileTable<-rbind(GeneralQuantileTable, c(quantile(filt$value, probs = c(0.05,0.25,0.5,0.75,0.95)), mean(filt$value), sd(filt$value)))
          }
  }}


    
substrRight <- function(x, n){
  sapply(x, function(xx)
    substr(xx, (nchar(xx)-n+1), nchar(xx))
  )
}
row.names(GeneralQuantileTable)<-substrRight(rownames,5)
library(kableExtra)
QuantileTransf<-t(GeneralQuantileTable)
Quantilediff1<-(QuantileTransf[,2]-QuantileTransf[,1])/QuantileTransf[,1]*100
Quantilediff2<-(QuantileTransf[,4]-QuantileTransf[,3])/QuantileTransf[,3]*100
Quantilediff3<-(QuantileTransf[,6]-QuantileTransf[,5])/QuantileTransf[,5]*100
Quantilediff4<-(QuantileTransf[,8]-QuantileTransf[,7])/QuantileTransf[,7]*100
GeneralQuantileTableT<-data.frame(QuantileTransf[,1:2], 'Direct(% change)'= Quantilediff1,
                                  QuantileTransf[,3:4], 'Directh (% change)'= Quantilediff2,
                                  QuantileTransf[,5:6], 'Collective (% change)'= Quantilediff3,
                                  QuantileTransf[,7:8], 'Collectiveh (% change'= Quantilediff4)
colnames(GeneralQuantileTableT)<- c("07-08","08-09", "% change", "07-08","08-09", "% change", "07-08","08-09", "% change", "07-08","08-09","% change") 

QuantileTab<-kable(GeneralQuantileTableT,"html", booktabs = TRUE, digits = 3) %>%
  kable_styling(font_size = 9) %>%
  add_header_above(c(" " = 1, "Direct" = 3, "Direct/h " = 3, "Collective" = 3, "Collective/h" = 3))%>%
  column_spec(c(4,7,10,13), bold = T, italic = T) 

      

hist1<-ggplot(quantiledata, aes(x= value))+
  facet_grid(Year~Dat, scales = "free") +
  #scale_fill_gradient("Count", low = "green", high = "red")+
  labs(#subtitle="Distribution of the 99.8% of the matches (Non- outliers shown)", 
       y="Frequency", 
       x="Player's valuation per match"#, title= paste0("Distribution of player's valuation for ", Season,"-",Season+1)
       #caption = "Source: Carles Illustration"
  )+
  geom_histogram(aes(x = value, 
                     y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]),
                 bins = 20, stat= "bin", fill = "blue" 
  )


hist1

boxplot1 <-ggplot(quantiledata, aes(x ="", y=value))+ 
  facet_grid(Dat~Year, scales = "free")+ 
  labs(#subtitle=paste0("99.8% of the player's performance (Non- outliers shown)"), 
       y="Valuation range", 
       x=""#, 
       #title= paste0("Players Valuation")#, 
       #caption = "Source: Carles Illustration"
  )+
  geom_boxplot(outlier.size = 0.1, outlier.color = "red")
boxplot1

mydb <- dbConnect(MySQL(), 
                  user='root', 
                  password='', 
                  dbname='nhl', 
                  host='localhost')


#### Getting names and
mylistDatasets<- list(DataSet2007, DataSet2008)
CompareGP<-list()
Seasons<- c(2007, 2008)
for(i in 1:length(mylistDatasets)){
  
  TopPlayers<-TopCols(mylistDatasets[[i]]$Direct, NTOP)
  TopDataset <- subset(mylistDatasets[[i]]$Direct, select = c("CountGame",TopPlayers))
  PlayerId <- TopPlayers
  query = paste0("SELECT PlayerName FROM `player` WHERE PlayerId IN (", paste(PlayerId,collapse=","),")")
  topNAMES <- QueryMySQL(mydb= mydb, query = query)
  SeasonVar<- SeasonCompletename(Season = Seasons[i])
  
  ################### Checking that time played in different matches and GP from Stats are the same
  
  GPquery = paste0("SELECT player.PlayerName, i.PlayerId, sum(i.GP) AS GP from player, (SELECT  DISTINCT team, PlayerId ,GP FROM `player_career_stats` WHERE Season = '",SeasonVar,"' AND SeasonType = 'Regular Season')i  WHERE i.PlayerId = player.PlayerId GROUP by PlayerId")
  GPPlayer<- QueryMySQL(mydb= mydb, GPquery)
  GPPlayers<-GPPlayer[!duplicated(GPPlayer),] #removing duplicated rows
  dim(GPPlayer)== dim(GPPlayers)
  SecTableGP<-colSums(mylistDatasets[[i]]$TimeSet[,2:ncol(mylistDatasets[[i]]$TimeSet)] != 0)
  mynames<-as.numeric(as.character(names(SecTableGP)))
  SecTableGP<-data.frame(PlayerId=mynames,
                         GPsec=unlist(SecTableGP,use.names = F))
  
  CompareGP[[i]]<-left_join(SecTableGP, GPPlayers, by = "PlayerId")
}
## Warning In. local(con, statement)... Decimal MySQL is GOOD

totPath <- paste0("C:/Users/Carles/Desktop/MasterThesis/CodeThesis/EvalCode/", 
                  "scrappingSalariesNHL.R")
source(totPath)
GeneralTableList<-list()
if(SalariesCalc ==FALSE){
  SalariesCalc <- TRUE
  Salaries2007<-main(2008) # stands for paste0((year-1),'-', year) 
  Salaries2008<-main(2009)}
listSalaries<- list(Salaries2007, Salaries2008)
for(i in 1:length(c(2007,2008))){
print(i)
  # change to 1 or 2 for 2007 or 2008  
GeneralTable<-data.frame(id =colnames(mylistDatasets[[i]]$Direct)[2:length(mylistDatasets[[i]]$Direct)])%>%
  mutate(Direct = apply(mylistDatasets[[i]]$Direct[,2:ncol(mylistDatasets[[i]]$Direct)],2,sum))%>%
  mutate(Directh = apply(mylistDatasets[[i]]$Directh[,2:ncol(mylistDatasets[[i]]$Directh)],2,sum))%>%
  mutate(Collective = apply(mylistDatasets[[i]]$Collective[,2:ncol(mylistDatasets[[i]]$Collective)],2,sum))%>%
  mutate(Collectiveh = apply(mylistDatasets[[i]]$Collectiveh[,2:ncol(mylistDatasets[[i]]$Collectiveh)],2,sum))
GeneralTable$id<- as.numeric(as.character(GeneralTable$id))

GeneralTable<-GeneralTable%>%left_join(CompareGP[[i]][c('PlayerId','PlayerName', 'GP','GPsec')], 
                                             by = c("id"= "PlayerId"))%>% 
  mutate(PlayerName = replace(PlayerName, PlayerName=='Alexander Edler', 'Alex Edler')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Alexander Steen', 'Alex Steen')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Alex Frolov', 'Alexander Frolov')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Alexandre Burrows', 'Alex Burrows')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Bates Battaglia', 'Jon "Bates" Battaglia')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Daniel Carcillo', 'Dan Carcillo')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Daniel Lacosta', 'Dan LaCosta')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Daniel Taylor', 'Dan Taylor')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Dany Sabourin', 'Dan Sabourin')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='David Steckel', 'Dave Steckel')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Dimitri Patzold', 'Dmitri Patzold')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='DJ King', 'D.J. King')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Douglas Murray', 'Doug Murray')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Freddy Modin', 'Fredrik Modin')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Gregory Campbell', 'Greg Campbell')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Gregory Stewart', 'Greg Stewart')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='J-P Dumont', 'J.P. Dumont')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Jason LaBarbera', 'Jason Labarbera')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Joe Dipenta', 'Joe DiPenta')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Jonathan Quick', 'Jon Quick')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Jordan Lavallee-Smotherman', 'Jordan LaVallee-Smotherman')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Joseph Motzko', 'Joe Motzko')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Marc-Antoine Pouliot', 'Marc Pouliot')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Martin St Pierre', 'Martin St. Pierre')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Matthew Carle', 'Matt Carle')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Maxime Talbot', 'Max Talbot')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Micki Dupont', 'Micki DuPont')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Michael Funk', 'Mike Funk')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Michael Grier', 'Mike Grier')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Michael Zigomanis', 'Mike Zigomanis')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Nicklas Grossmann', 'Niklas Grossman')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Niclas Bergfors', 'Nicklas Bergfors')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Nikolay Zherdev', 'Nikolai Zherdev')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Olie Kolzig', 'Olaf Kolzig')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Patrick Rissmiller', 'Pat Rissmiller')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Pete Vandermeer', 'Peter Vandermeer')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Teddy Purcell', 'Ted Purcell')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Vinny Prospal', 'Vaclav Prospal')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Vitaly Vishnevski', 'Vitali Vishnevsky')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Vyacheslav Kozlov', 'Slava Kozlov')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Alexandre Bolduc', 'Alex Bolduc')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Dan Lacouture', 'Dan LaCouture')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='David Van Der Gulik', 'David Van der Gulik')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Evgeny Artyukhin', 'Evgeni Artyukhin')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Jaime Sifers', 'Jamie Sifers')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Maksim Mayorov', 'Maxim Mayorov')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Martins Karsums', 'Martin Karsums')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Michael Sauer', 'Mike Sauer')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Mitchell Fritz', 'Mitch Fritz')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Nikolay Kulemin', 'Nikolai Kulemin')) %>%  
  mutate(PlayerName = replace(PlayerName, PlayerName=='Pierre-Luc Letourneau-Leblond', 'Pierre-Luc Leblond')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='TJ Galiardi', 'T.J. Galiardi')) %>%
  mutate(PlayerName = replace(PlayerName, PlayerName=='Patrick Dwyer', 'Pat Dwyer')) %>%
  left_join(listSalaries[[i]], by = c("PlayerName"= "Player"))%>%
  select(id, PlayerName,P, Age, Salary, GPsec, G,GA, PlusMin,NHL, Direct,Directh, Collective,Collectiveh)%>%
  filter(GPsec != 0)%>%
  dplyr::rename(Position = P)
  
  GeneralTable$Position[which(GeneralTable$Position%in%c("LW","RW", "C"))]<-"F"

  GeneralTable <- GeneralTable %>%
  dplyr::rename(GP = GPsec)%>%
  dplyr::rename(Points = NHL)%>%
  mutate(GPDirect = Direct/GP)%>%
  mutate(GPCollective = Collective/GP)%>%
  mutate(GPDirecth = Directh/GP)%>%
  mutate(GPCollectiveh = Collectiveh/GP)%>%
  mutate(GPPlusMin= PlusMin/GP)%>%
  mutate(GPPoints= Points/GP)%>%
  mutate_if(is.numeric, round ,2)%>% 
  filter(Directh!=Inf)%>%
  filter(Directh!=-Inf)%>%
  filter(Collectiveh!=Inf)%>%
  filter(Collectiveh!=-Inf)
GeneralTableList[[i]]<- GeneralTable %>% arrange(PlayerName)
}

GeneralTableList1<-cbind(GeneralTableList[[1]], Year = "07-08")
GeneralTableList2<-cbind(GeneralTableList[[2]], Year = "08-09")
TotalDataFrame<- rbind(GeneralTableList1, GeneralTableList2)
tableresData <- melt(TotalDataFrame, id.vars = colnames(TotalDataFrame)[c(1:8, length(colnames(TotalDataFrame)))])


Plottingdiffmeasures<-function(Data){
  ggplot(Data, aes(x = Salary, y = value)) + 
    facet_grid(Year~., scales = "free")+ 
    geom_point(aes(color = variable , group = Position
    ),show.legend = TRUE) +
    labs(subtitle="Metrics comparison", 
         y="Valuation by Player", 
         x="Salary (in Million of dollars)", 
         title=paste0("Player's valuation ")#, 
         #caption = "Source: Carles Illustration"
    )
}
scatterplot4<- Plottingdiffmeasures(tableresData%>% filter(grepl("GP",variable)))
scatterplot5<- Plottingdiffmeasures(tableresData%>% filter(!grepl("GP",variable)))
ind<-c(8:19)
normtableres<-data.frame(cbind(Salary =TotalDataFrame$Salary, Position=TotalDataFrame$Position, apply(TotalDataFrame[,ind],2,scale)),Year = TotalDataFrame$Year)
norm_tableresData <- reshape2::melt(normtableres, id.vars = c("Salary", "Position", "Year"))
norm_tableresData$Salary<- as.numeric(as.character(norm_tableresData$Salary))
norm_tableresData$Position<- as.character(norm_tableresData$Position)
norm_tableresData$value<- as.numeric(norm_tableresData$value)

scatterplot6<- Plottingdiffmeasures(norm_tableresData%>% filter(grepl("GP",variable)))
scatterplot7<- Plottingdiffmeasures(norm_tableresData%>% filter(!grepl("GP",variable)))


scatterplot891011<-function(Data, scaled ="Scaled", type = "by Games Played"){
  p<-ggplot2::ggplot(Data)+
    facet_grid(variable~Year, scales = "free")+        
    geom_point(aes(x =Salary, y = value, color = Position))+
    theme_bw()+
    labs(subtitle=paste0(scaled," ",type  ,"Regression of Metrics Valuation~Salary"), 
         y="Valuation", 
         x="Salary (in $M)", 
         title= paste0("Metrics regression")#, 
         #caption = "Source: Carles Illustration"
    )
  
  return(p)
}


scatterplot8 <- scatterplot891011(tableresData%>% filter(grepl("GP",variable)),
                                              type = "by Games Played",
                                  scaled = ""  )
scatterplot9 <- scatterplot891011(tableresData%>% filter(!grepl("GP",variable)),
                                  type = "by Season",
                                  scaled = ""  )
scatterplot10<- scatterplot891011(norm_tableresData%>% filter(grepl("GP",variable)),
                                  type = "by Games Played",
                                  scaled = "Scaled" )

scatterplot11<- scatterplot891011(norm_tableresData%>% filter(!grepl("GP",variable)),
                                  type = "by Season",
                                  scaled = "Scaled"  )

MetricsbyPosition<-function(Data, scaled ="Scaled", type = "by Games Played"){
  p<-ggplot2::ggplot(Data)+
    facet_grid(variable~Position, scales = "free")+        
    geom_point(aes(x =Salary, y = value, color = Year))+
    theme_bw()+
    labs(#subtitle=paste0(scaled," ",type  ,"Regression of Metrics Valuation~Salary"), 
         y="Valuation", 
         x="Salary (in $M)"#, 
         #title= paste0("Metrics regression")#, 
         #caption = "Source: Carles Illustration"
    )
  
  return(p)
}

byPosition<-MetricsbyPosition(tableresData%>% filter(!grepl("GP",variable)),
type = "by Season",
scaled = ""  )

byPositionGP<-MetricsbyPosition(tableresData%>% filter(grepl("GP",variable)),
                  type = "by Season",
                  scaled = ""  )

## The nice results are stored here
thelist<-list(boxplot1, hist1, scatterplot2, QuantileTab, byPosition, byPositionGP)
namslist<-c("boxplot", "histogram",
            "Quantile", "QuantileTable", 
            "PositionSalaryRegression","SalaryPositionRegressionGP")



