#!/bin/bash

cp -r /Zlarch/design/zlarch/ /usr/share/
cp -r /Zlarch/design/.config /etc/skel

#instalace yay pomoci uctu yayuser, protoze root ucet nemuze pouzit makepkg
yay() {
  useradd -m yayuser

  cd /home/yayuser

  sudo -u git clone https://aur.archlinux.org/yay.git

  cd yay
  sudo -u yayuser makepkg -si
  sudo -u yayuser yay -Sy mugshot #adapta
  cd ~

  userdel yayuser
  rm -rf /home/yayuser
}

grub_on() {
  if command -v grub-install > /dev/null; then    
    echo 'GRUB_COLOR_NORMAL="white/black"' >> /etc/default/grub
    echo 'GRUB_COLOR_HIGHLIGHT="black/light-gray"' >> /etc/default/grub
    echo 'GRUB_BACKGROUND="/usr/share/zlarch/grub.png"' >> /etc/default/grub

    sed -i -e 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT=""/' /etc/default/grub


  else
    # GRUB is not installed
    echo "GRUB neni stazen"
  fi
}


lightdm() {
  echo 'background=/usr/share/zlarch/wallpaper.svg' >> /etc/lightdm/lightdm-gtk-greeter.conf  
}



yay
grub_on
lightdm



users=$(ls /home)

for user in $users; do
  cp -r /etc/skel/.config /home/$user
  chown -R $user:$user /home/$user/.config
done




exit 0