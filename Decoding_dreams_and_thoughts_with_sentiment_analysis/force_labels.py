
"""## Load Data"""
import pandas as pd
import numpy as np



dftrain = pd.read_csv('giulia_train_data.csv',encoding='cp1252')
dftest = pd.read_csv('test data my labels.csv',encoding= 'cp1252')
dftrain['giulia'] = dftrain['sentiment'].apply(lambda x: 0 if x < 4 else 1)

np.random.seed(2209506)

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import RobertaTokenizer, RobertaForSequenceClassification, AdamW
from sklearn.metrics import precision_score, recall_score, classification_report

# Define the dataset class
class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, index):
        text = self.texts[index]
        label = self.labels[index]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'label': torch.tensor(label, dtype=torch.long)
        }

# Define hyperparameters and settings
batch_size = 4
epochs = 10
learning_rate = 2e-5
max_length = 300


# Load and tokenize the data
texts = list(dftrain['text']) # List of text data
labels = list(dftrain['giulia'])  # List of corresponding sentiment labels
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

# Create the dataset and data loaders
dataset = SentimentDataset(texts, labels, tokenizer, max_length)
train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Load the pre-trained RoBERTa model
model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)  # Adjust num_labels according to your sentiment classes

# Set up the optimizer and loss function
optimizer = AdamW(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()

# Training loop
model.train()

for epoch in range(epochs):
    total_loss = 0
    for batch in train_loader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['label']

        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    average_loss = total_loss / len(train_loader)
    print(f'Epoch {epoch+1}/{epochs} - Loss: {average_loss:.4f}')



# Save the trained model
model.save_pretrained('model_giulia/train_model')
tokenizer.save_pretrained('model_giulia/tokenizer')


# Load and tokenize the test data
test_texts = list(dftest['Text'])  # List of test text data
test_labels = list(dftest['label'])  # List of corresponding test sentiment labels

test_dataset = SentimentDataset(test_texts, test_labels, tokenizer, max_length)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Load the trained model
model_path = 'model_giulia/train_model'  # Path where the trained model is saved
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForSequenceClassification.from_pretrained(model_path)

#Evaluate the model on train data

model.eval()

predicted_train = []
true_label = []

with torch.no_grad():
    for batch in train_loader:
        input_ids=batch['input_ids']
        attention_mask=batch['attention_mask']
        labels=batch['label']

        outputs=model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        _,batch_predicted_train = torch.max(logits, dim=1)
        predicted_train.extend(batch_predicted_train.numpy())
        true_label.extend(labels.numpy())

#calculate accuracy
new = sum(predicted_label==true_label for predicted_label, true_label in zip(predicted_train,true_label))
accuracy = new/len(predicted_train)
precision=precision_score(predicted_train,true_label)
recall=recall_score(predicted_train, true_label)
print(f'Train Accuracy: {accuracy * 100:.2f}%')
print(f'Train Precision: {precision *100:.2f}%')
print(f'Train Recall: {recall * 100:.2f}%')

# Evaluate the model on test data


model.eval()


predicted_labels = []
true_labels = []

with torch.no_grad():
    for batch in test_loader:
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['label']

        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        _, batch_predicted_labels = torch.max(logits, dim=1)
        predicted_labels.extend(batch_predicted_labels.numpy())

        true_labels.extend(labels.numpy())

# Calculate accuracy
correct = sum(predicted_label == true_label for predicted_label, true_label in zip(predicted_labels, true_labels))
accuracy = correct / len(predicted_labels)
print('*'*60)
precision=precision_score(predicted_labels,true_labels)
recall=recall_score(predicted_labels, true_labels)
print(f'Test Accuracy: {accuracy * 100:.2f}%')
print(f'Test Precision: {precision *100:.2f}%')
print(f'Test Recall: {recall * 100:.2f}%')


# Add predicted labels to the test data
test_data_with_labels = pd.DataFrame({'Text': test_texts, 'Actual Sentiment': test_labels, 'Predicted Sentiment': predicted_labels})

# Print the test data with predicted labels
print(test_data_with_labels.head())
test_data_with_labels.to_csv('giulia_predict_new.csv', index = False)
