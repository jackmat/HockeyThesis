
library(XML)

Seasonyear<- 2008 # 2008 stands for 2007-2008 and so on
ExtactingSeasonPLayerSalariesStats<- function(Season){
  TeamVect<- 1:30
  TotalFrame<-data.frame()
  
  for( j in 1:length(TeamVect)){
    teamNum<- TeamVect[j]
    url<- paste0("http://dropyourgloves.com/Stat/Players.aspx?League=1&Team=",teamNum,"&Season=", Season)
    tables <- readHTMLTable(url)
    GoodTable<-tables[2]$`NULL`
    Onetab<-GoodTable[-1,]
    print(paste0(dim(Onetab)[2] ," columns in Team ", j))
    EndingCols<-c("GP", "G", "GA", "PlusMin", "PIMs", "Total",
                  "ClearWins", "Good", "NHL", "GordyHowesort","My")
    Firstcolnames<- c("#", "P","Player", "Age","Drafted,", "Salary")
    diff<-  dim(Onetab)[2]-17
    x<-rep("X",diff)
    colnames(Onetab)<- c(Firstcolnames, x, EndingCols)
    
    columns<- c("P","Player", "Age", "Salary","GP", "G", "GA", "PlusMin", "NHL")
    ExtractedFrame<-Onetab[,columns] 
    if(j==1){TotalFrame<-ExtractedFrame}
    else{TotalFrame<-rbind(TotalFrame, ExtractedFrame)}
  }
  return(TotalFrame)
}  

main<- function(Season){
  # It takes a minute per Season passed
  TotalFrame<- ExtactingSeasonPLayerSalariesStats(Season = Season)
  new <- gsub("\\$", "", TotalFrame$Salary)
  SalaryCol<-as.numeric(gsub(",","",new)) # NA introduced by coercion but it is 4 unknown
  TotalFrame$Salary<- round(SalaryCol/10^6,digits = 2) # iN Million
  TotalFrame$P<- as.character(TotalFrame$P)
  TotalFrame$Player<- as.character(TotalFrame$Player)
  TotalFrame$Age<- as.numeric(as.character(TotalFrame$Age))
  TotalFrame$GP<- as.numeric(as.character(TotalFrame$GP))
  TotalFrame$GA<- as.numeric(as.character(TotalFrame$GA))
  TotalFrame$PlusMin<- as.numeric(as.character(TotalFrame$PlusMin))
  TotalFrame$G<- as.numeric(as.character(TotalFrame$G))
  TotalFrame$NHL<- as.numeric(as.character(TotalFrame$NHL))
  TotalFrame%>% arrange(Player)
  #### Joning player's performance in from different teams in one year to the same characther
  ### Salary is maintained, since I have proven empirically that in all cases salary is the same, so the yearly one no matter the team
  ### Other measures has been summed up
  Salaries2007<- TotalFrame%>%arrange(Player)
  EndSalaries<- Salaries2007%>%
    group_by_("Player") %>%
    dplyr::summarize(
      Salary = mean(Salary), # repeated total data
      GP = sum(GP),
      G = sum(G),
      GA = sum(GA),
      PlusMin= sum(PlusMin),
      NHL = sum(NHL) 
      ) 
  
  GeneralData<-Salaries2007  %>% 
    select(c("P", "Player", "Age"))%>% 
    distinct(Player, .keep_all = TRUE)%>%arrange(Player)
  TotalSalaries2007<-left_join(GeneralData, EndSalaries, by = "Player")
  return(TotalSalaries2007)
}  
