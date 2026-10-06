import runpy
from pathlib import Path

from config import load_config

select = runpy.run_path(str(Path(__file__).with_name("watch.py")))[
    "interface_addresses"
]
dev_name, network, settings = load_config(
    Path(__file__).with_name("config.example.toml")
)
mesh = {
    "ifname": dev_name,
    "ifindex": 7,
    "flags": ["UP", "POINTOPOINT"],
    "addr_info": [{"family": "inet", "local": "192.0.2.10", "prefixlen": 24}],
}
assert settings["state_dir"] == "/data/adb/samba"
assert select([], dev_name, network) == ()
assert select([mesh], dev_name, network) == ("192.0.2.10/24",)
assert select([mesh | {"ifname": "wlan0"}], dev_name, network) == ()
assert select([mesh | {"flags": []}], dev_name, network) == ()
assert (
    select(
        [
            mesh
            | {
                "addr_info": [
                    {"family": "inet", "local": "198.51.100.10", "prefixlen": 24}
                ]
            }
        ],
        dev_name,
        network,
    )
    == ()
)
assert select([mesh | {"ifname": "mesh1"}], "mesh1", network) == ("192.0.2.10/24",)
assert select(
    [
        mesh
        | {"addr_info": [{"family": "inet", "local": "192.0.2.11", "prefixlen": 24}]}
    ],
    dev_name,
    network,
) == ("192.0.2.11/24",)
print("TOML interface and address selection checks passed")
