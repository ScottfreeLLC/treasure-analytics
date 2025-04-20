#!/usr/bin/env python3
import os, shutil, pathlib

# 1) where are we working?
ROOT = pathlib.Path('.')          # current directory
TEXT_DIR   = ROOT / 'text'
IMAGE_DIR  = ROOT / 'images'

# 2) make sub‑folders if they’re missing
TEXT_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)

# 3) iterate over everything in ROOT
for item in ROOT.iterdir():
    # skip the sub‑folders we’re creating
    if item.is_dir() and item.name in ('text', 'images'):
        continue

    if item.is_file():
        if item.suffix.lower() == '.txt':
            shutil.move(str(item), TEXT_DIR / item.name)
        else:
            shutil.move(str(item), IMAGE_DIR / item.name)

print('Done: .txt files → /text, everything else → /images')
