from flask import Flask
from flask_restful import Api, Resource, reqparse
import werkzeug
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO, StringIO

UPLOAD_FOLDER = 'src/test_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

parse_image = reqparse.RequestParser()
parse_image.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

class HelloWorld(Resource):
    def get(self):
        return "Hello World"

    def post(self):
        args = parse_image.parse_args()
        image_file = args['file']

        print(image_file)

        raw_img = BytesIO(image_file.stream.read())

        test_img = plt.imread(raw_img)
        print(test_img.shape)

        return 200

api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    app.run(port=5000, debug=True)