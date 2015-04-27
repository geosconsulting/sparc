__author__ = 'fabio.lana'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
ogr.UseExceptions()

pkl_file = r"C:\data\tools\sparc\conflicts\SPARC_GDELT\test_data\results\SouthSudan.pickle"
pkl_df = pd.io.pickle.read_pickle(pkl_file)








