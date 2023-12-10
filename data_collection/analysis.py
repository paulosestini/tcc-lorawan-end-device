import os
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

BASE_DIR = 'filtered_data'
files = os.listdir(BASE_DIR)

label_map = {
    'person': 0,
    'car': 1
}

data = {}
labels = {}

for file in files:
    filedata = pd.read_csv(os.path.join(BASE_DIR, file), header=None)
    filedata = filedata.apply(lambda s: s.apply(lambda x: max(x, -50))).values
    filedata /= filedata.mean()

    file_features = np.concatenate([
        filedata.mean(axis=0),
        filedata.std(axis=0)
    ])
    data[file] = file_features

    for key, value in label_map.items():
        if key in file:
            labels[file] = value

data = pd.DataFrame.from_dict(data, orient='index')
labels = pd.DataFrame.from_dict(labels, orient='index')
labels.columns=['label']

print(labels)

print(data)
#scaler = StandardScaler()
#scaled_data = scaler.fit_transform(data)
tsne = TSNE(n_components=2, random_state=0, perplexity=20)
tsne_result = tsne.fit_transform(data)

plt.figure(figsize=(12, 8))
plt.scatter(tsne_result[:, 0], tsne_result[:, 1], c=labels['label'])
plt.xlabel('t-SNE feature 1')
plt.ylabel('t-SNE feature 2')
plt.title('t-SNE Projection of Samples')

#for i, txt in enumerate(data.index):
#    plt.text(tsne_result[i, 0], tsne_result[i, 1], txt, fontsize=9)


plt.show()
