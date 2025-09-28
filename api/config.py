from decouple import AutoConfig

class Configuration:
    def __init__(self, config: AutoConfig):
        self.token_lifetime = int(config('TOKEN_LIFETIME_SECOND'))