#  CDataset, TimeDataset, PMDataset, PlusMinusTimeDataset
library(forecast)
library(tseries)
myData<-CDataset[,2]
mytime<- TimeDataset[,2]
MyTrueData<-myData[-which(mytime==0)]
fit<-arima(CDataset[,2])

accuracy(fit)
forecast(fit, 5)
plot(forecast(fit, 5))
fit2 <- ets(CDataset[,2])
fit3 <- auto.arima(CDataset[,2])
plot(forecast(fit2, 5))
plot(forecast(fit3, 5))

### 
adf.test(diff(log(AirPassengers)), alternative="stationary", k=0)
adf.test(diff(myData),alternative="stationary", k=0)


par(mfrow=c(1,2))

plot(diff(MyTrueData), type ="l")


plot(MyTrueData, type ="l")
acf(MyTrueData)
pacf(MyTrueData)
library(astsa)
lag1.plot(MyTrueData, max.lag = 12) # No trend
mydata<- as.data.frame(cbind(X= 1:length(MyTrueData), y=MyTrueData))
Box.test(ts(MyTrueData), lag=20, type="Ljung-Box")

res<-rep(0, times = length(2:ncol(CDataset)))

for(i in 2:ncol(CDataset)){
  ### The steps are:
  #(1) Selecting the matches Played by that player 
  #    (if time played is 0 in the timeDataset, then that player has not played a match)
  myData<-CDataset[,i]
  mytime<- TimeDataset[,i]
  
  MyTrueData<- myData[-which(mytime==0)]
  #(2) Generallywise, data is already quite stationary, however, detrending is used to be sure of it
  MydiffData<-diff(MyTrueData)
    #(3) If length of the time series is more than 5 matches:
    if((length(MydiffData)>10)==TRUE){
      # (3.1) Do an adftest to check stationarity. 
      s<-adf.test(MydiffData)  
      
      if((s$p.value <= 0.05)==TRUE){
        #(3.1.1) If stationary, do modelling
        fit<-auto.arima(MydiffData)
        #paste arima model (pdq), being p=AR,d=I,q=MA
        res[i]<-paste0(arimaorder(fit),collapse = ",")
      }else{res[i]<-"Not stationary"}
    }else{res[i]<-"short"}
}
cov(MyTrueData, 1:length(MyTrueData))
length(res)
hist(table(res))
## All being (p,d,q)== (0,0,0)

auto.arima(1:10+rnorm(10,0,1))



res<-rep(0, times = length(2:ncol(CDataset)))
obs<- rep(0, times = length(2:ncol(CDataset)))

for(i in 2:ncol(CDataset)){
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
ModelsByranges<-Mat%>%mutate(Frequency=1)%>% 
  group_by(ArimaModel, Range =as.factor(Range)) %>% 
  summarise(Frequency = sum(Frequency))%>%
  group_by(Range)%>% mutate(Prob= Frequency/sum(Frequency))
ggplot(Mat, aes (x =Range))+
  geom_histogram(stat="count",
        aes(group = ArimaModel, fill =ArimaModel))+ 
  theme_bw()+
  labs(title="Distribution of Time series Modelling", 
       subtitle="ARIMA models for nº of Games Played for each Player",
       x = "Nº of Games Played rounded",
       y = "Count for models suggested")  

ggplot(Mat, aes (x =ArimaModel))+
  geom_histogram(stat="count")+ 
  theme_bw()+
  labs(title="Distribution of Time series Modelling", 
       subtitle="ARIMA models for nº of Games Played for each Player",
       x = "Nº of Games Played rounded",
       y = "Count for models suggested")  + facet_grid(Range~.)

# which are the most typical Models?
ModelsByranges%>%group_by(Range)%>% filter(Frequency== max(Frequency))
## WHich are the models in this case assigned to more than 20% of the views in that case?
ModelsByranges%>% filter(Prob>0.2)%>% arrange(Range)
