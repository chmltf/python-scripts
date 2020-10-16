import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

cal_factor = 0.00000000133
t = 1/0.535947453971072 #in s
omega = 370.412875284764 #in m/s
surface_area = 26.68 #in cm2
volume = 221.4147 #in cm3

#Import HONO and NOx data
main_data1 = pd.read_csv('Main_data.csv', skip_blank_lines = True, index_col = 'Run Number')
main_data2 = pd.read_csv('Main_data2.csv', skip_blank_lines = True, index_col = 'Run Number')
NOx_data = pd.read_csv('11_03_20_NOx_test.csv')

main_data = main_data1.merge(main_data2, how = 'outer', on = main_data1.index)
data_info = pd.DataFrame([main_data.iloc[2, :], main_data.iloc[1, :], main_data.iloc[0, :]]) #Change individual online/offline values if incorrect
datetime = data_info.iloc[2, :] + str(' ') + data_info.iloc[1, :]
datetime = pd.to_datetime(datetime[1:], infer_datetime_format=True)
data_info = data_info.append(datetime, ignore_index = True)
data_info = data_info.reset_index(drop=True)
data_info.columns = list(range(0, len(data_info.columns)))

#Drop zero rows from data
data1 = main_data.iloc[8:, :].astype('float').reset_index(drop = True)
indices1 = [(x*100)+2 for x in range(0,150)]
indices2 = [(x*100)+3 for x in range(0,150)]
bin1 = data1.loc[indices1,:].reset_index(drop = True)
bin2 = data1.loc[indices2,:].reset_index(drop = True)
zeroes_out = bin1 + bin2

#Normalize data based on laser power for each individual run
LP = main_data.iloc[7, 1:].astype('float')
zeroes_out = zeroes_out.append(LP)
zeroes_out = zeroes_out.reset_index(drop = True)
x = list(range(0, len(zeroes_out.columns)))

LP_norm = pd.DataFrame()
for a in x: 
    norm_run = zeroes_out.iloc[:150, a]/zeroes_out.iloc[150, a] 
    LP_norm[a] = norm_run

#print(LP_norm)
#LP_norm.iloc[:,34].plot()  #Make sure runs/data look correct
#plt.show()

#Background subtract
background = pd.DataFrame()
for a in x:
    background_run = LP_norm.iloc[46:79, a].mean()
    BS_run = LP_norm.iloc[85, a] - background_run
    run_object = [background_run, BS_run]
    background[a] = run_object

BG_subtracted = pd.concat([data_info, background], axis = 0, ignore_index=True)
BG_subtracted.iloc[3,:] = BG_subtracted.iloc[3,:].dt.strftime('%H:%M')

#Format dataframe with NOx, HONO, ln(NO2/NO2+HONO)
NOx_data = NOx_data[['Time', 'NO2']]
NO_NO2 = NOx_data.groupby(['Time']).mean()
BG_subtracted = BG_subtracted.transpose()
BG_subtracted.columns = ['on/off', 'Time_full', 'Date', 'Time', 'Background', 'BG_subtract']
BG_subtracted['BG_subtract'] = BG_subtracted['BG_subtract'].astype('float')
BG_subtracted = BG_subtracted.join(NO_NO2, on = 'Time')
BG_subtracted['NO2'] = (1.7671*BG_subtracted['NO2']) + 16.796

#Identify online/offline data ONLY INCLUDE GOOD DATA
BG_subtracted['description'] = ''
BG_subtracted['description'].iloc[14:21] = 'dark_30ppb_NO2'
BG_subtracted['description'].iloc[50:58] = 'dark_104ppb_NO2'
BG_subtracted['description'].iloc[65:71] = 'dark_35ppb_NO2'
BG_subtracted['description'].iloc[102:110] = 'dark_85ppb_NO2'
BG_subtracted['description'].iloc[138:145] = 'dark_103ppb_NO2'
BG_subtracted['description'].iloc[168:179] = 'dark_118ppb_NO2'
BG_subtracted['description'].iloc[203:208] = 'dark_128ppb_NO2'

BG_subtracted['description'].iloc[33:44] = 'light_35ppb_NO2'
BG_subtracted['description'].iloc[90:99] = 'light_32ppb_NO2'
BG_subtracted['description'].iloc[118:134] = 'light_62ppb_NO2'
BG_subtracted['description'].iloc[150:165] = 'light_96ppb_NO2'
BG_subtracted['description'].iloc[184:198] = 'light_108ppb_NO2'
BG_subtracted['description'].iloc[214:226] = 'light_120ppb_NO2'

BG_subtracted['offline_desc'] = ''
BG_subtracted['offline_desc'].iloc[25:29] = 'off_dark_30ppb_NO2'
BG_subtracted['offline_desc'].iloc[61:63] = 'off_dark_104ppb_NO2'
BG_subtracted['offline_desc'].iloc[80:83] = 'off_dark_35ppb_NO2'
BG_subtracted['offline_desc'].iloc[113:118] = 'off_dark_85ppb_NO2'
BG_subtracted['offline_desc'].iloc[147:150] = 'off_dark_103ppb_NO2'
BG_subtracted['offline_desc'].iloc[180:184] = 'off_dark_118ppb_NO2'
BG_subtracted['offline_desc'].iloc[208:214] = 'off_dark_128ppb_NO2'
BG_subtracted['offline_desc'].iloc[46:50] = 'off_light_35ppb_NO2'
BG_subtracted['offline_desc'].iloc[99:102] = 'off_light_32ppb_NO2'
BG_subtracted['offline_desc'].iloc[134:137] = 'off_light_62ppb_NO2'
BG_subtracted['offline_desc'].iloc[165:168] = 'off_light_96ppb_NO2'
BG_subtracted['offline_desc'].iloc[198:201] = 'off_light_62ppb_NO2'
BG_subtracted['offline_desc'].iloc[226:231] = 'off_light_96ppb_NO2'

average_offline_table = BG_subtracted.groupby('offline_desc')['BG_subtract'].mean()

print(BG_subtracted)

BG_subtracted['HONO_off_subtracted'] = ''
BG_subtracted['HONO_off_subtracted'].iloc[14:21] = BG_subtracted['BG_subtract'].iloc[14:21]- average_offline_table.loc['off_dark_30ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[50:58] = BG_subtracted['BG_subtract'].iloc[50:58] - average_offline_table.loc['off_dark_104ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[65:71] = BG_subtracted['BG_subtract'].iloc[65:71] - average_offline_table.loc['off_dark_35ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[102:110] = BG_subtracted['BG_subtract'].iloc[102:110] - average_offline_table.loc['off_dark_85ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[138:145] = BG_subtracted['BG_subtract'].iloc[138:145] - average_offline_table.loc['off_dark_103ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[168:179] = BG_subtracted['BG_subtract'].iloc[168:179] - average_offline_table.loc['off_dark_118ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[33:44] = BG_subtracted['BG_subtract'].iloc[33:44] - average_offline_table.loc['off_light_35ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[90:99] = BG_subtracted['BG_subtract'].iloc[90:99] - average_offline_table.loc['off_light_32ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[118:134] = BG_subtracted['BG_subtract'].iloc[118:134] - average_offline_table.loc['off_light_62ppb_NO2']
BG_subtracted['HONO_off_subtracted'].iloc[150:165] = BG_subtracted['BG_subtract'].iloc[150:165] - average_offline_table.loc['off_light_96ppb_NO2']


BG_subtracted['NO2'] = BG_subtracted['NO2']*(2.46E10) #convert from ppb to molec /cm3
BG_subtracted['HONO'] = BG_subtracted['BG_subtract']/cal_factor
BG_subtracted['log'] = np.log(BG_subtracted['NO2'].astype('float')/(BG_subtracted['NO2'].astype('float')+BG_subtracted['HONO'].astype('float')))
BG_subtracted['k'] = -(1/t)*BG_subtracted['log']
BG_subtracted['HONO/SA'] = BG_subtracted['HONO']/surface_area

#Summarize gamma, HONO/SA and write to Excel file
summary = BG_subtracted.groupby('description').mean()
stdev = BG_subtracted.groupby('description').std()
summary['gamma'] = 4*summary['k']/omega/100/surface_area*volume
summary['gammastdev'] = 4*stdev['k']/omega/100/surface_area*volume
with pd.ExcelWriter('experiment_data_analysis.xlsx') as writer:
    summary.to_excel(writer)

#Plot of gamma versus NO2 (ppb)
fig = plt.figure(figsize = (6, 5))
ax = fig.add_subplot(1,1,1)
ax.plot(summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'NO2']/2.46E10, summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'gamma'], 'ko', label = 'dark')
ax.plot(summary.loc['light_108ppb_NO2':, 'NO2']/2.46E10, summary.loc['light_108ppb_NO2':, 'gamma'], 'co', label = 'light')
ax.set_xlabel('NO2 (ppb)')
ax.set_ylabel('gamma')
ax.legend(loc = 'upper right')
plt.errorbar(summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'NO2']/2.46E10, summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'gamma'], 
    yerr= summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'gammastdev'], xerr = None, fmt = 'o', c = 'k')
plt.errorbar(summary.loc['light_108ppb_NO2':, 'NO2']/2.46E10, summary.loc['light_108ppb_NO2':, 'gamma'], 
    yerr= summary.loc['light_108ppb_NO2':, 'gammastdev'], xerr = None, linestyle = None, fmt = 'o', c = 'c')
plt.savefig('gamma_vs_NO2.png')

#Plot of HONO/SA versus NO2 (ppb)
fig2 = plt.figure(figsize = (6, 5))
ax2 = fig2.add_subplot(1,1,1)
ax2.plot(summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'NO2']/2.46E10, summary.loc['dark_103ppb_NO2':'dark_85ppb_NO2', 'HONO/SA'], 'ko', label = 'dark')
ax2.plot(summary.loc['light_32ppb_NO2':, 'NO2']/2.46E10, summary.loc['light_32ppb_NO2':, 'HONO/SA'], 'co', label = 'light')
ax2.set_xlabel('NO2 (ppb)')
ax2.set_ylabel('HONO/surface area')
ax2.legend(loc = 'upper right')
plt.savefig('HONOdivSA_vs_NO2.png')