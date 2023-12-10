import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_matrix(csv_file):
    # Load matrix from CSV file
    matrix = pd.read_csv(csv_file, header=None).values

    
    # Create a heatmap of the matrix
    fig, ax = plt.subplots(dpi=150)
    sns.heatmap(matrix.T, cmap="plasma", cbar_kws={'label': 'dBm'}, vmin=-50, ax=ax)
    plt.title('Matriz de amplitudes CSI - Exemplo de carro')
    plt.ylabel('Índice da subportadora')
    plt.xlabel('Vetor CSI')
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Provide the path to your CSV file here
    csv_file = 'filtered_data/matrix_2023-11-09_18-24-00_car.csv'
    plot_matrix(csv_file)
