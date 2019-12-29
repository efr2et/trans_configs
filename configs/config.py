import yaml
from copy import deepcopy

try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import Loader as YamlLoader, Dumper as YamlDumper

class Config:

    def __init__(self):
        self.data = None

    def read(self, stream):
        self.data = yaml.load(stream, Loader=YamlLoader)
        meta = self.get_meta()
        if not "version" in meta:
            raise Exception('Config missing version')
        if not meta["version"] == 0:
            raise Exception('Unsupported config version')

    def export(self):
        return yaml.dump(self.data, default_flow_style=False)

    def get_secrets(self, decrypt=None):
        secrets = self.data['secrets_encrypted']
        if decrypt is not None:
            secrets = deepcopy(secrets)
            self._decrypt(secrets, decrypt)
        return secrets

    def _decrypt(self, obj, vault, path=[]):
        for k in obj.keys():
            path.append(k)
            if type(obj[k]) is dict:
                self._decrypt(obj[k], vault, path)
            else:
                obj[k] = vault.resolve(self, ".".join(path))
            path.pop()

    def get_meta(self):
        return self.data['meta']

    def get_transform_config(self, format):
        if not format in self.data['transform']:
            raise Exception('Config does not have transform definition for format: ' + format)

        return self.data['transform'][format]

    def get_vault_config(self, vault):
        if not vault in self.data['vault']:
            raise Exception('Config does not have config for vault: ' + vault)

        return self.data['vault'][vault]

    def get_merged(self, decrypt=None):
        return Config._merge_dicts(self.data['config'], self.get_secrets(decrypt))

    def _merge_dicts(a, b, path=None):
        # https://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    Config._merge_dicts(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a
