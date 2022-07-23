import ee, io, requests

import numpy as np
from datetime import date, timedelta

import Modules.GAIa.constants as constants

def fetch_DWData(region_shape: ee.Geometry.Polygon, start_t:str, end_t:str):
    search_filter = ee.Filter([ee.Filter.bounds(region_shape), ee.Filter.date('2021-04-02', '2021-04-03')]);
    dwCol = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filter(search_filter)

    latest_partition = dwCol.first().toInt8()

    data_url = latest_partition.getDownloadURL({
        'bands': ['label'],
        'region': region_shape,
        'scale': constants.MAX_RES_SCALE,
        'format': 'NPY'
    })

    response = requests.get(data_url)

    if response.status_code == 200:
        raw_data = np.load(io.BytesIO(response.content))
        return raw_data
    
    return None

def clean_data(raw:np.array):
    new_data = []
    for row in raw:
        new_row = []
        for item in row:
            new_row.append(item[0])
        new_data.append(new_row)

    return np.array(new_data)

def isolate_band(sat_data : np.array, band : str): 
    data_filter = sat_data == constants.BAND2VALUE[band]
    return sat_data[data_filter] / constants.BAND2VALUE[band]

def band_area(sat_data : np.array, band : str):
    band_pixels = isolate_band(sat_data, band)
    band_pixels = band_pixels.flatten()

    return np.add.reduce(band_pixels)

def calc_approx(region_shape: ee.Geometry.Polygon):
    today = date.today()
    tolerance_past = today - timedelta(days=30)

    start_t_str = tolerance_past.strftime("%Y-%m-%d")
    end_t_str = tolerance_past.strftime("%Y-%m-%d")

    raw_array = fetch_DWData(region_shape, start_t_str, end_t_str)
    if raw_array is None: return None

    dwData = clean_data(raw_array)
    elegible_area = 0

    for band in constants.ELEGIBLE_BANDS:
        halve = 0.5 if band == 'crops' else 1
        elegible_area += band_area(dwData, band)

    elegible_area *= constants.HECT_CONVERTION_FACTOR

    carbon_calc = 13.815 * elegible_area
    car_calc = carbon_calc / 0.43

    return {'elegible_area' : elegible_area,
            'carbon_calc'   : carbon_calc,
            'car_calc'      : car_calc} 