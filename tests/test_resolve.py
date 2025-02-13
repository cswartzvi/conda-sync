from pathlib import Path
from typing import Dict

import pytest

from conda_replicate.adapters.channel import CondaChannel
from conda_replicate.adapters.channel import LocalCondaChannel
from conda_replicate.adapters.channel import RepoData
from conda_replicate.resolve import Parameters
from conda_replicate.resolve import Resolver
from conda_replicate.resolve import UnsatisfiedRequirementsError


def make_temp_local_channel(path: Path, packages: Dict) -> CondaChannel:
    """Returns a test local channel based on a temporary directory."""

    channel = LocalCondaChannel(str(path.resolve()))
    channel.setup()
    repodata = RepoData(packages=packages)
    channel.write_repodata("noarch", repodata)
    return channel


VALID_QUERIES = {
    "valid00": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
        "final": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
    },
    "valid01": {
        "requirements": ["a >=2.0"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
        "final": {
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
    },
    "valid02": {
        "requirements": ["a 3.0 b001_0"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0-b001_0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "b001_0",
                "build_number": 0,
            },
        },
        "final": {
            "a-3.0-b001_0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "b001_0",
                "build_number": 0,
            },
        },
    },
    "valid03": {
        "requirements": ["a", "b >=2.0"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "build": "",
                "version": "1.0",
                "build_number": 0,
                "depends": ["b >=1.0,<2.0"],
                "name": "a",
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=3.0"],
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "version": "1.0",
                "build_number": 0,
                "depends": [],
                "name": "b",
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "b-3.0.tar.bz2": {
                "name": "b",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
        "final": {
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=3.0"],
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "b-3.0.tar.bz2": {
                "name": "b",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
    },
    "valid04": {
        "requirements": ["a", "b >=2.0"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=1.0,<2.0"],
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=3.0"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["c"],
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["c"],
            },
            "b-3.0.tar.bz2": {
                "depends": ["c"],
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "name": "b",
            },
            "c-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": [],
                "name": "c",
                "version": "1.0",
            },
            "c-2.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": [],
                "name": "c",
                "version": "2.0",
            },
        },
        "final": {
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=3.0"],
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["c"],
            },
            "b-3.0.tar.bz2": {
                "name": "b",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["c"],
            },
            "c-1.0.tar.bz2": {
                "name": "c",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "c-2.0.tar.bz2": {
                "name": "c",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
    },
    "valid05": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b"],
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
        "final": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
    },
    "valid06": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "d"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
        "final": {
            "a-3.0.tar.bz2": {
                "version": "3.0",
                "name": "a",
                "build": "",
                "build_number": 0,
                "depends": [],
            }
        },
    },
    "valid07": {
        "requirements": ["a"],
        "exclusions": ["a <2.0"],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
        "final": {
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
            },
        },
    },
    "valid08": {
        "requirements": ["a"],
        "exclusions": ["b <2.0"],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
        },
        "final": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b"],
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
            },
        },
    },
    "valid09-cyclic": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b"],
                "name": "a",
                "version": "1.0",
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["a"],
                "name": "b",
                "version": "1.0",
            },
        },
        "final": {
            "a-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b"],
                "name": "a",
                "version": "1.0",
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["a"],
                "name": "b",
                "version": "1.0",
            },
        },
    },
    "valid10-disposable": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": ["a"],
        "initial": {
            "a-1.0.tar.bz2": {
                "build": "",
                "version": "1.0",
                "build_number": 0,
                "depends": ["b >=1.0,<2.0"],
                "name": "a",
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0"],
            },
            "a-3.0.tar.bz2": {
                "name": "a",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=3.0"],
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "version": "1.0",
                "build_number": 0,
                "depends": [],
                "name": "b",
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "b-3.0.tar.bz2": {
                "name": "b",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
        "final": {
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "b-2.0.tar.bz2": {
                "name": "b",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "b-3.0.tar.bz2": {
                "name": "b",
                "version": "3.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
    },
    "valid10-disconnected": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "initial": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=1.0,<2.0"],
            },
            "a-2.0.tar.bz2": {
                "name": "a",
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=2.0,<3.0", "x"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "x-1.0.tar.bz2": {
                "name": "x",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["y"],
            },
            "y-1.0.tar.bz2": {
                "name": "y",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["z"],
            },
            "z-1.0.tar.bz2": {
                "name": "z",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["x"],
            },
        },
        "final": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b >=1.0,<2.0"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
        },
    },
}

INVALID_QUERIES = {
    "invalid00": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "packages": {
            "a-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b"],
                "name": "a",
                "version": "1.0",
            },
            "a-2.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b"],
                "name": "a",
                "version": "2.0",
            },
        },
    },
    "invalid01-cyclic": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "packages": {
            "a-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
                "name": "a",
                "version": "1.0",
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["a", "c"],
                "name": "b",
                "version": "1.0",
            },
        },
    },
    "invalid02": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "packages": {
            "a-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b", "d"],
                "name": "a",
                "version": "1.0",
            },
            "a-2.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
                "name": "a",
                "version": "1.0",
            },
            "b-1.0.tar.bz2": {
                "build": "",
                "build_number": 0,
                "depends": [],
                "name": "b",
                "version": "1.0",
            },
        },
    },
    "invalid03": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "packages": {
            "a-1.0.tar.bz2": {
                "name": "a",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
            },
            "b-1.0.tar.bz2": {
                "name": "b",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
            },
            "d-1.0.tar.bz2": {
                "name": "d",
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b"],
            },
        },
    },
    "invalid04": {
        "requirements": ["a"],
        "exclusions": [],
        "disposables": [],
        "packages": {
            "a-1.0.tar.bz2": {
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "c"],
                "name": "a",
            },
            "a-2.0.tar.bz2": {
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": ["b", "d", "e"],
                "name": "a",
            },
            "b-1.0.tar.bz2": {
                "version": "1.0",
                "build": "",
                "build_number": 0,
                "depends": [],
                "name": "b",
            },
            "b-2.0.tar.bz2": {
                "version": "2.0",
                "build": "",
                "build_number": 0,
                "depends": [],
                "name": "b",
            },
            "e-1.0.tar.bz2": {
                "version": "1.0",
                "name": "e",
                "build": "",
                "build_number": 0,
                "depends": ["b <=1.0"],
            },
        },
    },
}


@pytest.mark.parametrize("data", VALID_QUERIES.values())
def test_package_resolution_for_valid_queries(tmp_path_factory, data):
    initial_channel = make_temp_local_channel(
        tmp_path_factory.mktemp("initial"), data["initial"]
    )

    requirements = data["requirements"]
    exclusions = data["exclusions"]
    disposables = data["disposables"]
    subdirs = ["noarch"]
    parameters = Parameters(requirements, exclusions, disposables, subdirs)
    resolver = Resolver(initial_channel)
    actual = set(resolver.resolve(parameters))

    final_channel = make_temp_local_channel(
        tmp_path_factory.mktemp("final"), data["final"]
    )

    expected = set(final_channel.iter_packages(["noarch"]))

    assert set(expected) == set(actual)


@pytest.mark.parametrize("data", INVALID_QUERIES.values())
def test_package_resolution_for_invalid_queries(tmp_path, data):
    channel = make_temp_local_channel(tmp_path, data["packages"])
    with pytest.raises(UnsatisfiedRequirementsError):
        requirements = data["requirements"]
        exclusions = data["exclusions"]
        disposables = data["disposables"]
        subdirs = ["noarch"]
        parameters = Parameters(requirements, exclusions, disposables, subdirs)
        resolver = Resolver(channel)
        _ = set(resolver.resolve(parameters))
