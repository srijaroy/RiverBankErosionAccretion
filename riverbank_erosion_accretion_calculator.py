# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RiverBankErosionAndAccretion
 A QGIS plugin to calculate river erosion and accretion between two time periods.
 ***************************************************************************/
"""

import os
import geopandas as gpd
import numpy as np
from shapely.geometry import box
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog, QDialog
from qgis.PyQt import QtWidgets
from .riverbank_erosion_accretion_calculator_dialog import Ui_RiverBankErosionAndAccretionDialogBase

class RiverBankErosionAndAccretion:
    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = None
        self.actions = []
        self.menu = self.tr(u"&River Bank Erosion and Accretion")

    def tr(self, message):
        """Get the translation for a string using QGIS translation API."""
        return QCoreApplication.translate('RiverBankErosionAndAccretion', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/riverbank_erosion_accretion_calculator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr('Calculate River Erosion and Accretion'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu('&River Bank Erosion and Accretion', action)
            self.iface.removeToolBarIcon(action)
        self.actions.clear()

    def run(self):
        """Run the plugin dialog."""
        if self.dlg is None:
            self.dlg = QDialog()
            self.ui = Ui_RiverBankErosionAndAccretionDialogBase()
            self.ui.setupUi(self.dlg)

            # Connect UI elements to methods
            self.ui.mMapLayerComboBox.layerChanged.connect(self.select_year1_shapefile)
            self.ui.mMapLayerComboBox_2.layerChanged.connect(self.select_year2_shapefile)
            self.ui.mMapLayerComboBox_3.layerChanged.connect(self.select_study_area_shapefile)
            self.ui.startButton.clicked.connect(self.run_analysis)
            self.ui.pushButton.clicked.connect(self.select_output_folder)

        self.dlg.show()

    def select_year1_shapefile(self, layer):
        self.year1_shapefile = layer

    def select_year2_shapefile(self, layer):
        self.year2_shapefile = layer

    def select_study_area_shapefile(self, layer):
        self.study_area_shapefile = layer

    def select_output_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self.dlg, "Select Output Folder")
        if folder_name:
            self.ui.lineEdit.setText(folder_name)

    def run_analysis(self):
        """Main analysis workflow triggered by the Start button."""
        year1_shapefile = self.year1_shapefile
        year2_shapefile = self.year2_shapefile
        study_area = self.study_area_shapefile
        output_folder = self.ui.lineEdit.text()

        # Check inputs
        if not all([year1_shapefile, year2_shapefile, study_area, output_folder]):
            QMessageBox.warning(self.dlg, "Input Error", "Please fill in all fields!")
            return

        # Run the fishnet creation process
        self.process_fishnet(study_area, year1_shapefile, year2_shapefile, output_folder)

    def process_fishnet(self, study_area, year1_shapefile, year2_shapefile, output_folder):
        """Create a fishnet within the bounds of the study area and save it."""
        study_area_gdf = gpd.read_file(study_area.source())

        # Check if CRS is geographic, and reproject to UTM if needed
        if study_area_gdf.crs.is_geographic:
            utm_crs = self.get_utm_crs(study_area_gdf)
            study_area_gdf = study_area_gdf.to_crs(utm_crs)

        # Create a fishnet grid of 30m x 30m within the bounds of the study area
        fishnet_gdf = self.create_fishnet_grid(study_area_gdf.total_bounds, 30, study_area_gdf.crs, output_folder)

        # Clip the fishnet grid with the study area
        clipped_fishnet = self.clip_fishnet(fishnet_gdf, study_area_gdf, output_folder)

        # Number the grids
        clipped_fishnet['grid_id'] = range(1, len(clipped_fishnet) + 1)

        # Save the numbered fishnet
        clipped_fishnet_output_path = os.path.join(output_folder, 'Numbered_Clipped_Fishnet.shp')
        clipped_fishnet.to_file(clipped_fishnet_output_path)

        # Process Year 1 and Year 2
        self.process_year_data(clipped_fishnet, year1_shapefile, year2_shapefile, output_folder)

    def get_utm_crs(self, gdf):
        """Get UTM CRS based on the centroid of the GeoDataFrame."""
        centroid = gdf.to_crs(epsg=4326).geometry.centroid.iloc[0]
        lon = centroid.x
        lat = centroid.y
        utm_zone = int((lon + 180) / 6) + 1
        if lat >= 0:
            epsg_code = 32600 + utm_zone  # Northern Hemisphere
        else:
            epsg_code = 32700 + utm_zone  # Southern Hemisphere
        return f"EPSG:{epsg_code}"

    def create_fishnet_grid(self, bounds, cell_size, crs, output_folder):
        """Create a fishnet grid with the specified resolution and save as a shapefile."""
        minx, miny, maxx, maxy = bounds
        x_coords = np.arange(minx, maxx, cell_size)  # Create x-coordinates at 30m intervals
        y_coords = np.arange(miny, maxy, cell_size)  # Create y-coordinates at 30m intervals

        polygons = [box(x, y, x + cell_size, y + cell_size) for x in x_coords for y in y_coords]  # Create 30m x 30m cells

        fishnet = gpd.GeoDataFrame({'geometry': polygons}, crs=crs)
        fishnet_output_path = os.path.join(output_folder, 'Fishnet.shp')
        fishnet.to_file(fishnet_output_path)

        return fishnet

    def clip_fishnet(self, fishnet_gdf, study_area_gdf, output_folder):
        """Clip the fishnet grid with the study area GeoDataFrame."""
        if fishnet_gdf.crs != study_area_gdf.crs:
            study_area_gdf = study_area_gdf.to_crs(fishnet_gdf.crs)

        clipped_fishnet = gpd.clip(fishnet_gdf, study_area_gdf)
        clipped_fishnet_output_path = os.path.join(output_folder, 'Clipped_Fishnet.shp')
        clipped_fishnet.to_file(clipped_fishnet_output_path)

        return clipped_fishnet

    def process_year_data(self, fishnet_gdf, year1_layer, year2_layer, output_folder):
        """Overlay fishnet with year 1 and year 2 layers, calculate area, and save results."""
        year1_gdf = gpd.read_file(year1_layer.source())
        year2_gdf = gpd.read_file(year2_layer.source())

        # Ensure CRS matches
        year1_gdf = year1_gdf.to_crs(fishnet_gdf.crs)
        year2_gdf = year2_gdf.to_crs(fishnet_gdf.crs)

        # Overlay fishnet with Year 1 and Year 2
        fishnet_year1 = self.overlay_with_year(fishnet_gdf, year1_gdf, os.path.join(output_folder, 'Fishnet_Year1.shp'))
        fishnet_year2 = self.overlay_with_year(fishnet_gdf, year2_gdf, os.path.join(output_folder, 'Fishnet_Year2.shp'))

        # Calculate unchanged area by intersecting year 1 and year 2
        unchanged_area = self.calculate_unchanged_area(fishnet_year1, fishnet_year2, os.path.join(output_folder, 'Unchanged_Area.shp'))

        # Calculate erosion and accretion
        self.calculate_erosion_accretion(fishnet_year1, fishnet_year2, unchanged_area, output_folder)

    def overlay_with_year(self, fishnet, year_gdf, output_file):
        """Overlay fishnet with year data and calculate area."""
        overlay_result = gpd.overlay(fishnet, year_gdf, how='intersection')
        overlay_result['area'] = overlay_result.geometry.area

        # Save the result
        overlay_result.to_file(output_file)
        return overlay_result

    def calculate_unchanged_area(self, fishnet_year1, fishnet_year2, output_file):
        """Calculate unchanged area by intersecting year 1 and year 2 fishnets."""
        unchanged_area = gpd.overlay(fishnet_year1, fishnet_year2, how='intersection')
        unchanged_area['unchanged_area'] = unchanged_area.geometry.area  # Calculate unchanged area
        unchanged_area.to_file(output_file)
        return unchanged_area

    def calculate_erosion_accretion(self, fishnet_year1, fishnet_year2, unchanged_area, output_folder):
        """Calculate erosion and accretion based on year 1, year 2, and unchanged areas."""
       
        # Erosion = Year 2 river area - unchanged area (where river moved away)
        fishnet_year1['erosion'] = fishnet_year2['area'] - unchanged_area['unchanged_area']

        # Accretion = Year 1 river area - unchanged area (where river moved in)
        fishnet_year2['accretion'] = fishnet_year1['area'] - unchanged_area['unchanged_area']

        # Convert erosion and accretion to square kilometers
        fishnet_year1['erosion_km2'] = fishnet_year1['erosion'] / 1e6
        fishnet_year2['accretion_km2'] = fishnet_year2['accretion'] / 1e6

        # Combine grids into 3 km stretches (combine 300 grids)
        self.calculate_stretch_erosion_accretion(fishnet_year1, fishnet_year2, output_folder)

    def calculate_stretch_erosion_accretion(self, fishnet_year1, fishnet_year2, output_folder):
        """Calculate erosion and accretion for 3 km stretches (combine 300 grids)."""
        # Group grids by 3 km stretches (300 grids)
        fishnet_year1['stretch_id'] = (np.floor(fishnet_year1['grid_id'] / 100)).astype(int)
        fishnet_year2['stretch_id'] = (np.floor(fishnet_year2['grid_id'] / 100)).astype(int)

        # Dissolve by stretch_id and calculate total erosion and accretion
        fishnet_year1_stretch = fishnet_year1.dissolve(by='stretch_id', aggfunc={'erosion_km2': 'sum'})
        fishnet_year2_stretch = fishnet_year2.dissolve(by='stretch_id', aggfunc={'accretion_km2': 'sum'})

        # Save top 30 stretches
        self.save_top_stretch_erosion_accretion(fishnet_year1_stretch, fishnet_year2_stretch, output_folder)

    def save_top_stretch_erosion_accretion(self, fishnet_year1_stretch, fishnet_year2_stretch, output_folder):
        """Save the top 30 stretches with maximum erosion and accretion."""
        # Get the top 20 stretches with the maximum erosion
        top_20_stretch_erosion = fishnet_year1_stretch.nlargest(30, 'erosion_km2')
        top_20_stretch_erosion.to_file(os.path.join(output_folder, 'Top_30_Stretch_Erosion.shp'))

        # Get the top 20 stretches with the maximum accretion
        top_20_stretch_accretion = fishnet_year2_stretch.nlargest(30, 'accretion_km2')
        top_20_stretch_accretion.to_file(os.path.join(output_folder, 'Top_30_Stretch_Accretion.shp'))

        print("Top 20 stretches of erosion and accretion saved.")
