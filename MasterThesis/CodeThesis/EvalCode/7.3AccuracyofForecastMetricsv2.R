require(reshape2)
require(forecast)
require(ggplot2)
require(dplyr)
library(plyr)

#### Global variables
Boolean <- FALSE #Changing to TRUE if wanting to work with non-zero Data (reccommended)
NameVar <-""
NTOP<- 944
Season<-2007
SalariesCalc <- FALSE # Changing to True when scrapped Data is on the varible Salaries2007
loadpath<-"C:/Users/Carles/Desktop/MasterThesis/CodeThesis/CleanDatasets/" 
RegularMatches<-82
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
FilepathSrotingPlots<- "C:/Users/Carles/Desktop/MasterThesis/ResultsPhotos/"

### Loading Datasets
OrderModels<-c(as.character(ModelsMoreTypicals$ArimaModel), "best")
class(OrderModels)
lengthseries<-6
holdout<-1
## I am trying to predict whether I could predict the performance of a player better than their 
# mean using ARIMA models.
## First, I create a list of different length for each player removing those matches which each players has not played.
# I am supposing here that if a player does not play a consecutive, still their performance should be predictable
## For each dataset, I am selecting a starting position of matches. 
## All players (C,RW, LW, D) that have that as many games played are selected 
### Then 6 performances for matches starting from that specific position are taken.
## If they have not played during that matches or their evaluation in all matches is 0, they are not selected. 
## Then, they are modelled according to the best time series model according to auto.arima as well as with the ARIMA(0,0,0) 
# (mean) as control model
# Then, prediction is done on the following match. The ditribution of the residuals as well as the 
# as resume table are plotted.

### 

###################
# I am going to take all data with more than 30 observations and put their 
# first 30 observations in the following vector
TotList<- list(DataSet2007,DataSet2008)

GeneralNames<-c("Direct", "Directh", "Collective", "Collectiveh")
AccuracyEvaluationData<- function(lengthseries=lengthseries,
                                  holdout= holdout,
                                  GeneralNames = GeneralNames, 
                                  TotList= TotList,
                                  orderModels = OrderModels,
                                  n=76, 
                                  remove0 = FALSE){
  ######### It makes a forecast for for Players with more than lengthseries views, 
  #        and taking the first lengthseries observations        
  #        with holdout = houldout, and gives out several metrics accuracy
  #########
  ## Args:
  #     lengthseries: integer number that decides how long will be the serie to analyze
  #     holdout: integer number values to predict
  #     GeneralNames: vector of names to pass as definition of what is the metric of the Dataset about
  #     TotList: List of data.frames with same colnames and rownames and dimensions, accounting for years
  #     n: it checks from indx 1 to n how many possible time series of lengthseries observations can take from a specific time series
  #     remove0: If true, it will remove from forecasting all series where the real value for the forecast is 0.
  MyMat<-data.frame()

  for(Dataindex in 1:(length(TotList[[1]])-1)){
    series <-list()
    index <-  c()
    counter<-0 
    for(d in 1:length(TotList)){

      DatasetList<- TotList[[d]]
      Positions<-unique(GeneralTableList[[d]]$Position)

      Dataset<- DatasetList[[Dataindex]]
      IdFiltering<-GeneralTableList[[d]] %>% filter(Position %in% c("F", "D")) %>% select(id) %>% apply(1,as.character)
      
      Dataset<-Dataset[,c("CountGame",IdFiltering)]
      
      print(paste0("Doing Dataset ",Dataindex, " out of ", length(DatasetList)-1))
      TimseSeriesData<-list()
      for(z in 2:ncol(Dataset)){
        ### The steps are:
        #(1) Selecting the matches Played by that player 
        #    (if time played is 0 in the timeDataset, then that player has not played a match)
        
        myData<-Dataset[,z]
        mytime<- DatasetList[[5]][,z]
        MyTrueData<- myData[-which(mytime==0)]
        TimseSeriesData[[z-1]]<- MyTrueData
        
      }
    
    lengthlst<-lapply(TimseSeriesData, length)
    ### I predict on the last 5 and the first 25 are for training
    for(indexes in 1:n){
      print(indexes)
      positionIndex<- indexes #can be change for randomization of sample(1:50, 1) 
                        # It chooses randomly the number to start
      
      
      for(i in 1:length(lengthlst)){
        ## If the first n-1 points are equal to 0, do not take them, since modelling is obvious
        if((lengthlst[[i]]>=(positionIndex+lengthseries))==TRUE){
          timser<-ts(TimseSeriesData[[i]][positionIndex:(positionIndex+lengthseries-2)])
          if(all.equal(timser,ts(rep(0,(lengthseries-holdout))))==TRUE){
            
          }
          else{
            if(remove0==TRUE){
              if(TimseSeriesData[[i]][(positionIndex+lengthseries-1)]==0){
              }
              else{
                counter<-counter+1
                series[[counter]]<- ts(TimseSeriesData[[i]][positionIndex:(positionIndex+lengthseries-1)])
                index[counter]<- i # For the general number
              }
            }
            else{
            counter<-counter+1
            series[[counter]]<- ts(TimseSeriesData[[i]][positionIndex:(positionIndex+lengthseries-1)])
            index[counter]<- i # For the general number
            }
          }
        }
      }
    }
      print(length(series)) ## just to check that series variable is larger every time
    }
    
    RealData  <- do.call(rbind.data.frame, series)
    colnames(RealData)<-c(1:6)
    
    ##### Here changing lapply for sapply and getting a list dataframe forecast
    for( ARIMAindex in 1:length(OrderModels)){
      print(OrderModels[ARIMAindex])
      if(OrderModels[ARIMAindex]=="best"){
        forecasts <- lapply(series,function(foo) {
          subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
          forecast(auto.arima(subseries),h=holdout)} )
      }
      else{
      forecasts <- lapply(series,function(foo) {
        subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
        ## Doesnot converge with ML, do CSS
        t <- try(Arima(subseries, 
                       order = as.numeric(unlist(strsplit(OrderModels[ARIMAindex], ","))), 
                       include.mean = TRUE,
                       method="ML" ))
        if("try-error" %in% class(t)){print("Error solved by using CSS optimization")
                        t<- Arima(subseries, 
                         order = as.numeric(unlist(strsplit(OrderModels[ARIMAindex], ","))), 
                         include.mean = TRUE,
                         method="CSS" )
          }
        return(forecast(t,h=holdout))
         
      })
      ######## To do this, checking data eval
      
      } 
      
      for(nume in 1:length(series)){    
        if(nume ==1){
          PredictedData<-c(forecasts[[nume]]$fitted,  forecasts[[nume]]$mean)
        }
        else{
          PredictedData<-rbind(PredictedData,c(forecasts[[nume]]$fitted,  forecasts[[nume]]$mean))
          
        }}
      
    # result <- mapply(FUN=accuracy,f=forecasts,x=series,SIMPLIFY=FALSE)
    
    PredictedData<-as.data.frame(PredictedData)
    RealData<- as.data.frame(RealData)  
    Residuals<-PredictedData[,lengthseries]- RealData[, lengthseries]

    ## Generation of the metrics for the prediction == lengthseries
    if(Dataindex==1 & ARIMAindex ==1){
      MyMat<-data.frame(ME = mean(Residuals), 
                    RMSE =  sqrt(mean(Residuals^2)), 
                    MAE = mean(abs(Residuals)), 
                    Model = paste0(as.character(orderModels[ARIMAindex])),
                    Dataframe = GeneralNames[Dataindex])
      }else{    
      matbind<- data.frame(ME = mean(Residuals), 
                           RMSE =  sqrt(mean(Residuals^2)), 
                           MAE = mean(abs(Residuals)), 
                           Model = paste0(as.character(orderModels[ARIMAindex])),
                           Dataframe = GeneralNames[Dataindex])
      MyMat<-rbind(MyMat, matbind)
      }
    }
  }

  return(MyMat)
}



ErrorsForDatasets<-AccuracyEvaluationData(lengthseries=lengthseries,
                                          holdout= holdout,
                                          GeneralNames = GeneralNames, 
                                          TotList = TotList, 
                                          orderModels = OrderModels,
                                          n = 76, 
                                          remove0 = F) 
# Change to true if wanted for eliminating 0 values on the prediction



Dat<-ErrorsForDatasets %>%
  select(Model, ME, RMSE, MAE, Dataframe)

kable(Dat,"latex", booktabs = TRUE, digits= 3)


