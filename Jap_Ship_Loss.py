
#Shows the loss of Japanese war ships throughout the duration of WWII
#Use python3 Jap_Ship_Loss.py to run



from pickletools import long1
import numpy as np 
import pandas as pd 
import geopandas as gpd 
import rasterio
import rasterio.plot
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import Point, Polygon
from IPython.display import display



#Specify FFMpeg directory
mpl.rcParams['animation.ffmpeg_path'] = r'/Users/Revilo/Desktop/ffmpeg'

#Import data and verify its imported in console
data = pd.read_csv('Jap_Ship_Mod.csv')
display(data.head())

#Import the shapefile map
earth_land = gpd.read_file('earth_ocean/ne_110m_ocean.shp')

#Set coordinates and data
crs = {'init': 'epsg:4326'}
geometry = [Point(xy) for xy in zip(data['Longitude'], data['Latitude'])]
geo_data = gpd.GeoDataFrame(data, geometry = geometry, crs = crs)

#Change coordinates to match epsg 3832 projection
geo_data.to_crs(epsg=3832, inplace=True)

#Change projection to a Pacific centric one (epsg 3832)
earth_land = earth_land.to_crs("epsg:3832")

#Set a crs value equal to the projection used for the shapefile transform
dst_crs = earth_land.crs


#Convert raster into appropriate crs projection 
with rasterio.open('raster/HYP_LR_SR_OB_DR.tif') as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    with rasterio.open('reprojected_raster.tif', 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)

#Set reprojected raster 
raster = rasterio.open('reprojected_raster.tif')
#
#
#End of preperations



#Beginning of plotting
#
#
#Establish figure and size
fig, ax = plt.subplots(figsize=(10,5))

ax.set_axis_off()

#Turn off axis ticks
plt.xticks([])
plt.yticks([])

#Size x and y labels to match data range (In meters after reprojection)
plt.xlim(-7.92e+06, 9.94e+06)
plt.ylim(-3.41e+06, 6.25e+06)

#Break POINT geometry column into its respective longitude and latitude
#Used for placing circle around current ship on map
geo_data['lon'] = geo_data['geometry'].x
geo_data['lat'] = geo_data['geometry'].y

#Set initial title of graph before first ship plotted
ax.set_title('Japanese Warship Loss WWII', fontsize=15, fontweight='bold')

#Add labels to plot for years 
fourone_patch = mpatches.Patch(color='purple', label='1941')
fourtwo_patch = mpatches.Patch(color='deeppink', label='1942')
fourthree_patch = mpatches.Patch(color='blue', label='1943')
fourfour_patch = mpatches.Patch(color='red', label='1944')
fourfive_patch = mpatches.Patch(color='black', label='1945')
plt.legend(handles=[fourone_patch, fourtwo_patch, fourthree_patch, fourfour_patch, fourfive_patch], loc ="upper left")

#Set annotations for ship loss, ship type, and date
annotatedate = ax.annotate('Date:' + geo_data.loc[i]['Date'], xy = (-7.65e+06, -2.50e+06))
annotatetotal = ax.annotate('Total ships lost: ' + str(i), xy = (-7.65e+06, -2.90e+06)) 
annotateship = ax.annotate('Ship lost: ' + geo_data.loc[i]['Ship Type'] + ' ' + geo_data.loc[i]['Type of Vessel'], xy = (-7.65e+06, -3.30e+06))
annotatename = ax.annotate('O', xy = ((geo_data.loc[i]['lon'] - 0.13e+06), (geo_data.loc[i]['lat'] - 0.15e+06)))


#comment out raterio and re-enable earth_land for increased performance 
#at a loss of visual fidelity 
rasterio.plot.show(raster,ax=ax)
#earth_land.plot(ax=ax, alpha=1, facecolor ='none', edgecolor='black')



#animation loop for graphing (i is increased by 1 each time)
def animate(i):

    #Update annotations
    #Date
    annotatedate.xy = (-7.65e+06, -2.50e+06)
    annotatedate.set_text(geo_data.loc[i]['Date']) 
    #Total ships lost
    annotatetotal.xy = (-7.65e+06, -2.90e+06)
    annotatetotal.set_text('Total ships lost:' + str(i+1))
    #Ship lost info
    annotateship.xy = (-7.65e+06, -3.30e+06)
    annotateship.set_text('Ship lost: ' + geo_data.loc[i]['Ship Type'] + ' ' + geo_data.loc[i]['Type of Vessel'])
    #Put O on map where current ship is 
    annotatename.set_position(((geo_data.loc[i]['lon'] - 0.13e+06), (geo_data.loc[i]['lat'] - 0.15e+06)))
    annotatename.xy = (geo_data.loc[i]['lon'], geo_data.loc[i]['lat'])
    annotatename.set_text('O')
    
    #If plt.show() is off, can print i to know completion status of animation (goes to 686)
    #print(i)
    
    #Set today's date and convert it to a 2 number year (ex 12/12/1941 = 41)
    date_year = geo_data.loc[[i], 'Date']
    date_year = (date_year).values
    date_year = date_year.take(0)
    date_year = int(date_year[-2:])

    #if ship was destroyed in 1941 color it purple
    if 41 <= date_year < 42:
        geo_data.loc[[i], 'geometry'].plot(ax=ax, alpha=1, markersize=3, color = 'purple', label = '1941')

    #if ship was destroyed in 1942 color it deep pink
    if 42 <= date_year < 43:
        geo_data.loc[[i], 'geometry'].plot(ax=ax, alpha=1, markersize=3, color = 'deeppink', label = '1942')
        
    #if ship was destroyed in 1943 color it blue
    if 43 <= date_year < 44:
        geo_data.loc[[i], 'geometry'].plot(ax=ax, alpha=1, markersize=3, color = 'blue', label = '1943')

    #if ship was destroyed in 1944 color it red
    if 44 <= date_year < 45:
        geo_data.loc[[i], 'geometry'].plot(ax=ax, alpha=1, markersize=3, color = 'red', label = '1944')

    #if ship was destroyed in 1945 color it black
    if 45 <= date_year:
        geo_data.loc[[i], 'geometry'].plot(ax=ax, alpha=1, markersize=3, color = 'black', label = '1945')

    
    return animate

#frames is number of data entries, interval is millisecond value for animation (686 full frames)
ani = animation.FuncAnimation(fig, animate, frames = 686, interval= 3000, repeat = False)

#For live viewing as program runs remove # from plt.show()
#plt.show()
plt.close()

#To save animation as video (FFMpegWriter has to have its executable directory specified)
writer = animation.FFMpegWriter(fps=1)
ani.save("Jap_ship.mp4", dpi=300, writer=writer)


