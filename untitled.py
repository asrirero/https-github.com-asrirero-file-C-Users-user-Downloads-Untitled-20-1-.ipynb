# -*- coding: utf-8 -*-
"""Untitled

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oiLghVArRdIL218Lj8P8Tcg_-sgc9EDZ
"""

from google.colab import drive
drive.mount('/content/drive')

# INSTALL PACKAGE
mypack <- function(package){
  new.package <- package[!(package %in% installed.packages()[ Package])]
  if (length(new.package)) 
    install.packages(new.package, dependencies = TRUE)
  sapply(package, require, character.only = TRUE)
}

package <- c("wordcloud","wordcloud2","RColorBrewer","tm","tidyverse","naivebayes",
            "e1071","caret")

mypack(package)

library(wordcloud)
library(wordcloud2)
library(RColorBrewer)
library(tm)
library(tidyverse)
library(naivebayes)
library(e1071)
library(caret)

# IMPORT DATA

berita_csv <- read.csv('../input/bbc-news-data-2/BBC News Data.csv')
berita_text <- berita_csv$Text
berita_corp <- VCorpus(VectorSource(berita_text))

# CLEAN DATA

berita_clean <- berita_corp %>%
  tm_map(removeNumbers) %>%
  tm_map(removePunctuation) %>%
  tm_map(stripWhitespace)
berita_clean <- tm_map(berita_clean, content_transformer(tolower))
berita_clean <- tm_map(berita_clean, removeWords, stopwords("english"))

dtm <- TermDocumentMatrix(berita_clean) 
matrix <- as.matrix(dtm) 
words <- sort(rowSums(matrix),decreasing=TRUE) 
df <- data.frame(word = names(words),freq=words)

# WORDCLOUD

set.seed(1234) 
wordcloud(words = df$word, freq = df$freq,
          min.freq = 1, max.words=50, random.order=FALSE,
          rot.per=0.35, colors=brewer.pal(8, "Dark2"))

# NAIVE BAYES 

DTMberita <- DocumentTermMatrix(berita_clean)
beritafreq <- findFreqTerms(dtm, 1)
DTMberita.freq <- DTMberita[,beritafreq]
DTMberita.freq

convert_counts <- function(x) {
  x <- ifelse(x > 0, "yes", "no")
}

berita.train <- apply(DTMberita.freq,MARGIN = 2,convert_counts)
berita.tag <- factor(berita_csv$Category)
<<DocumentTermMatrix (documents: 682, terms: 14413)>>
Non-/sparse entries: 90850/9738816
Sparsity           : 99%
Maximal term length: 23
Weighting          : term frequency (tf)

#TRAIN-TEST SPLIT MODEL

n_berita <- nrow(berita.train)
sample_berita <- floor(0.75*n_berita)
set.seed(123)
train_berita <- base::sample(c(1:n_berita),size=sample_berita)

data_berita_train <- DTMberita[train_berita, ]
data_berita_test <- DTMberita[-train_berita, ]
label_berita_train <- berita_csv[train_berita,]$Category %>% as.factor()
label_berita_test <- berita_csv[-train_berita,]$Category %>% as.factor()

berita_freq_train <- data_berita_train %>%
  findFreqTerms(1) %>%
  data_berita_train[ , .]
berita_freq_test <- data_berita_test %>%
  findFreqTerms(1) %>%
  data_berita_test[ , .]

convert_counts <- function(x) {
  x <- ifelse(x > 0, "Yes", "No")
}

berita_train <- berita_freq_train %>%
  apply(MARGIN = 2, convert_counts)
berita_test <- berita_freq_test %>%
  apply(MARGIN = 2, convert_counts)

berita_classifier <- naiveBayes(berita_train, label_berita_train)
berita_pred <- predict(berita_classifier, berita_test)
confusionMatrix(berita_pred,label_berita_test)
Confusion Matrix and Statistics

          Reference
Prediction business sport
  business       90     0
  sport           0    81
                                     
               Accuracy : 1          
                 95% CI : (0.9787, 1)
    No Information Rate : 0.5263     
    P-Value [Acc > NIR] : < 2.2e-16  
                                     
                  Kappa : 1          
                                     
 Mcnemar's Test P-Value : NA         
                                     
            Sensitivity : 1.0000     
            Specificity : 1.0000     
         Pos Pred Value : 1.0000     
         Neg Pred Value : 1.0000     
             Prevalence : 0.5263     
         Detection Rate : 0.5263     
   Detection Prevalence : 0.5263     
      Balanced Accuracy : 1.0000     
                                     
       'Positive' Class : business   
                                     
  # SUPPORT VECTOR MACHINE

train_idx <- createDataPartition(berita_csv$Category, p=0.75, list=FALSE)

train1 <- berita_csv[train_idx,]
test1 <- berita_csv[-train_idx,]

train2 <- berita_clean[train_idx]
test2 <- berita_clean[-train_idx]

DTMberita <- DocumentTermMatrix(berita_clean)
dict2 <- findFreqTerms(DTMberita, lowfreq=1)

sms_train <- DocumentTermMatrix(train2, list(dictionary=dict2))
sms_test <- DocumentTermMatrix(test2, list(dictionary=dict2))

convert_counts <- function(x) {
  x <- ifelse(x > 0, 1, 0)
}

sms_train <- sms_train %>% apply(MARGIN=2, FUN=convert_counts)
sms_test <- sms_test %>% apply(MARGIN=2, FUN=convert_counts)
sms_train <- as.data.frame(sms_train)
sms_test <- as.data.frame(sms_test)

sms_train1 <- cbind(cat=factor(train1$Category), sms_train)
sms_test1 <- cbind(cat=factor(test1$Category), sms_test)
sms_train1<-as.data.frame(sms_train1)
sms_test1<-as.data.frame(sms_test1)

fit1 <- svm(cat~., data=sms_train1)
fit1.pred <- predict(fit1,sms_test1)
confMatrix1 <- confusionMatrix(fit1.pred, sms_test1$cat)
confMatrix1

"""# Bagian Baru"""