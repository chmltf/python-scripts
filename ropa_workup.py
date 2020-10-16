import pandas as pd 
import time
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.ticker as mtick

#model-specific variables
haze = [float(i) for i in range(43200, 288900, 900)] #use for model 2
#haze = [float(i) for i in range(403200, 612900, 900)]  #use for model 4
#haze =  [float(i) for i in range(43200, 93600, 900)] + [float(i) for i in range(205200, 381600, 900)] #use for model 5

start_time_unix = 1479254400 #use for model 2
#start_time_unix = 1480291200 #use for model 4
#start_time_unix = 1480809600 #use for model 5

def prod_or_dest(df):
    bool1 = df.loc[:,2].str.contains('HONO')
    bool2 = df.loc[:,1].str.contains('HONO')
    prod = df[bool1]
    dest = df[bool2]
    prod = prod.transpose()
    dest = dest.transpose()
    prod = prod.join(df.loc[0,:])
    dest = dest.join(df.loc[0,:])
    return prod, dest

def drop_nonhaze(haze_times, df):
    non_haze = []
    for times in df.loc[:,'rate']:
        if times in haze_times:
            pass
        else:
            non_haze.append(times)
    df.drop(non_haze, axis = 0, inplace = True)
    return df

def timeconverttounix(start_time, df1): #Convert from seconds past midnight on first day
    df1.loc[:,'rate'] = df1.loc[:,'rate'] + start_time
    return df1.loc[:,'rate']

def part_of_day(time_string):
    morning = ['06', '07', '08', '09', '10', '11']
    afternoon = ['12', '13', '14', '15', '16', '17']
    night = ['18', '19', '20', '21', '22', '23', '00', '01', '02', '03', '04', '05']
    morning_times = []
    afternoon_times = []
    night_times = []

    for i in morning:
        x = [f'{i}:00', f'{i}:15', f'{i}:30', f'{i}:45']
        morning_times.extend(x)

    for i in afternoon:
        x = [f'{i}:00', f'{i}:15', f'{i}:30', f'{i}:45']
        afternoon_times.extend(x)

    for i in night:
        x = [f'{i}:00', f'{i}:15', f'{i}:30', f'{i}:45']
        night_times.extend(x)
    
    time_of_day = []
    for i in time_string:    
        if i in morning_times:
            time_of_day.append('morning')
        elif i in afternoon_times:
            time_of_day.append('afternoon')
        elif i in night_times:
            time_of_day.append('night')
        else:
            time_of_day.append('do not recognize')
    return time_of_day
    
#Import the data and prep
ds = pd.read_csv('HONO_ropa_2e.csv', skip_blank_lines = True, skiprows = [0,8,18], header = None) #Update file name and skiprows
df1 = pd.DataFrame(ds)
prod, dest = prod_or_dest(df1)
#print('production equations =' , prod.loc[[1,2]])
#print('destruction equations =' , dest.loc[[1,2]])

##Production dataframe (prod) prep
prod.loc[:,0] = prod.loc[:,0].str.rstrip('.dat')
prod.columns = prod.loc[0]
prod.drop(index = [0,1,2], axis = 0, inplace = True)
prod.loc[:,'rate'] = prod.loc[:,'rate'].astype('float64')
prod.set_index('rate', inplace=True, drop = False)
#prod = drop_nonhaze(haze, prod) #include when focused on haze events
prod.drop(haze, axis = 0, inplace = True) #for dropping haze when focus is on nonhaze
prod.loc[:,'rate'] = timeconverttounix(start_time_unix, prod) #need to change number based on model run start time
prod.loc[:,'rate'] = pd.to_datetime(prod.loc[:,'rate'], unit = 's')
time_string = prod.loc[:,'rate'].dt.strftime('%H:%M')
prod = prod.join(time_string, rsuffix = '_str')
cols = ['KMT07', '1/MH/1000'] #Update based on production reactions
prod[cols] = prod[cols].apply(pd.to_numeric, errors = 'coerce')
prod.reset_index(inplace = True, drop = True)

##Destruction dataframe (dest) prep
dest.loc[:,0] = dest.loc[:,0].str.rstrip('.dat')
dest.columns = dest.loc[0]
dest.drop(index = [0,1,2], axis = 0, inplace = True)
dest.loc[:,'rate'] = dest.loc[:,'rate'].astype('float64')
dest.set_index('rate', inplace=True, drop = False)
#dest = drop_nonhaze(haze, dest) #include when focused on haze events
dest.drop(haze, axis = 0, inplace = True) #for dropping haze when focus is on nonhaze
dest.loc[:,'rate'] = timeconverttounix(start_time_unix, dest) #need to change number based on model run start time
dest.loc[:,'rate'] = pd.to_datetime(dest.loc[:,'rate'], unit = 's') #Converts to timestamp column for plotting
dest = dest.join(time_string, rsuffix = '_str') #Adds a column with the time (str) for grouping by time
cols = ['2.5D-12*EXP(260/TEMP)', 'J<7>', '2/MH'] #Update based on destruction reactions
dest[cols] = dest[cols].apply(pd.to_numeric, errors = 'coerce') 
dest.reset_index(inplace = True, drop = True)

#Plot of average hourly production and destruction of HONO
##production
bool3 = prod.loc[:,'rate_str'].str.contains(':00')
prod_on_hour = prod[bool3]
prod_by_time = prod_on_hour.groupby('rate_str')
prod_by_time_mean = prod_by_time.mean()
prod_by_time_mean.columns = ['OH + NO', 'dark heterogeneous']  #Update
#print(prod_by_time_mean)

##destruction
bool4 = dest.loc[:,'rate_str'].str.contains(':00')
dest_on_hour = dest[bool4]
dest_by_time = dest_on_hour.groupby('rate_str')
dest_by_time_mean = dest_by_time.mean()
dest_by_time_mean_neg = dest_by_time_mean*-1
dest_by_time_mean_neg.columns = ['OH + HONO', 'HONO photolysis', 'BL loss'] #Update
#print(dest_by_time_mean)
plotting_prod_and_dest = prod_by_time_mean.merge(dest_by_time_mean_neg, left_index = True, right_index = True)
#print(plotting_prod_and_dest)

##plot
ax1 = plotting_prod_and_dest.plot(kind = 'bar', figsize = (15,10), fontsize = 16, color = ['C0', 'C1', 'C2', 'C3', 'C4'])
ax1.set_ylabel('average rate', fontsize = 16)
ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
ax1.set_xlabel('time', fontsize = 16)
plt.savefig('ROPAs_RODAs_hour_2e.png')

#Bar graphs for morning, afternoon, evening -- production and destruction
morn_aft_nigh = part_of_day(prod.loc[:,'rate_str'])
morn_aft_nigh = pd.Series(morn_aft_nigh)
prod = prod.merge(morn_aft_nigh.rename('part_of_day'), left_index = True, right_index = True)
dest.drop(labels = 'rate', axis = 1, inplace = True)
dest_neg = dest *-1
prod_dest = prod.merge(dest_neg, left_index = True, right_index = True)
by_part_of_day = prod_dest.groupby('part_of_day')
by_part_of_day_mean = by_part_of_day.mean()
by_part_of_day_mean.columns = plotting_prod_and_dest.columns
by_part_of_day_mean = by_part_of_day_mean.reindex(['morning', 'afternoon', 'night'])
#print(by_part_of_day_mean)

ax2 = by_part_of_day_mean.plot(kind = 'bar', figsize = (15,10), fontsize = 16, color = ['C0', 'C1', 'C2', 'C3', 'C4'])
ax2.set_ylabel('average rate', fontsize = 16)
ax2.set_xlabel('part of day', fontsize = 16)
ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
plt.savefig('ROPAs_RODAs_part_of_day_2e.png')

#Pie charts
afternoon_mean_prod = by_part_of_day_mean.loc['afternoon', 'OH + NO':'dark heterogeneous']
morning_mean_prod = by_part_of_day_mean.loc['morning', 'OH + NO':'dark heterogeneous']
night_mean_prod = by_part_of_day_mean.loc['night', 'OH + NO':'dark heterogeneous']

afternoon_mean_dest = by_part_of_day_mean.loc['afternoon', 'OH + HONO':]*-1
morning_mean_dest = by_part_of_day_mean.loc['morning', 'OH + HONO':]*-1
night_mean_dest = by_part_of_day_mean.loc['night', 'OH + HONO':]*-1

explode = [0.1, 0.1] #Update -- later need list comprehension for # of columns
fig3 = plt.figure(figsize = (10, 5))
rcParams['font.size'] = 12
ax3 = fig3.add_axes([0.5, 0.05, 0.5, 0.5], aspect = 'equal')
ax3.pie(afternoon_mean_prod, explode = explode, autopct = '%1.1f%%', pctdistance = 1.1, colors = ['C0', 'C1'])
ax3.set_title('afternoon')
fig3.legend(prod_by_time_mean.columns, loc = 'upper center')
ax4 = fig3.add_axes([0, 0.05, 0.5, 0.5], aspect = 'equal')
ax4.set_title('morning')
ax4.pie(morning_mean_prod, explode = explode, autopct = '%1.1f%%', pctdistance = 1.1, colors = ['C0', 'C1'])
ax5 = fig3.add_axes([0.25, 0.05, 0.5, 0.5], aspect = 'equal')
ax5.pie(night_mean_prod, explode = explode, autopct = '%1.1f%%', pctdistance = 1.1, colors = ['C0', 'C1'])
ax5.set_title('night')
plt.savefig('prod_pies_2e.png')

explode2 = [0.1, 0.1, 0.1] #Update -- later need list comprehension for # of columns
fig4 = plt.figure(figsize = (10, 5))
ax6 = fig4.add_axes([0.5, 0.05, 0.5, 0.5], aspect = 'equal')
ax6.pie(afternoon_mean_dest, explode = explode2, autopct = '%1.1f%%', pctdistance = 0.9, colors = ['C2', 'C3', 'C4'])
ax6.set_title('afternoon')
ax7 = fig4.add_axes([0, 0.05, 0.5, 0.5], aspect = 'equal')
ax7.pie(morning_mean_dest, explode = explode2, autopct = '%1.1f%%', pctdistance = 0.9, colors = ['C2', 'C3', 'C4'])
ax7.set_title('morning')
ax8 = fig4.add_axes([0.25, 0.05, 0.5, 0.5], aspect = 'equal')
ax8.pie(night_mean_dest, explode = explode2, autopct = '%1.1f%%', pctdistance = 0.9, colors = ['C2', 'C3', 'C4'])
ax8.set_title('night')
fig4.legend(dest_by_time_mean_neg.columns, loc = 'upper center')
plt.savefig('dest_pies_2e.png')