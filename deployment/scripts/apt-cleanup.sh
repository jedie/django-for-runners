#!/bin/bash

# Cleanup installed packages by using apt-mark:
#
# 1. mark all packages as "auto"
# 2. install really needed packages "manual"
# 3. call "autoremove" to deinstall all not needed packages
#
# WARNING: You may need some more packages depend on your cloud provider!



###############################################################
# Remove this lines:
echo "Adjust this script first, before you use it!"
exit 1
###############################################################



set -e

if [ "$(whoami)" != "root" ]; then
    echo "Please start with 'sudo' !"
    exit 1
fi

clear

# These packages should be installed:
PACKAGES=(
    linux-image-virtual ubuntu-minimal acpid
    qemu-guest-agent
    command-not-found
    update-manager-core
    unattended-upgrades
    openssh-server
    rsync
    lshw htop mc nano
    git make
    apt-transport-https curl gnupg-agent software-properties-common
    docker-ce docker-ce-cli containerd.io
)

(
    set -ex

    apt update

    { echo "---------------------------------------------------"; } 2>/dev/null

    # Mark all installed packages as "auto":
    apt-mark auto $(apt-mark showinstall)

    { echo "---------------------------------------------------"; } 2>/dev/null

    # Install the really needed packages:
    apt -y install "${PACKAGES[@]}"

    { echo "---------------------------------------------------"; } 2>/dev/null

    # Update all installed packages:
    apt -y full-upgrade

    { echo "---------------------------------------------------"; } 2>/dev/null

    # Deinstall all not needed packages:
    apt autoremove
)
