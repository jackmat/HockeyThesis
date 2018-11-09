
  Data2007<-GeneralTableList[[1]] 
    
  DirectImpact07<-Data2007[,1:13]%>% 
  arrange(desc(Direct))  %>% 
  head(10)
  
  CollectiveImpact07<-Data2007[,1:13]%>% 
    arrange(desc(Collective))  %>% 
    head(10)
  
  DirectImpactTime07<-Data2007[,1:13]%>% 
    arrange(desc(Directh))  %>% 
    head(10)

  CollectiveImpactTime07 <- Data2007[,1:13]%>% 
    arrange(desc(Collectiveh))  %>% 
    head(10)
  
  

  
  GPDirectImpact07<-Data2007[,c(1:9,14:17)]%>% 
    arrange(desc(GPDirect))  %>% 
    head(10)

  GPCollectiveImpact07<-Data2007[,c(1:9,14:17)]%>% 
    arrange(desc(GPCollective))  %>% 
    head(10)
  
  GPDirecthImpact07<-Data2007[,c(1:9,14:17)]%>% 
    arrange(desc(GPDirecth))  %>% 
    head(10)

  GPCollectiveImpacth07<-Data2007[,c(1:9,14:17)]%>% 
    arrange(desc(GPCollectiveh))  %>% 
    head(10)
#############################################################
  Data2008<-GeneralTable 
  DirectImpact08<-Data2008[,1:13]%>% 
    arrange(desc(Direct))  %>% 
    head(10)
  
  CollectiveImpact08<-Data2008[,1:13]%>% 
    arrange(desc(Collective))  %>% 
    head(10)
  
  DirectImpactTime08<-Data2008[,1:13]%>% 
    arrange(desc(Directh))  %>% 
    head(10)

  
  CollectiveImpactTime08 <- Data2008[,1:13]%>% 
    arrange(desc(Collectiveh))  %>% 
    head(10)

  GPDirectImpact08<-Data2008[,c(1:9,14:17)]%>% 
    arrange(desc(GPDirect))  %>% 
    head(10)
  
  GPCollectiveImpact08<-Data2008[,c(1:9,14:17)]%>% 
    arrange(desc(GPCollective))  %>% 
    head(10)

  GPDirecthImpact08<-Data2008[,c(1:9,14:17)]%>% 
    arrange(desc(GPDirecth))  %>% 
    head(10)
  
  GPCollectiveImpacth08<-Data2008[,c(1:9,14:17)]%>% 
    arrange(desc(GPCollectiveh))  %>% 
    head(10)



library(kableExtra)
CompDirect<-rbind(DirectImpact07, DirectImpact08)
CompDirecth<-rbind(DirectImpactTime07, DirectImpactTime08)
CompCollective<-rbind(CollectiveImpact07,CollectiveImpact08)
CompCollectiveh<-rbind(CollectiveImpactTime07,CollectiveImpactTime08)
Top10Table0708<- function(Data, blackcol,  type = "latex"){
  CompDirect0708<- data.frame(TopPlayers = rep(1:10,2),Data)
  kable(Data,type, booktabs = TRUE) %>%
  column_spec(blackcol, bold = T) %>%
  kable_styling(font_size = 9) %>%
  group_rows(index=c("2007" = 10, "2008" = 10))
}

Top10Table0708(CompDirect, blackcol = 10 , "html")
Top10Table0708(CompDirecth, blackcol = 11, "html")
Top10Table0708(CompCollective, blackcol = 12)
Top10Table0708(CompCollectiveh, blackcol = 13, "html")



