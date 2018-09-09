###
path = "C:/Users/Carles/Desktop/MasterThesis/CodeThesis/"
PlayerValMatrix <- read.csv(paste0(path, "PlayerValMatrix.csv"),
                            sep = ",", dec = ".", header = TRUE)
PlayerbyTimeValMatrix <- read.csv(paste0(path, "PlayerbyTimeValMatrix.csv"),
                                  sep = ",", dec = ".", header = TRUE)
### Need to treat NA values
library(ggplot2)
library(reshape2)

options(scipen=999)  # turn-off scientific notation like 1e+48 NOT SURE WHAT IT DOES
theme_set(theme_bw())  # pre-set the bw theme.

PlotFunc<- function(Data, x, y, color){
  myData_melted <- melt(Data, id.vars = 'CountGame')
  ggplot(myData_melted, aes(x = CountGame, y = value)) + 
    geom_line(aes(color = variable #, group = cat
    ),show.legend = F) +  
    labs(subtitle="Valuation", 
         y="Valuation by Player", 
         x="Matches played by each player", 
         title="Player's valuation on season 2007"#, 
         #caption = "Source: Carles Illustration"
          )
}


### Reproducible example
myData = data.frame(counter = 1:10, 
                    Player1 = rnorm(10, 5,10),
                    Player2 = rnorm(10,5, 1),
                    Player3 = 4:13,
                    Player4 = 24:15,
                    player5 = rnorm(10,1,1))
PlotFunc(myData, x = 'counter', y = 'value', color = 'variable')
PlotFunc(PlayerValMatrix, x = 'CounterGame', y = 'value', color = 'variable')


# PlotFunc(PlayerValMatrix, x = 'counter', y = 'value', color = 'variable')
# PlotFunc(PlayerbyTimeValMatrix, x = 'counter', y = 'value', color = 'variable')

########################### Example to show the Data as the best players / worse players
# Data Prep
data("mtcars")  # load data
mtcars$`car name` <- rownames(mtcars)  # create new column for car names
mtcars$mpg_z <- round((mtcars$mpg - mean(mtcars$mpg))/sd(mtcars$mpg), 2)  # compute normalized mpg
mtcars$mpg_type <- ifelse(mtcars$mpg_z < 0, "below", "above")  # above / below avg flag
mtcars <- mtcars[order(mtcars$mpg_z), ]  # sort
mtcars$`car name` <- factor(mtcars$`car name`, levels = mtcars$`car name`)  # convert to factor to retain sorted order in plot.

library(ggplot2)
theme_set(theme_bw())

# Plot
ggplot(mtcars, aes(x=`car name`, y=mpg_z, label=mpg_z)) + 
  geom_point(stat='identity', aes(col=mpg_type), size=6)  +
  scale_color_manual(name="Mileage", 
                     labels = c("Above Average", "Below Average"), 
                     values = c("above"="#00ba38", "below"="#f8766d")) + 
  geom_text(color="white", size=2) +
  labs(title="Diverging Dot Plot", 
       subtitle="Normalized mileage from 'mtcars': Dotplot") + 
  ylim(-2.5, 2.5) +
  coord_flip()