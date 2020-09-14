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

Next, there is a `.secrets.json` file that sensitive and other config data is stored in, including the bot token, owner id and command prefixes.

Example `.secrets.json`:

```json
{
    "token": "this-is-a-secret-bot-token",
    "ownerId": "this-is-a-user-id",
    "prefixes": [
        "$",
        "e!"
    ]
}
```

Update these values according to your own user id and bot token. These will need to be updated in order for the bot to work.


### Usage

From here, the bot can be started and used simply with:  

```shell
python3 bin/bot.py
```

### Server Usage

To run this permenantly as a process, some additional setup is required.

Install [Supervisor](https://pypi.org/project/supervisor/):

```shell
pip3 install supervisor`  
```

Create/Modify the Supervisor config file `/etc/supervisor/conf.d/everybot.conf`

Sample `everybot.conf`:

```text
[program:everybot]
autostart=true
autorestart=true
command = python3 /srv/everyBot/bin/bot.py
```

Start the Supervisor service.

```shell
supervisorctl reread
supervisorctl start everybot
```

## Discord Usage

Use `$help` to get started with a list of commands.
