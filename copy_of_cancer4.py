# -*- coding: utf-8 -*-
"""Copy of cancer4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11xw2Sw4lrKxF31mvVX1OD5fkp9fgvRlF
"""

import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Lasso
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense

# Load your custom dataset from the specified path
dataset_path = "/content/data.csv"  # Replace with the actual file path
df = pd.read_csv(dataset_path)
df.head()

# Assuming your dataset has columns for features and a target variable (e.g., 'target_column_name')
X = df.drop(columns=['diagnosis'])  # Features
y = df['diagnosis']  # Target variable

#Data preprocessing
df.isnull().sum()

#feature selection
import seaborn as sns
import matplotlib.pyplot as plt
corr = df.iloc[:, 2:].corr()
colormap = sns.diverging_palette(220, 10, as_cmap=True)

plt.figure(figsize=(14, 14))
sns.heatmap(corr, cbar=True, square=True, annot=True, fmt='.2f', annot_kws={'size': 8},
            cmap=colormap, linewidths=0.1, linecolor='white')
plt.title('Correlation of df Features', y=1.05, size=15)

# Find relevant features based on a threshold (adjust threshold as needed)
threshold = 0.6
relevant_features = []

for i in range(len(corr.columns)):
    for j in range(i):
        if abs(corr.iloc[i, j]) > threshold:
            relevant_features.append((corr.columns[i], corr.columns[j]))

# Print the relevant features
print("Relevant Features:")
for feature_pair in relevant_features:
    print(f"{feature_pair[0]} and {feature_pair[1]}")

# Encode the target variable using label encoding
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Convert class labels to strings
class_names = label_encoder.classes_.astype(str)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
train_data_count = X_train.shape[0]
print("Number of training samples after standardization:", train_data_count)

# Count of testing data after standardization
test_data_count = X_test.shape[0]
print("Number of testing samples after standardization:", test_data_count)

# Step 1: Feature selection using Lasso
lasso = Lasso(alpha=0.01)
lasso.fit(X_train, y_train)
selected_feature_indices = np.where(lasso.coef_ != 0)[0]
X_train_lasso = X_train[:, selected_feature_indices]
X_test_lasso = X_test[:, selected_feature_indices]

# Output: List of selected features
selected_features = df.columns[selected_feature_indices]
print("Selected Features:")
for feature in selected_features:
    print(feature)

# Step 2: Train an ANN model
import tensorflow as tf
from tensorflow import keras

model_ann = keras.Sequential([
    Dense(64, activation='relu', input_shape=(X_train_lasso.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])
model_ann.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model_ann.fit(X_train_lasso, y_train, epochs=20, batch_size=64, verbose=0)

# Step 3: Train a Random Forest model
model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
model_rf.fit(X_train_lasso, y_train)

# Step 4: Make predictions using both models
y_pred_ann = model_ann.predict(X_test_lasso)
y_pred_rf = model_rf.predict(X_test_lasso)

# Output: Accuracy of ANN and Random Forest
accuracy_ann = accuracy_score(y_test, np.round(y_pred_ann))
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print("Accuracy of ANN:", accuracy_ann)
print("Accuracy of Random Forest:", accuracy_rf)

# Compute precision, recall, F1-score, and support
from sklearn.metrics import classification_report
report_ann = classification_report(y_test, np.round(y_pred_ann), target_names=label_encoder.classes_, output_dict=True)
report_rf = classification_report(y_test, y_pred_rf, target_names=label_encoder.classes_, output_dict=True)

# Convert the classification report dictionaries to DataFrames
df_report_ann = pd.DataFrame(report_ann).transpose()
df_report_rf = pd.DataFrame(report_rf).transpose()

# Display the classification reports as DataFrames
print("Classification Report (ANN):\n", df_report_ann)
print("\nClassification Report (Random Forest):\n", df_report_rf)

# Step 5: Create an ensemble model using Lasso
X_hybrid = np.column_stack((y_pred_ann, y_pred_rf))
lasso_hybrid = Lasso(alpha=0.01)
lasso_hybrid.fit(X_hybrid, y_test)

# Step 6: Make predictions with the ensemble model
hybrid_predictions = lasso_hybrid.predict(X_hybrid)
hybrid_predictions = np.round(hybrid_predictions)

# Output: Accuracy of the Ensemble Model
hybrid_accuracy = accuracy_score(y_test, hybrid_predictions)
print("Hybrid Model:", hybrid_accuracy)

import matplotlib.pyplot as plt

models = ['ANN', 'Random Forest', 'Hybrid']
accuracies = [accuracy_ann, accuracy_rf, hybrid_accuracy]
plt.bar(models, accuracies)
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim(0.9, 1.0)  # Adjust the y-axis limits if needed

# Annotate the percentages above each bar
for i, acc in enumerate(accuracies):
    plt.annotate(f'{acc*100:.2f}%', (i, acc), fontsize=12, ha='center', va='bottom')

plt.show()

# Create a bar chart to compare accuracies
models = ['ANN', 'Random Forest', 'Hybrid']
accuracies = [accuracy_ann, accuracy_rf, hybrid_accuracy]
plt.bar(models, accuracies)
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim(0.9, 1.0)  # Adjust the y-axis limits if needed

# Highlight the best-performing model
best_model_index = accuracies.index(max(accuracies))
plt.annotate(f"Best: {models[best_model_index]}", (best_model_index, accuracies[best_model_index]), fontsize=12, ha='center')

plt.show()

from sklearn.metrics import classification_report
import pandas as pd

# Assuming you have the classification report stored in 'classification_rep'
# 'class_names' should be a list of the class names
class_names = ['B', 'M']

report_dict = classification_report(y_test, hybrid_predictions, target_names=class_names, output_dict=True)

# Convert the classification report dictionary to a DataFrame
report_df = pd.DataFrame(report_dict)

# Transpose the DataFrame for better readability
report_df = report_df.transpose()

# Display the classification report in a table form
print(report_df)

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report

# Calculate classification reports for the ANN and Random Forest models
classification_rep_ann = classification_report(y_test, np.round(y_pred_ann), target_names=class_names, output_dict=True)
classification_rep_rf = classification_report(y_test, y_pred_rf, target_names=class_names, output_dict=True)

# Define a function to plot classification report metrics for each class in a bar chart
def plot_classification_report_metrics_bar(classification_rep_ann, classification_rep_rf, title):
    metrics = ['precision', 'recall', 'f1-score', 'support']
    x = np.arange(len(class_names))
    width = 0.35

    for metric in metrics:
        ann_metric_values = [classification_rep_ann[class_name][metric] for class_name in class_names]
        rf_metric_values = [classification_rep_rf[class_name][metric] for class_name in class_names]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, ann_metric_values, width, label='ANN', alpha=0.7)
        ax.bar(x + width/2, rf_metric_values, width, label='Random Forest', alpha=0.7)

        ax.set_xlabel('Class')
        ax.set_ylabel(metric.capitalize())
        ax.set_title(f'{metric.capitalize()} for Each Class ({title})')
        ax.set_xticks(x)
        ax.set_xticklabels(class_names, rotation=45, ha="right")
        ax.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Plot classification report metrics for the ANN and Random Forest models in a bar chart
plot_classification_report_metrics_bar(classification_rep_ann, classification_rep_rf, 'ANN vs. Random Forest')