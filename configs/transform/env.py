from pprint import pprint
import tempfile
import base64
import os

class Env:

    def __init__(self, transform_config):
        self.config = transform_config

    def transform(self, config, vault):
        out = []
        for k in self.config["fields"].keys():
            value = self.config["fields"][k]
            value = self._decode(value, config, vault)
            if value is None:
                out.append('# ' + k + '=null')
            else:
                out.append(k + '="' + value + '"')
        return os.linesep.join(out)

    def _decode(self, value, config, vault):
        if type(value) is dict:
            if len(value) != 1:
                raise Exception('Malformed object literal')

            if 'literal' in value:
                return value['literal']
            elif 'vault' in value:
                return vault.resolve(config, self._decode(value['vault'], config, vault))
            elif 'file' in value:
                temp = tempfile.NamedTemporaryFile(delete=False, prefix='configs')
                temp.write(self._decode(value['file'], config, vault).encode('utf-8'))
                temp.close()
                return temp.name
            elif 'base64' in value:
                return base64.b64decode(self._decode(value['base64'], config, vault)).decode('utf-8')
            else:
                raise Exception('Malformed object literal -- unknown: ' + value.keys()[0])

        else:
            return vault.resolve(config, value)
