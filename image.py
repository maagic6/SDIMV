from PIL import Image, ExifTags
import re, filetype, json
from mutagen.mp4 import MP4

class imageProcess:
    def __init__(self, fn):
        ft = filetype.guess(fn)
        self.data = {"prompt": "", 
                    "negative_prompt": "", 
                    "steps": "", 
                    "sampler": "", 
                    "cfg_scale": "", 
                    "seed": "", 
                    "size": "",
                    "model_hash": "",
                    "model": "",
                    "lora": ""}
        if ft == None:
            self.compatible = False
        elif ft.extension in ['png']:
            self.image = Image.open(fn)
            self.compatible = False

            if 'parameters' in self.image.info: #web ui
                self.info = str(self.image.info['parameters'])
                self.metadataType = 'parameters'
                self.compatible = True
                self.image.close()
                del self.image
            elif 'Comment' in self.image.info: #novelai
                self.info = json.loads(self.image.info['Comment'])
                self.metadataType = 'comment'
                self.compatible = True
                self.image.close()
                self.image = None
                del self.image
            elif 'prompt' in self.image.info: #comfyui
                self.info = json.loads(self.image.info['prompt'])
                self.metadataType = 'prompt'
                self.compatible = True
                self.image.close()
                self.image = None
                del self.image
        elif ft.extension == 'jpg':
            self.image = Image.open(fn)
            self.compatible = False
            exif_data = self.image._getexif()

            if exif_data is not None:
                for tag, value in ExifTags.TAGS.items():
                    if tag in exif_data:
                        if ExifTags.TAGS[tag] == "UserComment":
                            user_comment = exif_data[tag]
                            user_comment_unicode = user_comment.decode("utf-8") #decode
                            user_comment_unicode_sanitized = user_comment_unicode.replace('UNICODE', '').replace('\x00', '')
                            self.info = user_comment_unicode_sanitized
                            self.metadataType = 'parameters'
                            self.compatible = True
                        
            self.image.close()
            self.image = None
            del self.image
        elif ft.extension in ['mp4']:
            video = MP4(fn)
            self.data = {}
            try:
                if '\xa9cmt' in video.tags:
                    metadata = video.tags['\xa9cmt']
                    self.metadataType = "video"
                    self.info = json.loads(metadata[0])
                    self.compatible = True
                    video = None
                    del video
                else:
                    self.compatible = False
                    video = None
                    del video
            except:
                self.compatible = False
                video = None
                del video
        else:
            self.compatible = False
    
    def findKeyName(self, data, keys):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == keys:
                    return value
                result = self.findKeyName(value, keys)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.findKeyName(item, keys)
                if result is not None:
                    return result   
        return None

    def getInfo(self): # messy
        if self.metadataType == 'parameters':
            matches = re.findall(r'([^:,]+): ([^,]+)', self.info.replace('\n', ','))
            for match in matches:
                key = match[0].strip().lower().replace(' ', '_')
                value = match[1].strip()
                self.data[key] = value
            try:
                positive = str(re.split(r'Negative prompt: |Steps: ', self.info)[0])
            except:
                positive = ""
            self.data["prompt"]=positive
            try:
                negative = str(re.split(r'Negative prompt: ', self.info, maxsplit=1)[1].split('Steps:')[0].strip())
            except:
                negative = ""
            self.data["negative_prompt"] = negative
            loraTags = re.findall(r'<lora:[^>]+>', self.info)
            uniqueLoraTags = set(loraTags)
            loraString = ' '.join(uniqueLoraTags)
            self.data["lora"] = loraString
            if "model" not in self.data:
                self.data["model"] = ""
            return self.data
        if self.metadataType == 'comment': #novelai
            self.data["prompt"] = str(self.info["prompt"])
            self.data["negative_prompt"] = str(self.info["uc"])
            self.data["steps"] = str(self.info["steps"])
            self.data["sampler"] = str(self.info["sampler"])
            self.data["cfg_scale"] = str(self.info["scale"])
            self.data["seed"] = str(self.info["seed"])
            self.data["size"] = str(self.info["height"])+'x'+str(self.info["width"])
            self.data["model"] = ''
            self.data["model_hash"] = ''
            loraTags = re.findall(r'<lora:[^>]+>', str(self.info))
            uniqueLoraTags = set(loraTags)
            loraString = ' '.join(uniqueLoraTags)
            self.data["lora"] = loraString
            return self.data
        if self.metadataType == 'video':
            promptKey = self.findKeyName(data=self.info, keys="positive")[0]
            self.data["prompt"] = self.info.get('prompt', {}).get(f'{promptKey}', {}).get('inputs', {}).get('text')
            self.data["negative_prompt"] = self.info.get('prompt', {}).get('320', {}).get('inputs', {}).get('text')
            self.data["steps"] = self.info.get('prompt', {}).get('528', {}).get('inputs', {}).get('steps')
            self.data["sampler"] = self.info.get('prompt', {}).get('528', {}).get('inputs', {}).get('sampler_name')
            self.data["cfg_scale"] = self.info.get('prompt', {}).get('528', {}).get('inputs', {}).get('cfg')
            self.data["seed"] = self.info.get('prompt', {}).get('528', {}).get('inputs', {}).get('seed')
            self.data["size"] = str(self.info.get('prompt', {}).get('539', {}).get('inputs', {}).get('height'))+'x'+str(self.info.get('prompt', {}).get('539', {}).get('inputs', {}).get('width'))
            self.data["model"] = self.info.get('prompt', {}).get('513', {}).get('inputs', {}).get('model_name')
            self.data["model_hash"] = ""
            self.data["lora"] = ""
            return self.data
        if self.metadataType == 'prompt':
            promptKey = self.findKeyName(data=self.info, keys="positive")
            if type(promptKey) == list:
                promptKey = self.findKeyName(data=self.info, keys="positive")[0]
                if "pre_text" in self.info.get(f'{promptKey}', {}).get('inputs', {}):
                    self.data["prompt"] = re.search(r'([^--]+)--neg', str(self.info[f'{promptKey}']['inputs']['pre_text'])).group(1)
                else:
                    self.data["prompt"] = self.info[f'{promptKey}']['inputs'].get('text', None)
            else:
                self.data["prompt"] = promptKey
            negativePromptKey = self.findKeyName(data=self.info, keys="negative")
            if type(negativePromptKey) == list:
                negativePromptKey = self.findKeyName(data=self.info, keys="negative")[0]
                if "pre_text" in self.info.get(f'{promptKey}', {}).get('inputs', {}):
                    self.data["negative_prompt"] = re.search(r'--neg\s*([^\n]+)', str(self.info[f'{negativePromptKey}']['inputs']['pre_text'])).group(1).strip() #I hate ComfyUI
                else:
                    self.data["negative_prompt"] = self.info[f'{negativePromptKey}']['inputs'].get('text', None)
                    #self.data["negative_prompt"] = type(negativePromptKey)
            else:
                self.data["negative_prompt"] = negativePromptKey
            self.data["steps"] = self.findKeyName(data=self.info, keys="steps")
            self.data["sampler"] = self.findKeyName(data=self.info, keys="sampler_name")
            self.data["cfg_scale"] = self.findKeyName(data=self.info, keys="cfg")
            self.data["seed"] = self.findKeyName(data=self.info, keys="noise_seed") or self.findKeyName(data=self.info, keys="seed")
            self.data["size"] = self.findKeyName(data=self.info, keys="resolution")
            self.data["model"] = self.findKeyName(data=self.info, keys="ckpt_name")
            self.data["model_hash"] = ''
            self.data["lora"] = ''
            return self.data

    def save_metadata(self):
        #todo
        pass
    
    def getRaw(self):
        return self.info
    
    def positivePrompt(self):
        if self.compatible == False:
            return -1
        else:
            if self.metadataType == 'parameters':
                positive = ""
                return positive
            if self.metadataType == 'comment':
                positive = ""
                return positive

    '''def negativePrompt(self):
        if self.compatible == False:
            return -1    
        else:
            negative = ""
            return negative'''
