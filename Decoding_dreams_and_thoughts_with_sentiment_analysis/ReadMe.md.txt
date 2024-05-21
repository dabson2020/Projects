The project work centred around the text analysis of dreams 

Data:
Multiple data annotator annotated the data with 2 labels and then 3 labels
    Two labels
    The annotators' labels were 0 for negative sentiment and 1 for positive sentiment.
    THe ground truth were compared amongst the annotators to establish the sneitment of dreamers.


Three labels
The annotators also labelled the data with three labels: 0 for negative sentiments, 1 for neutral sentiment and 2 for positive sentiments
The ground truth was also established here

Model
The Language Model, ROBERTa BERT was trained with the text data to extract the sentiments in each text
The ground truth was compared with the model prediction, with about 90% accuracy of model performance on test data with 2-labelled data
For the 3-labelled data, the model performance was about 74% accuracy.

THe model was well generalized on both training and test data.