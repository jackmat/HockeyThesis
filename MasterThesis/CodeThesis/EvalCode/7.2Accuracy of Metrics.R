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

### Loading Datasets
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
lengthseries<-30
holdout<-5

###################
# I am going to take all data with more than 30 observations and put their 
# first 30 observations in the following vector
DatasetsList<- list(CDataset, TimeDataset, PlusMinusTimeDataset, PMDataset)
GeneralNames<-c("Val", "ValTime", "PMTime", "PM")
AccuracyEvaluationData<- function(lengthseries=lengthseries,
                                  holdout= holdout,
                                  GeneralNames = GeneralNames, 
                                  DatasetList= DatasetsList){
  ######### It makes a forecast for for Players with more than lengthseries views, 
  #        and taking the first lengthseries observations        
  #        with holdout = houldout, and gives out several metrics accuracy
  #########
  ## Args:
  #     lengthseries: integer number that decides how long will be the serie to analyze
  #     holdout: integer number values to predict
  #     GeneralNames: vector of names to pass as definition of what is the metric of the Dataset about
  #     DatasetList: List of data.frames with same colnames and rownames and dimensions
  
  trainError<-data.frame()
  testError<-data.frame()
  
  
  for(Dataindex in 1:length(DatasetsList)){
    Dataset<- DatasetList[[Dataindex]]
    print(paste0("Doing Dataset ",Dataindex, " out of ", length(DatasetList)))
    TimseSeriesData<-list()
    for(i in 2:ncol(Dataset)){
      ### The steps are:
      #(1) Selecting the matches Played by that player 
      #    (if time played is 0 in the timeDataset, then that player has not played a match)
      myData<-Dataset[,i]
      mytime<- TimeDataset[,i]
      MyTrueData<- myData[-which(mytime==0)]
      TimseSeriesData[[i-1]]<- MyTrueData
    }
    
    lengthlst<-lapply(TimseSeriesData, length)
    ### I predict on the last 5 and the first 25 are for training
    series <-list()
    index <-  c()
    counter<-0
    for(i in 1:length(lengthlst)){
      if((lengthlst[[i]]>lengthseries)==TRUE){
        counter<-counter+1
        series[[counter]]<- ts(TimseSeriesData[[i]][1:lengthseries])
        index[counter]<- i # For the general number
      }
    }
    seriesdata<-df <- data.frame(matrix(unlist(series), nrow=length(series), byrow=T),stringsAsFactors=FALSE)
    summary(seriesdata)
    forecasts <- lapply(series,function(foo) {
      subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
      forecast(auto.arima(subseries),h=holdout)
    } ) 
    
    Meanforecasts <- lapply(series,function(foo) {
      subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
      forecast(Arima(subseries, order = c(0,0,0)),h=holdout)
    } ) 
    
    result <- mapply(FUN=accuracy,f=forecasts,x=series,SIMPLIFY=FALSE)
    resultComparison<- mapply(FUN=accuracy,f=Meanforecasts,x=series,SIMPLIFY=FALSE)
    
    
    AccuracyMats <- AccuracyInMatrices(trainError=trainError, 
                            testError = testError,
                            Name = paste0("Arima ",GeneralNames[Dataindex]),
                            result = result) 
    trainError<-AccuracyMats$trainError
    testError<- AccuracyMats$testError
    AccuracyMats <- AccuracyInMatrices(trainError=trainError, 
                                       testError = testError,
                                       Name = paste0("Arima(0,0,0) ",GeneralNames[Dataindex]),
                                       result = resultComparison) 
    trainError<-AccuracyMats$trainError
    testError<- AccuracyMats$testError
    }

  return(list(trainError=trainError, testError=testError))
}

AccuracyInMatrices<-function(trainError, testError,Name, result){
  # name: variable just to say the name of the column to identify where that observations come from
  # datasets trainError and testError are passed where the result will be given
  # result is the accuracy result got from 'accuracy()' function
  b<-result[[1]] # to extract column names and row names
  for (type in 1:length(rownames(b))){
    setType <- rownames(b)[type]
    if(setType == "Training set"){
      for(j in 1:length(colnames(b))){
        name<- colnames(b)[j]
        errtrain<- sapply(result, "[", setType, name)
        if(j==1){smallDataset<-data.frame(errtrain)}
        else{smallDataset<-cbind(smallDataset, errtrain)}
      }
      smallDataset<- cbind(smallDataset, Name)
      colnames(smallDataset)<-c(colnames(b), "DataframeName")
      if(all.equal(dim(trainError),c(0,0))==TRUE){
        trainError<- smallDataset
        colnames(trainError)<-c(colnames(b), "DataframeName")
      }
      else{trainError<-rbind(trainError, smallDataset)}
    }
    else if(setType == "Test set"){
      for(j in 1:length(colnames(b))){
        
        name<- colnames(b)[j]
        errtest<- sapply(result, "[", setType, name)
        if(j==1){smallTestDataset<-data.frame(errtest)}
        else{smallTestDataset<-cbind(smallTestDataset, errtest)}
      }
      smallTestDataset<- cbind(smallTestDataset, Name)      
      colnames(smallTestDataset)<-c(colnames(b), "DataframeName")
      if(all.equal(dim(testError),c(0,0))==TRUE){
        testError<- smallTestDataset
        colnames(testError)<-c(colnames(b), "DataframeName")
      }
      else{testError<-rbind(testError, smallTestDataset)}
    }
    else{ print("Not allocated to anywhere !")}
  }
  return(list(trainError= trainError, 
              testError= testError))
}

ErrorsForDatasets<-AccuracyEvaluationData(lengthseries=lengthseries,
                      holdout= holdout,
                      GeneralNames = GeneralNames, 
                      DatasetList= DatasetsList)

TrainErrorsforDatasets<-  ErrorsForDatasets$trainError
TestErrorsforDatasets<-  ErrorsForDatasets$testError
colnames(df2_melted)
TrainErrorsforDatasets
colnames(TrainErrorsforDatasets)
df2_melted<-melt(TrainErrorsforDatasets,id.vars = "DataframeName")
TrainModelEvaluation<-TrainErrorsforDatasets%>%
  ddply(.(DataframeName), summarize, 
        MeanME = mean(ME, na.rm =T),  SdME = sd(ME, na.rm =T),
        MeanRMSE = mean(RMSE, na.rm =T),  SdRMSE = sd(RMSE, na.rm =T),
        MeanMAE = mean(MAE, na.rm =T),  SdMAE = sd(MAE, na.rm =T),
        MeanMPE = mean(MPE, na.rm =T),  SdMPE = sd(MPE, na.rm =T),
        MeanMAPE = mean(MAPE, na.rm =T),  SdMAPE = sd(MAPE, na.rm =T),
        MeanMASE = mean(MASE, na.rm =T),  SdMASE = sd(MASE, na.rm =T),
        MeanACF1 = mean(ACF1, na.rm =T),  SdACF1 = sd(ACF1, na.rm =T))

TestModelEvaluation<-TestErrorsforDatasets%>%
  ddply(.(DataframeName), summarize, 
        MeanME = mean(ME, na.rm =T),  SdME = sd(ME, na.rm =T),
        MeanRMSE = mean(RMSE, na.rm =T),  SdRMSE = sd(RMSE, na.rm =T),
        MeanMAE = mean(MAE, na.rm =T),  SdMAE = sd(MAE, na.rm =T),
        MeanMPE = mean(MPE, na.rm =T),  SdMPE = sd(MPE, na.rm =T),
        MeanMAPE = mean(MAPE, na.rm =T),  SdMAPE = sd(MAPE, na.rm =T),
        MeanMASE = mean(MASE, na.rm =T),  SdMASE = sd(MASE, na.rm =T),
        MeanACF1 = mean(ACF1, na.rm =T),  SdACF1 = sd(ACF1, na.rm =T))

# Plotting  metrics distribution for data1 and two
ggplot(df2_melted%>%filter(variable !="Theil's U" ))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(subtitle=paste0("Accuracy distribution comparison for trained data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Range of values", 
       title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )

df2_meltedTest<-melt(TestErrorsforDatasets,id.vars = "DataframeName")
ggplot(df2_meltedTest%>%filter(variable !="Theil's U"))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Range of values", 
       title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )
