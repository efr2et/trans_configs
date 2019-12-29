from pprint import pprint
import os

class Env:

    def __init__(self, transform_config):
        self.config = transform_config

    def transform(self, config, vault):
        out = []
        for k in self.config["fields"].keys():
            value = vault.resolve(config, self.config["fields"][k])
            if value is None:
                out.append('# ' + k + '=null')
            else:
                out.append(k + '="' + value + '"')
        return os.linesep.join(out)
