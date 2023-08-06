import time
import re

with open('active_sta/serial.csv', 'r') as file:
    while True:
        time.sleep(0.01)
        csi_line = file.readline()
        components = re.findall('\[.*\]', csi_line)
        if len(components) == 0:
            continue
        components = re.sub('(\[)|(\])', '', components[0]).split()
        components = list(map(int, components))
        print(components)
