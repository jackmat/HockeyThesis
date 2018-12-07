################## Possible Analysis


SalaryRanges<- c(0:8,10,12,14,16,18,20)*0.5
Positions<- unique(GeneralTableList[[1]]$Position)
Variables<-colnames(GeneralTableList[[1]])[7:20]
matrixmean<-data.frame(ncol = length(7:20))
matrixmedian<-data.frame(ncol = length(7:20))
matrix5<-data.frame(ncol = length(7:20))
matrix25<-data.frame(ncol = length(7:20))
matrix75<-data.frame(ncol = length(7:20))
matrix95<-data.frame(ncol = length(7:20))
counter<-1
namecols<-integer(0)

for(indexpos in 1:length(Positions)){
  for(d in 1:length(GeneralTableList)){
    if(d ==1){
      PositionDataFilter<-GeneralTableList[[d]]%>%filter(Position == Positions[indexpos])}
    else{
      PositionDataFilter<-rbind(PositionDataFilter, GeneralTableList[[d]]%>%filter(Position == Positions[indexpos]))
    }
  }  
  for(indexSalary in 1:(length(SalaryRanges)-1)){
    PosSalaryFilte<- PositionDataFilter %>% filter(Salary > SalaryRanges[indexSalary] &
                                                     Salary <= SalaryRanges[indexSalary+1])
    if(counter==1){
      matrixmean<-data.frame(apply(PosSalaryFilte[,7:20],2,mean),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]), SalaryRanges[indexSalary])
      matrixmedian<-data.frame(apply(PosSalaryFilte[,7:20],2,median),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary])
      matrix5<-data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.05),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary])
      matrix25<-data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.25),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary])
      matrix75<-data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.75),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary])
      matrix95<-data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.95),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary])
      
      
      counter<- counter+1   
    }else{
      matrixmean<-rbind(matrixmean, data.frame(apply(PosSalaryFilte[,7:20],2,mean),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      matrixmedian<-rbind(matrixmedian,data.frame(apply(PosSalaryFilte[,7:20],2,median),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      matrix5<-rbind(matrix5,data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.05),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      matrix25<-rbind(matrix25,data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.25),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      matrix75<-rbind(matrix75,data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.75),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      matrix95<-rbind(matrix95,data.frame(apply(PosSalaryFilte[,7:20],2,quantile, probs = 0.95),Positions[indexpos],paste0(SalaryRanges[indexSalary],"-",SalaryRanges[indexSalary+1]),SalaryRanges[indexSalary]))
      
      counter<- counter+1 
    }
    
    
  }}
DataClean<- function(Data, onlyGP="Yes"){
  matrixmean<- cbind(Data, rownames(Data)[1:14]) 
  colnames(matrixmean)<- c("Valuation", "Position", "SalaryRange","indexSalary" ,"Metric")
  matrixmean$Valuation<- as.numeric(as.character(matrixmean$Valuation))
  if(onlyGP == "Yes"){
    matrixmean<-matrixmean%>% filter(!is.na(Valuation)) %>% filter(Position %in% c("F","D"))%>%
      filter(grepl("GP",Metric))
  }
  else{matrixmean<-matrixmean%>% filter(!is.na(Valuation)) %>% filter(Position %in% c("F","D"))%>%
    filter(!grepl("GP",Metric))}
  return(matrixmean)
}
GPmatrixmean<- DataClean(matrixmean)
GPmatrixmedian<- DataClean(matrixmedian)
GPmatrix5<- DataClean(matrix5)
GPmatrix25<- DataClean(matrix25)
GPmatrix75<- DataClean(matrix75)
GPmatrix95<- DataClean(matrix95)

Tmatrixmean<- DataClean(matrixmean,"NO")
Tmatrixmedian<- DataClean(matrixmedian,"NO")
Tmatrix5<- DataClean(matrix5,"NO")
Tmatrix25<- DataClean(matrix25,"NO")
Tmatrix75<- DataClean(matrix75,"NO")
Tmatrix95<- DataClean(matrix95,"NO")

ggplot(GPmatrixmean, ## replace for whatever matrix interested
       aes(x = SalaryRange , y = Valuation, group = Position))+facet_grid(Metric~., scales = "free")+
  geom_line(aes(color = Position))
#####

MedianGP<-GPmatrixmedian%>%cbind(measure ="Q50")
MeanGP<-GPmatrixmean%>%cbind(measure ="Mean")
GPQ05<-GPmatrix5%>%cbind(measure ="Q5")
GPQ25<-GPmatrix25%>%cbind(measure ="Q25")
GPQ75<-GPmatrix75%>%cbind(measure ="Q75")
GPQ95<-GPmatrix95%>%cbind(measure ="Q95")


TotGP<- rbind(GPQ05,GPQ25,MedianGP, MeanGP, GPQ75,GPQ95)
TotGPscatterplot<-ggplot(TotGP, 
       aes(x =  as.factor(indexSalary), y = Valuation, group = measure, color = measure))+
  facet_grid(Metric~Position, scales = "free")+
  geom_line(aes(color = measure))+
  labs(x = "Salary ranges")


TableTotGP<-TotGP %>% group_by(Position, SalaryRange, Metric, measure) %>%
  dplyr::summarize(meanValue = mean(Valuation))

TMedian<-Tmatrixmedian%>%cbind(measure ="Q50")
TMean<-Tmatrixmean%>%cbind(measure ="Mean")
TQ05<-Tmatrix5%>%cbind(measure ="Q5")
TQ25<-Tmatrix25%>%cbind(measure ="Q25")
TQ75<-Tmatrix75%>%cbind(measure ="Q75")
TQ95<-Tmatrix95%>%cbind(measure ="Q95")
TotT<- rbind( TQ05,TQ25,TMedian, TMean,TQ75,TQ95)
Totscatterplot<-ggplot(TotT%>% filter(Metric %in% c("Collective","Collectiveh","Direct","Directh", "PlusMinus","Points")), 
       aes(x =  as.factor(indexSalary), y = Valuation, group = measure, color = measure))+
  facet_grid(Metric~Position, scales = "free")+
  geom_line(aes(color = measure))+
  labs(x = "Salary ranges")

graphLists<- list(TotGPscatterplot,Totscatterplot)
namevec<- c("TotGPscatterplot", "Totscatterplot")