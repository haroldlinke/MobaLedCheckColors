# -*- coding: utf-8 -*-
#
#         MobaLedCheckColors: Color checker for WS2812 and WS2811 based MobaLedLib
#
# * Version: 1.0
# * Author: Harold Linke
# * Date: November 23rd, 2019
# * Copyright: Harold Linke 2019
# *
# * 
# * MobaLedCheckColors on Github: https://github.com/haroldlinke/MobaLedCheckColors
# * 
# *
# * History of Change
# * V1.00 23.11.2019 - Harold Linke - first release
# *
# * MobaLedCheckColors supports the MobaLedLib by Hardi Stengelin
# * https://github.com/Hardi-St/MobaLedLib
# *
# * MobaLedCheckColors is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# * 
# * MobaLedCheckColors is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# * 
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# * MobaLedCheckColors is based on tkColorPicker by Juliette Monsel
# * https://sourceforge.net/projects/tkcolorpicker/
# * 
# * tkcolorpicker - Alternative to colorchooser for Tkinter.
# * Copyright 2017 Juliette Monsel <j_4321@protonmail.com>
# * 
# * tkcolorpicker is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# * 
# * tkcolorpicker is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# * 
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# * 
# * The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# * License: http://creativecommons.org/licenses/by-sa/3.0/	
# ***************************************************************************

import tkinter as tk
from tkinter import ttk
from tkcolorpicker.functions import tk, ttk, round2, create_checkered_image, \
    overlay, PALETTE, hsv_to_rgb, hexa_to_rgb, rgb_to_hexa, col2hue, rgb_to_hsv
from tkcolorpicker.alphabar import AlphaBar
from tkcolorpicker.gradientbar import GradientBar
from tkcolorpicker.lightgradientbar import LightGradientBar
from tkcolorpicker.colorsquare import ColorSquare
from tkcolorpicker.colorwheel import ColorWheel
from tkcolorpicker.spinbox import Spinbox
from tkcolorpicker.limitvar import LimitVar
from locale import getdefaultlocale
import re
import math
import os
import serial
import sys
from tkinter import messagebox

LARGE_FONT= ("Verdana", 12)
SMALL_FONT= ("Verdana", 7)

PARAM_FILENAME = 'MobaLedTest_param.json'
CONFIG_FILENAME = 'MobaLedTest_config.json'
DISCONNECT_FILENAME = 'MobaLedTest_disconnect.txt'

# --- Translation - not used
EN = {}
FR = {"Red": "Rouge", "Green": "Vert", "Blue": "Bleu",
      "Hue": "Teinte", "Saturation": "Saturation", "Value": "Valeur",
      "Cancel": "Annuler", "Color Chooser": "Sélecteur de couleur",
      "Alpha": "Alpha"}
DE = {"Red": "Rot", "Green": "Grün", "Blue": "Blau",
      "Hue": "Farbton", "Saturation": "Sättigung", "Value": "Helligkeit",
      "Cancel": "Beenden", "Color Chooser": "Farbwähler",
      "Alpha": "Alpha"}

try:
    TR = EN
    if getdefaultlocale()[0][:2] == 'fr':
        TR = FR
    else:
        if getdefaultlocale()[0][:2] == 'de':
            TR = DE        
except ValueError:
    TR = EN


def _(text):
    """Translate text."""
    return TR.get(text, text)


import json


# ----------------------------------------------------------------
# Class ConfigFile
# ----------------------------------------------------------------
class ConfigFile():
    """ Configuration File """

    def __init__(self):
        # type: 
        """ SDConfig Constructor Method (__init__)

        Arguments:
            None

        Raises:
            None
        """
        
        filedir = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(filedir, CONFIG_FILENAME)
        
        try:
            with open(filepath, "r") as read_file:
                data = json.load(read_file)
        except:
            data = ""

        self.serportnumber    = 0       # define serial port
        self.serportname      = "No Device"  # define serial port name
        self.maxLEDcount      = 255     # defines, the maximum LED count
        self.lastLed          = 0
        self.lastLedCount     = 1
        self.pos_x            = 100
        self.pos_y            = 100
        self.colorview        = 1
        self.startpage        = 0
        self.led_correction_r = 100
        self.led_correction_g = 69
        self.led_correction_b = 94
        self.use_led_correction = False
        self.old_color        = (255,255,255)
        self.palette = ("Kerze \n 1500K", "Natriumlampe \n 2000K", "Gluehlampe \n 2600K", "Hallogenlampe \n 3000K", "Fotolampe \n 3400K", "Neonroehre \n 4000K", "Mondlicht \n 4120K",
                   "Xeonlampe \n 4500K", "Morgensonne \n 5000K", "Nachmtgsonne \n 5500K", "Mittagssonne \n 5800K", "Bed. Himmel \n 7000K", "Nebel \n 8000K",
                   "Blauer Himmel \n 10000K")

        try:
            if "serportnumber" in data:
                self.serportnumber = data["serportnumber"]    # define serial port
            if "serportname" in data:
                self.serportname = data["serportname"]    # define serial port
            if "maxLEDcount" in data:
                self.maxLEDcount = data["maxLEDcount"]         # defines, the maximum LED count
            if "lastLedCount" in data:
                self.lastLedCount = data["lastLedCount"]         # stores the last LED count                
            if "lastLed" in data:
                self.lastLed = data["lastLed"]         # store last led numt                
            if "pos_x" in data:
                self.pos_x = data["pos_x"]                    
            if "pos_y" in data:
                self.pos_y = data["pos_y"]
            if "colorview" in data:
                self.colorview = data["colorview"]
            if "startpage" in data:
                self.startpage = data["startpage"]              
            if "led_correction_r" in data:
                self.led_correction_r = data["led_correction_r"]         
            if "led_correction_g" in data:
                self.led_correction_g = data["led_correction_g"]                    
            if "led_correction_b" in data:
                self.led_correction_b = data["led_correction_b"]
            if "use_led_correction" in data:
                self.use_led_correction = data["use_led_correction"]
            if "old_color" in data:
                self.old_color = data["old_color"]                
            if "palette" in data:
                self.palette = data["palette"]
       

        except:
            print ("Error in Config File")
            print(data)

    
    def save(self):
                
        filedir = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(filedir, CONFIG_FILENAME)
        
        data=dict(serportnumber=self.serportnumber,serportname=self.serportname,maxLEDcount=self.maxLEDcount,lastLedCount=self.lastLedCount,lastLed=self.lastLed,pos_x=self.pos_x,pos_y=self.pos_y,
                  colorview=self.colorview, startpage = self.startpage, led_correction_r = self.led_correction_r, 
                  led_correction_g = self.led_correction_g,led_correction_b = self.led_correction_b,
                  use_led_correction = self.use_led_correction, old_color=self.old_color, palette = self.palette)
 
        # Write JSON file
        with open(filepath, 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)   

# ----------------------------------------------------------------

# ----------------------------------------------------------------
# Global Var sdConfig
# ----------------------------------------------------------------
sdConfig = ConfigFile()

# ----------------------------------------------------------------
# Class ML_Param
#
# transfer of params between MobaLedLib via JSON file
# ----------------------------------------------------------------
class ParamFile():
    """ Configuration of VEGASScenDetect """

    def __init__(self):
        # type: 
        """ SDConfig Constructor Method (__init__)

        Arguments:
            None

        Raises:
            None
        """
        self.filename = PARAM_FILENAME
        
        filedir = os.path.dirname(os.path.realpath(__file__))
        self.filepath = os.path.join(filedir, self.filename)
        
        try:
            with open(self.filepath, "r") as read_file:
                data = json.load(read_file)
            self.fileexists     = True
        except:
            data = ""
            self.fileexists     = False

        
        self.color          = ""  # color param
        self.cor_color      = ""  # corrected color for ARDUINO - only output
        self.Lednum         = -1
        self.LedCount       = 0
        self.comport        = ""

        try:
            if "color" in data:
                self.color = data["color"]   
            if "cor_color" in data:
                self.cor_color = data["cor_color"]   
            if "Lednum" in data:
                self.Lednum = data["Lednum"]         
            if "LedCount" in data:
                self.LedCount = data["LedCount"]
            if "comport" in data:
                self.comport = data["comport"]   
 
        except:
            print ("Error in Param File")
            print(data)

    
    def save(self):
                
        filedir = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(filedir, self.filename)
        
        data=dict(color=self.color,cor_color=self.cor_color,Lednum=self.Lednum,LedCount=self.LedCount,comport=self.comport)
 
        # Write JSON file
        with open(filepath, 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
            
    def check(self):
        return os.path.isfile(self.filename)


# ----------------------------------------------------------------

# ----------------------------------------------------------------
# Global Var MLLParam - transfers params
# ----------------------------------------------------------------
MLLparam = ParamFile()

# --- replace config data with paramters from MLLparam file if the data was transferred
if MLLparam.fileexists:
    if MLLparam.color != "":
        sdConfig.old_color = MLLparam.color
    if MLLparam.Lednum >= 0:
        sdConfig.lastLed = MLLparam.Lednum
    if MLLparam.LedCount > 0:
        sdConfig.lastLedCount = MLLparam.LedCount
    if MLLparam.comport != "":
        sdConfig.serportname = MLLparam.comport

# ----------------------------------------------------------------
# Class LEDColorTest
# ----------------------------------------------------------------

class LEDColorTest(tk.Tk):

    # ----------------------------------------------------------------
    # LEDColorTest __init__
    # ----------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.arduino = None
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if sdConfig.pos_x < screen_width and sdConfig.pos_y < screen_height:
    
            self.geometry('+%d+%d' % (sdConfig.pos_x, sdConfig.pos_y))
        else:
            self.geometry("+100+100")

#        tk.Tk.iconbitmap(self,default='clienticon.ico')
        tk.Tk.wm_title(self, "MobaLedLib")

        self.title("MobaLedLib")
        self.transient(self.master)
        self.resizable(False, False)
        self.rowconfigure(1, weight=1)

        self.color = ""
        style = ttk.Style(self)
        style.map("palette.TFrame", relief=[('focus', 'sunken')],
                  bordercolor=[('focus', "#4D4D4D")])
        self.configure(background=style.lookup("TFrame", "background"))
        # --- define container for configuration and colortest frame
        container = tk.Frame(self)
        
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (ColorCheckPage, ConfigurationPage, HelpPage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        if sdConfig.startpage == 1:
            self.show_frame(ColorCheckPage)
        else:
            self.show_frame(ConfigurationPage)

    # ----------------------------------------------------------------
    # LEDColorTest show_frame
    # ----------------------------------------------------------------
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    # ----------------------------------------------------------------
    # LEDColorTest cancel
    # ----------------------------------------------------------------        
    def cancel(self):
        sdConfig.pos_x = self.winfo_x()
        sdConfig.pos_y = self.winfo_y()
        sdConfig.save()
        self.destroy()


    # ----------------------------------------------------------------
    # LEDColorTest connect ARDUINO
    # ----------------------------------------------------------------        
    def connect(self):

        print("connect")
        
        port = sdConfig.serportname

        self.arduino=None
        self.ARDUINO_message = ""
        
        timeout = False
        
        if port!="NO DEVICE":
        
            try:
                
                self.arduino = serial.Serial(port,baudrate=115200,timeout=2,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
               
                print("connected to: " + self.arduino.portstr)
            
                message = "#BEGIN\n"
                self.arduino.write(message.encode())
                print("Message send to ARDUINO: ",message) 
                
                seq = []
                count = 1
                timeout = False
                while count==1 and not timeout:
                    timeout = True
                    for c in self.arduino.read():
                        timeout = False
                        seq.append(chr(c)) #convert from ANSII
                        joined_seq = ''.join(str(v) for v in seq) #Make a string from array
                
                        if chr(c) == '\n':
                            print("Feedback from ARDUINO: " + joined_seq)
                            self.ARDUINO_message = joined_seq
                            seq = []
                            count += 1
                            break
                if timeout:
                    messagebox.showerror("Error", "ARDUINO is not answering")
                    self.ARDUINO_message = "ARDUINO is not answering"
                    port = "NO DEVICE"
                    self.arduino = None
                    return False
                else:
                    return True
                    
            except:
                messagebox.showerror("Error", "Serial Interface to ARDUINO could not be opened")
                self.ARDUINO_message = "ERROR! Connection could not be opened"
                port = "NO DEVICE"
                self.arduino = None
                return False
                
            return not timeout
        else:
            return False


    # ----------------------------------------------------------------
    # LEDColorTest disconnect ARDUINO
    # ----------------------------------------------------------------        
    def disconnect(self):

        print("disconnect") 
        if self.arduino:
            message = "#END\n"
            self.arduino.write(message.encode())
            print("Message send to ARDUINO: ",message) 
        
            self.arduino.close()
            self.arduino = None
            
# ----------------------------------------------------------------
# Class ConfigurationPage
# ----------------------------------------------------------------
        
class ConfigurationPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

          
        title_frame = ttk.Frame(self, relief="ridge", borderwidth=2)
        title_frame.columnconfigure(0, weight=1)
        
        label = ttk.Label(title_frame, text="Konfiguration", font=LARGE_FONT)
        label.pack(padx=50,pady=(10,10))

        
        cfg_frame = ttk.Frame(self, relief="ridge", borderwidth=2)
        cfg_frame.columnconfigure(0, weight=1)

        label2text = tk.Label(cfg_frame, text="ARDUINO Port:")
        label2text.pack(side="left", padx=10, pady=(10,10))
        
        self.combo = ttk.Combobox(cfg_frame)
        self.combo["value"] = ("NO DEVICE", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6")
        self.combo.current(sdConfig.serportnumber) #set the selected item
        
        self.combo.pack(side="right", padx=10, pady=(10,10) )
        
        view_frame = ttk.Frame(self, relief="ridge", borderwidth=2)
        view_frame.columnconfigure(0, weight=1)
        
        label3text = tk.Label(view_frame, text="Farbauswahlansicht (Neustart notwendig):")
        label3text.pack(side="left", padx=10, pady=(10,10))
        
        self.comboview = ttk.Combobox(view_frame)
        self.comboview["value"] = ("Farbton, Sättigung, Helligkei", "Farbrad und Helligkeit")
        self.comboview.current(sdConfig.colorview) #set the selected colorview
        
        self.comboview.pack(side="right", padx=10, pady=(10,10))    

        page_frame = ttk.Frame(self, relief="ridge", borderwidth=2)
        page_frame.columnconfigure(0, weight=1)
        
        label4text = tk.Label(page_frame, text="Startseite:")
        label4text.pack(side="left", padx=10, pady=(10,10))
        
        self.combopage = ttk.Combobox(page_frame)
        self.combopage["value"] = ("Konfiguration", "LED Farbauswahl")
        self.combopage.current(sdConfig.startpage) #set the selected colorview
        
        self.combopage.pack(side="right", padx=10, pady=(10,10))
        
        
        # --- LED MaxCount
        
        maxcount_frame = ttk.Frame(self, relief="ridge", borderwidth=2)
        maxcount_frame.columnconfigure(0, weight=1)
        
        self.ledmaxcount = LimitVar(1, 256, self)
        
        self.ledmaxcount.set(sdConfig.maxLEDcount)
        
        self.s_ledmaxcount = Spinbox(maxcount_frame, from_=1, to=256, width=5, name='spinbox',
                          textvariable=self.ledmaxcount, command=self._update_led_count)
        self.s_ledmaxcount.delete(0, 'end')
        self.s_ledmaxcount.insert(1, sdConfig.maxLEDcount)
        self.s_ledmaxcount.pack(side="right", padx=10, pady=(10,10))      


        ttk.Label(maxcount_frame, text=_('Maximale LED Anzahl')).pack(side="left", padx=10, pady=(10,10))
        
        

        # --- Buttons
        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Zur LED Farbauswahlseite",
                            command=lambda: controller.show_frame(ColorCheckPage)).pack(side="right", padx=10)
        ttk.Button(button_frame, text="Beenden",
                            command=controller.cancel).pack(side="right", padx=10)        
        ttk.Button(button_frame, text=_("Konfiguration Speichern"), command=self.save_config).pack(side="right", padx=10) 
        
        ttk.Button(button_frame, text=_("Hilfe"),
                            command=lambda: controller.show_frame(HelpPage)).pack(side="right", padx=10)        

        # --- placement
        title_frame.grid(row=1, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="new")
        cfg_frame.grid(row=2, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="new")

        view_frame.grid(row=5, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="new")
        page_frame.grid(row=6, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="new")
        maxcount_frame.grid(row=7, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="new")

        button_frame.grid(row=8, columnspan=2, pady=(20, 30), padx=10)
        
    # ----------------------------------------------------------------
    # ConfigurationPage save_config
    # ----------------------------------------------------------------

    def save_config(self):
        
        sdConfig.pos_x = self.winfo_x()
        sdConfig.pos_y = self.winfo_y()        
        sdConfig.serportnumber= self.combo.current()
        sdConfig.serportname= self.combo.get()
        sdConfig.maxLEDcount = self.s_ledmaxcount.get()
        sdConfig.colorview = self.comboview.current()
        sdConfig.startpage = self.combopage.current()
        sdConfig.save()

    # ----------------------------------------------------------------
    # ConfigurationPage _update_led_count
    # ----------------------------------------------------------------

    def _update_led_count(self, event=None):
        if event is None or event.widget.old_value != event.widget.get():
            maxledcount = self.s_ledmaxcount.get()

# ----------------------------------------------------------------
# Class ColorCheckPage
# ----------------------------------------------------------------

class ColorCheckPage(tk.Frame):

    # ----------------------------------------------------------------
    # ColorCheckPage __init__
    # ----------------------------------------------------------------

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
#        label = ttk.Label(self, text="Page One!!!", font=LARGE_FONT)
#        label.pack(pady=10,padx=10)

        color = sdConfig.old_color
        self.controller = controller
        
        if isinstance(color, str):
            if re.match(r"^#[0-9A-F]{8}$", color.upper()):
                col = hexa_to_rgb(color)
                self._old_color = col[:3]
                old_color = color[:7]
            elif re.match(r"^#[0-9A-F]{6}$", color.upper()):
                self._old_color = hexa_to_rgb(color)
                old_color = color
            else:
                col = self.winfo_rgb(color)
                self._old_color = tuple(round2(c * 255 / 65535) for c in col)
                args = self._old_color
                old_color = rgb_to_hexa(*args)
        else:
            self._old_color = color[:3]
            old_color = rgb_to_hexa(*color)
        
        led = sdConfig.lastLed
        
        ledcount = sdConfig.lastLedCount
         
        serport = controller.arduino
        
        title=_("MobaLedLib LED Farbentester")
        
        # --- Buttons
        button_frame = ttk.Frame(self)
        
        button_width = 25
        ttk.Button(button_frame, text=_("Einstellungen vornehmen"),width=button_width, command=lambda: controller.show_frame(ConfigurationPage)).grid(row=0, column=0, padx=10, pady=(10, 4), sticky='n')
        ttk.Button(button_frame, text=_("Programm Beenden"),width=button_width, command=self.cancel).grid(row=0, column=1, padx=10, pady=(10, 4), sticky='n')        
        ttk.Button(button_frame, text=_("Hilfe"), command=lambda: controller.show_frame(HelpPage)).grid(row=0, column=2, padx=10, pady=(10, 4), sticky='n')     

        # --- Colorwheel or Colorquare ?
        if sdConfig.colorview == 0:
            # --- GradientBar
            hue = col2hue(*self._old_color)
            bar = ttk.Frame(self, borderwidth=2, relief='groove')
            self.bar = GradientBar(bar, hue=hue, width=200, highlightthickness=0)
            self.bar.pack() 
    
            # --- ColorSquare
            square = ttk.Frame(self, borderwidth=2, relief='groove')
            self.square = ColorSquare(square, hue=hue, width=200, height=200,
                                      color=rgb_to_hsv(*self._old_color),
                                      highlightthickness=0)
            self.square.pack()
    
            frame = ttk.Frame(self)
            frame.columnconfigure(1, weight=1)
            frame.rowconfigure(1, weight=1)
        else:
            # --- LightGradientBar
            hue = 0
            h,s,v=rgb_to_hsv(*self._old_color)
            bar = ttk.Frame(self, borderwidth=2, relief='groove')
            self.bar = LightGradientBar(bar, hue=h, value=v, width=200, highlightthickness=0)
            self.bar.pack()
    
            # --- ColorWheel
            square = ttk.Frame(self, borderwidth=2, relief='groove')
            self.square = ColorWheel(square, hue=hue, width=200, height=200,
                                      color=rgb_to_hsv(*self._old_color),
                                      highlightthickness=0)
            self.square.pack()
    
            frame = ttk.Frame(self)
            frame.columnconfigure(1, weight=1)
            frame.rowconfigure(1, weight=1)        
       
        # --- color preview: initial color and currently selected color side by side
        preview_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        preview_frame.grid(row=0, column=0, sticky="nw", pady=2)
        old_color_prev = tk.Label(preview_frame, background=old_color[:7],
                                  width=5, highlightthickness=0, height=2,
                                  padx=0, pady=0)
        self.color_preview = tk.Label(preview_frame, width=5, height=2,
                                      pady=0, background=old_color[:7],
                                      padx=0, highlightthickness=0)
        old_color_prev.bind("<1>", self._reset_preview)
        old_color_prev.grid(row=0, column=0)
        self.color_preview.grid(row=0, column=1)

        # --- palette
        palette = ttk.Frame(frame)
        palette.grid(row=0, column=1, rowspan=2, sticky="ne")
        for i, col in enumerate(sdConfig.palette):
            coltemp = int(col[-6:-1])
            r,g,b = self._convert_K_to_RGB(coltemp)
            args = (r,g,b)
            hexcolor = rgb_to_hexa(*args)
            f = ttk.Frame(palette, borderwidth=1, relief="raised",
                          style="palette.TFrame")
            l = tk.Label(f, background=hexcolor, width=12, height=2,text=_(col))
            l.bind("<1>", self._palette_cmd)
            f.bind("<FocusOut>", lambda e: e.widget.configure(relief="raised"))
            l.pack()
            f.grid(row=i % 4, column=i // 4, padx=2, pady=2)

        # --- hsv
        
        col_frame = ttk.Frame(self)
  
        hsv_frame = ttk.Frame(col_frame, relief="ridge", borderwidth=2)
        hsv_frame.pack(pady=(0, 4), fill="x")
        hsv_frame.columnconfigure(0, weight=1)
        self.hue = LimitVar(0, 360, self)
        self.saturation = LimitVar(0, 100, self)
        self.value = LimitVar(0, 100, self)

        self.s_h = Spinbox(hsv_frame, from_=0, to=360, width=5, name='spinbox',
                      textvariable=self.hue, command=self._update_color_hsv)
        self.s_s = Spinbox(hsv_frame, from_=0, to=100, width=5,
                      textvariable=self.saturation, name='spinbox',
                      command=self._update_color_hsv)
        self.s_v = Spinbox(hsv_frame, from_=0, to=100, width=5, name='spinbox',
                      textvariable=self.value, command=self._update_color_hsv)
        h, s, v = rgb_to_hsv(*self._old_color)
        self.s_h.delete(0, 'end')
        self.s_h.insert(0, h)
        self.s_s.delete(0, 'end')
        self.s_s.insert(0, s)
        self.s_v.delete(0, 'end')
        self.s_v.insert(0, v)
        self.s_h.grid(row=0, column=1, sticky='w', padx=4, pady=4)
        self.s_s.grid(row=1, column=1, sticky='w', padx=4, pady=4)
        self.s_v.grid(row=2, column=1, sticky='w', padx=4, pady=4)
        ttk.Label(hsv_frame, text=_('Farbton [F/f]')).grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        ttk.Label(hsv_frame, text=_('Sättigung [S/s]')).grid(row=1, column=0, sticky='e',
                                                        padx=4, pady=4)
        ttk.Label(hsv_frame, text=_('Helligkeit [H/h]')).grid(row=2, column=0, sticky='e',
                                                   padx=4, pady=4)

        # --- rgb
        rgb_frame = ttk.Frame(col_frame, relief="ridge", borderwidth=2)
        rgb_frame.pack(pady=4, fill="x")
        rgb_frame.columnconfigure(0, weight=1)
        self.red = LimitVar(0, 255, self)
        self.green = LimitVar(0, 255, self)
        self.blue = LimitVar(0, 255, self)

        self.s_red = Spinbox(rgb_frame, from_=0, to=255, width=5, name='spinbox',
                        textvariable=self.red, command=self._update_color_rgb)
        self.s_green = Spinbox(rgb_frame, from_=0, to=255, width=5, name='spinbox',
                          textvariable=self.green, command=self._update_color_rgb)
        self.s_blue = Spinbox(rgb_frame, from_=0, to=255, width=5, name='spinbox',
                         textvariable=self.blue, command=self._update_color_rgb)
        self.s_red.delete(0, 'end')
        self.s_red.insert(0, self._old_color[0])
        self.s_green.delete(0, 'end')
        self.s_green.insert(0, self._old_color[1])
        self.s_blue.delete(0, 'end')
        self.s_blue.insert(0, self._old_color[2])
        self.s_red.grid(row=0, column=1, sticky='e', padx=4, pady=4)
        self.s_green.grid(row=1, column=1, sticky='e', padx=4, pady=4)
        self.s_blue.grid(row=2, column=1, sticky='e', padx=4, pady=4)
        ttk.Label(rgb_frame, text=_('Rot (LED 1)[R/r]')).grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        ttk.Label(rgb_frame, text=_('Grün (LED2) [G/g]')).grid(row=1, column=0, sticky='e',
                                                   padx=4, pady=4)
        ttk.Label(rgb_frame, text=_('Blau (LED3) [B/b]')).grid(row=2, column=0, sticky='e',
                                                  padx=4, pady=4)
        
        # --- hexa
        hexa_frame = ttk.Frame(col_frame)
        hexa_frame.pack(fill="x")
        self.hexa = ttk.Entry(hexa_frame, justify="center", width=10, name='entry')
        self.hexa.insert(0, old_color.upper())
        ttk.Label(hexa_frame, text="HTML").pack(side="left", padx=4, pady=(4, 1))
        self.hexa.pack(side="left", padx=6, pady=(4, 1), fill='x', expand=True)

        
        # --- Colortemperature
        ct_frame = ttk.Frame(col_frame, relief="ridge", borderwidth=2)
        ct_frame.pack(pady=4, fill="x")
        ct_frame.columnconfigure(0, weight=1)
        ct_min = 1000
        ct_max = 20000
        self.ct = LimitVar(ct_min, ct_max, self)

        self.s_ct = Spinbox(ct_frame, from_=ct_min, to=ct_max, width=5, name='spinbox',
                        textvariable=self.ct, command=self._update_ct, increment = 25)
        self.s_ct.delete(0, 'end')
        self.s_ct.insert(0, ct_min)
        self.s_ct.grid(row=0, column=1, sticky='e', padx=4, pady=4)

        ttk.Label(ct_frame, text=_('Farbtemperature (K) [T/t]')).grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        # --- ARDUINO Steuerung

        arduino_frame = ttk.Frame(self,relief="ridge", borderwidth=2,width=500)
        ttk.Label(arduino_frame, text=_('ARDUINO Steuerung')).grid(row=0, column=0, columnspan=3, sticky='', padx=4, pady=4)
        self.arduino_status = tk.Label(arduino_frame, text=_('Nicht verbunden'), bg="lightgray",width=20)
        self.arduino_status.grid(row=1, column=2, sticky='', padx=4, pady=(10, 4))
        
        # --- ARDUINO LED
        led_frame = ttk.Frame(arduino_frame, relief="ridge", borderwidth=2)
        led_frame.columnconfigure(0, weight=1)

        self.lednum = LimitVar(0, 255, self)
        self.ledcount = LimitVar(1, 256, self)
        
        self.lednum.set(sdConfig.lastLed)
        self.ledcount.set(sdConfig.lastLedCount)
        
        self.s_led = Spinbox(led_frame, from_=0, to=255, width=5, name='spinbox',
                        textvariable=self.lednum, command=self._update_led_num)
        self.s_ledcount = Spinbox(led_frame, from_=1, to=256, width=5, name='spinbox',
                          textvariable=self.ledcount, command=self._update_led_count)
        self.s_led.delete(0, 'end')
        self.s_led.insert(0, led)
        self.s_led.grid(row=0, column=1, sticky='e', padx=4, pady=4)
        self.s_ledcount.delete(0, 'end')
        self.s_ledcount.insert(1, ledcount)
        self.s_ledcount.grid(row=1, column=1, sticky='e', padx=4, pady=4)       

        ttk.Label(led_frame, text=_('LED Adresse [+/-]')).grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        ttk.Label(led_frame, text=_('LED Anzahl [A/a]')).grid(row=1, column=0, sticky='e',
                                                 padx=4, pady=4)


        button_width = 15
        ttk.Button(arduino_frame, text=_("Verbinden"),width=button_width, command=self.connect).grid(row=1, column=0, padx=10, pady=(10, 4), sticky='')      
        ttk.Button(arduino_frame, text=_("Trennen"),width=button_width, command=self.disconnect).grid(row=1, column=1, padx=10, pady=(10, 4), sticky='')
        led_frame.grid(row=4,column=0,columnspan=2,padx=10,pady=(10, 4),sticky="w")
        ttk.Button(arduino_frame, text=_("Alle LED aus [CTRL-c]"),width=20, command=self.led_off).grid(row=4, column=2, padx=10, pady=(10, 4), sticky='')


        # --- LED Color correction
        ledcor_frame = ttk.Frame(arduino_frame, relief="ridge", borderwidth=2)
        ledcor_frame.columnconfigure(0, weight=1)
        self.s_ledcorvar = tk.IntVar()
        self.s_ledcor = ttk.Checkbutton(ledcor_frame,text=_("LED Farbstichkorrektur"),variable=self.s_ledcorvar,onvalue = 1, offvalue = 0, command=self.cb)
        self.s_ledcor.grid(sticky='w', padx=4, pady=4, row=0,column=0)
        self.s_ledcorvar.set(sdConfig.use_led_correction)
        
        
 
        ledcor_frame.grid(row=5,column=0,columnspan=3,padx=10,pady=(10, 4),sticky="w")

        rgb_frame = ttk.Frame(ledcor_frame, relief="ridge", borderwidth=2)
        rgb_frame.grid(row=2,column=0,columnspan=3,padx=10,pady=(10, 4),sticky="w")
        rgb_frame.columnconfigure(0, weight=1)
        self.c_red = LimitVar(0, 100, self)
        self.c_green = LimitVar(0, 100, self)
        self.c_blue = LimitVar(0, 100, self)

        self.cs_red = Spinbox(rgb_frame, from_=0, to=100, width=5, name='spinbox',
                        textvariable=self.c_red, command=self._update_cor_rgb)
        self.cs_green = Spinbox(rgb_frame, from_=0, to=100, width=5, name='spinbox',
                          textvariable=self.c_green, command=self._update_cor_rgb)
        self.cs_blue = Spinbox(rgb_frame, from_=0, to=100, width=5, name='spinbox',
                         textvariable=self.c_blue, command=self._update_cor_rgb)
        self.cs_red.delete(0, 'end')
        self.cs_red.insert(0, sdConfig.led_correction_r)
        self.cs_green.delete(0, 'end')
        self.cs_green.insert(0, sdConfig.led_correction_g)
        self.cs_blue.delete(0, 'end')
        self.cs_blue.insert(0, sdConfig.led_correction_b)
        self.cs_red.grid(row=0, column=2, sticky='e', padx=4, pady=4)
        self.cs_green.grid(row=0, column=4, sticky='e', padx=4, pady=4)
        self.cs_blue.grid(row=0, column=6, sticky='e', padx=4, pady=4)
        ttk.Label(rgb_frame, text=_('Farbkorrektur (%)')).grid(row=0, column=0, sticky='news',
                                                 padx=4, pady=4)        
        ttk.Label(rgb_frame, text=_('Rot')).grid(row=0, column=1, sticky='e',
                                                 padx=4, pady=4)
        ttk.Label(rgb_frame, text=_('Grün')).grid(row=0, column=3, sticky='e',
                                                   padx=0, pady=4)
        ttk.Label(rgb_frame, text=_('Blau')).grid(row=0, column=5, sticky='e',
                                                  padx=4, pady=4)

        ttk.Label(ledcor_frame, text=_('ARDUINO:')).grid(row=4, column=0, columnspan=1, sticky='w', padx=4, pady=4)
        self.s_ledcorvalue = ttk.Label(ledcor_frame, text=_(' '))
        self.s_ledcorvalue.grid(row=4, column=2, columnspan=1, sticky='w', padx=4, pady=4)
        self.ledcorvalue = "#FFFFFF"


        # --- placement
        bar.grid(row=0, column=0, padx=10, pady=(10, 4), sticky='n')
        square.grid(row=1, column=0, padx=10, pady=(9, 0), sticky='n')
        col_frame.grid(row=0, rowspan=2, column=1, padx=(4, 10), pady=(10, 4))
        frame.grid(row=3, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="nsew")
        arduino_frame.grid(row=4, column=0, columnspan=2,pady=(0, 10), padx=10)
        button_frame.grid(row=5, column=0, columnspan=2,pady=(0, 10), padx=10)

        # --- bindings
        self.bar.bind("<ButtonRelease-1>", self._change_color, True)
        self.bar.bind("<Button-1>", self._unfocus, True)
        self.square.bind("<Button-1>", self._unfocus, True)
        self.square.bind("<ButtonRelease-1>", self._change_sel_color, True)
        self.square.bind("<B1-Motion>", self._change_sel_color, True)
        self.s_red.bind('<FocusOut>', self._update_color_rgb)
        self.s_green.bind('<FocusOut>', self._update_color_rgb)
        self.s_blue.bind('<FocusOut>', self._update_color_rgb)
        self.s_red.bind('<Return>', self._update_color_rgb)
        self.s_green.bind('<Return>', self._update_color_rgb)
        self.s_blue.bind('<Return>', self._update_color_rgb)
        self.s_red.bind('<Control-a>', self._select_all_spinbox)
        self.s_green.bind('<Control-a>', self._select_all_spinbox)
        self.s_blue.bind('<Control-a>', self._select_all_spinbox)
        self.s_led.bind('<Control-a>', self._select_all_spinbox)
        self.s_ledcount.bind('<Control-a>', self._select_all_spinbox)
        self.s_h.bind('<FocusOut>', self._update_color_hsv)
        self.s_s.bind('<FocusOut>', self._update_color_hsv)
        self.s_v.bind('<FocusOut>', self._update_color_hsv)
        self.s_h.bind('<Return>', self._update_color_hsv)
        self.s_s.bind('<Return>', self._update_color_hsv)
        self.s_v.bind('<Return>', self._update_color_hsv)
        self.s_h.bind('<Control-a>', self._select_all_spinbox)
        self.s_s.bind('<Control-a>', self._select_all_spinbox)
        self.s_v.bind('<Control-a>', self._select_all_spinbox)
        self.s_ct.bind("<FocusOut>", self._update_ct)
        self.s_ct.bind("<Return>", self._update_ct)
        self.s_ct.bind("<Control-a>", self._select_all_entry)
        self.hexa.bind("<FocusOut>", self._update_color_hexa)
        self.hexa.bind("<Return>", self._update_color_hexa)
        self.hexa.bind("<Control-a>", self._select_all_entry)        
        
        self.controller.bind("F",self.s_h.invoke_buttonup)
        self.controller.bind("f",self.s_h.invoke_buttondown)
        self.controller.bind("S",self.s_s.invoke_buttonup)
        self.controller.bind("s",self.s_s.invoke_buttondown)
        self.controller.bind("H",self.s_v.invoke_buttonup)
        self.controller.bind("h",self.s_v.invoke_buttondown)
        self.controller.bind("R",self.s_red.invoke_buttonup)
        self.controller.bind("r",self.s_red.invoke_buttondown) 
        self.controller.bind("G",self.s_green.invoke_buttonup)
        self.controller.bind("g",self.s_green.invoke_buttondown) 
        self.controller.bind("B",self.s_blue.invoke_buttonup)
        self.controller.bind("b",self.s_blue.invoke_buttondown)
        self.controller.bind("+",self.s_led.invoke_buttonup)
        self.controller.bind("-",self.s_led.invoke_buttondown)         
        self.controller.bind("A",self.s_ledcount.invoke_buttonup)
        self.controller.bind("a",self.s_ledcount.invoke_buttondown)           
        self.controller.bind("T",self.s_ct.invoke_buttonup)
        self.controller.bind("t",self.s_ct.invoke_buttondown)
        self.controller.bind("<Escape>",self.cancel)
        self.controller.bind("<Control-c>",self.led_off)
        
        self._update_color_hsv()
        
        self.onCheckDisconnectFile()
#        self.focus_set()
#        self.lift()
#        self.grab_set()

     
     
    def cb(self):
        print ("update checkbutton")
        self._update_cor_rgb()
        
        #self._update_preview()
        
    def connect(self):
        if self.controller.connect():
            self.arduino_status.configure(bg="green",text=_("Verbunden"))
        
        max_len = 40
        if len(self.controller.ARDUINO_message) > max_len:
            message = self.controller.ARDUINO_message[:max_len]
        else:
            message = self.controller.ARDUINO_message
        
        self.s_ledcorvalue.configure(text=message)
            
        
    def disconnect(self):
        self.controller.disconnect()
        self.arduino_status.configure(bg="lightgray",text=_("Nicht Verbunden"))        

    def get_color(self):
        """Return selected color, return an empty string if no color is selected."""
        return self.color

    @staticmethod
    def _select_all_spinbox(event):
        """Select all entry content."""
        event.widget.selection('range', 0, 'end')
        return "break"

    @staticmethod
    def _select_all_entry(event):
        """Select all entry content."""
        event.widget.selection_range(0, 'end')
        return "break"

    def _unfocus(self, event):
        """Unfocus palette items when click on bar or square."""
        w = self.focus_get()
        if w != self and 'spinbox' not in str(w) and 'entry' not in str(w):
            self.focus_set()

    def _update_preview(self):
        """Update color preview."""
        color = self.hexa.get()
        self.color_preview.configure(background=color)
        
        ledcount = self.ledcount.get()
        
        if ledcount >0:
            
            if False: # self.s_ledcorvar.get():
                red = int(self.red.get() * int(self.cs_red.get()) / 100.0)
                green = int(self.green.get() * int(self.cs_green.get()) / 100.0)
                blue = int(self.blue.get() * int(self.cs_blue.get()) / 100.0)
            else:
                red = self.red.get()
                green = self.green.get()
                blue = self.blue.get()
                    
            lednum = self.lednum.get()
            message = "#L" + '{:02x}'.format(self.lednum.get()) + " " + '{:02x}'.format(red) + " " + '{:02x}'.format(green) + " " + '{:02x}'.format(blue) + " " + '{:02x}'.format(self.ledcount.get()) + "\n"  

            self.ledcorvalue = "("+str(red)+","+str(green)+","+str(blue)+")  "+ "#"+ '{:02x}'.format(red) + '{:02x}'.format(green) + '{:02x}'.format(blue)
            self.s_ledcorvalue.configure(text=self.ledcorvalue.upper())
            
           
        if self.controller.arduino:
            self.controller.arduino.write(message.encode())
            print("Message send to ARDUINO: ",message)
#            cc=str(self.serport.readline())
#            print("ARDUINO Feedback:",cc[2:][:-5])        

    def _reset_preview(self, event):
        """Respond to user click on a palette item."""
        label = event.widget
        label.master.focus_set()
        label.master.configure(relief="sunken")
        args = self._old_color
        color = rgb_to_hexa(*args)
        h, s, v = rgb_to_hsv(*self._old_color)
        self.red.set(self._old_color[0])
        self.green.set(self._old_color[1])
        self.blue.set(self._old_color[2])
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        self.bar.set(h, s, v)
        self.square.set_hsv((h, s, v))
        self._update_preview()

    def _palette_cmd(self, event):
        """Respond to user click on a palette item."""
        label = event.widget
        label.master.focus_set()
        label.master.configure(relief="sunken")
        r, g, b = self.winfo_rgb(label.cget("background"))

        text = event.widget["text"]
        coltemp = int(text[-6:-1])
        self.ct.set(coltemp)
        
        r = round2(r * 255 / 65535)
        g = round2(g * 255 / 65535)
        b = round2(b * 255 / 65535)
        
        if self.s_ledcorvar.get():
            cr = int(self.cs_red.get())
            cg = int(self.cs_green.get())
            cb = int(self.cs_blue.get())
            
            crf = cr/100
            cgf = cg/100
            cbf = cb/100
            
            rxy = int(r*crf)
            gxy =  int(g*cgf)
            bxy =  int(b*cbf)
            if rxy > 255: rxy = 255
            if gxy > 255: gxy = 255
            if bxy > 255: bxy = 255
            
            r = rxy
            g = gxy
            b = bxy        
        
        
 
        args = (r, g, b)
        color = rgb_to_hexa(*args)
        h, s, v = rgb_to_hsv(r, g, b)
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        self.bar.set(h,s,v)
        self.square.set_hsv((h, s, v))
        self._update_preview()

    def _change_sel_color(self, event):
        """Respond to motion of the color selection cross."""
        (r, g, b), (h, s, v), color = self.square.get()
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.saturation.set(s)
        self.hue.set(h)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        self._update_preview()

    def _change_color(self, event):
        """Respond to motion of the hsv/brightness cursor."""
        hv = self.bar.get()
        self.square.set_hue(hv)
        (r, g, b), (h, s, v), sel_color = self.square.get()
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, sel_color.upper())
        self._update_preview()

    def _change_alpha(self, event):
        """Respond to motion of the alpha cursor."""
        a = self.alphabar.get()
        self.alpha.set(a)
        hexa = self.hexa.get()
        hexa = hexa[:7] + ("%2.2x" % a).upper()
        self.hexa.delete(0, 'end')
        self.hexa.insert(0, hexa)
        self._update_preview()

    def _update_color_hexa(self, event=None):
        """Update display after a change in the HEX entry."""
        color = self.hexa.get().upper()
        self.hexa.delete(0, 'end')
        self.hexa.insert(0, color)
        if re.match(r"^#[0-9A-F]{6}$", color):
            r, g, b = hexa_to_rgb(color)
            self.red.set(r)
            self.green.set(g)
            self.blue.set(b)
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            self.bar.set(h,s,v)
            self.square.set_hsv((h, s, v))
        else:
            self._update_color_rgb()
        self._update_preview()

    def _update_color_hsv(self, event=None):
        """Update display after a change in the HSV spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            h = self.hue.get()
            s = self.saturation.get()
            v = self.value.get()
            sel_color = hsv_to_rgb(h, s, v)
            self.red.set(sel_color[0])
            self.green.set(sel_color[1])
            self.blue.set(sel_color[2])
            hexa = rgb_to_hexa(*sel_color)
            self.hexa.delete(0, "end")
            self.hexa.insert(0, hexa)
            self.square.set_hsv((h, s, v))
            self.bar.set(h,s,v)
            self._update_preview()

    def _update_color_rgb(self, event=None):
        """Update display after a change in the RGB spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            r = self.red.get()
            g = self.green.get()
            b = self.blue.get()
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            args = (r, g, b)
            hexa = rgb_to_hexa(*args)
            self.hexa.delete(0, "end")
            self.hexa.insert(0, hexa)
            self.square.set_hsv((h, s, v))
            self.bar.set(h,s,v)
            self._update_preview()

    def _update_cor_rgb(self, event=None):
        """Update display after a change in the RGB spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            r = self.cs_red.get()
            g = self.cs_green.get()
            b = self.cs_blue.get()
            sdConfig.led_correction_r=r
            sdConfig.led_correction_g=g
            sdConfig.led_correction_b=b
            self._update_preview()
            if self.s_ledcorvar.get():
                self.square.set_colorcorrection(r,g,b)
            else:
                self.square.set_colorcorrection(100,100,100)

            
    def _update_led_num(self, event=None):
        """Update display after a change in the LED spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            led = self.lednum.get()
            self._update_preview()

    def _update_led_count(self, event=None):
        """Update display after a change in the LED count spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            ledcount = self.ledcount.get()
            self._update_preview()
            
    def _convert_K_to_RGB(self, colour_temperature):
        """
        Converts from K to RGB, algorithm courtesy of 
        http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
        """
        #range check
        if colour_temperature < 1000: 
            colour_temperature = 1000
        elif colour_temperature > 40000:
            colour_temperature = 40000
        
        tmp_internal = colour_temperature / 100.0
        
        # red 
        if tmp_internal <= 66:
            red = 255
        else:
            tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
            if tmp_red < 0:
                red = 0
            elif tmp_red > 255:
                red = 255
            else:
                red = int(tmp_red)
        
        # green
        if tmp_internal <=66:
            tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
            if tmp_green < 0:
                green = 0
            elif tmp_green > 255:
                green = 255
            else:
                green = int(tmp_green)
        else:
            tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
            if tmp_green < 0:
                green = 0
            elif tmp_green > 255:
                green = 255
            else:
                green = int(tmp_green)
        
        # blue
        if tmp_internal >=66:
            blue = 255
        elif tmp_internal <= 19:
            blue = 0
        else:
            tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
            if tmp_blue < 0:
                blue = 0
            elif tmp_blue > 255:
                blue = 255
            else:
                blue = int(tmp_blue)
        
        return red, green, blue

    def _update_ct(self, event=None):
        """Update display after a change in the ct spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            ct = self.ct.get()
            
            r,g,b = self._convert_K_to_RGB(ct)
            
           
            if self.s_ledcorvar.get():
                cr = int(self.cs_red.get())
                cg = int(self.cs_green.get())
                cb = int(self.cs_blue.get())
                
                crf = cr/100
                cgf = cg/100
                cbf = cb/100
                
                rxy = int(r*crf)
                gxy =  int(g*cgf)
                bxy =  int(b*cbf)
                if rxy > 255: rxy = 255
                if gxy > 255: gxy = 255
                if bxy > 255: bxy = 255
                
                r = rxy
                g = gxy
                b = bxy
            
            self.red.set(r)
            self.green.set(g)
            self.blue.set(b)
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            args = (r, g, b)
            hexa = rgb_to_hexa(*args)
            self.hexa.delete(0, "end")
            self.hexa.insert(0, hexa)
            self.square.set_hsv((h, s, v))
            self.bar.set(h)
            self._update_preview()                 

        
    def led_off(self,_event=None):

            # switch off all LED

        message = "#L00 00 00 00 FF\n"  
    
        if self.controller.arduino:
            self.controller.arduino.write(message.encode())
            print("Message send to ARDUINO: ",message)
            cc=str(self.controller.arduino.readline())
            print("ARDUINO Feedback:",cc[2:][:-5])                


    def cancel(self,_event=None):

        message = "#L00 00 00 00 FF\n"  

        if self.controller.arduino:
            self.controller.arduino.write(message.encode())
            print("Message send to ARDUINO: ",message)
            cc=str(self.controller.arduino.readline())
            print("ARDUINO Feedback:",cc[2:][:-5])
        
        sdConfig.lastLed = self.lednum.get()
        sdConfig.lastLedCount = self.ledcount.get()
        
        sdConfig.use_led_correction = self.s_ledcorvar.get()
        
        sdConfig.led_correction_r = self.cs_red.get()
        sdConfig.led_correction_g = self.cs_green.get()
        sdConfig.led_correction_b = self.cs_blue.get()
        
        sdConfig.old_color = self.hexa.get()
        
        if MLLparam.fileexists: # write params only when the file existed
            MLLparam.color = self.hexa.get() # current color
            MLLparam.cor_color = self.ledcorvalue.upper()[-7:] # corrected color
            MLLparam.Lednum = self.lednum.get()
            MLLparam.LedCount = self.ledcount.get()
            
            MLLparam.save()
  
        self.controller.cancel()

        
    def onCheckDisconnectFile(self):
        # checks every 1 Second if the file DISCONNECT_FILENAME is found.
        # if yes: then disconnect ARDUINO - is used by external program to request a disconnect of the ARDUINO
        if os.path.isfile(DISCONNECT_FILENAME):
            self.led_off()
            self.disconnect()
            
            # delete the file to avoid a series of disconnects
            try:
                os.remove(DISCONNECT_FILENAME)
            except:
                pass
                
        self.after(1000, self.onCheckDisconnectFile)        



class HelpPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Hilfe Seite", font=LARGE_FONT)
        label.grid(row=0, column=0,padx=10, pady=(10, 4))


 
        button_frame = ttk.Frame(self)
        
        button_width = 20
        ttk.Button(button_frame, text=_("zurück zu Einstellungen"),width=button_width, command=lambda: controller.show_frame(ConfigurationPage)).grid(row=0, column=0, padx=10, pady=(10, 4), sticky='n')
        ttk.Button(button_frame, text=_("zur LED Farbtestseite"),width=button_width, command=lambda: controller.show_frame(ColorCheckPage)).grid(row=0, column=1, padx=10, pady=(10, 4), sticky='n')        
        
        button_frame.grid(row=1, column=0,padx=10, pady=(10, 4))
        
        help_text01 = """
        
Farbauswahlseite:

Die Farbauswahlseite erlaubt es die  Wirkung einer LED-Farbe direkt zu testen.
Dazu bietet sie die Möglichkeit die LED auszuwählen, die gewünschte LED-Farbe einzustellen und diese dann an den ARDUINO zu senden.

Zur Auswahl der Farbe stehen folgende Hilfsmittel zur Verfügung:

1. Farbrad mit Helligkeitsbalken
Durch Anklicken eines Punktes im Farbrad kann die Farbe und Sätigung eingestellt werden.
Die Helligkeit kann über den Helligkeitsbalken oberhalb eingestellt werden.
2. Farbbalken mit Helligkeit/Sättigungs Auswahlfläche
Nach Auswahl des Farbtons mit dem farbbalken, kann die gewünschte Sättigung und Helligkeit auf der Farbfläche ausgewählt werden.

Die Auswahl, welches Hilfsmittel genutzt werden soll, kann auf der Konfigurationsseite vorgenommen werden. 
Nach der Auswahl ist ein Neustart der Applkation notwndig, um die Anzeige neuaufzubauen.

Eingabefelder:

Die Eingabefelder rechts zeigen die eingestellte Farbe in verschiedenen Farbmodi an:
1. Farbton/Sattigung/Helligkeit:  HSV-Modus
2. Rot/Grün/Blau: RGB-Modus
3. HTML: Headezimaldarstellung der Farbe
4. Farbtemperatur

Farbpalette:
Einige voreingestellte Farben für typische Beleuchtung - kann durch Anklicken ausgewählt werden

ARDUINO Steuerung:
Hier finden sich die Eonstellungen für den ARDUINO, die LED Auswahl und eine Farbstichkorrektur.

1. Schalter Verbinden / Trennen
Mit diesen Schaltern kann eine Verbindung zum ARDUINO aufgebaut oder getrennt werden. Das Statusfeld zeigt grün und den Text "Verbunden", wenn die verrbindung steht.
Der Comport für die Verbindung, kann in der Konfigurationsseite eingestellt werden.
Die Trennung der Verbindung zum ARDUINO kann übrigens auch von einem externen Program z.b. Excel aus erfolgen, wenn diese Programm sich mit dem ARDUINO verbinden will.

2. LED-Adresse:
Gibt die Nummer der LED an, die in der ausgewählten Farbe leuchten soll
3. LED Anzahl:
Gibt die Anzahl der LEDs an, die mit der Farbe leuchten sollen. Sinnvoll z.B: bei Strassen und Bahnsteigbeleuchtung, bei der viele LEDs mit der gleichen Farbe/Helligkeit leuchten solen

4. Schalter "Alle LED aus":
Beim Anklicken, werden alle LEDS aus geschaltet.

5. LED Farbstichkorrektur:
Bei den benutzten RGB LEDS WS2812 haben nicht alle drei Farben dieselbe Helligkeit. Dadurch ergibt sich ein Farbstich, wenn z.B. die LED eigentlich weiss leuchten sollte.
Vorgeschlagen wird folgende Farbkorrektur als Ausgangspunkt: (Liefert zumindest bei mir ganz gute Ergebnisse)
Rot: 100%, Grün: 69% Blau: 94%
Die Korrektur kann natürlcih individuell eingestellt werden.
Mit dem Check-Button "LED-Farbkorrektur", kann die Farbkorrektur ein und aus geschaltet werden.
Die Farben im Farbrad werdenn durch die Korrektur an den Farbstich der LED angepasst.
Die RGB Werte der Farbe, die dann an den ARDUINO gesendet wird, werden unten angezeigt. Diese Werte sind dann für das MobaLedLib Programm zu verwenden.


"""
        
        label_help = ttk.Label(self, text=help_text01, font=SMALL_FONT,anchor="ne",justify="left",wraplength=500)
        label_help.grid(row=2, column=0, padx=10, pady=(10, 4),sticky="ne")        
        

#        button_width = 20
#        button1 = ttk.Button(self, width=button_width,text="zurück zu Einstellungen",
#                            command=lambda: controller.show_frame(ConfigurationPage))
        
#        button1.grid(row=1, column=0, padx=10, pady=(10, 4), sticky='n')

#        button2 = ttk.Button(self, width=button_width,text="zur LED Farbtestseite",
#                            command=lambda: controller.show_frame(ColorCheckPage))
#        button2.grid(row=1, column=1, padx=10, pady=(10, 4), sticky='n')



        
        # --- palette
#        led_palette = ttk.Frame(self)
#        led_palette.grid(row=0, column=1, rowspan=2, sticky="ne")

#        led_palette.pack(pady=10,padx=10) 


    def _palette_cmd(self, event):
        """Respond to user click on a palette item."""
        label = event.widget
        label.master.focus_set()
        label.master.configure(relief="sunken")
        r, g, b = self.winfo_rgb(label.cget("background"))
        text = event.widget["text"]



app = LEDColorTest()
app.mainloop()