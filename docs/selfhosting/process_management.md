# Selfhosting Kurisu with a process manager

For some features of Kurisu to work such as the restart command. It requires a process manager to follow up on it closing. 

## Systemd
#### Prerequisites:
* Systemd

### Step 1:
****
**Create a unit file**\
`sudo nano /etc/systemd/system/kurisu.service`
### Step 2:
****
**Paste and fill out unit file**\
Upon you editing the unit file. Paste this in.
```
[Unit]
Description=Kurisu Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=on-success
RestartSec=1
User=root
ExecStartPre=/path/to/Kurisu/venv/bin/pip install -Ur requirements.txt
ExecStart=/path/to/Kurisu/venv/bin/python3 -u main.py
WorkingDirectory=/path/to/Kurisu

[Install]
WantedBy=multi-user.target
```
**Keep in mind to actually change the file paths**\
**Also if you're using poetry for pkg management. You can swap out the `ExecStartPre`**

After pasting and filling out everything. Do `ctrl+o` and `ctrl+x`
###Step 3:
****
**Reload**\
`sudo systemctl daemon-reload`
### Step 4:
****
`sudo systemctl start kurisu && journalctl -u kurisu -f -n 30`
### Step 5(Optional):
****
If you want Kurisu to startup upon your system dying. Use the following command.
`sudo systemctl enable kurisu`

After all of that you should be good as far as Systemd

## Pm2(Persistent through shutdown)
#### Prerequisites 
* PM2(`npm install pm2 -g` or `yarn global add pm2`)

### Step 1:
****
While in the working directory of the bot\
`sudo pm2 start pm2.json`
### Step 2:
****
**Profit**

## Extras
* If anything fails during any part of either setup. Feel free to hit up [this place](https://discord.gg/Cs5RdJF9pb)