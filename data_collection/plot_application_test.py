import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

label_map = {
    'pessoa': 0,
    'carro': 1
}

conf_matrix = np.array([
    [6, 1],
    [0, 15]
])

plt.figure(figsize=(3.25, 3), dpi=125)
sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues', xticklabels=list(label_map.keys()), yticklabels=list(label_map.keys()))
plt.xlabel('Classe predita')
plt.ylabel('Classe real')
plt.title('Matriz de confusão')
plt.tight_layout()
plt.show()