# EveryBot

A completely modular and centralised Discord bot for all purposes.

## Invite Link:
[Click here to invite *everyBot* to your server](https://discord.com/api/oauth2/authorize?client_id=602687220058554368&permissions=8&scope=bot)

## Vision

*everybot* aims to go where no Discord bot has gone before

To create a **community driven**, completely **modular** and fully **centralised** Discord bot. 

## So why a new bot?

The [mee6](https://mee6.xyz/) bot is both modular and centralised. But not community driven - only having a limited amount of modules available for use

[Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) bot is fully modular and allows you to create your own cogs, but is self hosted only. 

*everyBot* intends to create something new. By combining the best parts (Community driven, Modular and fully hosted by us) and encouraging community members to create and maintain their own modules, for all to use, without the restriction of everyone having to setup and host the bot themselves. 

## How To Contribute
Contributing to the bot is easy! 

### Setting up a development instance
Before you can contribute, you'll first need a development instance for the bot:

1. You'll need to create a bot account through Discord and add a new bot to a Discord server you have administrator privileges for.  
*A tutorial on how to do this can be found [here](https://discordpy.readthedocs.io/en/latest/discord.html).*

2. Create a fork of the everyBot repository:
![Fork](https://i.imgur.com/ahYqQOO.png)

3. Clone your newly forked repository:
```
$ git clone https://github.com/<username>/everyBot.git
```

4. Update the .env file, there is a sample env file located [here](./.env.example)  
The only parts you have to change are the bot token (which you can get from the Discord developer portal you used in step 1), and your user id.  
*If you're having trouble finding your Discord user id, try following [this](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) tutorial.*

5. Make sure docker and docker-compose are installed on your computer.  
*[Windows](https://docs.docker.com/docker-for-windows/install-windows-home/)*  
*Debian linux:*
```
$ sudo apt install docker.io docker-compose
```
*Redhat Linux:*
```
$ sudo yum install docker.io docker-compose
```

6. Use docker to start your new everyBot instance
```
docker-compose up -d
```

There are two ways you can contribute:
### 1. Developing a new module


### 2. Contributing to the base bot



## Is it functional?
Yes! everyBot is completely functional and ready to be used in your servers. All you have to do is click the link above to add it to your Discord server.
