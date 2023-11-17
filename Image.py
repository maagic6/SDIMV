from PIL import Image
import re
import filetype
import json
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
            self.metadata_type = 'parameters'
            self.data = {"prompt": "", 
                            "nprompt": "", 
                            "steps": "", 
                            "sampler": "", 
                            "cfg_scale": "", 
                            "seed": "", 
                            "size": "",
                            "model_hash": "",
                            "model": "",
                            "lora": ""}

            if 'parameters' in self.image.text:
                self.info = str(self.image.text['parameters'])
                self.metadata_type = 'parameters'
                self.compatible = True
    
            elif 'Comment' in self.image.text:
                self.info = json.loads(self.image.text['Comment'])
                self.metadata_type = 'comment'
                self.compatible = True

        else:
            self.compatible = False

    def getInfo(self):
        if self.metadata_type == 'parameters':
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
            lora_tags = re.findall(r'<lora:[^>]+>', self.info)
            unique_lora_tags = set(lora_tags)
            lora_string = ' '.join(unique_lora_tags)
            self.data["lora"] = lora_string
            return self.data
        if self.metadata_type == 'comment':
            self.data["prompt"] = str(self.info["prompt"])
            self.data["nprompt"] = str(self.info["uc"])
            self.data["steps"] = str(self.info["steps"])
            self.data["sampler"] = str(self.info["sampler"])
            self.data["cfg_scale"] = str(self.info["scale"])
            self.data["seed"] = str(self.info["seed"])
            self.data["size"] = str(self.info["height"])+'x'+str(self.info["width"])
            self.data["model"] = "Novel AI"
            return self.data
            
    
    def getRaw(self):
        return self.info
    
    def positivePrompt(self):
        if self.compatible == False:
            return -1
        else:
            if self.metadata_type == 'parameters':
                positive = str(re.split(r'Negative prompt: |Steps: ', self.info)[0])
                return positive
            if self.metadata_type == 'comment':
                positive = "nigger"
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