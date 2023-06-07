import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from CSIKit.filters.passband import lowpass
from CSIKit.filters.statistical import running_mean
from CSIKit.util.filters import hampel

def get_csi_data_from_csv(filename):
  df = pd.read_csv(filename)
  csi_data = df['CSI_DATA']
  csi_data = csi_data.str[1:-2].str.split(' ').to_list()
  csi_data = map(lambda csi: np.array(list(map(float, csi))), csi_data)

  return np.array(list(csi_data)).T

def remove_null_subporters(csi_data):
  left_cutpoint = 6
  central_subporter_index = 32
  right_cutpoint = -5

  return np.concatenate((
    csi_data[left_cutpoint*2: central_subporter_index*2, :],
    csi_data[(central_subporter_index+1)*2: right_cutpoint*2, :],
  ))

def extract_subporters_magnitudes(csi_data):
  real_parts = csi_data[::2, :]
  imaginary_parts = csi_data[1::2, :]
  amplitudes = np.sqrt(real_parts**2 + imaginary_parts**2)

  return amplitudes

def apply_filters(csi_data):
  csi_data = np.apply_along_axis(lambda subcarrier_data: lowpass(subcarrier_data, 10, 100, 5), 1, csi_data)
  csi_data = np.apply_along_axis(lambda subcarrier_data: hampel(subcarrier_data, 10, 3), 1, csi_data)
  csi_data = np.apply_along_axis(lambda subcarrier_data: running_mean(subcarrier_data, 10), 1, csi_data)

  return csi_data

csi_data = get_csi_data_from_csv('csi_data.csv')
csi_data = remove_null_subporters(csi_data)
csi_data = extract_subporters_magnitudes(csi_data)
csi_data = apply_filters(csi_data)

ax = sns.heatmap(csi_data)
plt.title("CSI Amplitude Heatmap")
ax.set(xlabel='Frame number', ylabel='Subcarrier Index')
plt.show()
