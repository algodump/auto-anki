import logging

class Env(object): 
    # TODO: how to make this private
    PATH_TO_ENV = ".env"
    _env_variables = {}

    @staticmethod
    def init():
        env_vars = [line.strip().split('=') for line in open(Env.PATH_TO_ENV).readlines()]
        Env._env_variables = {line[0] : line[1] for line in env_vars}

    @staticmethod
    def export(key, value):
        if key in Env._env_variables and Env._env_variables[key] == value:
            return
        
        logging.debug(f"Updating env file with {key} = {value}")
        Env._env_variables[key] = value
        
        with open(Env.PATH_TO_ENV, 'w') as file:
            for (key, value) in Env._env_variables.items():
                file.write(f"{key}={value}\n")

    @staticmethod
    def get(name):
        return Env._env_variables.get(name, None)