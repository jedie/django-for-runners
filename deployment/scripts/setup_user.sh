#!/usr/bin/env bash

if [ "$(whoami)" != "root" ]; then
    echo "Please start with 'sudo' !"
    (
      set -x
      id
      exit 1
    )
fi


set -ex

export USERNAME=${1}

adduser --disabled-password --gecos "" --home=/home/${USERNAME} ${USERNAME}
mkdir -p /home/${USERNAME}/.ssh
cp /root/.ssh/authorized_keys /home/${USERNAME}/.ssh/
chown -Rfc ${USERNAME}.${USERNAME} /home/${USERNAME}/
echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL">/etc/sudoers.d/${USERNAME}