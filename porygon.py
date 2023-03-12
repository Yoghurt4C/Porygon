import base64
import json
import os
import time
import tkinter as tk
from glob import glob
from idlelib.tooltip import Hovertip
from pathlib import Path
from tkinter import BooleanVar, StringVar, IntVar
from tkinter import Frame, Label, Entry, Checkbutton, OptionMenu, Scale, Button
from tkinter import HORIZONTAL

import PIL.Image
import poryicon

# holder object for tk vars
opt_settings = {}
format_settings = {}


def getScale(num):
    return int(num * 0.01)


def pipe():
    bIn = wnd.getvar('input_directory')
    bOut = wnd.getvar('output_directory')
    fltr = wnd.getvar('filter')
    frmt = wnd.getvar('format')

    if not bIn.endswith(os.sep):
        bIn += os.sep
    if not bOut.endswith(os.sep):
        bOut += os.sep

    inputs = glob(bIn + fltr)
    pth = Path(bOut)
    if not pth.exists():
        pth.mkdir(parents=True)

    config['input_directory'] = bIn
    config['output_directory'] = bOut
    config['filter'] = fltr
    config['format'] = frmt

    for opt in opt_settings:
        config[opt] = opt_settings[opt].get()

    for k in format_settings:
        for key in format_settings[k]:
            v = format_settings[k][key]
            if isinstance(v, BooleanVar):
                config['format_settings'][k][key] = bool(v.get())
            elif isinstance(v, IntVar):
                config['format_settings'][k][key] = int(v.get())
            else:
                config['format_settings'][k][key] = v.get()

    settings = config['format_settings'][frmt]
    params = {}
    for stg in settings:
        if stg == 'subsampling':
            if settings[stg] > -1:
                params[stg] = get_subsampling(settings[stg]).lower()
        if stg != 'preserve_icc' and stg != 'preserve_exif':
            params[stg] = settings[stg]

    for path in inputs:
        name = ''
        nameArr = os.path.basename(path).split('.')
        for i in range(len(nameArr) - 1):
            name += nameArr[i]
        img = PIL.Image.open(path)

        if config['resize']:
            if config['resize_scale']:
                size = (img.width * getScale(config['resize_width']), img.height * config['resize_height'])
            else:
                size = (config['resize_width'], config['resize_height'])
            img = img.resize(size, resample=PIL.Image.Resampling(config['resampling']))

        if frmt == 'JPEG':
            if settings['preserve_icc']:
                params['icc_profile'] = img.info.get('icc_profile')
            if settings['preserve_exif']:
                params['exif'] = img.getexif()
            img.save(bOut + name + supported[frmt], format=frmt, **params)
        time.sleep(1)
        # os.remove(img)

    with open('porygon.json', 'w') as defaults:
        json.dump(config, defaults, indent=4)
        defaults.close()


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def get_subsampling(num):
    if num == -1:
        return 'Auto'
    elif num == 0:
        return '4:4:4'
    elif num == 1:
        return '4:2:2'
    elif num == 2:
        return '4:2:0'
    elif num == 3:
        return 'Keep'


def get_resampling(num):
    if num == 0:
        return 'Nearest Neighbour'
    elif num == 1:
        return 'Lanczos'
    elif num == 2:
        return 'Bilinear'
    elif num == 3:
        return 'Bicubic'
    elif num == 4:
        return 'Box'
    elif num == 5:
        return 'Hamming'


def build_ops():
    clear_frame(fOps)
    Frame(fOps, width=0, height=0, borderwidth=0).grid(row=0)
    Checkbutton(fOps, text='Resize', variable=opt_settings['resize'], onvalue=True, offvalue=False,
                command=build_ops).grid(row=0)
    if opt_settings['resize'].get():
        scaleButton = Checkbutton(fOps, text='Scale', variable=opt_settings['resize_scale'], onvalue=True,
                                  offvalue=False)
        scaleButton.grid(row=0, column=1)
        Hovertip(scaleButton,
                 'If ticked, resizes inputs by a percentage.\nIf not ticked, all inputs will be resized to the same resolution.')
        Label(fOps, textvariable=StringVar(fOps, 'Width')).grid(row=1, column=0)
        Entry(fOps, textvariable=opt_settings['resize_width'], width=15).grid(row=1, column=1)
        Label(fOps, textvariable=StringVar(fOps, 'Height')).grid(row=2, column=0)
        Entry(fOps, textvariable=opt_settings['resize_height'], width=15).grid(row=2, column=1)
        Label(fOps, textvariable=StringVar(fOps, 'Resampling')).grid(row=3, column=0)
        fScale = Frame(fOps, borderwidth=0, width=5)
        resampling_text = StringVar(fScale, get_resampling(opt_settings['resampling'].get()))
        Label(fScale, textvariable=resampling_text).pack()
        Scale(fScale, showvalue=False, variable=opt_settings['resampling'], from_=0, to=5, orient=HORIZONTAL,
              command=lambda num: resampling_text.set(get_resampling(int(num)))).pack()
        fScale.grid(row=3, column=1)

    fOps.pack(after=fTxt)


def build_format(selectedFormat):
    clear_frame(fFrmtOpts)
    # workaround for the window not being resized after clearing the frame
    Frame(fFrmtOpts, width=0, height=0, borderwidth=0).grid(row=0)
    if selectedFormat == 'GIF':
        settings = format_settings['GIF']
        Checkbutton(fFrmtOpts, text='Optimize', variable=settings['optimize'])
    elif selectedFormat == 'JPEG':
        settings = format_settings['JPEG']
        Label(fFrmtOpts, text='Quality').grid(row=0)
        fe1 = Scale(fFrmtOpts, variable=settings['quality'], from_=0, to=100, orient=HORIZONTAL, resolution=5,
                    borderwidth=0)
        fe1.grid(row=0, column=1)
        Checkbutton(fFrmtOpts, text='Optimize', variable=settings['optimize'], onvalue=True, offvalue=False).grid(row=1)
        Checkbutton(fFrmtOpts, text='Progressive', variable=settings['progressive'], onvalue=True, offvalue=False).grid(
            row=1, column=1)
        Checkbutton(fFrmtOpts, text='Preserve ICC', variable=settings['preserve_icc'], onvalue=True,
                    offvalue=False).grid(row=2)
        Checkbutton(fFrmtOpts, text='Preserve EXIF', variable=settings['preserve_exif'], onvalue=True,
                    offvalue=False).grid(row=2, column=1)
        Label(fFrmtOpts, text='Subsampling').grid(row=3)
        fScale = Frame(fFrmtOpts, borderwidth=0, width=5)
        subsampling_text = StringVar(fFrmtOpts, get_subsampling(settings['subsampling'].get()))
        fe2 = Scale(fScale, showvalue=False, variable=settings['subsampling'], from_=-1, to=3, orient=HORIZONTAL,
                    command=lambda num: subsampling_text.set(get_subsampling(int(num))))
        fe2.grid()
        Label(fScale, textvariable=subsampling_text, width=4, height=1).grid(row=0, column=1)
        fScale.grid(row=3, column=1)

    fFrmtOpts.pack(after=fFrmt)


supported = {'BMP': '.bmp', 'GIF': '.gif', 'ICO': '.ico', 'JPEG': '.jpg', 'PNG': '.png', 'WebP': '.webp'}
config = {
    'input_directory': '',
    'output_directory': '',
    'filter': '*',
    'resize': False,
    'resize_scale': True,
    'resize_width': 200,
    'resize_height': 200,
    'resampling': 0,
    'format': 'JPEG',
    'format_settings': {
        'GIF': {
            'save_all': True,
            'include_color_table': False,
            'interlace': True,
            'optimize': True,
            'loop': True

        },
        'JPEG': {
            'quality': 75,
            'optimize': True,
            'progressive': False,
            'preserve_icc': False,
            'preserve_exif': False,
            'subsampling': -1
        }
    }
}

if os.path.exists('porygon.json'):
    with open('porygon.json', 'r') as defaults:
        config2 = json.load(defaults)
        for k in config:
            if k not in config2:
                config2[k] = config[k]
        for k in config['format_settings']:
            if k not in config2['format_settings']:
                config2['format_settings'][k] = config['format_settings'][k]

        config = config2
        del config2
        defaults.close()
        del defaults

else:
    with open('porygon.json', 'x') as defaults:
        json.dump(config, defaults, indent=4)
        defaults.close()
        del defaults

wnd = tk.Tk()
wnd.title('Porygon')
wnd.wm_iconphoto(True, tk.PhotoImage(data=poryicon.icon()))

for k in config['format_settings']:
    format_settings[k] = {}
    for key in config['format_settings'][k]:
        v = config['format_settings'][k][key]
        if isinstance(v, bool):
            format_settings[k][key] = BooleanVar(wnd, v)
        elif isinstance(v, int):
            format_settings[k][key] = IntVar(wnd, v)
        else:
            format_settings[k][key] = StringVar(wnd, v)

fTxt = Frame(wnd)
Label(fTxt, text='Input Directory').grid(row=0)
Label(fTxt, text='Output Directory').grid(row=1)
Label(fTxt, text='Filter').grid(row=2)
wnd.setvar('input_directory', config['input_directory'])
e1 = Entry(fTxt, textvariable=StringVar(wnd, name='input_directory'))
wnd.setvar('output_directory', config['output_directory'])
e2 = Entry(fTxt, textvariable=StringVar(wnd, name='output_directory'))
wnd.setvar('filter', config['filter'])
e3 = Entry(fTxt, textvariable=StringVar(wnd, name='filter'))
tip = Hovertip(e3, 'Wildcard filtering for inputs. Examples:\n\n'
                   '* - everything in the Input Directory.\n'
                   '*.bmp - every .bmp file in the Input Directory.')
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
fTxt.pack()

fOps = Frame(wnd)
opt_settings['resize'] = BooleanVar(wnd, config['resize'])
opt_settings['resize_scale'] = StringVar(wnd, config['resize_scale'])
opt_settings['resize_width'] = IntVar(wnd, config['resize_width'])
opt_settings['resize_height'] = IntVar(wnd, config['resize_height'])
opt_settings['resampling'] = IntVar(wnd, config['resampling'])
build_ops()

fFrmt = Frame(wnd)
wnd.setvar('format', config['format'])
Label(fFrmt, text='Target Format').grid(row=0)
fm1 = OptionMenu(fFrmt, StringVar(wnd, name='format'), *supported, command=build_format)
fm1.grid(row=0, column=1)
fFrmt.pack()

fFrmtOpts = Frame(wnd)
build_format(wnd.getvar('format'))
fFrmtOpts.pack(after=fFrmt)

doug = Button(wnd, text='Commence', width=15, command=pipe)
doug.pack()

wnd.mainloop()
