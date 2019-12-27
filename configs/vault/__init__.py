from .aws import Aws
from .sops import Sops
from .stack import Stack

Vaults = {
    "aws": Aws,
    "sops": Sops
}
