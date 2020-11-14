#!/bin/bash

(
    set -x
    sudo apt update
    { echo "---------------------------------------------------"; } 2>/dev/null
    sudo apt -y full-upgrade
    { echo "---------------------------------------------------"; } 2>/dev/null
    sudo apt -y autoremove
    { echo "---------------------------------------------------"; } 2>/dev/null
    # Delete old entries:
    sudo journalctl --vacuum-size=1G
    sudo journalctl --vacuum-time=1years
)
