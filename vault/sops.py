import logging
import subprocess
import yaml

from pprint import pprint

try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import Loader as YamlLoader, Dumper as YamlDumper

class Sops:

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("configs")

    def resolve(self, config, path):
        self.logger.debug("Resolving " + path)

        # Convert data back to yaml
        config_str = config.export()

        # Decrypt file
        result = subprocess.run([
                'sops',
                '--ignore-mac',
                '--input-type', 'yaml', 
                '--output-type', 'yaml',
                '--decrypt', '/dev/stdin'
            ], stdout=subprocess.PIPE, input=config_str.encode('utf-8'))

        # Read decrypted file back
        decrypted_config = yaml.load(result.stdout.decode('utf-8'), Loader=YamlLoader)
        data = Sops._merge_dicts(decrypted_config['config'], decrypted_config['secrets_encrypted'])

        return Sops._resolve_in_object(data, path.split('.'))

    def _resolve_in_object(obj, path):
        nextkey = path.pop(0)

        if not nextkey in obj:
            return None

        if len(path) == 0:
            return obj[nextkey]
        else:
            return Sops._resolve_in_object(obj[nextkey], path)

    def _merge_dicts(a, b, path=None):
        # https://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    Sops._merge_dicts(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a


