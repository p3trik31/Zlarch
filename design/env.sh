#!/bin/bash

echo '[zlarch-repo]' >> /etc/pacman.conf
echo 'SigLevel = Optional' >> /etc/pacman.conf
echo 'Server = http://35.207.153.25/zlarch-repo/' >> /etc/pacman.conf  #vlastni repozitar


cp -r /Zlarch/design/zlarch/ /usr/share/
cp -r /Zlarch/design/.config /etc/skel

pacman -Sy mugshot #stazeni xfce4 balicku z vlastniho repozitare, protoze neni v oficialnim

grub_on() {     #uprava vzhledu pokud je nainstalovan grub
  if command -v grub-install > /dev/null; then    
    echo 'GRUB_COLOR_NORMAL="black/black"' >> /etc/default/grub
    echo 'GRUB_COLOR_HIGHLIGHT="white/dark-gray"' >> /etc/default/grub
    echo 'GRUB_BACKGROUND="/usr/share/zlarch/grub.png"' >> /etc/default/grub

    sed -i -e 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT=""/' /etc/default/grub


  else
    echo "GRUB neni stazen"
  fi
}


lightdm() {     #uprava vzhledu lightdm
  echo 'background=/usr/share/zlarch/wallpaper.svg' >> /etc/lightdm/lightdm-gtk-greeter.conf
  echo 'theme-name = Adapta' >> /etc/lightdm/lightdm-gtk-greeter.conf
  echo 'indicators = ~host;~spacer;~clock;~spacer;~layout;~language;~session;~a11y;~power' >> /etc/lightdm/lightdm-gtk-greeter.conf

}

grub_on
lightdm



users=$(ls /home)

for user in $users; do    #aplikace vzhledu pro existujici uzivatale
  cp -r /etc/skel/.config /home/$user
  chown -R $user:$user /home/$user/.config
done




exit 0