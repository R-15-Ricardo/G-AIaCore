from flask import Flask
from flask import request as flaskreq
from flask_restful import Api, Resource, reqparse
import requests
import werkzeug

import ee

from Modules.GAIa.constants import CARBON_RATE as GAIA_CARBON_RATE
import Modules.GAIa.calc as GAIa

#hola

app = Flask(__name__)
api = Api(app)

parse_image = reqparse.RequestParser()
parse_image.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

class GAIAPort(Resource):
    def get(self, req_id):
        return "Hola :D"

    def put(self, req_id):
        print(req_id)

        current_geoJS = flaskreq.json
        poligon_coordinates = current_geoJS['features'][0]['geometry']['coordinates']

        print(poligon_coordinates)
        loaded_polygon = ee.Geometry.Polygon(poligon_coordinates,None,False)

        scan_results = GAIa.calc_approx(loaded_polygon)

        dollar_res = requests.get('https://v6.exchangerate-api.com/v6/5e3481394f866fbf4bf07bac/latest/USD')
        now_mxn_rate = (dollar_res.json())['conversion_rates']['MXN']

        nasdaq_current_equiv = scan_results['carbon_calc']*now_mxn_rate*GAIA_CARBON_RATE

        scan_results.update({'nasdaq_current_equiv' : nasdaq_current_equiv})

        return scan_results

api.add_resource(GAIAPort, "/<int:req_id>")

if __name__ == "__main__":
    ee.Initialize()
    app.run(port=5000, debug=False)