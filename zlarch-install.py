#zlarch 0.2
#Pacman -Sy archlinux-keyring
import json
import logging
import os
import pathlib
import time
import getpass
import archinstall


	
if os.getuid() != 0:
	print("Program potřebuje root pravomoce pro spuštění")
	exit(1)
 
 
 
  #ascii logo
print(r"""\
_______  _        _______  _______  _______          
/ ___   )( \      (  ___  )(  ____ )(  ____ \|\     /|
\/   )  || (      | (   ) || (    )|| (    \/| )   ( |
    /   )| |      | (___) || (____)|| |      | (___) |
   /   / | |      |  ___  ||     __)| |      |  ___  |
  /   /  | |      | (   ) || (\ (   | |      | (   ) |
 /   (_/\| (____/\| )   ( || ) \ \__| (____/\| )   ( |
(_______/(_______/|/     \||/   \__/(_______/|/     \|
                                   
                """)


os.system('sudo pacman -Sy archlinux-keyring --noconfirm')
#Pacman -Sy archlinux-keyring
 
 
 
 
 

# Logovani informací
# promazat
archinstall.log(f"Hardware model detected: {archinstall.sys_vendor()} {archinstall.product_name()}; UEFI mode: {archinstall.has_uefi()}", level=logging.DEBUG)
archinstall.log(f"Processor model detected: {archinstall.cpu_model()}", level=logging.DEBUG)
archinstall.log(f"Memory statistics: {archinstall.mem_available()} available out of {archinstall.mem_total()} total installed", level=logging.DEBUG)
archinstall.log(f"Virtualization detected: {archinstall.virtualization()}; is VM: {archinstall.is_vm()}", level=logging.DEBUG)
archinstall.log(f"Graphics devices detected: {archinstall.graphics_devices().keys()}", level=logging.DEBUG)
archinstall.log(f"Disk states before installing: {archinstall.disk_layouts()}", level=logging.DEBUG)



def ask_user_questions():
	"""
		First, we'll ask the user for a bunch of user input.
		Not until we're satisfied with what we want to install
		will we continue with the actual installation steps.
	"""
	
    #nastaveni cz klavesnice
	archinstall.arguments['keyboard-layout'] = 'cz'   

	# okna
	if not archinstall.arguments.get('mirror-region', None):
		archinstall.arguments['mirror-region'] = archinstall.select_mirror_regions()

	#jazyk
	archinstall.arguments['sys-language'] = 'cs_CZ'
	
	archinstall.arguments['sys-encoding'] = 'utf-8'

	# Ask which harddrives/block-devices we will install to
	# and convert them into archinstall.BlockDevice() objects.
	if archinstall.arguments.get('harddrives', None) is None:
		archinstall.arguments['harddrives'] = archinstall.select_harddrives()

	if archinstall.arguments.get('harddrives', None) is not None and archinstall.storage.get('disk_layouts', None) is None:
		archinstall.storage['disk_layouts'] = archinstall.select_disk_layout(archinstall.arguments['harddrives'], archinstall.arguments.get('advanced', False))

	# Get disk encryption password (or skip if blank)
	if archinstall.arguments['harddrives'] and archinstall.arguments.get('!encryption-password', None) is None:
		if passwd := archinstall.get_password(prompt='Enter disk encryption password (leave blank for no encryption): '):
			archinstall.arguments['!encryption-password'] = passwd

	if archinstall.arguments['harddrives'] and archinstall.arguments.get('!encryption-password', None):
		# If no partitions was marked as encrypted, but a password was supplied and we have some disks to format..
		# Then we need to identify which partitions to encrypt. This will default to / (root).
		if len(list(archinstall.encrypted_partitions(archinstall.storage['disk_layouts']))) == 0:
			archinstall.storage['disk_layouts'] = archinstall.select_encrypted_partitions(archinstall.storage['disk_layouts'], archinstall.arguments['!encryption-password'])

	# Ask which boot-loader to use (will only ask if we're in BIOS (non-efi) mode)
	if not archinstall.arguments.get("bootloader", None):
		archinstall.arguments["bootloader"] = archinstall.ask_for_bootloader(archinstall.arguments.get('advanced', False))

	if not archinstall.arguments.get('swap', None):
		archinstall.arguments['swap'] = archinstall.ask_for_swap()

	# Get the hostname for the machine
	if not archinstall.arguments.get('hostname', None):
		archinstall.arguments['hostname'] = input('hostname: ').strip(' ')

	# Ask for a root password (optional, but triggers requirement for super-user if skipped)
	if not archinstall.arguments.get('!root-password', None):
		archinstall.arguments['!root-password'] = archinstall.get_password(prompt='Enter root password (leave blank to disable root & create superuser): ')

	# Ask for additional users (super-user if root pw was not set)
	# if not archinstall.arguments.get('!root-password', None) and not archinstall.arguments.get('!superusers', None):
		archinstall.arguments['!superusers'] = archinstall.ask_for_superuser_account('Create a required super-user with sudo privileges: ', forced=True)
		users, superusers = archinstall.ask_for_additional_users('Enter a username to create an additional user (leave blank to skip & continue): ')
		archinstall.arguments['!users'] = users
		archinstall.arguments['!superusers'] = {**archinstall.arguments['!superusers'], **superusers}

	# Ask for archinstall-specific profiles (such as desktop environments etc)
	if not archinstall.arguments.get('profile', None):
		archinstall.arguments['profile'] = archinstall.select_profile()
	#archinstall.arguments['profile'] = 
	# Check the potentially selected profiles preparations to get early checks if some additional questions are needed.
	if archinstall.arguments['profile'] and archinstall.arguments['profile'].has_prep_function():
		namespace = f"{archinstall.arguments['profile'].namespace}.py"
		with archinstall.arguments['profile'].load_instructions(namespace=namespace) as imported:
			if not imported._prep_function():
				archinstall.log(' * Profile\'s preparation requirements was not fulfilled.', fg='red')
				exit(1)

	# Ask about audio server selection if one is not already set
	if not archinstall.arguments.get('audio', None):
		# The argument to ask_for_audio_selection lets the library know if it's a desktop profile
		archinstall.arguments['audio'] = archinstall.ask_for_audio_selection(archinstall.is_desktop_profile(archinstall.arguments['profile']))

	# Ask for preferred kernel:
	if not archinstall.arguments.get("kernels", None):
		archinstall.arguments['kernels'] = archinstall.select_kernel()
	
	# Ask or Call the helper function that asks the user to optionally configure a network.
	if not archinstall.arguments.get('nic', None):
		archinstall.arguments['nic'] = archinstall.ask_to_configure_network()
		if not archinstall.arguments['nic']:
			archinstall.log("No network configuration was selected. Network is going to be unavailable until configured manually!", fg="yellow")

	if not archinstall.arguments.get('timezone', None):
		archinstall.arguments['timezone'] = archinstall.ask_for_a_timezone()

	if archinstall.arguments['timezone']:
		if not archinstall.arguments.get('ntp', False):
			archinstall.arguments['ntp'] = input("Would you like to use automatic time synchronization (NTP) with the default time servers? [Y/n]: ").strip().lower() in ('y', 'yes', '')
			if archinstall.arguments['ntp']:
				archinstall.log("Hardware time and other post-configuration steps might be required in order for NTP to work. For more information, please check the Arch wiki.", fg="yellow")


def perform_filesystem_operations():
	print()
	print('This is your chosen configuration:')
	archinstall.log("-- Guided template chosen (with below config) --", level=logging.DEBUG)
	user_configuration = json.dumps({**archinstall.arguments, 'version' : archinstall.__version__} , indent=4, sort_keys=True, cls=archinstall.JSON)
	archinstall.log(user_configuration, level=logging.INFO)
	with open("/var/log/archinstall/user_configuration.json", "w") as config_file:
		config_file.write(user_configuration)
	if archinstall.storage.get('disk_layouts'):
		user_disk_layout = json.dumps(archinstall.storage['disk_layouts'], indent=4, sort_keys=True, cls=archinstall.JSON)
		archinstall.log(user_disk_layout, level=logging.INFO)
		with open("/var/log/archinstall/user_disk_layout.json", "w") as disk_layout_file:
			disk_layout_file.write(user_disk_layout)
	print()

	if archinstall.arguments.get('dry-run'):
		exit(0)

	if not archinstall.arguments.get('silent'):
		input('Press Enter to continue.')

	"""
		Issue a final warning before we continue with something un-revertable.
		We mention the drive one last time, and count from 5 to 0.
	"""

	if archinstall.arguments.get('harddrives', None):
		print(f" ! Formatting {archinstall.arguments['harddrives']} in ", end='')
		archinstall.do_countdown()

		"""
			Setup the blockdevice, filesystem (and optionally encryption).
			Once that's done, we'll hand over to perform_installation()
		"""
		mode = archinstall.GPT
		if archinstall.has_uefi() is False:
			mode = archinstall.MBR

		for drive in archinstall.arguments.get('harddrives', []):
			if archinstall.storage.get('disk_layouts', {}).get(drive.path):
				with archinstall.Filesystem(drive, mode) as fs:
					fs.load_layout(archinstall.storage['disk_layouts'][drive.path])

def perform_installation(mountpoint):
	user_credentials = {}
	if archinstall.arguments.get('!users'):
		user_credentials["!users"] = archinstall.arguments['!users']
	if archinstall.arguments.get('!superusers'):
		user_credentials["!superusers"] = archinstall.arguments['!superusers']
	if archinstall.arguments.get('!encryption-password'):
		user_credentials["!encryption-password"] = archinstall.arguments['!encryption-password']

	with open("/var/log/archinstall/user_credentials.json", "w") as config_file:
		config_file.write(json.dumps(user_credentials, indent=4, sort_keys=True, cls=archinstall.UNSAFE_JSON))

	"""
	Performs the installation steps on a block device.
	Only requirement is that the block devices are
	formatted and setup prior to entering this function.
	"""
	with archinstall.Installer(mountpoint, kernels=archinstall.arguments.get('kernels', 'linux')) as installation:
		# Mount all the drives to the desired mountpoint
		# This *can* be done outside of the installation, but the installer can deal with it.
		if archinstall.storage.get('disk_layouts'):
			installation.mount_ordered_layout(archinstall.storage['disk_layouts'])

		# Placing /boot check during installation because this will catch both re-use and wipe scenarios.
		for partition in installation.partitions:
			if partition.mountpoint == installation.target + '/boot':
				if partition.size <= 0.25: # in GB
					raise archinstall.DiskError(f"The selected /boot partition in use is not large enough to properly install a boot loader. Please resize it to at least 256MB and re-run the installation.")

		# if len(mirrors):
		# Certain services might be running that affects the system during installation.
		# Currently, only one such service is "reflector.service" which updates /etc/pacman.d/mirrorlist
		# We need to wait for it before we continue since we opted in to use a custom mirror/region.
		installation.log('Waiting for automatic mirror selection (reflector) to complete.', level=logging.INFO)
		while archinstall.service_state('reflector') not in ('dead', 'failed'):
			time.sleep(1)
		# Set mirrors used by pacstrap (outside of installation)
		if archinstall.arguments.get('mirror-region', None):
			archinstall.use_mirrors(archinstall.arguments['mirror-region'])  # Set the mirrors for the live medium
		if installation.minimal_installation():
			installation.set_locale(archinstall.arguments['sys-language'], archinstall.arguments['sys-encoding'].upper())
			installation.set_hostname(archinstall.arguments['hostname'])
			if archinstall.arguments['mirror-region'].get("mirrors", None) is not None:
				installation.set_mirrors(archinstall.arguments['mirror-region'])  # Set the mirrors in the installation medium
			if archinstall.arguments["bootloader"] == "grub-install" and archinstall.has_uefi():
				installation.add_additional_packages("grub")
			installation.add_bootloader(archinstall.arguments["bootloader"])
			if archinstall.arguments['swap']:
				installation.setup_swap('zram')

			# If user selected to copy the current ISO network configuration
			# Perform a copy of the config
			if archinstall.arguments.get('nic', {}) == 'Copy ISO network configuration to installation':
				installation.copy_iso_network_config(enable_services=True)  # Sources the ISO network configuration to the install medium.
			elif archinstall.arguments.get('nic', {}).get('NetworkManager', False):
				installation.add_additional_packages("networkmanager")
				installation.enable_service('NetworkManager.service')
			# Otherwise, if a interface was selected, configure that interface
			elif archinstall.arguments.get('nic', {}):
				installation.configure_nic(**archinstall.arguments.get('nic', {}))
				installation.enable_service('systemd-networkd')
				installation.enable_service('systemd-resolved')

			if archinstall.arguments.get('audio', None) is not None:
				installation.log(f"This audio server will be used: {archinstall.arguments.get('audio', None)}", level=logging.INFO)
				if archinstall.arguments.get('audio', None) == 'pipewire':
					print('Installing pipewire ...')

					installation.add_additional_packages(["pipewire", "pipewire-alsa", "pipewire-jack", "pipewire-media-session", "pipewire-pulse", "gst-plugin-pipewire", "libpulse"])
				elif archinstall.arguments.get('audio', None) == 'pulseaudio':
					print('Installing pulseaudio ...')
					installation.add_additional_packages("pulseaudio")
			else:
				installation.log("No audio server will be installed.", level=logging.INFO)

			if archinstall.arguments.get('packages', None) and archinstall.arguments.get('packages', None)[0] != '':
				installation.add_additional_packages(archinstall.arguments.get('packages', None))

			if archinstall.arguments.get('profile', None):
				installation.install_profile(archinstall.arguments.get('profile', None))

			for user, user_info in archinstall.arguments.get('!users', {}).items():
				installation.user_create(user, user_info["!password"], sudo=False)

			for superuser, user_info in archinstall.arguments.get('!superusers', {}).items():
				installation.user_create(superuser, user_info["!password"], sudo=True)

			if timezone := archinstall.arguments.get('timezone', None):
				installation.set_timezone(timezone)

			if archinstall.arguments.get('ntp', False):
				installation.activate_time_syncronization()

			if archinstall.accessibility_tools_in_use():
				installation.enable_espeakup()

			if (root_pw := archinstall.arguments.get('!root-password', None)) and len(root_pw):
				installation.user_set_pw('root', root_pw)

			# This step must be after profile installs to allow profiles to install language pre-requisits.
			# After which, this step will set the language both for console and x11 if x11 was installed for instance.
			installation.set_keyboard_language(archinstall.arguments['keyboard-layout'])

			if archinstall.arguments['profile'] and archinstall.arguments['profile'].has_post_install():
				with archinstall.arguments['profile'].load_instructions(namespace=f"{archinstall.arguments['profile'].namespace}.py") as imported:
					if not imported._post_install():
						archinstall.log(' * Profile\'s post configuration requirements was not fulfilled.', fg='red')
						exit(1)

		# If the user provided a list of services to be enabled, pass the list to the enable_service function.
		# Note that while it's called enable_service, it can actually take a list of services and iterate it.
		if archinstall.arguments.get('services', None):
			installation.enable_service(*archinstall.arguments['services'])

		# If the user provided custom commands to be run post-installation, execute them now.
		if archinstall.arguments.get('custom-commands', None):
			archinstall.run_custom_user_commands(archinstall.arguments['custom-commands'], installation)

		#

		print("Konfigurace Bootloaderu")
  		#archinstall.run_custom_user_commands(['sed -i -e 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT=""/' /etc/default/grub'], installation, showLog = False)
    
   		
		
		archinstall.run_custom_user_commands(['grub-mkconfig -o /boot/grub/grub.cfg'], installation, showLog = False)

		print("Pridani repozitare do pacmana") #zatim neni funkcni
		
		#archinstall.run_custom_user_commands([f'echo "[zlarch-repo]\nSigLevel = Optional DatabaseOptional\nServer = 1.1.1.1" >> /etc/pacman.conf'], installation, showLog = False)
		archinstall.run_custom_user_commands(["pacman -Sy"], installation, showLog=False)

		print("instalace balíčků")
		archinstall.run_custom_user_commands(["pacman -S git neofetch man firefox openssl-1.1 --noconfirm"], installation, showLog=False)
  
		print("Konfigurace prostředí")
		#archinstall.run_custom_user_commands(['mkdir /tmp'], installation, showLog = False)
		#archinstall.run_custom_user_commands(['cd /tmp'], installation, showLog = False)
		archinstall.run_custom_user_commands(['echo "NAME=\"Zlarch\"" > /etc/os-release'], installation, showLog = False)
		archinstall.run_custom_user_commands(['echo "VESION=1.0" >> /etc/os-release'], installation, showLog = False)
		archinstall.run_custom_user_commands(['echo "ID=Zlarch" >> /etc/os-release'], installation, showLog = False)
		archinstall.run_custom_user_commands(['echo "PRETTY_NAME=\"Zlarch_OS\"" >> /etc/os-release'], installation, showLog = False)
  
		archinstall.run_custom_user_commands(['touch pokus.sh'], installation, showLog=False)
		archinstall.run_custom_user_commands(['echo "touch idk.txt" >> pokus.sh'], installation, showLog=False)
		archinstall.run_custom_user_commands(['sh pokus.sh'], installation, showLog=False)
		
		
		
	
		
		if not archinstall.arguments.get('silent'):
			choice = input("Would you like to chroot into the newly created installation and perform post-installation configuration? [Y/n] ")
			if choice.lower() in ("y", ""):
				try:
					installation.drop_to_shell()
				except:
					pass

	# For support reasons, we'll log the disk layout post installation (crash or no crash)
	archinstall.log(f"Disk states after installing: {archinstall.disk_layouts()}", level=logging.DEBUG)





# Prikaz --Silent nebude bude se to ptat standartne
#if not archinstall.arguments.get('silent'):
#	ask_user_questions()


ask_user_questions()
perform_filesystem_operations()
perform_installation(archinstall.storage.get('MOUNT_POINT', '/mnt'))
