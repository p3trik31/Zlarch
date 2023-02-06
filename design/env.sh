#!/bin/bash




  #naklonovat git

mkdir -p /usr/share/zlarch


  #zkopirovat git do slozky

grub_on() {
  if command -v grub-install > /dev/null; then    
    echo 'GRUB_COLOR_NORMAL="white/black"' >> /etc/default/grub
    echo 'GRUB_COLOR_HIGHLIGHT="black/light-gray"' >> /etc/default/grub
    echo 'GRUB_BACKGROUND="/usr/share/backgrounds/xfce/xfce-evil.jpg"' >> /etc/default/grub

    sed -i -e 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT=""/' /etc/default/grub


  else
    # GRUB is not installed
    echo "GRUB neni stazen"
  fi
}


lightdm() {






  
}



grub_on


exit 0