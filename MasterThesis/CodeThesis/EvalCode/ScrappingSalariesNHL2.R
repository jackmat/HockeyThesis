library(XML)
url<- paste0("https://www.nhlnumbers.com/team-salaries/anaheim-ducks-salary-cap")
tables <- readHTMLTable(url)
