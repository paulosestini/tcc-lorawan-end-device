import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import seaborn as sns
import re
import threading
import time
import os

from CSIKit.filters.passband import lowpass
from CSIKit.filters.statistical import running_mean
from CSIKit.util.filters import hampel

from functools import reduce

n_subporters = 64

class CsiReader:
  def __init__(self, device_path, max_frames=500):
    self.device_path = device_path
    self.max_frames = max_frames
    self.frame_counter = 0
    self.frames = np.zeros((self.max_frames, n_subporters))
    self.reference_frame = None
    self.thread_args = [False]

  def run(self):
    self.thread = threading.Thread(target=self.__run, args=(), daemon=True)
    self.thread.start()

  def __run(self):
    with open(self.device_path) as file:

      content = ''

      while True:
          time.sleep(0.01)

          content += file.read()
          split_content = content.split('\n')
          if len(split_content) <= 1:
            continue
          
          line = split_content[0]
          content = '\n'.join(split_content[1:])

          csi_data_match = re.search('CSI_DATA.*', line)
          if not csi_data_match:
            print("Error - no match")
            continue
          csi_line = csi_data_match[0]

          if(len(csi_line.split(',')) != 26):
            print('Error - broken line')
            continue

          rssi = float(csi_line.split(',')[3])
          rssi_power = 10**(rssi/10)

          csi_vector_match = re.findall('\[.*\]', csi_line)

          if len(csi_vector_match) == 0:
            print('Error - null length ')
            continue

          csi_vector = re.sub('(\[)|(\])', '', csi_vector_match[0]).split()

          try:
            csi_vector = np.array(list(map(int, csi_vector)))
          except Exception as e:
            print('Error - broken component')
            continue

          if len(csi_vector) != 128:
            print('Error - missing values')
            continue

          #csi_vector = self.remove_null_subporters(csi_vector)
          
          real_parts = csi_vector[::2]
          imaginary_parts = csi_vector[1::2]
          amplitudes = np.sqrt(real_parts**2 + imaginary_parts**2)

          scale_factor = rssi_power / (sum(amplitudes) / n_subporters)
          amplitudes = amplitudes * scale_factor**0.5

          amplitudes_in_dbm = 10*np.log10(amplitudes + 1e-30)

          if self.frame_counter < self.max_frames:
            self.frames[self.frame_counter] = amplitudes_in_dbm
          else:
            if self.frame_counter == self.max_frames:
              self.reference_frame = self.frames
            self.frames = np.roll(self.frames, -1, axis=0)
            self.frames[-1] = amplitudes_in_dbm

          self.frame_counter += 1


  def remove_null_subporters(self, csi_vector):
    left_cutpoint = 6
    central_subporter_index = 32
    right_cutpoint = -5

    return np.concatenate((
      csi_vector[left_cutpoint*2: central_subporter_index*2],
      csi_vector[(central_subporter_index+1)*2: right_cutpoint*2],
    ))



def apply_filters(csi_data):
  #csi_data = np.apply_along_axis(lambda subcarrier_data: lowpass(subcarrier_data, 10, 100, 5), 1, csi_data)
  #csi_data = np.apply_along_axis(lambda subcarrier_data: hampel(subcarrier_data, 10, 3), 1, csi_data)
  #csi_data = np.apply_along_axis(lambda subcarrier_data: running_mean(subcarrier_data, 10), 1, csi_data)

  return csi_data

reader = CsiReader('/dev/ttyACM0', max_frames=500)
reader.run()
  
time.sleep(1)

csi_data = apply_filters(reader.frames.T)
fig, ax = plt.subplots(1, 1, figsize=(16, 8), dpi=100)
  
ax.set_title("CSI Amplitude Heatmap")
img0 = ax.imshow(csi_data, vmin=-40, vmax=-15)



should_beep = False

previous_level = 1
current_level = 1

def update(frame, *fargs):
  global current_level
  global previous_level
  global should_beep

  csi_data = apply_filters(reader.frames.T)

  if reader.frame_counter > reader.max_frames:
    reference_power = apply_filters(reader.reference_frame.T).sum(axis=0).mean()
    current_power = csi_data[:, -20].sum(axis=0).mean()
    print(current_power, reference_power)

    previous_level = current_level
    if current_power <= 1.10 * reference_power:
      current_level = 0
    else:
      current_level = 1

    if current_level == 0 and previous_level == 1:
      should_beep = True
    else:
      should_beep = False

    if should_beep:
      os.system('play -n synth 1 sine 440 vol 0.5')
      already_beeped = True

      


  img0.set_data(csi_data)
  return

ani = FuncAnimation(fig, update, frames=range(500),interval=1)
plt.show()

"""
fig, ax = plt.subplots(2, 1, figsize=(4, 6), dpi=200)
plot1 = sns.heatmap(csi_data, ax=ax[0], vmin=0, vmax=30)
ax[0].set_title("CSI Amplitude Heatmap")
plot1.set(xlabel='Frame number', ylabel='Subcarrier Index')

sns.heatmap(np.expand_dims(np.sum(csi_data.T**2, axis=1), axis=0), ax=ax[1])
plt.show()

"""