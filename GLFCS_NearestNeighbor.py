#!/usr/bin/env python
# coding: utf-8

# ### Extract single CSV from
# ### Great Lakes Forecasting System (GLFCS) netCDFs
# -------
# #### GEOG573 Final Project
# #### Collin Roland
# #### April 14, 2021
# -------
# ##### This code takes a point of interest along the Lake Michigan-Huron shoreline, identifies the nearest cell of the Great Lakes Forecasting System netCDF's, and extracts a timeseries of variables from those netCDF's into a single CSV.

# In[1]:


import geopandas as gpd
import os
import matplotlib as mp
import contextily as ctx
import pandas as pd
import numpy as np
#os.chdir('Z:\UW_PROJECTS\Bluff\GLCFS_WAVE_DATA')
get_ipython().run_line_magic('cd', 'Z:\\\\UW_PROJECTS\\\\Bluff\\\\GLCFS_WAVE_DATA')


# In[2]:


GLFCS_points = gpd.read_file('GLFCS_Points.shp')
GLFCS_points.head()


# In[3]:


IndexPoints = GLFCS_points['geometry']
Longitude= IndexPoints.x
Latitude= IndexPoints.y
GLFCS_df = pd.DataFrame({'Name':GLFCS_points['Name'],'Longitude':Longitude,'Latitude':Latitude})
GLFCS_df.head()
GLFCS_gdf = gpd.GeoDataFrame(GLFCS_df,geometry=gpd.points_from_xy(GLFCS_df.Longitude,GLFCS_df.Latitude),crs=4326)
GLFCS_gdf.head()


# In[4]:


GLFCS_points_WebMerc=GLFCS_points.to_crs(epsg=3857)


# In[6]:

## Create point of interest
from shapely.geometry import Point
import pandas as pd
POI_df =pd.DataFrame({'Name':['LionsDen'],'Longitude':[-87.880980],'Latitude':[43.342447]})
POI_gdf = gpd.GeoDataFrame(POI_df,geometry=gpd.points_from_xy(POI_df.Longitude,POI_df.Latitude),crs=4326)
POI_gdf.set_crs(epsg=4326)
POI_gdf.crs


# In[7]:


POI_gdf_WebMerc = POI_gdf.to_crs(epsg=3857)


# In[8]:


#xlim=([-88.5, -85])
#ylim=([41.5, 46.2])
xlim=([-0.985*(10**7), -0.945*(10**7)])
ylim=([5.1*(10**6), 5.8*(10**6)])
#fig, ax = mp.pyplot.subplots(figsize=(18,10))
#fig.suptitle('GLFCS Lake MI netCDF cell centers')
#mp.pyplot.xlabel('Longitude')
#mp.pyplot.ylabel('Latitude')
ax = GLFCS_points_WebMerc.plot(marker='.', markersize=2,color='red')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ctx.add_basemap(ax, zoom=8)
POI_gdf_WebMerc.plot(ax=ax,markersize=100,marker='*',color='black')
fig = mp.pyplot.gcf()
fig.set_size_inches(24,18)
mp.pyplot.xlabel('Easting[m]')
mp.pyplot.ylabel('Northing[m]')
fig.suptitle('GLFCS Lake MI netCDF cell centers')
#mp.pyplot.axis('equal')


# In[9]:


## Find nearest neighbor to POI
from shapely.ops import nearest_points
from shapely.geometry import MultiPoint
Pts = GLFCS_gdf.geometry.unary_union
Pts.type
POI = POI_gdf.geometry.unary_union
NearestGeoms = nearest_points(POI,Pts)
nearest = GLFCS_gdf['geometry']==NearestGeoms[1]
Index = np.where(nearest)
print(Index)
NameIndex = GLFCS_gdf['Name'][Index[0]]
#b = GLFCS_gdf.loc[Index[0]].at['Name']
NameSeries = GLFCS_gdf.loc[Index[0], 'Name']
NameArray = NameSeries.to_numpy()
NameString = np.array2string(NameArray)
i_start = NameString.rindex('i=')+1
i_end = NameString.rfind(',j=')
j_start = NameString.rfind('j=')+1
j_end = NameString.rfind(']')-1
i = NameString[i_start+1:i_end]
j = NameString[j_start+1:j_end]
i=int(i)
j=int(j)
print('i=',i)
print('j=',j)


# In[10]:


## Looping over netCDF4 files
import netCDF4 as nc
import os
get_ipython().run_line_magic('pwd', '')
get_ipython().run_line_magic('cd', '.\\netCDF')
netpath = 'Z:\\UW_PROJECTS\\Bluff\\GLCFS_WAVE_DATA\\netCDF\\'

from os import walk

AllNetPaths = []
for subdir, dirs, files in os.walk(netpath):
    for file in files:
        filepath = subdir+os.sep+file
        if filepath.endswith("out1.nc"):
            AllNetPaths.append(filepath)


# In[11]:


import time
import datetime
ChristopherFarmNorth_DF = pd.DataFrame(columns=['time','waveheight','waveperiod','wavedirection','wavesetup'])
for count,value in enumerate(AllNetPaths):
    print(count)
    ds = nc.Dataset(AllNetPaths[count])
    time_var = ds.variables['time']
    dtime = nc.num2date(time_var[:],time_var.units)
    time_df = pd.DataFrame(dtime)
    time_df = time_df.rename(columns={0:'time'})
    waveheight =pd.Series(ds.variables['wvh'][:,j,i])
    waveheight_df = pd.DataFrame(waveheight)
    waveheight_df=waveheight_df.rename(columns={0:'waveheight'})
    waveperiod = pd.Series(ds.variables['wvp'][:,j,i])
    waveperiod_df = pd.DataFrame(waveperiod)
    waveperiod_df=waveperiod_df.rename(columns={0:'waveperiod'})
    wavedirection = pd.Series(ds.variables['wvd'][:,j,i])
    wavedirection_df = pd.DataFrame(wavedirection)
    wavedirection_df=wavedirection_df.rename(columns={0:'wavedirection'})
    wavesetup = pd.Series(ds.variables['eta'][:,j,i])
    wavesetup_df = pd.DataFrame(wavesetup)
    wavesetup_df=wavesetup_df.rename(columns={0:'wavesetup'})
    TempDF = pd.concat([time_df, waveheight_df, waveperiod_df, wavedirection_df, wavesetup_df],axis=1)#,columns=['time','waveheight','waveperiod','wavedirection','wavesetup'])
    ChristopherFarmNorth_DF = ChristopherFarmNorth_DF.append(TempDF, ignore_index=True)


# In[12]:


print(ChristopherFarmNorth_DF)
ChristopherFarmNorth_DF = ChristopherFarmNorth_DF.sort_values(by=['time'])
print(ChristopherFarmNorth_DF)


# In[14]:


ChristopherFarmNorth_DF.to_csv('lionsDen_CompiledWaveData.csv')


# In[80]:


import matplotlib.pyplot as plt
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

mp.rc('font', **font)

get_ipython().run_line_magic('cd', 'Z:\\UW_PROJECTS\\Bluff\\GLCFS_WAVE_DATA\\CSV_Extract')
CFWave = pd.read_csv('ChristopherFarmNorthCompiledWaveData.csv',header=0)
#print(CFWave)
CFWave.head()
CFWave['time'][0]
from datetime import datetime
CFWave['datetime'] = pd.to_datetime(CFWave['time'],format="%Y-%m-%d %H:%M:%S")


# In[90]:


import datetime
fig, ax = plt.subplots(num=4,figsize = (20,6))
plt.plot(CFWave['datetime'],CFWave['waveheight'])
plt.xlabel('Date')
plt.ylabel('Wave height [m]')
ax.set_xlim([datetime.date(2020, 12, 31), datetime.date(2021, 4, 10)])
plt.title('Christopher Farm Significant Wave Height')
plt.savefig('CFS_sigwave.png')


# In[28]:


time = np.transpose(ds.variables['time'][:])
waveheight = ds.variables['wvh'][:,j,i]
waveperiod = ds.variables['wvp'][:,j,i]
wavedirection = ds.variables['wvd'][:,j,i]
wavesetup = ds.variables['eta'][:,j,i]


# In[ ]:





# In[35]:


print(time)
print(type(time))
print(len(time))
print(np.size(time))
print(waveheight)
print(type(waveheight))
print(len(waveheight))
print(np.size(waveheight))
waveheight_ser = pd.Series(waveheight)
print(waveheight_ser)
#TempDF = pd.DataFrame([time, waveheight, waveperiod, wavedirection, wavesetup],columns=['time','waveheight','waveperiod','wavedirection','wavesetup'])


# In[22]:


print(wavesetup)
print(type(wavesetup))
SouthBeach_DF.append({'wavesetup':wavesetup},ignore_index=True)


# In[30]:


depth = ds.variables['utm'][:,j,i]
print(len(depth))


# In[37]:


lat = ds.variables['lat'][j,i]
lon = ds.variables['lon'][j,i]
print(lat)
print(lon)
print(NearestGeoms[1])


# In[20]:


print(type(ds))
dim = depth.dimensions
print(dim)
for dimobj in ds.dimensions.values():
    print(dimobj)


# In[19]:


test = ds.variables['][:,i,j]
ds.variables['ny']


# In[ ]:




