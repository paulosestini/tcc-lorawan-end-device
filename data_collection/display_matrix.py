import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_matrix(csv_file):
    # Load matrix from CSV file
    matrix = pd.read_csv(csv_file, header=None).values
    
    # Create a heatmap of the matrix
    sns.heatmap(matrix.T, cmap="viridis", cbar_kws={'label': 'Value'})
    plt.title('Matrix Heatmap')
    plt.xlabel('Column')
    plt.ylabel('Row')
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Provide the path to your CSV file here
    csv_file = 'matrices/matrix_2023-10-21_13-48-32.csv'
    plot_matrix(csv_file)
