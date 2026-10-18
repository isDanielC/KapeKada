# KapeKada Coffee Cart Website

Interactive business website for KapeKada Coffee Cart, built with PyScript for the
Event-Driven Programming final project (EVD 31). It uses the same business concept as the
Business Analytics feasibility study: an affordable specialty-coffee cart on Leon Kilat St.,
Pahina Central, Cebu City, serving everyone on the corridor — not just students or employees.

## Tech stack

- Plain HTML5 + CSS3 for structure and styling (no frameworks).
- [PyScript](https://pyscript.net) (core, 2024.11.1) running Python in the browser via Pyodide.
- All interactivity — calculations, form handling, DOM updates — is written in Python (`main.py`), not JavaScript.

## Hero background video

The hero currently uses a temporary coffee-machine clip from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Blinking_lights_on_panel_of_Philips_automatic_coffee_machine_during_descaling_process.webm) (CC0), saved as `videos/coffee-promo.webm`. Replace that file with your own WebM clip to swap the video directly. For an MP4, update the `<source>` path and type in `index.html` to match your file.