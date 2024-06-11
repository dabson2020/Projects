	### Introduction
	There are different tools for performing data analytics. In the project, we combine the function of Data analyst, Data Engineering and Data Science using Microsoft Fabric. The data cleaning is performed with Synapse Data Engineering, Sentiment analysis of the twitter data and the extraction of unigram and bigrams was carried out with the Synapse Data Science of Microsoft Engineering. Microsoft Fabric provides a platform for collaboration amongst these roles.
	
	The Microsoft Fabrics tools utilized in this projects are:
	
		- Data Factory: For extracting and copying data from twitter using the Twitter API. The extracted data is written into the lakehouse database as a delta table.
		- Synapse Data Engineering: The twitter data usually come messy and required cleaning. With Synapse Data Engineering, the data undergoes the cleaning process, writing the clean tweets in the lakehouse database as a delta table
		- Synapse Data Science: Two different notebooks are created for sentiment analysis and the tokenization of tweets into unigrams and bigrams. The results are written as delta tables in our lakehouse database.
		- Power BI: a dashboard is created to visualize our analysis, which includes the sentiments of the tweets
		- Data Activator: This tool is utilized to set alerts to trigger and send an email if a condition is met.
		
		### Data
		13124 Twitter data were extracted with twitter API. These tweets were created by 312 unique users in April and May of 2023. With Microsoft Fabrics, this data went through a series of data processing including data cleaning, data processing, tokenization and sentiment analysis
		
		### Data Cleaning
		Twitter data can be unstructured and there is need to clean the data in order to give it good and readable structure. Twitter data usually contains unwanted characters which includes hashtags, emojis, URLs, mentions, smileys and specific words. These characters are removed in order to structure the data. Unwanted punctuation and digits are also removed using regular expression (Regex). The process was carried out with a Synapse Data Engineering notebook of Fabric.
		
		### Data Preprocessing
		After cleaning, data is preprocessed by converting all the characters to lowercase, removing extra whitespaces and removing the stopwords. Stopwords are commonly used words that do not carry much meaning. Removal of these words do not have any effect on the meaning of the words and hence focusing on more meaningful words in the tweets. Example of stopwords are "the", "a", "an", "in", "and", "to", etc. Words with 3 characters are also removed from the tweets. Unwanted banned words were also removed to have a final clean tweets. This process was performed with Synapse Data Science notebook
		
		### Tokenization and Word Frequencies
		The tweets are tokenized (broken down) into words in order to determine the frequency of each word. After tokenization, the unigrams and bigrams of the words are extracted, and the frequencies of the words were computed. The top 20 unigrams and bigrams and their frequencies were written as a delta table in our lakehouse database.
	
		### Sentiment Analysis
		The sentiments of the tweets are determined with a machine learning sentiment model, to understand the sentiment of the each tweet, which could be positive sentiment (the tweet has positive connotation), negative tweets (the tweet contain negative meaning), or neutral sentiment (the tweet is neither positive or negative).
		
		### Visualization
		A Power BI dashboard is created to visualize these analysis. See the dashboard below:
		
		### Data Activator
		For this project, there is need to set alert to monitor the negative sentiment. Tracking the amount of negative sentiment, an alert is set with Data Activator to send an email when a condition is met. In this project, the condition is that, when the negative sentiment reaches 50\% of the total tweet, it should trigger an email for notification.