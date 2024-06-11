### Introduction
There are different tools for performing data analytics. In this project, we combine the functions of Data Analyst, Data Engineer, and Data Scientist using Microsoft Fabric. We utilize various tools provided by Microsoft Fabric to extract, clean, analyze, and visualize Twitter data.

The Microsoft Fabric tools utilized in this project are:

- Data Factory: Used to extract and copy data from Twitter using the Twitter API. The extracted data is written into a lakehouse database as a delta table.
- Synapse Data Engineering: Used to clean the Twitter data. The cleaned tweets are written into the lakehouse database as a delta table.
- Synapse Data Science: Used for sentiment analysis and tokenization of tweets into unigrams and bigrams. The results are written as delta tables in the lakehouse database.
- Power BI: A dashboard is created to visualize the analysis, including the sentiments of the tweets.
- Data Activator: Used to set alerts and trigger an email when a condition is met.

![alt text](<twitter microsoft fabric.jpg>)

### Data
A total of 13,164 Twitter data were extracted using the Twitter API. These tweets were created by 342 unique users in April and May of 2023. With Microsoft Fabric, this data went through a series of data processing steps, including data cleaning, data processing, tokenization, and sentiment analysis.

### Data Cleaning
Twitter data can be unstructured, so it is important to clean the data to give it a good and readable structure. Unwanted characters such as hashtags, emojis, URLs, mentions, smileys, and specific words are removed. Punctuation, digits, and stopwords are also removed using regular expressions. The data cleaning process was performed using a Synapse Data Engineering notebook.

### Data Preprocessing
After cleaning, the data is preprocessed by converting all characters to lowercase, removing extra whitespaces, and removing stopwords. Stopwords are commonly used words that do not carry much meaning. Words with 3 characters are also removed from the tweets. Unwanted banned words are also removed to obtain a final set of clean tweets. This process was performed using a Synapse Data Science notebook.

### Tokenization and Word Frequencies
The tweets are tokenized (broken down) into words to determine the frequency of each word. After tokenization, the unigrams and bigrams of the words are extracted, and the frequencies of the words are computed. The top 20 unigrams and bigrams and their frequencies are written as a delta table in the lakehouse database.

### Sentiment Analysis
The sentiments of the tweets are determined using a machine learning sentiment model. This helps understand whether a tweet has a positive, negative, or neutral sentiment.

### Orchestration
All these processes are orchestrated using a data pipeline, which automates the process on a set schedule. Below is a visual representation of the complete orchestrated pipeline.

![Orchestrated Pipeline](microsoft_fabric_project.png)

### Visualization
A Power BI dashboard is created to visualize the analysis. The dashboard provides a comprehensive view of the project's findings.

![alt text](<power bi.png>)

### Data Activator
For this project, an alert is set to monitor negative sentiment. When the negative sentiment reaches 50% of the total tweets, an email notification is triggered using Data Activator.