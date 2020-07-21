# EveryBot
A completely modular discord bot for all purposes.

## Usage

### Installation
`git clone https://github.com/Givo29/everyBot.git`

Or, alternatively download the zip file and unpack into destination directory.

### Application Setup
Create a new discord application following this [setup guide](https://discordpy.readthedocs.io/en/latest/discord.html).  
Make sure you invite the bot to your server and copy the token as you will need it for the next step.

### Bot Setup
First, python dependencies must be installed:  
`pip3 -r install requirements.txt`

In `bin/bot.py`:

The last line in this file is where you need to put your token:
```python
bot.run("<token>", bot=True, reconnect=True)
```
Make sure it is surrounded in quotation marks as it is a string.

### Usage
From here, the bot can be started and used simply with:  
`python3 bin/bot.py`

### Server Usage
To run this permenantly as a process, some additional setup is required:

`pip3 install supervisor`  
`sudo vim /etc/supervisor/conf.d/everybot.conf`  
Sample `everybot.conf`:
```
[program:everybot]
autostart=true
autorestart=true
command = python3 /srv/everyBot/bin/bot.py
```

`supervisorctl reread`  
`supervisorctl start everybot`

## Discord Usage
Use `$help` to get started with a list of commands.