# This is the HackNotts 2023 verification bot
It uses *Hikari* and *Lighbulb* to verify users as they enter the HackNotts Discord server
Adds a `/verify` command that takes in the users ticket reference and checks to make sure its valid.
If the user already entered their Discord Tag when getting their ticket then they will be automatically verified and given the roles when joining the server (the theory...)

**Python library dependencies:**
* *hikari-lightbulb*
* *mysql-connector-python*
* *APScheduler*
* *requests*

**For Linux**
* "hikari[speedups]"

**For Windows**
* *hikari*
You must have VS C++ build tools installed

**Other dependencies:**
* *MySQL to store tito tickets and user info*