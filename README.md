# Image-to-MakeCode-Arcade

A Python tool to convert a MIDI file to a MakeCode Arcade song!

Web version will be available soon in a different repo.

## Install

1. Download and install Python.
2. Clone this repo.
3. Install all the requirements in [`requirements.txt`](requirements.txt)

> You may need to edit commands listed in this repo to use `py` or `python3`
> if `python` doesn't work.

> Don't want to/can't install `numpy` or `scipy`? Go to
> [`scr/converter.py`](src/converter.py) and change the import statements to
> use Python-only palette processing!
> (change it to import [`utils.palette`](src/utils/palette.py) instead of
> [`utils.fast_palette`](src/utils/fast_palette.py)) It will be slower but
> won't matter unless you are converting huge GIFs

## Usage

Run [`src/main.py`](src/main.py) at the root of the repository in the terminal.
(It is a CLI app)

### Example commands

To convert the JPEG file `image.jpg` and print the Arcade image to standard
output with the default palette and no resizing.

```commandline
python src/main.py -i "image.jpg"
```

To preview the JPEG file at the absolute path
`E:\Arcade Image to Image\testing\image.jpg` and write the output to
`image.ts` in the current directory with a width of 160 and a height of 120,
and with debug messages on.

```commandline
python src/main.py -i "E:\Arcade Image to Image\testing\image.jpg" -o "image.ts" --width 160 --height 120 --debug --preview
```

To convert the GIF file `image.gif` and write the output to `image.ts` in the
current directory.

```commandline
python src/main.py -i "image.gif" -o "image.ts" --gif
```

### Help text

```commandline
usage: main.py [-h] -i PATH [-o PATH] [-p] [--width W] [--height H]
               [--palette PALETTE] [-g] [--debug]

Convert an image to a MakeCode Arcade image!

options:
  -h, --help            show this help message and exit
  -i PATH, --input PATH
                        The input image.
  -o PATH, --output PATH
                        The output text file which contains a MakeCode Arcade
                        image.
  -p, --preview         Whether to preview the outputted image in the default
                        image viewer instead of writing to a file or standard
                        output.
  --width W             The width of the resulting MakeCode Arcade image.If
                        height is omitted, aspect ratio will be respected.
  --height H            The height of the resulting MakeCode Arcade image.If
                        width is omitted, aspect ratio will be respected.
  --palette PALETTE     The palette to use. Must be a string of comma
                        separated 6-digit hex codes. For example: "#000000,#ff
                        ffff,#ff2121,#ff93c4,#ff8135,#fff609,#249ca3,#78dc52,#
                        003fad,#87f2ff,#8e2ec4,#a4839f,#5c406c,#e5cdc4,#91463d
                        ,#000000" (that is the default palette for this tool
                        and MakeCode Arcade)
  -g, --gif             Whether to try to read the image as a GIF. If
                        specified, the output will be a TypeScript list of
                        images.
  --debug               Include debug messages. Defaults to info and greater
                        severity messages only.
```
