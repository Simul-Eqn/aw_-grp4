# to help with colour converesion 
from colorutils import Color 


# Tableau 10 Colour Palette, from https://gist.github.com/leblancfg/b145a966108be05b4a387789c4f9f474 
blue = Color(hex='#5778a4') 
orange = Color(hex='#e49444')
red = Color(hex='#d1615d')
teal = Color(hex='#85b6b2')
green = Color(hex='#6a9f58')
yellow = Color(hex='#e7ca60')
purple = Color(hex='#a87c9f')
pink = Color(hex='#f1a2a9')
brown = Color(hex='#967662')
grey = Color(hex='#b8b0ac')

# own additions
darkgrey = Color(hex='#474442')
midgrey = Color(hex='#807a77')
white = Color(hex='#ffffff')



# for compatibility with flet things 
import flet as ft 
import numpy as np 

def clip_hsv_vals(arr): 
    arr = np.where(arr>0, arr, 0) # >= 0 
    maxs = np.array([256, 1, 1])
    return np.where(arr<maxs, arr, maxs) # <= maxs 

def hex_to_adjusted_hsv(colour, hsv_trans): 
    if isinstance(colour, str): 
        col = Color(hex=colour) 
    elif isinstance(colour, Color): 
        col = colour 
    else: 
         raise ValueError("'colour' inputted to hex_adjust_hsv is not 'str' or 'Color'!")

    return clip_hsv_vals(np.array(col.hsv)+np.array(hsv_trans)) 


def buttonColsFor(base_col, hovered_hsv_trans=[0,0,-0.1], disabled_hsv_trans = [0, -0.2, +0.3]): 
    
    coldict = {} 
    coldict[ft.ControlState.DEFAULT] = base_col.hex 

    coldict[ft.ControlState.HOVERED] = Color(hsv=hex_to_adjusted_hsv(base_col, hovered_hsv_trans)).hex 

    coldict[ft.ControlState.DISABLED] = Color(hsv=hex_to_adjusted_hsv(base_col, disabled_hsv_trans)).hex 

    return coldict 

