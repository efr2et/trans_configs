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
                out.append(k + '="' + str(value) + '"')
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
                if type(value['file']) is list:
                    if len(value['file']) >= 1:
                        file_contents = self._decode(value['file'][0], config, vault).encode('utf-8')
                    if len(value['file']) >= 2:
                        file_permissions = self._decode(value['file'][1], config, vault)
                    else:
                        file_permissions = 0o666
                else:
                    file_contents = self._decode(value['file'], config, vault).encode('utf-8')
                    file_permissions = 0o666
                temp.write(file_contents)
                temp.close()
                os.chmod(temp.name, file_permissions)
                return temp.name
            elif 'base64' in value:
                return base64.b64decode(self._decode(value['base64'], config, vault)).decode('utf-8')
            else:
                raise Exception('Malformed object literal -- unknown: ' + value.keys()[0])

        else:
            return vault.resolve(config, value)
