import fcntl
import ipaddress
import json
import logging
import logging.handlers
import os
import selectors
import signal
import socket
import subprocess
from pathlib import Path
from typing import Any

from config import load_config

MODULE = Path(__file__).resolve().parent


def interface_addresses(
    interfaces: list[dict[str, Any]], dev_name: str, network: ipaddress.IPv4Network
) -> tuple[str, ...]:
    addresses = []
    for interface in interfaces:
        if interface["ifname"] != dev_name or "UP" not in interface["flags"]:
            continue
        for entry in interface["addr_info"]:
            if (
                entry["family"] == "inet"
                and ipaddress.IPv4Address(entry["local"]) in network
            ):
                addresses.append(f"{entry['local']}/{entry['prefixlen']}")
    return tuple(sorted(addresses))


if __name__ == "__main__":
    os.umask(0o077)
    dev_name, network, settings = load_config()
    STATE = Path(settings["state_dir"])
    PREFIX = Path(settings["termux_prefix"])
    lock = (STATE / "run/module.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.handlers.RotatingFileHandler(
                STATE / "log/module.log", maxBytes=262144, backupCount=1
            )
        ],
    )
    child: subprocess.Popen[bytes] | None = None

    def stop_server() -> None:
        global child
        if child is not None:
            # This session contains only the smbd and helpers started here.
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass  # The child may have exited before the address event was handled.
            child.wait(timeout=15)
            child = None
            logging.info("Samba stopped")

    def start_server(addresses: tuple[str, ...]) -> None:
        global child
        version = subprocess.check_output(
            [PREFIX / "bin/smbd", "--version"], text=True
        ).strip()
        env = os.environ | {"LD_PRELOAD": str(MODULE / "libheap-untag.so")}
        child = subprocess.Popen(
            [
                PREFIX / "bin/smbd",
                "-F",
                "--no-process-group",
                "-s",
                STATE / "smb.conf",
                "--option",
                "interfaces=" + " ".join((*addresses, "127.0.0.1/8")),
                "--option",
                f"hosts allow={network} 127.0.0.0/8",
            ],
            env=env,
            start_new_session=True,
        )
        logging.info("Starting Samba %s on %s", version, ", ".join(addresses))

    # Subscribe before reading addresses so changes during startup are not lost.
    events = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
    events.bind((0, 1 | 0x10))  # RTMGRP_LINK | RTMGRP_IPV4_IFADDR
    wake_read, wake_write = socket.socketpair()
    wake_write.setblocking(False)
    signal.set_wakeup_fd(wake_write.fileno())
    for signum in (signal.SIGCHLD, signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: None)
    selector = selectors.DefaultSelector()
    selector.register(events, selectors.EVENT_READ)
    selector.register(wake_read, selectors.EVENT_READ)
    current = (0, (), network)
    refresh = True
    try:
        # A manual daemon must be stopped explicitly before handing ownership over.
        probe = subprocess.run(["/system/bin/pidof", "smbd"], capture_output=True)
        if probe.returncode == 0:
            raise RuntimeError(
                "An smbd instance is already running; leaving it untouched"
            )
        logging.info("Waiting for network interface events")
        while not (MODULE / "disable").exists():
            if refresh:
                # Interface events also refresh settings after configuration changes.
                dev_name, network, _ = load_config()
                interfaces = json.loads(
                    subprocess.check_output(
                        ["/system/bin/ip", "-j", "-4", "address", "show"], text=True
                    )
                )
                addresses = interface_addresses(interfaces, dev_name, network)
                index = next(
                    (i["ifindex"] for i in interfaces if i["ifname"] == dev_name), 0
                )
                # Interface recreation or access subnet changes require a new binding.
                binding = (index, addresses, network)
                if binding != current:
                    stop_server()
                    if addresses:
                        start_server(addresses)
                    current = binding
                refresh = False
            ready = selector.select()
            shutting_down = False
            for key, _ in ready:
                if key.fileobj is events:
                    events.recv(65536)
                    refresh = True
                else:
                    signals = wake_read.recv(4096)
                    shutting_down |= any(
                        s in signals for s in (signal.SIGTERM, signal.SIGINT)
                    )
            if shutting_down:
                break
            if child is not None and child.poll() is not None:
                status = child.returncode
                child = None
                raise RuntimeError(
                    f"Samba exited with status {status}; inspect its log before restarting"
                )
    except Exception:
        logging.exception("Samba module stopped")
        raise
    finally:
        stop_server()
        signal.set_wakeup_fd(-1)
        selector.close()
        events.close()
        wake_read.close()
        wake_write.close()
        lock.close()
