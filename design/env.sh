#!/bin/bash

echo '[zlarch-repo]' >> /etc/pacman.conf
echo 'SigLevel = Optional' >> /etc/pacman.conf
echo 'Server = http://35.210.221.91/zlarch-repo' >> /etc/pacman.conf


cp -r /Zlarch/design/zlarch/ /usr/share/
cp -r /Zlarch/design/.config /etc/skel

pacman -Sy 

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
  echo 'theme-name = Adapta' >> /etc/lightdm/lightdm-gtk-greeter.conf
  echo 'indicators = ~host;~spacer;~clock;~spacer;~layout;~language;~session;~a11y;~power' >> /etc/lightdm/lightdm-gtk-greeter.conf

}

grub_on
lightdm



users=$(ls /home)

for user in $users; do
  cp -r /etc/skel/.config /home/$user
  chown -R $user:$user /home/$user/.config
done




exit 0