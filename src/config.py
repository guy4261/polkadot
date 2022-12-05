import json
import os
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import List, Literal

from dacite import from_dict


class RepoType(Enum):
    github = auto()
    gitlab = auto()


@dataclass
class RepoConfig:
    label: str
    remote: str
    local: str
    default_branch: str
    type: Literal["github", "gitlab"]


@dataclass
class PolkadotConfig:
    repos: List[RepoConfig]


POLKADOT_CONFIG_DEFAULT_PATH = "~/.polkadot.json"
POLKADOT_CONFIG_DEFAULT_PATH = os.path.expanduser(POLKADOT_CONFIG_DEFAULT_PATH)
if not os.path.isfile(POLKADOT_CONFIG_DEFAULT_PATH):
    json.dump(
        asdict(
            PolkadotConfig(
                repos=[
                    RepoConfig(
                        label="polkadot",
                        remote="github.com/guy4261/polkadot",
                        local="~/Documents/polkadot",
                        type="github",
                        default_branch="main",
                    )
                ]
            )
        ),
        open(POLKADOT_CONFIG_DEFAULT_PATH, "w"),
    )


def load_polkadot_config(path=POLKADOT_CONFIG_DEFAULT_PATH) -> PolkadotConfig:
    path = os.path.expandvars(os.path.expanduser(path))
    obj = json.load(open(path))
    conf = from_dict(PolkadotConfig, obj)
    return conf
