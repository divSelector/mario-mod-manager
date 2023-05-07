# smwcentral-scraper

The end goal of this project was to have a large collection of Super Mario World romhacks and be able to dive into them effortlessly -- one after the other -- with some idea of what you're looking for, but ultimately with no idea what to pick.

So I began scraping [smwcentral.net]((https://www.smwcentral.net)) for download links.

## What is SMW Central?

[SMW Central](https://www.smwcentral.net) is a website dedicated to Super Mario World ROM hacking. It is a community-driven platform where users can upload and download ROM hacks, discuss ROM hacking techniques, and collaborate on projects. SMW Central also hosts a variety of resources such as tutorials, tools, and custom graphics for Super Mario World ROM hacking. The website has been active since 2005 and has a large and active user base.

## What Does This Scraper Do?

It automates gathering romhacks, unzipping the archives, extracting the BPS patches out of them, and outputting playable ROMs. It enders the records of each all the information about them that it scrapes into a database and allows the user to query it for what to launch in an emulator.

It's more than a scraper really.

What's great about the tool is that it takes all the effort out of finding something to play. If you don't like the game, just quit. Put on another one. You spend no time looking for new ones or clicking on buttons to patch them. Just put on another. And another. And another.

You'll be surprised what you can find.

## Installation

Clone the repo. Open virtual environment. Install python dependencies:

```bash
git clone https://github.com/divSelector/smwcentral-scraper.git
cd smwcentral-scraper
python3 -m pip install virtualenv
python3 -m virtualenv venv
. venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

There are two additional binaries required:

### 1. flips (required to use the option `--scrape`)

Install [Floating IPS (flips)](https://github.com/Alcaro/Flips) in order to pathc the downloaded romhacks. After downloading it, move the binary to system `PATH` and confirm you can access it with `which flips`. The program will be able to find it once you do this.

You can otherwise open `smwc/config.py` and add any path to a flips binary that you like into the quotations of `FLIPS_BIN`.

For example:

`FLIPS_BIN = '/path/to/flips'`

### 2. retroarch (required to use the launch options; like `--random`)

Install [RetroArch](https://github.com/libretro/RetroArch) in order to use the launcher. You basically follow the same procedure as above. If you put `retroarch` on system `PATH`, it will be found. If you can't do that, you can specify that PATH in `smwc/config.py` under `RETROARCH_BIN`.

**Another thing...** Once you have downloaded retroarch, you'll need to download a snes core. I use `snes9x_libretro.so` but you can use any SNES core for RA if you specify the path to it in `smwc/config.py`.

#### I have build script for retroarch on debian systems btw

[Here](https://github.com/divSelector/ra-sh/blob/main/build.sh)...

#### I've written more about setting up retroarch before if you're interested

[Here](https://divsel.neocities.org/blog/2023/03/retroarch-linux/)...

### 3. Oh yeah... you need a clean Super Mario World rom

Obviously I can't help you with that. Use [Google](https://www.google.com) and get the USA version.

You'll put the sfc file (not the zip) into the `roms/clean/` directory. It doesn't matter what the filename is. If you put it there, it will find it.

## Usage

### Getting Help With Commands

`$ python smwcentral.py --help`

```
usage: smwc.py [-h] [--scrape] [--random] [--id X] [--title X] [--type X] [--author X] [--rating-over X]
               [--rating-under X] [--exits-over X] [--exits-under X] [--downloads-over X] [--downloads-under X]
               [--date-after X] [--date-before X] [--featured X] [--demo X] [--rewind | --no-rewind]
               [--show-beaten] [--show-started]

smwcentral.net scraper, downloader, database, romhack patcher and launcher by divselector

options:
  -h, --help           show this help message and exit

Main Options:
  --scrape             Scrape SMWCentral and Build Database of Patched Romhacks
  --random             Choose a random SMW hack and launch in RetroArch
  --id X               Launch a specific hack by ID number. Ignores --random and query options.

Query Modifiers (use these with --random):
  --title X            Substring to match against hack titles to include (e.g., "Super", "World")
  --type X             Substring to match against hack types to include (e.g., "Easy", "Kaizo")
  --author X           Substring to match against hack authors to include (e.g., "NewPointless", "yeahman")
  --rating-over X      Minimum rating for a hack to be considered (e.g., 4.5)
  --rating-under X     Maximum rating for a hack to be considered (e.g., 2.1)
  --exits-over X       Minimum exits for a hack to be considered (e.g., 10)
  --exits-under X      Maximum exits for a hack to be considered (e.g., 96)
  --downloads-over X   Minimum times downloaded for a hack to be considered (e.g., -1)
  --downloads-under X  Maximum times downloaded for a hack to be considered (e.g., 9999999)
  --date-after X       Must be uploaded after this date for hack to be considered (e.g., 1999-08-24)
  --date-before X      Must be uploaded before this date for hack to be considered (e.g., 2023-03-24)
  --featured X         Use "Yes" or "No" to consider hacks marked as *featured* by smwentral.net
  --demo X             Use "Yes" or "No" to consider hacks marked as demos

Launch Options:
  --rewind             When launching Retroarch, enable rewind support. The default option is determined by your RA
                       config.
  --no-rewind          When launching Retroarch, disable rewind support. The default option is determined by your
                       RA config.

Show Info Options:
  --show-beaten        Display hacks in database where all exits are cleared.
  --show-started       Display hacks in database where any exits are marked cleared.
  ```


### Scrape

