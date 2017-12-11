<img src="./img/twin_plus_echo.jpg" crossorigin="https://mountsutro.org/library/sutro/hawk-thomas_sutro-tower-twin-peaks-silhouette.jpg" alt="Sutro, Twin Peaks, and Future Machine Overlords" width=346 height=176>

Scraping cool things to do in San Francisco with Python <i>and Amazon Echo</i>

# Overview

Goings On About San Francisco is a Python tool to identify cool things to do in San Francisco ... now with integration into Amazon Echo.

Inspired by The New Yorker's [Goings On About Town](http://www.newyorker.com/goings-on-about-town), this tool is intended to make searching through San Francisco events easy.

GoingsOn v1 was built on a series of webscrapers. For v2's beta, we'll use the data from [DoTheBay](https://dothebay.com'), an event data aggregator with a slick UI and voting system. We'll then push the top events into an Alexa Skill's App using [Flask-Ask](https://github.com/johnwheeler/flask-ask)

# How to Run

So far, the simplest usage is to run the DoTheBay scraper with the desired output directory as the first command line argument.

```bash
git clone https://github.com/kazistan/alex_goingson.git
cd goingson/bin
./dothebay --outdir [directory]
```

The result is a **dothebay.csv** despoited in the directory specified on the command line <directory>. This file will serve as the database from which the Alexa will draw.

# Copyright

DoTheBay data comes from https://dothebay.com, a site maintained by The DoStuff Network (DoStuff Media, LLC).

Image: "Sutro Tower" by Thomas Hawk licensed under CC BY 2.0, Amazon Echo - White (1st Generation) by Amazon.
