# Windows Selfhosting Guide

### Prerequisites:
**Please make sure you have all of the following**:
* Python>=3.9
* PIP
* git
### Step 0:
****
**Open a terminal.**\
Either `Windows Terminal`, `Powershell`, or `cmd(Command Prompt)` works
### Step 1:
****
Clone the repository:\
`git clone https://github.com/Yat-o/Kurisu`
### Step 2:
****
**Change Your Working Directory**\
`cd path/to/Kurisu`
### Step 3:
****
**Initialize and activate a Virtual Environment**
* `py -3 -m pip install virtualenv `
* `py -3 -m venv venv`
* `./venv/Scripts/activate`
### Step 4:
****
**Install project requirements**\
`pip install -Ur requirements.txt`
### Step 5:
**Rename and fill out config files**
* While in a file manager, right click on `configexample.toml` and rename it to `config.toml`
* Open `config.toml` in notepad, notepad++, vsc, etc
* Fill out accordingly\

`configoptions.toml` does not need to be renamed. It is globally the same for everyone
### Step 6
****
**Run the bot**\
If everything you've done went as planned in this tutorial everything should be ready to go

While in the projects root directory,  run `python main.py`

Hopefully the startup process went smoothly and your bot is online.\

### Extras
* If anything throughout the process failed. Please reach out on the support server [here](https://discord.gg/Cs5RdJF9pb)
* Poetry is not supported in this part of the selfhosting guides because of how bad of an environment windows is for it
* Process Management docs can be found [here](https://github.com/Yat-o/Kurisu/blob/rewrite/docs/selfhosting/process_management.md)
