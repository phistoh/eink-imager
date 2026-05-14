# eink-imager

> *Disclaimer*: As an experiment, this project is largely developed with the help of AI.


## Description

**eink-imager** is a simple Python application, which provides an HTTP endpoint serving image files (from an *output folder*). This endpoint will later be queried by a digital photo frame using an e-ink display. To add new images to serve, the application watches an *input folder* and processes all `*.jpg` files.

## Usage
- Run `einker.web` and `einker.watcher` as modules from the root directory (`eink-imager/`).
    - `einker.web` serves the Flask endpoints
    - `einker.watcher` checks `watch-dir` and processes incoming files

## Attribution
- Wall pattern by [Sisters.seamless](https://commons.wikimedia.org/wiki/File:Cream_textured_finish_seamless_building_wall_texture.jpg)
- Image frame by [ImageFramer](https://imageframer.net/web/)