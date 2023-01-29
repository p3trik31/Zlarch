#!/bin/bash

mkdir /usr/share/zlarch


grub_on() {
  if command -v grub-install > /dev/null; then
    # GRUB is installed, perform desired action
    echo "GRUB is installed and running"
    echo 'GRUB_COLOR="light-orange/black"' >> /etc/default/grub
  else
    # GRUB is not installed
    echo "GRUB is not installed"
  fi
}
