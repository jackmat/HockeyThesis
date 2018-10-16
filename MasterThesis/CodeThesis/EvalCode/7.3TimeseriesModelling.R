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
# res<-rep(0, times = length(2:ncol(CDataset)))
# 
# for(i in 2:ncol(CDataset)){
#   ### The steps are:
#   #(1) Selecting the matches Played by that player 
#   #    (if time played is 0 in the timeDataset, then that player has not played a match)
#   myData<-CDataset[,i]
#   mytime<- TimeDataset[,i]
#   
#   MyTrueData<- myData[-which(mytime==0)]
#   #(2) Generallywise, data is already quite stationary, however, detrending is used to be sure of it
#   MydiffData<-diff(MyTrueData)
#     #(3) If length of the time series is more than 5 matches:
#     if((length(MydiffData)>10)==TRUE){
#       # (3.1) Do an adftest to check stationarity. 
#       s<-adf.test(MydiffData)  
#       
#       if((s$p.value <= 0.05)==TRUE){
#         #(3.1.1) If stationary, do modelling
#         fit<-auto.arima(MydiffData)
#         #paste arima model (pdq), being p=AR,d=I,q=MA
#         res[i]<-paste0(arimaorder(fit),collapse = ",")
#       }else{res[i]<-"Not stationary"}
#     }else{res[i]<-"short"}
# }

## All being (p,d,q)== (0,0,0)



res<-rep(0, times = length(2:ncol(CDataset)))
obs<- rep(0, times = length(2:ncol(CDataset)))

for(i in 2:ncol(CDataset)){
  print(paste0(i , " out of ", ncol(CDataset)))
  ### The steps are:
  #(1) Selecting the matches Played by that player 
  #    (if time played is 0 in the timeDataset, then that player has not played a match)
  myData<-CDataset[,i]
  mytime<- TimeDataset[,i]
  MyTrueData<- myData[-which(mytime==0)]
  len<-length(MyTrueData)
  # Saving variables in 10s
  obs[i]<- round(len/10)*10
  if((obs[i]==0)==TRUE){res[i]<-"0,0,0"}
  else{
    #(2) Generallywise, data is already quite stationary, however, detrending is used to be sure of it
    MydiffData<-diff(MyTrueData)
    #(3) If length of the time series is more than 5 matches:
    #(3.1.1) If stationary, do modelling
    fit<-auto.arima(MydiffData)
    res[i]<-paste0(arimaorder(fit),collapse = ",")  }
}
Mat<-data.frame(ArimaModel=res[2:length(res)], 
                Range= obs[2:length(obs)]) 
Mat[,1]<-as.factor(Mat[,1])
Mat[,2]<-as.factor(Mat[,2])
class(Mat)
ModelsByranges<-Mat%>%
  group_by(ArimaModel, Range)%>% 
  dplyr::summarise(Frequency = n())%>%
  group_by(Range)%>% dplyr::mutate(Prob= Frequency/sum(Frequency))
# which are the most typical Models?
MostTypicalModelperRange<-ModelsByranges%>%group_by(Range)%>% filter(Frequency== max(Frequency))
## WHich are the models in this case assigned to more than 20% of the views in that case?
Probability<- 0.15
BiggerModelsPerRange<-ModelsByranges%>% filter(Prob>Probability)%>% arrange(Range)

FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"


hist1<-ggplot(Mat, aes (x =Range))+
  geom_histogram(stat="count",
                 aes(group = ArimaModel, fill =ArimaModel))+ 
  theme_bw()+
  labs(title="Distribution of Time series Modelling", 
       subtitle="ARIMA models for nº of Games Played for each Player",
       x = "Nº of Games Played rounded",
       y = "Count for models suggested")  

Comphist<- ggplot(Mat, aes (x =ArimaModel))+
  facet_grid(Range~.)+
  geom_histogram(stat="count")+ 
  theme_bw()+
  labs(title="Distribution of Time series Modelling", 
       subtitle="ARIMA models for nº of Games Played for each Player",
       x = "Nº of Games Played rounded",
       y = "Count for models suggested")

listPlots<- list()
listPlots[[1]]<-hist1 # CHangning the date only to written once
listPlots[[2]]<-Comphist

NamePlots<- c(paste0(Season," Histogram display of most typical ARIMA models per Range in", Season),
              paste0(Season," Histogram Comparison display of most typical ARIMA models per Range in", Season),
              paste0(Season," Most typical ARIMA model for Player's valuation based on matches played by player in ",Season),
              paste0(Season," Most typical ARIMA models for Player's valuation based on matches played by player in ",Season, " with Porbability > ", Probability))
# Can I say it has a higher impact than the other measures on salary ?
NamePlots<-gsub(" ", "",gsub("[^[:alnum:] ]", "", NamePlots))

for( i in 1:length(listPlots)){
  totname<-paste0(FilepathSrotingPlots,NamePlots[i],'.png')
  ggsave(plot= listPlots[[i]], file = totname,  device = 'png', limitsize = FALSE)
  # make plot
}

listTables<- list()
listTables[[1]]<-MostTypicalModelperRange
listTables[[2]]<-BiggerModelsPerRange

print(xtable(listTables[[1]], type = "latex"), file = paste0(FilepathSrotingPlots,NamePlots[3],'.tex'))
write.table(listTables[[1]], paste0(FilepathSrotingPlots,NamePlots[3],".csv"))
print(xtable(listTables[[2]], type = "latex"), file = paste0(FilepathSrotingPlots,NamePlots[4],'.tex'))
write.table(listTables[[2]], paste0(FilepathSrotingPlots,NamePlots[4],".csv"))


