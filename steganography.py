from PIL import Image
import os

class Image:

    def  __init__ (self,payload_path,image_path):
        self.payload_path = payload_path
        self.carrier_image = image_path
        self.file_type = None
        self.img = None
        self.image_type = None
        self.max_image_size = 0
        self.image_mode = None
        self.payload = None
        self.common = common.Common(self.payload_to_hide)
        self.supported = ['PNG','TIFF','TIF','BMP','ICO']

        assert self.carrier_image is not None

        self.file_type = self.payload_path.split('.')[-1] if self.payload_path else None
        self.analyze_image()

    def analyze_image(self):
        try:
            self.img = Image.open(self.carrier_image)
            self.img_type = self.carrier_image.split('.')[-1]
            #size is a 2-tuple containing width and height in pixels
            self.img_size = self.img.size[1]*self.img.size[0]
            #returns a tuple containing each band; i.e. ('R', 'G', 'B')
            self.image_mode = ''.join(self.img.getbands())
        except Exception as e:
            raise Exception('Error analyzing image')

    def get_payload_size(self, file_path):
        return os.path.getsize(file_path)*8

        