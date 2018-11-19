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
                                  n){
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

    
  for(Dataindex in 1:(length(TotList[[1]])-1)){
    series <-list()
    index <-  c()
    counter<-0 
    for(d in 1:length(TotList)){
      DatasetList<- TotList[[d]]
      Positions<-unique(GeneralTableList[[d]]$Position)

      Dataset<- DatasetList[[Dataindex]]
      IdFiltering<-GeneralTableList[[d]] %>% filter(Position %in% c("RW","LW","C", "D")) %>% select(id) %>% apply(1,as.character)
      Dataset<-Dataset[,c("CountGame",IdFiltering)]
      print(paste0("Doing Dataset ",Dataindex, " out of ", length(DatasetList)))
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
      positionIndex<- n #sample(1:50, 1) # It chooses randomly the number to start
      
      
      for(i in 1:length(lengthlst)){
        ## If the first n-1 points are equal to 0, do not take them, since modelling is obvious
        if((lengthlst[[i]]>(positionIndex+lengthseries))==TRUE){
          timser<-ts(TimseSeriesData[[i]][positionIndex:(positionIndex+lengthseries-2)])
          if(all.equal(timser,ts(rep(0,(lengthseries-holdout))))==TRUE){
            
          }
          else{
            counter<-counter+1
            series[[counter]]<- ts(TimseSeriesData[[i]][positionIndex:(positionIndex+lengthseries)])
            index[counter]<- i # For the general number
          }
        }
      }
    }
      print(length(series)) ## just to check that series variable is larger every time
    }
    
    for( ARIMAindex in 1:length(OrderModels)){
      if(OrderModels[ARIMAindex]=="best"){
        forecasts <- lapply(series,function(foo) {
          subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
          forecast(auto.arima(subseries),h=holdout)} )
      }
      else{
      forecasts <- lapply(series,function(foo) {
        subseries <- ts(head(foo,length(foo)-holdout),start=start(foo),frequency=frequency(foo))
        forecast(Arima(subseries, 
                       order = as.numeric(unlist(strsplit(OrderModels[ARIMAindex], ","))), 
                       include.mean = TRUE,
                       method="ML"),h=holdout)
    } )} 
    

      
    result <- mapply(FUN=accuracy,f=forecasts,x=series,SIMPLIFY=FALSE)

    
    ##On the first pass, i get the trainError, testError that I pass for the result comparison
    AccuracyMats <- AccuracyInMatrices(trainError=trainError, 
                            testError = testError,
                            Name = paste0(as.character(orderModels[ARIMAindex])," ",GeneralNames[Dataindex]),
                            result = result) 
    trainError<-AccuracyMats$trainError
    testError<- AccuracyMats$testError
    }
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
                      TotList = TotList, 
                      orderModels = OrderModels,
                      n = 74)

TrainErrorsforDatasets<-  ErrorsForDatasets$trainError
TestErrorsforDatasets<-  ErrorsForDatasets$testError

df2_melted<-melt(TrainErrorsforDatasets,id.vars = "DataframeName")
TrainModelEvaluation<-TrainErrorsforDatasets%>%
  ddply(.(DataframeName), summarize, 
        MeanME = mean(ME, na.rm =T),  SdME = sd(ME, na.rm =T),
        MeanRMSE = mean(RMSE, na.rm =T),  SdRMSE = sd(RMSE, na.rm =T),
        MeanMAE = mean(MAE, na.rm =T),  SdMAE = sd(MAE, na.rm =T))

TestModelEvaluation<-TestErrorsforDatasets%>%
  ddply(.(DataframeName), summarize, 
        MeanME = mean(ME, na.rm =T),  SdME = sd(ME, na.rm =T),
        #MeanRMSE = mean(RMSE, na.rm =T),  SdRMSE = sd(RMSE, na.rm =T),
        MeanMAE = mean(MAE, na.rm =T),  SdMAE = sd(MAE, na.rm =T))
colnames(TestModelEvaluation)[1]<- "Arima Model"
# Plotting  metrics distribution for data1 and two

  
quantiledata<- matrix()
DatVars<-unique(df2_melted$variable)
yearVars<-unique(df2_melted$DataframeName)
GeneralQuantileTable<-matrix(ncol = 7)
rownames<-integer(0)
counter<-0

for(j in 1:length(DatVars)){
  for(year in 1:length(yearVars)){
    filt<-df2_melted %>% filter(variable == DatVars[j]& DataframeName == yearVars[year])%>% 
      filter(value !=-Inf)%>% filter(value !=Inf) 
    rownames<-c(rownames, paste0(DatVars[j],yearVars[year]))    
    FilteredData<- filt%>% filter(value < quantile(filt$value, 0.95)) %>% 
      filter( value >  quantile(filt$value, 0.05)) 
    if(counter ==0){
      quantiledata<- FilteredData
      counter<- counter+1
      GeneralQuantileTable<-c(quantile(filt$value, probs = c(0.05,0.25,0.5,0.75,0.95)), mean =mean(filt$value), sd= sd(filt$value))}
    else{quantiledata<-rbind(quantiledata, FilteredData)
    counter <- counter +1
    GeneralQuantileTable<-rbind(GeneralQuantileTable, c(quantile(filt$value, probs = c(0.05,0.25,0.5,0.75,0.95)), mean(filt$value), sd(filt$value)))
    }
  }}

  

TrainHistComparison<-ggplot(quantiledata%>%filter(variable !="Theil's U" ))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for trained data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Range of values", 
       title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )

df2_meltedTest<-melt(TestErrorsforDatasets,id.vars = "DataframeName")
TestHistComparison<-ggplot(df2_meltedTest%>%filter(variable %in% c("ME", "MAE")))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Range of values"#, 
       #title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )
TestHistComparison1<-ggplot(df2_meltedTest%>%filter(variable %in% c("ME", "MAE"))%>%
                        filter(DataframeName %in% paste0(OrderModels," ", "Direct")))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Distribution range of the residuals"#, 
       #title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )

TestHistComparison2<-ggplot(df2_meltedTest%>%filter(variable %in% c("ME", "MAE"))%>%
                             filter(DataframeName %in% paste0(OrderModels," ", "Directh")))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Distribution range of the residuals"#, 
       #title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )
TestHistComparison3<-ggplot(df2_meltedTest%>%filter(variable %in% c("ME", "MAE"))%>%
                              filter(DataframeName %in% paste0(OrderModels," ", "Collective")))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Distribution range of the residuals"#, 
       #title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )

TestHistComparison4<-ggplot(df2_meltedTest%>%filter(variable %in% c("ME", "MAE"))%>%
                              filter(DataframeName %in% paste0(OrderModels," ", "Collectiveh")))+
  facet_grid(DataframeName~variable, drop = T, scales = "free")+
  geom_histogram(aes(x=value, y=(..count..)/tapply(..count..,..PANEL..,sum)[..PANEL..]))+
  labs(#subtitle=paste0("Accuracy distribution comparison for test data in ", Season,"-",Season+1), 
       y="Probability distribution", 
       x="Distribution range of the residuals" #, 
       #title= paste0("Metric analysis of player's evaluation prediction")#, 
       #caption = "Source: Carles Illustration"
  )

listPlots<- list()
listPlots[[1]]<-TrainHistComparison # CHangning the date only to written once
listPlots[[2]]<-TestHistComparison
listPlots[[3]]<-TestHistComparison1+ theme(strip.text= element_text(size = 12))
listPlots[[4]]<-TestHistComparison2+ theme(strip.text= element_text(size = 12))
listPlots[[5]]<-TestHistComparison3+ theme(strip.text= element_text(size = 12))
listPlots[[6]]<-TestHistComparison4+ theme(strip.text= element_text(size = 12))

NamePlots<- c(paste0(Season," Error distribution of the forecast for Trained Data in", Season),
              paste0(Season," Error distribution of the forecast for predicted Data points in ", Season),
              paste0(Season," Table evaluation of the models for Trained Data in comparison to basic ARIMA (0,0,0) for ",Season),
              paste0(Season," Table evaluation of the models for predicted Data in comparison to basic ARIMA (0,0,0) for ",Season))
              # Can I say it has a higher impact than the other measures on salary ?
NamePlots<-gsub(" ", "",gsub("[^[:alnum:] ]", "", NamePlots))

for( i in 1:length(listPlots)){
  totname<-paste0(FilepathSrotingPlots,NamePlots[i],'.png')
  ggsave(plot= listPlots[[i]], file = totname,  device = 'png', limitsize = FALSE)
  # make plot
}

options("scipen"=-100, "digits"=2)
options("scipen"=100, "digits"=2)
options("scipen"=0, "digits"=2)
listTables<- list()
listTables[[1]]<-TrainModelEvaluation
listTables[[2]]<-TestModelEvaluation

print(xtable(listTables[[1]], type = "latex"), file = paste0(FilepathSrotingPlots,NamePlots[3],'.tex'))
write.table(listTables[[1]], paste0(FilepathSrotingPlots,NamePlots[3],".csv"))
print(xtable(listTables[[2]], type = "latex"), file = paste0(FilepathSrotingPlots,NamePlots[4],'.tex'))
write.table(listTables[[2]], paste0(FilepathSrotingPlots,NamePlots[4],".csv"))


kable(TestModelEvaluation,"latex", booktabs = TRUE, digits= 3)  %>%
  kable_styling(font_size = 9) 

