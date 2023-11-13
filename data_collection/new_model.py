import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

BASE_DIR = 'filtered_data'
files = os.listdir(BASE_DIR)

label_map = {
    'person': 0,
    'car': 1
}

data = {}
labels = {}

for file in files:
    filedata = pd.read_csv(os.path.join(BASE_DIR, file), header=None).values
    filedata /= filedata.mean()

    file_features = np.concatenate([
        filedata.mean(axis=0),
        filedata.std(axis=0)
    ])

    important_features = np.array([40, 44, 41, 43, 42, 94, 95, 93, 46, 96, 92, 45, 39, 38, 36, 49, 97,
            15, 14, 91, 47, 37, 64, 90, 48])
    data[file] = file_features[important_features]

    for key, value in label_map.items():
        if key in file:
            labels[file] = value

data = pd.DataFrame.from_dict(data, orient='index')
labels = pd.DataFrame.from_dict(labels, orient='index')
labels.columns=['label']

print(labels)
print(data)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(data, labels['label'])
preds = model.predict(data.values)
print(accuracy_score(labels['label'], preds)*100)
print(confusion_matrix(labels['label'], preds))