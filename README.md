# WellLit-OrderedCollections
#---- This is a work in progress and currently non-functional

This is a fork of the WellToWell repository from CZ Biohub's Well-Lit device. The code has been updated so that it works with more recent versions of the python and kivy dependencies, and a new widget configuration has been added to facilitate a specific build of the device with different electronic components.

While public, this code is currently a work in progress and non-functional. This README will updated when the project is ready to use.

From the original:
> This repository contains the code needed to run the CZ Biohub's Well-Lit device in the "Tube to Well-Lit" configuration, as described in the manuscript at:
> https://www.biorxiv.org/content/10.1101/2021.12.17.473010v2
>
> The files needed to build the Well-Lit device can be downloaded from https://osf.io/f9nh5/.

## Installation Instructions for Mac (updated instructions, debug only, not a final product)

1. Install Anaconda (from www.anaconda.com - tested on Anaconda version 4.8.3).
2. Make anaconda environment:<br/>
        Open up anaconda prompt and type: `conda create -n well_lit python=3.10`
3. Activate the environment with `conda activate well_lit`
4. Install dependencies:<br/>
        `conda install matplotlib`<br/>
        `conda install pandas`<br/>
        `conda install -c conda-forge kivy`<br/>
        `pip install kivy-garden`<br/>
        `pip install kivy_garden.graph --extra-index-url https://kivy-garden.github.io/simple/ `<br/>
        `pip install kivy_garden.matplotlib --extra-index-url https://kivy-garden.github.io/simple/ `<br/>
5. Clone this repo (https://github.com/AnthonyShiverMicrobes/WellLit-OrderedCollections.git)<br/>
6. In the official version of the package, one would next download the submodule for WellLit, because this code has been modified, its been included within this fork (no action needed)<br/>
7. To run the program:<br/>
        `python WellToWellGUI.py`<br/>

## Installation Instructions for Windows (updated instructions, final product)

1. Install Anaconda (from www.anaconda.com - tested on Anaconda version 4.8.3).
2. Make anaconda environment:<br/>
        Open up anaconda prompt and type: `conda create -n well_lit python=3.10`
3. Activate the environment with `conda activate well_lit`
4. Install dependencies:<br/>
        `conda install matplotlib`<br/>
        `conda install pandas`<br/>
        `pip install pypiwin3`<br/>
        `conda install -c conda-forge kivy`<br/>
        `pip install kivy-deps.angle~=0.3.3`<br/>
        `pip install kivy-deps.glew~=0.3.1`<br/>
        `pip install kivy-deps.sdl2~=0.6.0`<br/>   
        `pip install kivy-garden`<br/>
        `pip install kivy_garden.graph --extra-index-url https://kivy-garden.github.io/simple/ `<br/>
        `pip install kivy_garden.matplotlib --extra-index-url https://kivy-garden.github.io/simple/ `<br/>
5. Clone this repo (https://github.com/AnthonyShiverMicrobes/WellLit-OrderedCollections.git)<br/>


### Software Configuration
Unmodified from the original:<br/>
> To configure the software open 'wellLitConfig.json' in a text editor and modify the following entries to suit the users application. > If invalid directory locations are given in this configuration file, the software will default to using subfolders named 'samples', 'records', and 'protocols' in the parent repository folder.
> 
> 1. 'num_wells' configures the software for either 96 or 384 well format. If an invalid number is entered the software defaults to 96-well format.
> 2. 'records_dir' configures the directory for storing records. The software automatically records every transfer in a CSV file with timestamps as soon as the action is completed.
> 3. 'A1_X_dest' and 'A1_Y_dest' control the position of well A1 on the screen. The numeric values are given as fractions of the screen area, and so will likely need to be adjusted if using a screen different than the one specified in this build guide. These values increment from the upper left corner of the Graphical User Interface (GUI). If the lighting is misaligned with the wells on your screen, adjust these parameters to achieve good alignment.
> 4. 'size_param' controls the size of the illuminated circle or square which appears beneath a well.
> 5. 'well_spacing' controls the distance between adjacent wells.
> 6. 'protocols_dir' sets the directory to load cherry picking lists. Examples of cherry-picking lists are given in the 'protocols' directory in the repository.
> 7. 'A1_X_dest' and 'A1_Y_source' control the position of well A1 for the plate on the bottom half of the screen where samples are aliquoted to.

## Use instructions
Unmodified from the original:<br/>
> The GUI will display instructions for the user as they use the device, plus popups if the user attempts any invalid commands.
> 
> 1. Ensure that the 'WellLit-WelltoWell' repository is active, and that the software configurations have been set.
> 2. To produce a cherry picking transfer protocol, create a new CSV file in the folder specified in the 'wellLitConfig.json' configuration file ('protocol_dir' parameter - see Software Configuration section). Examples of cherry picking CSV files can be seen in the '/protocols' folder in the software repository. The format must be as follows:<br/>
>    a. First Line: Name of destination plate<br/>
>    b. Lines 2...N: Source plate, source well, destination well
> 3. Launch the Well-Lit GUI either by double clicking on the startup.bat you copied to the desktop, or by launching 'WellToWellGUI.py' from a python terminal.
> 4. Insert the plates into the holders. Ensure that the A1 wells are in the top left corner of the holder (the holder for each type of multi-well plate is designed to ensure that the plate can only be inserted in the right orientation).<br/>
>    Top plate is always the source plate<br/>
>    Bottom plate is always the destination plate
> 5. Load a transfer protocol by clicking on the “Load Protocol” button. The source and destination plate areas will be populated with lights corresponding to each well in the plate. Wells are highlighted with the following colors:<br/>
>    Yellow: Source and destination wells for the current transfer<br/>
>    Red: Wells that are listed for transfer in the protocol file<br/>
>    Gray: Wells that were NOT listed for transfer in the protocol file
> 6. Each user action is recorded with a timestamp in a CSV file saved to the folder specified in the 'wellLitConfig.json' configuration file ('records_dir' parameter - see Software Configuration section).
> 7. Well-Lit to Well-Lit sample transfer procedure:<br/>
>    a. Press “Next”  or use the hotkey shortcut 'n' to light a source well and its corresponding destination well in yellow.<br/>
>    b. Press “Failed” if the transfer was unsuccessful and should be skipped - it will be marked as 'Failed' in the log file.<br/>
>    c. Press “Skip” if you do not wish to complete the current transfer that is lit up in yellow - it will be marked as 'Skipped' in the log file.<br/>
>    d. After successfully transferring the sample from the source well to the destination well, press “Next” or use the hotkey shortcut 'n'. The source well will be lit in gray and the destination well will be lit in red to denote that the source has been emptied and the destination has been filled. The next pair of source and transfer wells will be lit in yellow.<br/>
>    e. The last transfer can be undone with the “Undo” button, giving the user the opportunity to redo it. Only the most recent transfer can be undone (not transfers before the last), and a user cannot mark a transfer as undone after they press the “Next Plate” button, even if that transfer was the most recently completed.<br/>
>    f. To complete a plate, press “Next Plate” or use the hotkey shortcut 'p'. If not all transfers on the current plate are complete, the user will be asked to confirm the command. If the user confirms, all of the incomplete transfers are marked as 'Skipped' in the log file.
> 8. When the transfer protocol is complete press on “Complete Transfer Protocol” to finish the transfers and allow a new protocol CSV file to be uploaded.
