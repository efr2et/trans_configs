import logging

class Stack:

    def __init__(self, vaults):
        self.logger = logging.getLogger("configs")
        self.vaults = vaults

    def resolve(self, config, path):

        for vault in self.vaults:
            result = vault.resolve(config, path)
            if result is not None:
                return result

        return None
