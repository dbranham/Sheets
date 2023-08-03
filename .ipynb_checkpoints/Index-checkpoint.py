#imports
import pandas as pd
import numpy as np
import seaborn as sns

import librosa
import librosa.display
from IPython.display import display
from itertools import cycle

import matplotlib.pyplot as plt
from glob import glob


#visual color themes
sns.set_theme(style= "white", palette=None)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])

file_paths = glob.glob("*.mp3")
print(file_paths)