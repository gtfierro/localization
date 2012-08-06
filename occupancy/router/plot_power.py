import pickle
import pandas
import numpy as np
from matplotlib import pyplot as plt

data = pickle.load(open('power.db'))
print 'Mean',np.mean(data)
print 'Median',np.median(data)
print 'Std Dev',np.std(data)

ts = pandas.Series(data)

ts.hist().plot()

plt.show()
