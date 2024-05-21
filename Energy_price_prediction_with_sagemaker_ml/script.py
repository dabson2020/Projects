import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score,classification_report, confusion_matrix
import joblib
import sklearn
import boto3
import pathlib
from io import StringIO
import numpy as np



def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf

if __name__=="__main__":
    print("[INFO] Extracting arguments")
    parser = argparse.ArgumentParser()

    # Hyperparameters are described here
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--random_state', type=int, default=100)

    #Data, model, and output directories
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))
    parser.add_argument('--train-file', type=str, default='train_data.csv')
    parser.add_argument('--test-file', type=str, default='test_data.csv')

    args, _ = parser.parse_known_args()

    print("Sklearn version is:", sklearn.__version__)
    print("Joblib version is:", joblib.__version__)

    print("[INFO] Reading data")
    train_df = pd.read_csv(os.path.join(args.train, args.train_file))
    test_df = pd.read_csv(os.path.join(args.test, args.test_file))

    features = list(train_df.columns)
    label = features.pop(-1)

    print("Building training and testing datasets")
    ()
    X_train = train_df[features]
    X_test = test_df[features]
    y_train = train_df[label]
    y_test = test_df[label]

    print("Column order ")
    print(features)
    print()

    #print the shape of the training and testing datasets
    print("The shape of X_train is:", X_train.shape)
    print("The shape of X_test is:", X_test.shape)
    print("The shape of y_train is:", y_train.shape)
    print("The shape of y_test is:", y_test.shape)

    print("Training the RadomForest Model")
    print()
    clf = RandomForestClassifier(n_estimators=args.n_estimators, random_state=args.random_state)
    clf.fit(X_train, y_train)
    print()

    model_path = os.path.join(args.model_dir, "model.joblib")
    print("Saving the model")
    joblib.dump(clf, model_path)
    print("Model has been persisted at:", model_path)
    print()

    print("METRIC RESULTS FOR TESTING DATA")
    print()
    y_pred_test = clf.predict(X_test)
    y_pred_train = clf.predict(X_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    test_recall = recall_score(y_test, y_pred_test)
    test_precision = precision_score(y_test, y_pred_test)
    test_f1 = f1_score(y_test, y_pred_test)
    print("[TESTING] Model Accuracy is:", test_acc)
    print("[TESTING] Model Precision is:", test_precision)
    print("[TESTING] Model Recall is:", test_recall)
    print("[TESTING] Model F1 Score is:", test_f1)
    print('[TESTING] Model Classification Report is', classification_report(y_test, y_pred_test))
    print()
