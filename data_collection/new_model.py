import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns

BASE_DIR = 'filtered_data'
files = os.listdir(BASE_DIR)

label_map = {
    'person': 0,
    'car': 1
}

data = {}
labels = {}

for file in files:
    filedata = pd.read_csv(os.path.join(BASE_DIR, file), header=None).astype(np.float16).values
    filedata /= filedata.mean()

    file_features = np.concatenate([
        filedata.mean(axis=0),
        filedata.std(axis=0)
    ])

    #important_features = np.array([40, 44, 41, 43, 42, 94, 95, 93, 46, 96, 92, 45, 39, 38, 36, 49, 97,
    #        15, 14, 91, 47, 37, 64, 90, 48])
    important_features = np.array([ 70,  71,  69,  72,  31,  35,  16, 102,  37,  39, 101,  36, 103,
        33,  20, 100])
    
    data[file] = file_features[important_features]

    for key, value in label_map.items():
        if key in file:
            labels[file] = value

data = pd.DataFrame.from_dict(data, orient='index')
labels = pd.DataFrame.from_dict(labels, orient='index')
labels.columns=['label']

#new_vec = [1.153,1.064,1.167,1.088,1.12,0.1718,0.0948,0.3618,1.028,0.0836,0.2888,1.046,1.124,1.116,1.066,1.002,0.0746,0.942,0.935,0.1837,1.018,1.085,0.0649,0.255,1.008 ]
#new_vec = [1.029,1.039,1.032,1.038,1.038,0.0855,0.0875,0.08276,1.034,0.09393,0.08246,1.043,1.023,1.02,1.012,1.031,0.1711,0.979,0.9766,0.0791,1.034,1.014,0.08295,0.0804,1.031] 
#new_vec =  [1.029,1.007,1.027,1.017,1.025,0.05487,0.04922,0.05804,0.988,0.0466,0.0593,0.9985,1.026,1.022,1.018,0.97,0.044,0.989,0.9824,0.05762,0.982,1.017,0.0628,0.05576,0.976 ] 
#new_vec = np.array(new_vec)
#distance = ((data - new_vec)**2).sum(axis=1)**0.5
#print(distance)
#print(distance.index[distance.argmin()])


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(data, labels['label'], test_size=0.5, random_state=1, shuffle=True)



print(X_train)
print(X_test)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
preds = model.predict(X_test.values)
print(accuracy_score(y_test, preds)*100)
conf_matrix = confusion_matrix(y_test, preds)
print(conf_matrix)


## Fit all data
#model = KNeighborsClassifier(n_neighbors=5)
#model.fit(data, labels['label'])
#preds = model.predict(data.values)
#print(accuracy_score(labels['label'], preds)*100)
#conf_matrix = confusion_matrix(labels['label'], preds)
#print(conf_matrix)


plt.figure(figsize=(3.5, 3))
sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues', xticklabels=list(label_map.keys()), yticklabels=list(label_map.keys()))
plt.xlabel('Classe predita')
plt.ylabel('Classe real')
plt.title('Matriz de confusão')
plt.tight_layout()
plt.show()

#import pickle
#pickle_file = open('knn_pickle', 'wb')
#pickle.dump(model, pickle_file)
#pickle_file.close()

