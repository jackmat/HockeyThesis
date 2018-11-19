#  CDataset, TimeDataset, PMDataset, PlusMinusTimeDataset
library(forecast)
library(tseries)
library(astsa)
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
Season<- 2007
TotList<- list(DataSet2007,DataSet2008)
TotMat<-data.frame()
Seasonvect<- 2007:2008
for(d in 1:length(TotList)){
  DatasetList<- TotList[[d]]
  Positions<-unique(GeneralTableList[[1]]$Position)
  count<-1
  SeasonYear<- Seasonvect[d]
  
  for(posindex in 1: length(Positions)){
    print(paste0(posindex, "Out of ", length(Positions)))
    ## Selecting only ids by order
  
    IdFiltering<-GeneralTableList[[d]] %>% filter(Position == Positions[posindex]) %>% select(id) %>% apply(1,as.character)
  
    ## All being (p,d,q)== (0,0,0)
    GeneralNames<-c("Direct", "Directh", "Collective", "Collectiveh")
    
  
    for(dataset in 1:(length(DatasetList)-1)){
      print(paste0("Doing dataset", dataset))
      Data<- DatasetList[[dataset]]
      Data<-Data[,IdFiltering]
      res<-rep(0, times = length(2:ncol(Data)))
      obs<- rep(0, times = length(2:ncol(Data)))
  
      for(i in 2:ncol(Data)){
        #print(paste0(i , " out of ", ncol(Data)))
        ### The steps are:
        #(1) Selecting the matches Played by that player 
        #    (if time played is 0 in the timeDataset, then that player has not played a match)
        myData<-Data[,i]
        mytime<- DatasetList[[2]][,i]
        MyTrueData<- myData[-which(mytime==0)]
        len<-length(MyTrueData)
        # Saving variables in 10s
        obs[i]<- round(len/10)*10
        if((len==0)==TRUE){res[i]<-"None"}
        else{
          #(2) Generallywise, data is already quite stationary, however, detrending is used to be sure of it
          #MydiffData<-diff(MyTrueData)
          #(3) If length of the time series is more than 5 matches:
          #(3.1.1) If stationary, do modelling
          fit<-auto.arima(MyTrueData)
          res[i]<-paste0(arimaorder(fit),collapse = ",")  }
      }
          Mat<-data.frame(ArimaModel=res[2:length(res)], 
                          Range= obs[2:length(obs)]) 
          Mat[,1]<-as.factor(Mat[,1])
          Mat[,2]<-as.factor(Mat[,2])
          PartMat<-cbind(Mat, Position = Positions[posindex], Dataset=GeneralNames[dataset], Year = SeasonYear)
          if(count == 1){
            TotMat<- PartMat
            count<-count+1
          }else{
            TotMat<-rbind(TotMat, PartMat)
          }
        
            }
  }
}

MinimumModelFreq<-round(dim(TotMat%>%filter(ArimaModel != "None"))[1]*0.02, digits = 0) 
# Filterout models with less than 2% since it they are less typical than 1% of the models

ModelsMoreTypicals<-TotMat%>%filter(ArimaModel != "None")%>%group_by(ArimaModel)%>% 
  dplyr::summarise(Frequency = n())%>% arrange(Frequency)%>%  
  filter(Frequency>MinimumModelFreq )

TotMatFilt<- TotMat %>% filter(ArimaModel %in% ModelsMoreTypicals$ArimaModel)

ModelsByranges<-TotMatFilt%>%filter(ArimaModel != "None")%>%
  group_by(ArimaModel, Position, Dataset)%>% 
  dplyr::summarise(Frequency = n())%>%
  group_by(Position, Dataset)%>% dplyr::mutate(Prob= Frequency/sum(Frequency))
# which are the most typical Models?
MostTypicalModelperRange<-ModelsByranges%>%group_by(Position, Dataset)%>% filter(Frequency== max(Frequency))
## WHich are the models in this case assigned to more than 20% of the views in that case?
Probability<- 0.15
BiggerModelsPerRange<-ModelsByranges%>% filter(Prob>Probability)%>% arrange(desc(Dataset))

kable(MostTypicalModelperRange,"latex", booktabs = TRUE)  %>%
  kable_styling(font_size = 9) 


# library(kableExtra)
# kable(GeneralQuantileTableT,"latex", booktabs = TRUE, digits = 3) %>%
#   kable_styling(font_size = 9) %>%
#   add_header_above(c(" " = 1, "Direct" = 3, "Direct/h 1" = 3, "Collective" = 3, "Collective/h" = 3))%>%
#   column_spec(c(4,7,10,13), bold = T, italic = T)
# 




FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"



Positionfilt<-c( "F")

ComphistPosition<- ggplot(TotMatFilt%>%filter(Position != Positionfilt), aes (x =ArimaModel))+
  facet_grid(Position~Dataset)+
  geom_histogram(stat="count")+ 
  theme_bw()+
  labs(#title="Distribution of Time series Modelling", 
       #subtitle="ARIMA models for nº of Games Played for each Player",
       x = "Best choice of Arima(p,d,q)",
       y = "Count for models suggested")
ComphistRange<- ggplot(TotMatFilt%>%filter(Position != Positionfilt), aes (x =ArimaModel))+
  facet_grid(Range~Dataset)+
  geom_histogram(stat="count")+ 
  theme_bw()+
  labs(#title="Distribution of Time series Modelling", 
    #subtitle="ARIMA models for nº of Games Played for each Player",
    x = "Best choice of Arima(p,d,q)",
    y = "Count for models suggested")


listPlots<- list()
listPlots[[1]]<- ComphistRange
listPlots[[2]]<- ComphistPosition

# NamePlots<- c(paste0(Season,GeneralNames[dataset]," Histogram display of most typical ARIMA models per Range in", Season),
#               paste0(Season,GeneralNames[dataset]," Histogram Comparison display of most typical ARIMA models per Range in", Season),
#               paste0(Season,GeneralNames[dataset]," Most typical ARIMA model for Player's valuation based on matches played by player in ",Season),
#               paste0(Season,GeneralNames[dataset]," Most typical ARIMA models for Player's valuation based on matches played by player in ",Season, " with Porbability > ", Probability))
# # Can I say it has a higher impact than the other measures on salary ?
# NamePlots<-gsub(" ", "",gsub("[^[:alnum:] ]", "", NamePlots))

# for( i in 1:length(listPlots)){
#   totname<-paste0(FilepathSrotingPlots,NamePlots[i],'.png')
#   ggsave(plot= listPlots[[i]], file = totname,  device = 'png', limitsize = FALSE)
#   # make plot
# }

listTables<- list()
listTables[[1]]<- MostTypicalModelperRange%>% arrange(Range)
listTables[[2]]<- BiggerModelsPerRange

