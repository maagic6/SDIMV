from PIL import Image
import re
import filetype
from io import BytesIO

class ImageProcess:
    def __init__(self, fn):
        ft = filetype.guess(fn)
        if ft == None:
            self.compatible = False
        elif ft.extension == 'png':
            self.image = Image.open(fn)
            self.image.load()
            self.compatible = False
            if 'parameters' in self.image.info:
                self.info = str(self.image.info['parameters'])
                self.compatible = True
                self.data = {"prompt": "", 
                            "nprompt": "", 
                            "steps": "", 
                            "sampler": "", 
                            "cfg_scale": "", 
                            "seed": "", 
                            "size": "",
                            "model_hash": "",
                            "model": ""}
        else:
            self.compatible = False

    def getInfo(self):
        positive = str(re.split(r'Negative prompt: |Steps: ', self.info)[0])
        self.data["prompt"]=positive
        negative = str(re.split(r'Negative prompt: |Steps: ', self.info)[1])
        self.data["nprompt"]=negative
        steps = str(re.split(r',' ,re.split(r'Steps: ', self.info)[1])[0])
        self.data["steps"]=steps
        sampler = str(re.split(r',' ,re.split(r'Sampler: ', self.info)[1])[0])
        self.data["sampler"]=sampler
        cfg_scale = str(re.split(r',' ,re.split(r'CFG scale: ', self.info)[1])[0])
        self.data["cfg_scale"]=cfg_scale
        seed = str(re.split(r',' ,re.split(r'Seed: ', self.info)[1])[0])
        self.data["seed"]=seed
        size = str(re.split(r',', re.split(r'Size: ', self.info)[1])[0])
        self.data["size"]=size
        model_hash = str(re.split(r',' ,re.split(r'Model hash: ', self.info)[1])[0])
        self.data["model_hash"]=model_hash
        model = str(re.split(r',' ,re.split(r'Model: ', self.info)[1])[0])
        self.data["model"]=model
        return self.data
    
    def getRaw(self):
        return self.info
    
    def positivePrompt(self):
        if self.compatible == False:
            return -1
        else:
            positive = str(re.split(r'Negative prompt: |Steps: ', self.info)[0])
            return positive

    def negativePrompt(self):
        if self.compatible == False:
            return -1    
        else:
            negative = str(re.split(r'Negative prompt: |Steps: ', self.info)[1])
            return negative

    def configSettings(self):
        if self.compatible == False:
            return -1
        else:
            config = str(re.split('Steps:', self.info)[1])
            return('Steps: ' + config)
    
    def readBytes(self):
        if self.compatible == False:
            return -1
        else:
            image_byte = BytesIO()
            self.image.save(image_byte, format='JPEG')
            image_byte = image_byte.getvalue()
            return image_byte
    
    def compress(self):
        self.image.save("image-file-compressed","JPEG",optimize=True,quality=1)