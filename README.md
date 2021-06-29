# HimejiBot
***

<a href="https://github.com/Yat-o/HimejiBot"><img src="https://cdn.myanimelist.net/r/250x350/images/clubs/8/163534.jpg?s=9ec45fdd4232591c01f3c4009caf55e9" alt="HimejiBot"></a>

- Invite [Here](https://discordapp.com/oauth2/authorize?&client_id=784474257832804372&scope=bot&permissions=8)

- Himeji is a discord bot that I am currently developing. Hoping to make it big one day.

- If you find any issues within the code please submit a issue via this
  Repo's [Issue Page](https://github.com/Yat-o/HimejiBot/issues)

- HimejiBot Uses Python Version [3.8.5](https://www.python.org/downloads/release/python-385/)
  and [Discord.py](https://discordpy.readthedocs.io/en/latest/#) Version 2.0.a
  
# Sources
***
- [RoboDanny](https://github.com/Rapptz/RoboDanny) (REPL Command)
- [RedBot](https://github.com/Cog-Creators/Red-DiscordBot) (PR Template)
- [@6days9weeks](https://www.github.com/6days9weeks/) (Help with code, few cogs and questions)
- The rest is me and excerpts from bots I've wrote in the past.

# Self-Hosting(LINUX ONLY)
**This guide is also mainly written for Ubuntu/Debian(More Distro Support coming soon**
* To start off make sure you have the base requirements: **Python3.7+(PIP Included) and Git**
### Basic Setup
* Clone the repository\
`git clone https://github.com/Yat-o/HimejiBot/`
* CD your way into the projects root directory\
`cd path/to/HimejiBot`
* Setup your Virtual Environment(Venv)
```shell
python3 -m pip install venv #install venv
python3 -m venv venv #initialize the venv for this project
source venv/bin/activate #activate it
```
* Next it is time to get install setuptools and wheel so packages dont fail to build
  ```shell
  pip3 install setuptools
  pip3 install wheel 
  ```
* After that you are set to now install the bot's requirements\
`pip3 install -r requirements.txt -U`
* Now rename the configexample.py and fill it out as needed
```shell
mv configexample.py config.py #CASE SENSITIVE
nano config.py #After filling it out. Save and exit with ctrl+x
```
* Now then if you did everything right you should now be able to run the bot\
Its as simple as `python3 main.py`
* Congrats you have the bot running 🥳
### Pm2 Setup
Alright so this process if also fairly easy. Just do all the steps in the Basic Setup but dont run the last step
* Make sure you have the one of these: **npm or yarn**
* Install PM2 if you don't already have it\
`npm install pm2 -g` or `yarn global add pm2`
* After installing PM2 you are ready to run the bot\
`pm2 start pm2.json`
* After that you can check on the bot with\
`pm2 logs Himeji`
### Systemd Setup
Alright this setup is for people who want to run the bot as a Systemd service. Just do everything in the Basic Setup excep the last step.
* First off make sure you have root or sudo access
* Create and edit the service's unit file\
  `sudo nano /etc/systemd/system/himeji.service`
* Next you will arrive onto an empty file. Copy and paste this into it
```
[Unit]
Description=Himeji Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=on-success
RestartSec=1
User=root
ExecStartPre=/path/to/HimejiBot/venv/bin/python3 -m pip install -U -r requirements.txt
ExecStart=/path/to/HimejiBot/venv/bin/python3 -u main.py
WorkingDirectory=/path/to/HimejiBot

[Install]
WantedBy=multi-user.target
```
**It is crucial to change the file paths to whichever path you have your clone on!**
* Now save and exit
* After that run\
`sudo systemctl daemon-reload`
  
* Now if all is done. You can now run this to start the service\
`systemctl start himeji && journalctl -u himeji.service -f -n 30`
  
* OPTIONAL: If you want the service to start on system restart. You can run this command.\
`systemctl enable himeji`

**If you have any problems with any setup and need help join the support server [here](https://discord.gg/Cs5RdJF9pb)**
# Supporters 
[![Stargazers repo roster for @Yat-o/HimejiBot](https://reporoster.com/stars/Yat-o/HimejiBot)](https://github.com/Yat-o/HimejiBot/stargazers)

[![Forkers repo roster for @Yat-o/HimejiBot](https://reporoster.com/forks/Yat-o/HimejiBot)](https://github.com/Yat-o/HimejiBot/network/members)

