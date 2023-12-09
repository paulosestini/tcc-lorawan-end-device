import os
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = 'new_matrices'
files = os.listdir(BASE_DIR)



data = {}
print(files)

for file in files:
    filedata = pd.read_csv(os.path.join(BASE_DIR, file), header=None)
    filedata = filedata.apply(lambda s: s.apply(lambda x: max(x, -50)))
    #filedata /= abs(filedata.mean())

    file_features = np.concatenate([
        filedata.mean(axis=0),
        filedata.std(axis=0)
    ])
        
        # Create a heatmap of the matrix
    fig, ax = plt.subplots(3, 1)
    file_features = np.concatenate([
        filedata.mean(axis=0),
        filedata.std(axis=0)
    ])
    sns.heatmap(filedata.T, cmap="viridis", cbar_kws={'label': 'Value'}, ax=ax[0])
    sns.heatmap(np.expand_dims(filedata.mean(axis=0), axis=1).T, cmap="viridis", cbar_kws={'label': 'Value'}, ax=ax[1])
    sns.heatmap(np.expand_dims(filedata.std(axis=0), axis=1).T, cmap="viridis", cbar_kws={'label': 'Value'}, ax=ax[2])


    fig.suptitle(file)
    
    # Show the plot
    plt.show()
