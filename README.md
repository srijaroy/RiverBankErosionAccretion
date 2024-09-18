Plugin Builder Results

RiverBankErosionAndAccretion QGIS Plugin
A QGIS plugin to calculate river bank erosion and accretion between two time periods by comparing river bank shapefiles or rasters for different years and using a study area extent.

Features
Projection Handling: Automatically checks the coordinate system of the input shapefiles and reprojects them to WGS 1984 UTM Zone 43N if necessary.
Shapefile to Raster Conversion: Converts vector shapefiles to raster format with a 30m resolution, or converts rasters back to shapefiles if rasters are used as input.
Fishnet Grid Creation: Creates a fishnet grid (30m x 30m cells) within the study area extent.
Erosion and Accretion Calculation: Computes grid-wise and stretch-wise erosion and accretion values between two time periods.
Top 20 Stretches: Saves the top 30 river stretches with the most erosion and accretion.
Requirements
QGIS (version 3.x or later)
Python (version 3.x)
GeoPandas: A powerful Python library for spatial data.
GDAL: Geospatial Data Abstraction Library.
Numpy: For numerical operations.
Shapely: For handling and analyzing geometric objects.
Install the required libraries using pip:

pip install geopandas numpy shapely gdal

Installation
Step 1: Download the Plugin
Clone or download this plugin repository and ensure that the folder is named riverbank_erosion_accretion_calculator.
Step 2: Install the Plugin
Copy the riverbank_erosion_accretion_calculator folder to your QGIS plugin directory:
Windows: C:\Users\<Your Username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
macOS: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
Step 3: Activate the Plugin in QGIS
Open QGIS, go to Plugins > Manage and Install Plugins.
In the Installed tab, search for River Bank Erosion and Accretion and activate the plugin.
Usage
Open the Plugin:

After installation, the plugin will be available in the QGIS menu under Plugins > River Bank Erosion and Accretion.
Input Data:

Year 1 Shapefile: Select the shapefile for the riverbank geometry in Year 1.
Year 2 Shapefile: Select the shapefile for the riverbank geometry in Year 2.
Study Area Shapefile: Select the study area boundary shapefile.
Output Folder: Choose the directory where the results (fishnet, grid files, etc.) will be saved.
Run the Plugin:

Click on Start to run the erosion and accretion analysis.
Results:

Fishnet: The generated fishnet grid will be saved as Fishnet.shp.
Clipped Fishnet: The fishnet clipped to the study area extent will be saved as Clipped_Fishnet.shp.
Year-specific Results:
The fishnet grids overlaid with Year 1 and Year 2 data will be saved as Fishnet_Year1.shp and Fishnet_Year2.shp.
Top 30 Stretches: The top 30 river stretches with the highest erosion and accretion will be saved as Top_30_Stretch_Erosion.shp and Top_30_Stretch_Accretion.shp.
Example Workflow
Open QGIS and load your riverbank shapefiles for Year 1, Year 2, and your study area.
Activate the River Bank Erosion and Accretion plugin.
Select the input shapefiles for Year 1, Year 2, and the study area, and choose an output folder.
Click Start to begin the analysis.
View and analyze the output files, such as the fishnet grid, erosion and accretion results, and top stretches.
Troubleshooting
Missing Dependencies:

Ensure all required Python libraries are installed. Run:
pip install geopandas numpy shapely gdal
Projection Issues:

The plugin automatically reprojects geographical coordinate system shapefiles (e.g., WGS 84) to WGS 1984 UTM Zone 43N. Make sure your shapefiles have valid CRS information.
Error Logs:

If you encounter errors during execution, check the QGIS log by going to View > Panels > Log Messages Panel.
License
This plugin is licensed under the MIT License. See the LICENSE file for details.

For more information, see the PyQGIS Developer Cookbook at:
http://www.qgis.org/pyqgis-cookbook/index.html

(C) 2011-2018 GeoApt LLC - geoapt.com
