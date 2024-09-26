# This is the HackNotts verification and checkin bot

## Overview
It uses *Hikari* and *Lighbulb* to verify users as they enter the HackNotts Discord server.
Adds a `/verify` command that takes in the users ticket reference and checks to make sure its valid.
If the user already entered their Discord username when getting their ticket then they will be automatically verified and given the roles when joining the server (in theory...). It also uses a separate webhook listener to write ticket data to a database, this is then read by the bot when a user needs to be verified. This also is used to give users the "I was here" role when they have checked in. For the time being the user must use the `/here` command rather than being given it automatically.

### Other features
It also is capable of automatically announcing scheduled events. There are several options:
* name - Name of the event
* description - Description of the event, markdown is fine to use!
* datetime - Must be in the format: yyyy-mm-dd hh:mm 24 hour UTC
* author - Name of the organiser for the event
* author_url - The url for the organiser
* location - Location of the event
* delta - The number of minuets to make the announcement before the start time
* url - The url for the event, default is the HackNotts schedule page
* colour - The hex colour for the embed, default is HackNotts themed

An announcement will be made as an embed tagging the relevant roles, all data is stored in a MySQL database.

## Dependencies
**Python library dependencies:**
* *hikari-lightbulb*
* *mysql-connector-python*
* *APScheduler*
* *requests*
* *flask* - This is for the Tito webhook listener

**For Linux**
* *"hikari[speedups]"*

**For Windows**
* *hikari*
You must have VS C++ build tools installed

**Other dependencies:**
* *MySQL* - to store tito tickets and user info
