from decouple import AutoConfig

class Configuration:
    def __init__(self, config: AutoConfig):
        self.token_lifetime = config('TOKEN_LIFETIME_SECOND')