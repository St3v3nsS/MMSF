#!/usr/bin/python3

from json import loads
import os
import platform
import subprocess
from subprocess import DEVNULL, PIPE
import sys
from bs4 import BeautifulSoup
from colorama import Fore
import requests
from Classes.utils import quit
from Classes.constants import Constants

class Installer:
	def __init__(self, forced=False) -> None:
		self.packages = ['docker', 'apktool', 'ubersigner', 'java', 'reflutter', 'objection', 'frida', 'abe', 'zipalign', 'drozer']
		self._forced = forced
		self.__init_dirs()

	def __mkdir(self, path):
		if not os.path.isdir(path):
			try:
				os.mkdir(path)
			except OSError as e:
				print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)

	def __init_dirs(self):
		print(Fore.YELLOW + '[*] Initiating directories' + Fore.RESET)
		for path in (Constants):
			if path.name.startswith('DIR_'):
				self.__mkdir(path.value)

	@property
	def forced(self):
		return self._forced

	@forced.setter
	def forced(self, forced):
		self._forced = forced

	def _is_sudo(self):
		if os.getuid() == 0:
			return True
		return False

	def install_packages(self):
		# if not self._is_sudo():
		#     print(Fore.RED + '[-] sudo required!'  + Fore.RESET)
		#     quit()
		for package in self.packages:
			self._install(package)

	def _install(self, package):
		if package == "apktool":
			self._install_apktool()
		elif package == "abe":
			self._install_abe()
		elif package == "ubersigner":
			self._install_ubersigner()
		elif package == "java":
			self._install_java()
		elif package == "drozer":
			self._install_drozer()
		elif package == "reflutter":
			self._install_reflutter()
		elif package == "objection":
			self._install_objection()
		elif package == "frida":
			self._install_frida_server()
			self._install_frida_client()
		elif package == "zipalign":
			self._install_zipalign()
		elif package == "docker":
			self._install_docker()
		
	def _check_installed(self, cmd):
		def is_zipalign_installed():
			# Check if zipalign is available in the system's PATH
			try:
				p = subprocess.run('zipalign', stderr=subprocess.PIPE, stdout=subprocess.PIPE)
				print(Fore.GREEN + '[+] Installed' + Fore.RESET)
				return True
			except:
				# Check common directories for zipalign
				for directory in Constants.ZIPALIGN_COMMON_DIRECTORIES.value:
					cmd = ['find', os.path.expanduser(directory), '-name', 'zipalign']
					p = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
					if "No such file or directory" in p.stderr.decode() and "No such file or directory" in p.stdout.decode() or len(p.stdout.decode()) == 0:
						pass
					else:
						zipalign = p.stdout.splitlines()[0]
						print(Fore.BLUE + f'[*] Found the zipalign at {zipalign}' + Fore.RESET)
						print(Fore.GREEN + '[+] Installed' + Fore.RESET)
						return True
				
				return False
			
		def is_drozer_installed():
			image_name = 'fsecurelabs/drozer'
			try:
				# Run the `docker images` command to list installed images
				output = subprocess.check_output(["docker", "images", image_name], universal_newlines=True)
				# Check if the image is in the output
				return image_name in output
			except subprocess.CalledProcessError as e:
				# If an error occurs (e.g., Docker not installed), return False
				return False
		
		try:
			print(Fore.BLUE + '[*] Checking for ' + cmd + Fore.RESET)
			if cmd == "zipalign":
				return is_zipalign_installed()
			elif cmd == "drozer":
				return is_drozer_installed()
			p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
			if 'Unable to find image' in p.stderr.decode() or 'Unable to access jarfile' in p.stderr.decode() or 'command not found' in p.stderr.decode().lower():
				print(Fore.RED + '[-] Not installed ' + Fore.RESET )
				return False
			print(Fore.GREEN + '[+] Installed' + Fore.RESET)
			return True
		except Exception:
			print(Fore.RED + f'[-] {cmd} not found' + Fore.RESET)
			return False

	def _install_apktool(self):
		installed = self._check_installed('apktool')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			resp = requests.get("https://api.github.com/repos/iBotPeaches/Apktool/releases/latest")
			latest = loads(resp.content)['tag_name'][1:]
			jar_url = f'https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_{latest}.jar'
			apktool_jar = requests.get(jar_url)
			open(Constants.APKTOOL_JAR_PATH.value, 'wb').write(apktool_jar.content)
			apktool_wrapper_url = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool'
			apktool = requests.get(apktool_wrapper_url)
			open(Constants.APKTOOL_PATH.value, 'wb').write(apktool.content)
			subprocess.run(['chmod', '+x', Constants.APKTOOL_JAR_PATH.value], stdout=DEVNULL, stderr=DEVNULL)
			subprocess.run(['chmod', '+x', Constants.APKTOOL_PATH.value], stdout=DEVNULL, stderr=DEVNULL)

	def _install_ubersigner(self):
		installed = self._check_installed(Constants.UBERSIGNER.value)
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ubersigner' + Fore.RESET)
			url = "https://github.com/patrickfav/uber-apk-signer/releases"
			page = requests.get(f"{url}")
			soup = BeautifulSoup(page.content, "html.parser")
			classes = soup.find_all("a", class_="Link--primary")
			latest = ""
			for class_ in classes:
				if class_.text.startswith("v"):
					latest = class_.text
					break
			jar_url = f'{url}/download/{latest}/uber-apk-signer-{latest[1:]}.jar'
			print(jar_url)
			jar_file = requests.get(jar_url)
			open(Constants.UBERSIGNER_PATH.value, 'wb').write(jar_file.content)
			p = subprocess.run(Constants.UBERSIGNER.value.split(), stdout=PIPE, stderr=PIPE)
			if "Error" in p.stderr.decode():
				print(Fore.RED + '[-] Some error occured, please manually install it from https://github.com/patrickfav/uber-apk-signer/releases' + Fore.RESET)
			else:
				print(Fore.GREEN + '[+] Installed' + Fore.RESET)

	def _install_zipalign(self):
		installed = self._check_installed('zipalign')
		if not installed or self._forced:
			if (platform.system() == "Darwin"):
				cmd = f'find {os.path.expanduser("~")}/Library/Android/sdk/build-tools -name "zipalign"'
				p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
				cmd2 = f'find /Library/Android/sdk/build-tools -name "zipalign"'
				p1 = subprocess.run(cmd2.split(), stderr=PIPE, stdout=PIPE)
				if "No such file or directory" in p.stderr.decode() or "No such file or directory" in p1.stderr.decode():
					print(Fore.RED + '[-] Zipalign was not found. Please manually install it or export the path' + Fore.RED)
					quit()
				else:
					zipalign = p.stdout.splitlines()[0]
					print(Fore.BLUE + f'[*] Found the zipalign at {zipalign}' + Fore.RESET)
					installed = True
			else:
				print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
				subprocess.run(['sudo', 'apt-get', 'install','zipalign'])

	def _install_java(self):
		installed = self._check_installed('java')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			subprocess.run(['sudo', 'apt-get', 'install','default-jdk'])
			subprocess.run(['sudo', 'apt-get', 'instal', 'default-jre'])

	def _install_drozer(self):
		installed = self._check_installed('drozer')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			# subprocess.check_output(['docker', 'buildx', 'create', '--use'])
			# p = subprocess.run(f'docker buildx build --platform=linux/amd64,linux/arm64/v8  --rm -t fsecure/drozer -f {os.getcwd()}/docker_files/drozer/Dockerfile .'.split(), stderr=PIPE, stdout=PIPE)
			p = subprocess.run('docker pull fsecurelabs/drozer'.split(), stderr=PIPE, stdout=PIPE)
			if 'Successfully tagged fsecure/drozer:latest' in p.stdout.decode() or 'Downloaded newer image for fsecurelabs/drozer:latest' in p.stdout.decode():
				print(Fore.GREEN + '[*] Successfully installed drozer'  + Fore.RESET)
			else:
				print(Fore.RED + p.stderr.decode() + Fore.RESET)
		else:
			print(Fore.GREEN + '[+] Installed' + Fore.RESET)
	def _install_reflutter(self):
		installed = self._check_installed('reflutter')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			cmd = 'pipx install reflutter --force'
			subprocess.run(cmd.split(), stderr=DEVNULL, stdout=DEVNULL)

	def _install_objection(self):
		installed = self._check_installed('objection')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			cmd = "pipx install objection --force"
			p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
			print(p.stderr)
			print(p.stdout)

	def _check_frida_server(self):
		p = subprocess.run([Constants.ADB.value, 'shell', 'ls /tmp/frida-server'], capture_output=True)
		if "No such file" in p.stderr.decode() or "No such file" in p.stdout.decode():
			p1 = subprocess.run([Constants.ADB.value, 'shell', 'ls /data/local/tmp/frida-server'], capture_output=True)
			if "No such file" in p1.stderr.decode() or "No such file" in p1.stdout.decode():
				return False
		return True

	def _install_frida_client(self):
		installed = self._check_installed('frida')
		if not installed or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			subprocess.run('pipx install frida-tools --force'.split(), stderr=DEVNULL, stdout=DEVNULL)

	def _install_frida_server(self):
		installed_server = self._check_frida_server()
		frida_path = os.path.join(Constants.DIR_UTILS_PATH.value, 'frida-server')
		if not installed_server or self._forced:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			try:
				abi = subprocess.run([Constants.ADB.value, 'shell', 'getprop ro.product.cpu.abi'], stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[0]
				print(Fore.GREEN + f'[*] Downloading frida-server for {abi}' + Fore.RESET)
			except IndexError as e:
				print(Fore.RED + '[-] Device not running. Power on the device first... Exitting...' + Fore.RESET)
				quit()
			url = "https://github.com/frida/frida/releases"
			page = requests.get(url)
			soup = BeautifulSoup(page.content, "html.parser")
			classes = soup.find_all("a", class_="Link--primary")
			latest_ver = ""
			for class_ in classes:
				if class_.text.startswith("Frida"):
					latest_ver = class_.text.split(" ")[1]
					break
			file_to_download = url + "/download/" + latest_ver + "/frida-server-" + latest_ver + "-android-" + abi + ".xz"
			frida_server = requests.get(file_to_download)
			frida_server_xz_path = frida_path + '.xz'
			open(frida_server_xz_path, 'wb').write(frida_server.content)

			# Decompress frida server and push it to the mobile
			print(Fore.GREEN + f'[*] Decompressing the file and installing to device' + Fore.RESET)
			subprocess.run(['xz', '-f', '-d', frida_server_xz_path])
			subprocess.run([Constants.ADB.value, 'push', frida_path, '/tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)
			subprocess.run([Constants.ADB.value, 'shell', 'chmod +x /tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)

	def _install_abe(self):
		abe_cmd = f'java -jar {os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar")}'
		installed = self._check_installed(abe_cmd)
		if self.forced or not installed:
			print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
			url = "https://github.com/nelenkov/android-backup-extractor/releases/"
			page = requests.get(url)
			soup = BeautifulSoup(page.content, "html.parser")
			classes = soup.find_all("a", class_="Link--primary")
			latest_ver = ""
			for class_ in classes:
				if class_.text.startswith("master-"):
					latest_ver = class_.text.split(":")[0]
					print(Fore.GREEN + "[+] Downloading abe.jar... " + Fore.RESET)
					print(os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar"))
					if not os.path.isdir(Constants.DIR_UTILS_PATH.value):
						try:
							print(Fore.YELLOW + f"[*] Creating directory in {Constants.DIR_UTILS_PATH.value}")
							os.makedirs(Constants.DIR_UTILS_PATH.value)
						except OSError as e:
							print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)
					new_url = f"https://github.com/nelenkov/android-backup-extractor/releases/download/{latest_ver}/abe.jar"
					open(os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar"), "wb").write(requests.get(new_url).content)
					break

	def _install_docker(self):
		installed = self._check_installed("docker --version")
		if self.forced or not installed:
			def install_docker_ubuntu():
				try:
					# Update the package list for upgrades and new package installations
					subprocess.check_call(['sudo', 'apt', 'update'])
					
					# Install required dependencies
					subprocess.check_call(['sudo', 'apt', 'install', '-y', 'apt-transport-https', 'ca-certificates', 'curl', 'software-properties-common'])
					
					# Add Docker's official GPG key
					curl_process = subprocess.Popen(['curl', '-fsSL', 'https://download.docker.com/linux/ubuntu/gpg'], stdout=subprocess.PIPE)
					gpg_process = subprocess.Popen(['sudo', 'gpg', '--dearmor', '-o', '/usr/share/keyrings/docker-archive-keyring.gpg'], stdin=curl_process.stdout)
					gpg_process.communicate()  # Wait for the processes to finish                    
					
					# Set up the stable Docker repository
					try:
						subprocess.check_call(['sudo', 'curl', '-fsSL', 'https://download.docker.com/linux/ubuntu/gpg', '|', 'sudo', 'gpg', '--dearmor', '-o', '/usr/share/keyrings/docker-archive-keyring.gpg'])
					except subprocess.CalledProcessError as e:
						print(f"An error occurred while adding Docker's GPG key: {e}")

					# Create a Docker repository file
					docker_repo = """
					deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable
					"""
					try:
						subprocess.check_call(['sudo', 'sh', '-c', f'echo "{docker_repo}" > /etc/apt/sources.list.d/docker.list'])
					except subprocess.CalledProcessError as e:
						print(f"An error occurred while creating the Docker repository file: {e}")


					# Update the package list
					try:
						subprocess.check_call(['sudo', 'apt', 'update'])
					except subprocess.CalledProcessError as e:
						print(f"An error occurred while updating the package list: {e}")                    
										# Update the package list again
					subprocess.check_call(['sudo', 'apt', 'update'])
					
					# Install Docker
					subprocess.check_call(['sudo', 'apt', 'install', '-y', 'docker-ce', 'docker-ce-cli', 'containerd.io'])
					
					# Download the buildx binary
					docker_buildx_url = "https://github.com/docker/buildx/releases"

					try:
						# Send an HTTP GET request to the releases page
						page = requests.get(docker_buildx_url)
						page.raise_for_status()

						# Parse the HTML content of the page
						soup = BeautifulSoup(page.content, "html.parser")

						# Find all <a> elements with class "Link--primary"
						link_elements = soup.find_all("a", class_="Link--primary")

						# Search for release versions in the text of the link elements
						latest = ""
						for class_ in link_elements:
							if class_.text.startswith("v"):
								latest = class_.text
								break
						buildx_version = latest
						print(f"The latest version of buildx is: {latest}")
						subprocess.check_output(['curl', '-L', '-o', '/tmp/buildx', f'https://github.com/docker/buildx/releases/download/{buildx_version}/buildx-{buildx_version}.linux-amd64'])


					except requests.exceptions.RequestException as e:
						print(f"An error occurred while fetching the page: {e}")
					except Exception as e:
						print(f"An error occurred: {e}")
					
					# Make the binary executable
					subprocess.check_output(['chmod', '+x', '/tmp/buildx'])
					
					# Move the binary to a directory in the PATH
					subprocess.check_output(['sudo', 'mv', '/tmp/buildx', '/usr/local/bin/buildx'])
					
					# Verify the installation
					subprocess.check_output(['buildx', 'version'])
					
					print(Fore.GREEN + "[+] Docker has been installed successfully." + Fore.RESET)
				except subprocess.CalledProcessError as e:
					print(Fore.RED + f"[-] An error occurred: {e}" + Fore.RESET)

			def install_docker_macbook():
				def install_homebrew():
					try:
						# Install Homebrew
						subprocess.check_call(['/bin/bash', '-c', '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)'])
						print(Fore.GREEN + "[+] Homebrew has been installed successfully." + Fore.RESET)
					except subprocess.CalledProcessError as e:
						print(Fore.RED + f"[-] An error occurred while installing Homebrew: {e}"+ Fore.RESET)

				def install_docker():
					try:
						# Install Docker using Homebrew
						subprocess.check_call(['brew', 'install', 'docker'])
										# Check if Docker Desktop is installed
						subprocess.check_output(['docker', '--version'])
						
						# Enable experimental features in Docker Desktop
						subprocess.check_output(['docker', 'config', 'set', 'core.experimental', 'enabled'])
						
						# Create a new builder instance
						subprocess.check_output(['docker', 'buildx', 'create', '--use'])
						print(Fore.GREEN + "[+] Docker has been installed successfully."+ Fore.RESET)
					except subprocess.CalledProcessError as e:
						print(Fore.RED + f"[-] An error occurred while installing Docker: {e}"+ Fore.RESET)

				# Check if Homebrew is already installed
				try:
					subprocess.check_output(['brew', '--version'])
				except subprocess.CalledProcessError:
					print(Fore.RED + f"[-] Homebrew is not installed. Installing Homebrew..."+ Fore.RESET)
					install_homebrew()

				# Install Docker using Homebrew
				install_docker()

			system_name = platform.system()
			if system_name == "Darwin":
				print(Fore.YELLOW + '[*] Installing docker' + Fore.RESET)
				install_docker_macbook()
			elif system_name == "Linux":
				print(Fore.YELLOW + '[*] Installing docker' + Fore.RESET)
				install_docker_ubuntu()
			else:
				print(Fore.RED + f"[-] The system is {system_name}, which is not macOS or Ubuntu." + Fore.RESET)
				quit()

if __name__ == "__main__":
	installer = Installer()
	if len(sys.argv) > 1:
		if sys.argv[1] == "apktool":
			installer.forced = True
			installer._install_apktool()
		elif sys.argv[1] == "ubersigner":
			installer.forced = True
			installer._install_ubersigner()
		elif sys.argv[1] == "java":
			installer.forced = True
			installer._install_java()
		elif sys.argv[1] == "drozer":
			installer.forced = True
			installer._install_drozer()
		elif sys.argv[1] == "reflutter":
			installer.forced = True
			installer._install_reflutter()
		elif sys.argv[1] == "objection":
			installer.forced = True
			installer._install_objection()
		elif sys.argv[1] == "frida_client":
			installer.forced = True
			installer._install_frida_client()
		elif sys.argv[1] == "frida_server":
			installer.forced = True
			installer._install_frida_server()
		elif sys.argv[1] == "abe":
			installer.forced = True
			installer._install_abe()
		elif sys.argv[1] == "docker":
			installer.forced = True
			installer._install_docker()
		elif sys.argv[1] == "zipalign":
			installer.forced = True
			installer._install_zipalign()
	else:
		installer.install_packages()