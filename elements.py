import flet as ft 

from PIL import Image, ImageDraw, ImageFont 
from matplotlib import font_manager 
from fuzzywuzzy import process, fuzz 
from pathlib import Path 
import tempfile 

from typing import List 


class FontHandler(): 
    
    @classmethod 
    def find_font(cls, fontname:str): 
        fontpath = None 

        # get system fonts 
        fontpaths = font_manager.findSystemFonts(fontpaths=None, fontext='otf')
        fontnames = [Path(fp).name.lower() for fp in fontpaths] 
        res_ttf = process.extract(fontname.lower()+".ttf", fontnames, scorer=fuzz.ratio) 
        res_otf = process.extract(fontname.lower()+".otf", fontnames, scorer=fuzz.ratio) 
        for filename, score in res_ttf + res_otf: 
            if score >= 0.8: 
                # THIS IS A GOOD ENOUGH MATCH! 
                fontpath = fontpaths[fontnames.index(filename)] 
                break 
        
        if fontpath is None: 
            raise ValueError("font name {} doesn't exist in system files!".format(fontname))

        return fontpath 
    
    def __init__(self, fontname:str=None, fontpath:str=None, font:ImageFont.ImageFont=None): 
        if font is not None: 
            self.font = font 
        elif fontpath is not None: 
            self.fontpath = fontpath 
            self.font = ImageFont.truetype(fontpath) 
        else: 
            assert (fontname is not None), "In FontHandler(), either fontname:str, fontpath:str, or font:ImageFont.ImageFont must not be None!" 
            self.fontpath = FontHandler.find_font(fontname) 
            self.font = ImageFont.truetype(self.fontpath) 
    
    def font_with_size(self, fontsize): 
        return self.font.font_variant(size=fontsize) 

    def get_text_width(self, text, fontsize): 
        bbox = self.font_with_size(fontsize).getbbox(text) 
        return bbox[2] + bbox[0] 
    
    def get_text_wh(self, text, fontsize): 
        bbox = self.font_with_size(fontsize).getbbox(text) 
        print(bbox) 
        return bbox[2] + bbox[0] , bbox[3] + bbox[1] #fontsize
    


class AutoResizeText(ft.UserControl):
    def __init__(self, text, width, height, text_kwargs:dict, min_font_size=8, max_font_size=100, fonthandler=FontHandler(fontname='Arial')):
        super().__init__()
        self.text = text
        self.width = width
        self.height = height
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size

        self.fonthandler = fonthandler

        self.fontsize = self.get_largest_single_line_font_size() 

        text_wh = self.fonthandler.get_text_wh(self.text, self.fontsize)

        self.img = Image.new('RGBA', text_wh, color=(255,255,255,0)) 
        draw = ImageDraw.Draw(self.img) 
        draw.text((0,0), self.text, font=self.fonthandler.font_with_size(self.fontsize), fill=(0,0,0,255))  

        self.tf = tempfile.NamedTemporaryFile(suffix='.png', delete=False) 
        with open(self.tf.name, 'w+b') as fout: 
            self.img.save(fout)
        self.fletimg = ft.Image(self.tf.name, fit=ft.ImageFit.CONTAIN, width=text_wh[0], height=text_wh[1]) 
        
    
    def get_largest_single_line_font_size(self):
        low = self.min_font_size 
        high = self.max_font_size 
        while high-low > 1: 
            mid = (high+low)//2 
            if self.fonthandler.get_text_width(self.text, mid) > self.width or mid > self.height: 
                high = mid 
            else: 
                low = mid 
        # as long as we ever set high = mid, high is out of bounds. 
        # so, unless the ideal font size is self.min_font_size+1, the ideal font size will always be low. 

        # let's treat low as the ideal font size 
        print("FONT SIZE {}: WIDTH {}".format(low, self.fonthandler.get_text_width(self.text, low)))
        return low 

    def build(self):
        return ft.Container(
            content=self.fletimg,
            width=self.width,
            height=self.height, 
            alignment=ft.Alignment(0, 0), 
        )



    def _remove_control_recursively(self, index, control: ft.Control) -> List[ft.Control]:
        removed_controls = []

        if control.__uid in index:
            del index[control.__uid]

            for child in control._get_children():
                removed_controls.extend(self._remove_control_recursively(index, child))
            for child in control._previous_children:
                removed_controls.extend(self._remove_control_recursively(index, child))
            removed_controls.append(control)

        # delete tempfile to free memory 
        self.tf.close() 
        del self.tf 

        return removed_controls

