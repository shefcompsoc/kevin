from os import environ


class Environment:
    def __init__(self):
        self.DISCORD_TOKEN: str = environ.get("DISCORD_TOKEN", "")
        self.DISCORD_ATTENDEE_ROLE_ID: int = int(environ.get("DISCORD_ATTENDEE_ROLE_ID", ""))
        self.DISCORD_ORGANISER_ROLE_ID: int = int(environ.get("DISCORD_ORGANISER_ROLE_ID", ""))
        self.DISCORD_VOLUNTEER_ROLE_ID: int = int(environ.get("DISCORD_VOLUNTEER_ROLE_ID", ""))
        self.DISCORD_GUILD_ID: int = int(environ.get("DISCORD_GUILD_ID", ""))
        self.TITO_TOKEN: str = environ.get("TITO_API_KEY", "")
        self.TITO_ACCOUNT_SLUG: str = environ.get("TITO_ACCOUNT_SLUG", "")
        self.TITO_EVENT_SLUG: str = environ.get("TITO_EVENT_SLUG", "")
        self.TITO_QUESTION_SLUG: str = environ.get("TITO_QUESTION_SLUG", "")
        self.ENABLED_EXTENSIONS: list = environ.get("ENABLED_EXTENSIONS", "").split(",")


env = Environment()
