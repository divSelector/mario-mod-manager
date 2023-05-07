# smwcentral-scraper

The end goal of this project was to have a large collection of Super Mario World romhacks and be able to dive into them effortlessly -- one after the other -- with some idea of what you're looking for, but ultimately with no idea what to pick.

## What is SMW Central?

[SMW Central](https://www.smwcentral.net) is a website dedicated to Super Mario World ROM hacking. It is a community-driven platform where users can upload and download ROM hacks, discuss ROM hacking techniques, and collaborate on projects. SMW Central also hosts a variety of resources such as tutorials, tools, and custom graphics for Super Mario World ROM hacking. The website has been active since 2005 and has a large and active user base.

## What Does This Scraper Do?

It automates gathering romhacks, unzipping the archives, extracting the BPS patches out of them, and outputting playable ROMs. It enders the records of each all the information about them that it scrapes into a database and allows the user to query it for what to launch in an emulator.

It's more than a scraper really.

What's great about the tool is that it takes all the effort out of finding something to play. If you don't like the game, just quit. Put on another one. You spend no time looking for new ones or clicking on buttons to patch them. Just put on another. And another. And another.

You'll be surprised what you can find.

## Usage

Let's look at what it does and we'll save installation for last.

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


### Scrape, Download, Patch

`$ python smwcentral.py --scrape`

By default it will only scrape one page (50 hacks). You can set `DEBUG_SCRAPER = {'ONE_PAGE_ONLY': False}` in `smwc/config.py` and it will do every page. There is self imposed ratelimit where batches of 10 downloads are spaced out for 8 seconds. Each download per batch is spaced out by three seconds. 

```
Clean Super Mario World ROM found and validated...
Requesting page: https://www.smwcentral.net/?p=section&s=smwhacks
Requesting page: https://www.smwcentral.net/?p=section&s=smwhacks&n=1
[0/5] Downloading batch of 10 archives...
[0/10] Downloading archive from https://dl.smwcentral.net/33861/SeekTheDiscrepancy.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/SeekTheDiscrepancy.zip
Waiting 3 second(s) till next download...

[1/10] Downloading archive from https://dl.smwcentral.net/33806/Bro%27s%20Adventure%20%28Demo%29.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/Bro27s_Adventure_28Demo29.zip
Waiting 3 second(s) till next download...

[2/10] Downloading archive from https://dl.smwcentral.net/33592/Incredibous%20Shells%20v1.3.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/Incredibous_Shells_v1.3.zip
Waiting 3 second(s) till next download...

[3/10] Downloading archive from https://dl.smwcentral.net/33789/burningstar1.2.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/burningstar1.2.zip
Waiting 3 second(s) till next download...

[4/10] Downloading archive from https://dl.smwcentral.net/33813/The%20Hodgepodge.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/The_Hodgepodge.zip
Waiting 3 second(s) till next download...

[5/10] Downloading archive from https://dl.smwcentral.net/33817/M.Mania.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/M.Mania.zip
Waiting 3 second(s) till next download...

[6/10] Downloading archive from https://dl.smwcentral.net/33685/MTMGR1_7.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/MTMGR1_7.zip
Waiting 3 second(s) till next download...

[7/10] Downloading archive from https://dl.smwcentral.net/33695/NebulaVer.1.1.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/NebulaVer.1.1.zip
Waiting 3 second(s) till next download...

[8/10] Downloading archive from https://dl.smwcentral.net/33795/Vampire%20Hunter%20Savior%20Of%20The%20Kingdom.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/Vampire_Hunter_Savior_Of_The_Kingdom.zip
Waiting 3 second(s) till next download...

[9/10] Downloading archive from https://dl.smwcentral.net/33784/Bowser%27s%20Kaizo%20Conspiracy%20v1.1.zip...
File saved as /mnt/hdd/hacks/smwc-scraper/tmp/zips/Bowser27s_Kaizo_Conspiracy_v1.1.zip
Waiting 3 second(s) till next download...

Waiting 8 second(s) to start next batch of downloads...
```

When the downloading is finished, it will begin unzipping and patching

```

Unzipping /mnt/hdd/hacks/smwc-scraper/tmp/zips/SeekTheDiscrepancy.zip...
Moving tmp/unzip/std.bps to tmp/bps/std.bps
Executing flips to patch romhack...
The patch was applied successfully!

Unzipping /mnt/hdd/hacks/smwc-scraper/tmp/zips/Bro27s_Adventure_28Demo29.zip...
Moving tmp/unzip/Bro's Adventure (Demo).bps to tmp/bps/Bro's_Adventure_(Demo).bps
Executing flips to patch romhack...
The patch was applied successfully!

Unzipping /mnt/hdd/hacks/smwc-scraper/tmp/zips/Vampire_Hunter_Savior_Of_The_Kingdom.zip...
Moving tmp/unzip/Vampire Hunter Savior Of The Kingdom.bps to tmp/bps/Vampire_Hunter_Savior_Of_The_Kingdom.bps
Executing flips to patch romhack...
The patch was applied successfully!

Unzipping /mnt/hdd/hacks/smwc-scraper/tmp/zips/Bowser27s_Kaizo_Conspiracy_v1.1.zip...
Moving tmp/unzip/Bowser's Kaizo Conspiracy v1.1.bps to tmp/bps/Bowser's_Kaizo_Conspiracy_v1.1.bps
Executing flips to patch romhack...
The patch was applied successfully!

```

When this is done, it will begin entering data into the database.

```
Preparing to write 50 records
Inserting records for Seek the Discrepancy
Inserting records for Bro's Adventure
Inserting records for Incredibous Shells v1.3
Inserting records for Burning Star
Inserting records for The Hodgepodge: A Collection of Would Be Scrapped Levels
Inserting records for Mario Mania
Inserting records for Mario - The Mystical Gem
Inserting records for Nebula
Inserting records for Vampire Hunter Savior Of The Kingdom
Inserting records for Super Mario World: Bowser's Kaizo Conspiracy
Inserting records for SMW The Princess Rescue 3 - The Turnabout
Inserting records for Chicanery
Inserting records for Play To Win
```

#### Running It Again?

If you try to run the scraper again, it will not work until there are new roms to pull. It will not download the same rom twice.

`$ python smwcentral.py --scrape`

```
Clean Super Mario World ROM found and validated...
Requesting page: https://www.smwcentral.net/?p=section&s=smwhacks
Requesting page: https://www.smwcentral.net/?p=section&s=smwhacks&n=1
Downloading batches complete
Preparing to write 0 records
```

### Random Game

Let's say you want to play a random game that has 'Standard' somewhere in the type... the rating is over 3.9, and the upload date is something after 2018. And... turn the rewind feature off in RA so you're not tempted to use it.

`python smwcentral.py --random --type Standard --rating-over 3.9 --date-after 2019-01-01 --no-rewind`

```
ID: 439
Title: Super Mario The Trip
Created On: 2022-05-12 16:18:21
Page URL: https://www.smwcentral.net/?p=section&a=details&id=30265
Is Demo: No
Is Featured: No
Exit Count: 75
Exits Cleared: 0
Rating: 4.8
Size: 3.64 MiB
Download Count: 4115
Type: ['Standard: Normal']
Path: ['Super_Mario_The_Trip-20230502120514.sfc']
Author: ['Sig_AM']

PRESS ANY KEY TO START
```

Press any key and you'll start. When the emulator closes out... it will tell you what file you just played and update the number of exits that you cleared (sometimes -- this feature is wonky.)

```
/mnt/hdd/hacks/smwc-scraper/roms/hacks/Super_Mario_The_Trip-20230502120514.sfc
Super Mario The Trip updated exits_cleared from 0 to 0
```

I didn't beat any exits this time because I just closed the emulator immediately in this example. But let's look at some of what I have been doing lately.

`$ python smwcentral.py --show-started --show-beaten`

```
HACKS WITH ALL EXITS CLEARED:
102: Forgotten Town -- 9/9 Exits Clear!
392: Zap & Lena Adventures -- 19/19 Exits Clear!


HACKS WITH SOME EXITS CLEARED:
581: NOT SO SADISTIC MARIO. -- 4/22 Exits Clear!
623: Mario's Lost World -- 3/27 Exits Clear!
778: Super Mario World Remix -- 3/32 Exits Clear!
986: The Second Reality Project 2 Reloaded: Zycloboo's Challenge -- 4/112 Exits Clear!
1016: Mushroom Kingdom - Under Crimson Skies -- 1/25 Exits Clear!
1093: Super Demo World: The Legend Continues -- 6/120 Exits Clear!
1306: K-16 - Story of Steel -- 1/25 Exits Clear!
1428: Shipwrecked -- 5/24 Exits Clear!
1612: Mario's Walk Home: Extended Collector's Edition -- 1/15 Exits Clear!
1917: Myth of Mana -- 119/1 Exits Clear!

```

Neat! You may have noticed the last one that says 119/1 exits cleared! I told you; this feature is mostly cool but very imperfect and occasionally very wrong. It's the most unreliable bug in the program. Luckily it's not too important (for now).

### Select Game By ID

`$ python smwcentral.py --id 581`

The IDs are quite useful for working on the games you have started but not finished yet.



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

I'm hoping to automate this more in the future but for now, you just need to get these things installed yourself.

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

#### I've written more about setting up retroarch and downloading cores before if you're interested

[Here](https://divsel.neocities.org/blog/2023/03/retroarch-linux/)...

### 3. Oh yeah... you need a clean Super Mario World rom

Obviously I can't help you with that. Use [Google](https://www.google.com) and get the USA version.

You'll put the .sfc file (not the zip) into the `roms/clean/` directory. It doesn't matter what the filename is. If you put it there, it will find it.




## Please Submit Issues.

I'm interested in your thoughts and opinions. My DMs are open for concerns.