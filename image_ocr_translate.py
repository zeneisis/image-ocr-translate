from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from winocr import recognize_pil_sync
from deep_translator import GoogleTranslator
import json 
import timeit

def get_texts():
    text_list = []
    for text_data in collect_data["lines"]:
        text_list.append(text_data["text"])
    return text_list

def get_text_positions():
    position_list = []
    for text_data in collect_data["lines"]:
        for bounding_rect in text_data["words"][0:1]:
            x = int(bounding_rect["bounding_rect"]["x"])
            y = int(bounding_rect["bounding_rect"]["y"])
            positions = (x, y)
            position_list.append(positions)
    return position_list

def translate(text):
    #Must setting proxy if you don't want get limit translate per day
    proxies = {
        "https": "put_your_proxy_here",  # example: 34.195.196.27:8080
        "http": "put_your_proxy_here" 
        
    }
    trans_set = GoogleTranslator(source='auto', target='vi', proxies = proxies) #Change target to what language you want translate
    translated_text = (f'{trans_set.translate(text)}')
    return translated_text

#set text style for drawing 
myFont = ImageFont.truetype('bahnschrift.ttf', 25)
fill_color = (255, 255, 255)
stroke_color = (0, 0, 0)

start_time = timeit.default_timer() #start processing time counter

pil_img = Image.open('img_in.png')
draw = ImageDraw.Draw(pil_img)
data = json.dumps(recognize_pil_sync(pil_img, "ja-JP")) #Change language same with input image for better performance (en-US is fastest)
collect_data = json.loads(data)

#using concurrent.furtures to increase translate speed
with ThreadPoolExecutor(max_workers=len(get_texts())+1) as excutor:
    result = list(excutor.map(translate, get_texts()))
    for text, position in zip(result, get_text_positions()):
        left, top, right, bottom = draw.textbbox(position, text, font=myFont)
        draw.rectangle((left-5, top-5, right+5, bottom+5), fill = 'black')
        draw.text(position, text, font=myFont, fill = 'white')

pil_img.save('img_out.png')

elapsed_time = timeit.default_timer() - start_time
print(f'Elapsed time: {elapsed_time:.6f} seconds') #end processing time counter
