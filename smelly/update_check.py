#!/usr/bin/env python3
# License: GPLv3 Copyright: 2019, anders Goyal <anders at backbiter-no.net>

import os
import subprocess
import time
from contextlib import suppress
from typing import Dict, NamedTuple, Optional, Tuple
from urllib.request import urlopen

from .config import atomic_save
from .constants import Version, cache_dir, clear_handled_signals, smelly_exe, version, website_url
from .fast_data_types import add_timer, get_boss, monitor_pid
from .notify import notify
from .utils import log_error, open_url

CHANGELOG_URL = website_url('changelog')
RELEASED_VERSION_URL = website_url() + 'current-version.txt'
CHECK_INTERVAL = 24 * 60 * 60.0


class Notification(NamedTuple):
    version: Version
    time_of_last_notification: float
    notification_count: int


def notification_activated() -> None:
    open_url(CHANGELOG_URL)


def version_notification_log() -> str:
    override = getattr(version_notification_log, 'override', None)
    if isinstance(override, str):
        return override
    return os.path.join(cache_dir(), 'new-version-notifications-1.txt')


def notify_new_version(release_version: Version) -> None:
    notify('smelly update available!', 'smelly version {} released'.format(
        '.'.join(map(str, release_version))), identifier='new-version', )


def get_released_version() -> str:
    try:
        raw = urlopen(RELEASED_VERSION_URL).read().decode('utf-8').strip()
    except Exception:
        raw = '0.0.0'
    return str(raw)


def parse_line(line: str) -> Notification:
    parts = line.split(',')
    version, timestamp, count = parts
    parts = version.split('.')
    v = Version(int(parts[0]), int(parts[1]), int(parts[2]))
    return Notification(v, float(timestamp), int(count))


def read_cache() -> Dict[Version, Notification]:
    notified_versions = {}
    with suppress(FileNotFoundError):
        with open(version_notification_log()) as f:
            for line in f:
                try:
                    n = parse_line(line)
                except Exception:
                    continue
                notified_versions[n.version] = n
    return notified_versions


def already_notified(version: Tuple[int, int, int]) -> bool:
    notified_versions = read_cache()
    return version in notified_versions


def save_notification(version: Version) -> None:
    notified_versions = read_cache()
    if version in notified_versions:
        v = notified_versions[version]
        notified_versions[version] = v._replace(
            time_of_last_notification=time.time(),
            notification_count=v.notification_count + 1)
    else:
        notified_versions[version] = Notification(version, time.time(), 1)
    lines = []
    for version in sorted(notified_versions):
        n = notified_versions[version]
        lines.append(
            '{},{},{}'.format(
                '.'.join(map(str, n.version)),
                n.time_of_last_notification, n.notification_count))
    atomic_save('\n'.join(lines).encode('utf-8'), version_notification_log())


def process_current_release(raw: str) -> None:
    release_version = Version(*tuple(map(int, raw.split('.'))))
    if release_version > version and not already_notified(release_version):
        save_notification(release_version)
        notify_new_version(release_version)


def run_worker() -> None:
    import random
    import time

    time.sleep(random.randint(1000, 4000) / 1000)
    with suppress(BrokenPipeError):  # happens if parent process is killed before us
        print(get_released_version())


def update_check() -> bool:
    try:
        p = subprocess.Popen(
            [smelly_exe(),
             '+runpy',
             'from smelly.update_check import run_worker; run_worker()'],
            stdout=subprocess.PIPE, preexec_fn=clear_handled_signals)
    except OSError as e:
        log_error(f'Failed to run smelly for update check, with error: {e}')
        return False
    monitor_pid(p.pid)
    get_boss().set_update_check_process(p)
    return True


def update_check_callback(timer_id: Optional[int]) -> None:
    update_check()


def run_update_check(interval: float = CHECK_INTERVAL) -> None:
    if update_check():
        add_timer(update_check_callback, interval)
