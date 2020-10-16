# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 16:38:19 2020

@author: Lauren-Nizkorodov
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
from datetime import datetime
import matplotlib.ticker as mtick

#Import the data
ds = pd.read_csv('C:\\airprow\model_4.csv')

#Format the data
ds.columns = ['Time', 'observed_HONO', 'gas phase', 'emissions', 'heterogeneous', 'illuminated heterogeneous', 'particulate nitrate'] 
ds['Time'] = pd.to_datetime(ds['Time']) #Converts time to a timestamp list
#Haze = ds.loc[:272, 'Time':'HONO_2he']
#Nonhaze = ds.loc[273:, 'Time':'HONO_24n']

#Make a blank figure
fig = plt.figure(figsize= (10,5))
ax = fig.add_subplot(1,1,1) 

#Add data to your figure
ax.plot(ds['Time'], ds['observed_HONO'], '-', label = 'Observed')
ax.plot(ds['Time'], ds['gas phase'], '-', label = 'Gas phase')
ax.plot(ds['Time'], ds['emissions'], '-', label = 'Emissions')
ax.plot(ds['Time'], ds['heterogeneous'], '-', label = 'Heterogeneous')
ax.plot(ds['Time'], ds['illuminated heterogeneous'], '-', label = 'Illuminated heterogeneous')
ax.plot(ds['Time'], ds['particulate nitrate'], '-', label = 'Particulate nitrate')

#Plot formatting
ax.set_ylabel(u'HONO (molec /cm\u00b3)')
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
ax.legend(loc = 'upper left')
plt.gcf().autofmt_xdate()
date_format = mpl_dates.DateFormatter('%d %b %Y, %H:%M')
plt.gca().xaxis.set_major_formatter(date_format)
#ax.axvspan(datetime(2016, 11, 16, 12), datetime(2016,11,19,8), alpha=0.2, color='orange', label = 'haze') #shows haze period, 

#Display your plot!
plt.savefig('model_4s.png')
#plt.show()