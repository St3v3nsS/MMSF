"""
ReFlutter Module for MMSF
Handles SSL pinning bypass for Flutter applications
"""

import os
import subprocess
import sys
import time
from subprocess import PIPE
from colorama import Fore
import pexpect
from .constants import Constants

class reflutter:
    """
    ReFlutter integration for bypassing SSL pinning in Flutter apps
    """
    
    def __init__(self, low_power_mode=False):
        self.low_power_mode = low_power_mode
        self.config = {
            "app": None,
            "apk_path": None,
            "output_path": None,
            "burp_host": "127.0.0.1",
        }
    
    def is_flutter_app(self, apk_path):
        """
        Detect if APK is a Flutter application
        
        Args:
            apk_path: Path to the APK file
        
        Returns:
            Boolean indicating if app is Flutter-based
        """
        print(Fore.YELLOW + "[*] Checking if app is Flutter-based..." + Fore.RESET)
        
        try:
            # Determine the correct APKTool path based on OS
            import platform
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                apktool_path = Constants.APKTOOL_PATH_MACOS.value
            elif system == "linux":  # Linux
                apktool_path = Constants.APKTOOL_PATH.value
            else:  # Default to Windows or other
                apktool_path = Constants.APKTOOL_PATH.value
            
            # Use apktool to check for Flutter signatures
            temp_dir = os.path.join(os.path.dirname(apk_path), "flutter_check")
            
            cmd = f"{apktool_path} d {apk_path} -o {temp_dir} --no-src --no-res -f"
            subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE, timeout=30)
            
            # Check for Flutter indicators
            flutter_indicators = [
                os.path.join(temp_dir, "lib", "arm64-v8a", "libflutter.so"),
                os.path.join(temp_dir, "lib", "armeabi-v7a", "libflutter.so"),
                os.path.join(temp_dir, "assets", "flutter_assets")
            ]
            
            is_flutter = any(os.path.exists(indicator) for indicator in flutter_indicators)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if is_flutter:
                print(Fore.GREEN + "[+] Flutter app detected!" + Fore.RESET)
            else:
                print(Fore.YELLOW + "[-] Not a Flutter app" + Fore.RESET)
            
            return is_flutter
            
        except Exception as e:
            print(Fore.RED + f"[-] Flutter detection failed: {e}" + Fore.RESET)
            return False
    
    def patch_apk(self):
        """
        Patch Flutter APK to bypass SSL pinning
        
        Returns:
            Path to patched APK if successful, None otherwise
        """
        output_dir = None
        # Set proxy configuration
        proxy_host = self.config["burp_host"]
        
        # Set output directory
        if not output_dir:
            output_dir = os.path.dirname(self.config["apk_path"])
        
        print(Fore.CYAN + "\n" + "="*60 + Fore.RESET)
        print(Fore.YELLOW + "[*] Starting ReFlutter SSL Pinning Bypass" + Fore.RESET)
        print(Fore.CYAN + "="*60 + "\n" + Fore.RESET)
        
        print(Fore.YELLOW + f"[*] Target APK: {self.config['apk_path']}" + Fore.RESET)
        print(Fore.YELLOW + f"[*] Proxy: {proxy_host}:8083" + Fore.RESET)
        print(Fore.YELLOW + f"[*] Output: {output_dir}" + Fore.RESET)

        original_dir = os.getcwd()
        os.chdir(output_dir)
        
        try:
            child = pexpect.spawn(f'reflutter {self.config["apk_path"]}', encoding='utf-8', timeout=300)
            # child.logfile_read = sys.stdout  # Stream output to console
            
            # Wait for option prompt
            child.expect(r'\[1/2\]\?', timeout=30)
            
            # Select option 1 (Traffic monitoring and interception)
            child.sendline('1')
            
            # Wait for IP prompt
            child.expect(r'Please enter your BurpSuite IP:', timeout=30)
            
            # Send Burp Suite IP
            child.sendline(proxy_host)
            
            # Wait for the output file message
            index = child.expect([
                r'The resulting apk file: (.*\.apk)',
                pexpect.EOF,
                pexpect.TIMEOUT
            ], timeout=300)
            
            if index == 0:
                # Extract the patched APK path
                patched_apk = child.match.group(1).strip()
                print(Fore.GREEN + f"\n[+] Patched APK created: {patched_apk}" + Fore.RESET)
                
                # Wait for process to complete
                child.expect(pexpect.EOF, timeout=10)
                
                # Display Burp configuration instructions
                print(Fore.CYAN + "\n" + "="*70 + Fore.RESET)
                print(Fore.YELLOW + "    Burp Suite Configuration Required" + Fore.RESET)
                print(Fore.CYAN + "="*70 + "\n" + Fore.RESET)
                
                print(Fore.YELLOW + f"1. Configure Burp Suite proxy to listen on *:8083" + Fore.RESET)
                print(Fore.YELLOW + "   Proxy Tab → Options → Proxy Listeners → Edit → Binding Tab" + Fore.RESET)
                print(Fore.YELLOW + "\n2. Enable invisible proxying in Request Handling Tab" + Fore.RESET)
                print(Fore.YELLOW + "   Support Invisible Proxying → true" + Fore.RESET)
                
                print(Fore.CYAN + "\n" + "="*70 + "\n" + Fore.RESET)
            
            
                # Find the patched APK
                patched_apk = os.path.join(output_dir, "release.RE.apk")
                os.chdir(original_dir)
                return patched_apk
            else:
                print(Fore.RED + "[-] Could not locate patched APK" + Fore.RESET)
                return None
                
        except Exception as e:
            print(Fore.RED + f"[-] ReFlutter error: {e}" + Fore.RESET)
            return None
    
    def setup_burp_proxy(self):
        """
        Guide user through Burp Suite proxy setup
        """
        print(Fore.CYAN + "\n" + "="*60 + Fore.RESET)
        print(Fore.YELLOW + "[*] Burp Suite Proxy Setup Guide" + Fore.RESET)
        print(Fore.CYAN + "="*60 + "\n" + Fore.RESET)
        
        print(Fore.YELLOW + "1. Start Burp Suite" + Fore.RESET)
        print(Fore.YELLOW + "2. Go to Proxy → Options" + Fore.RESET)
        print(Fore.YELLOW + "3. Ensure proxy listener is on 127.0.0.1:8080" + Fore.RESET)
        print(Fore.YELLOW + "4. Enable 'Invisible Proxying' (optional but recommended)" + Fore.RESET)
        
        print(Fore.CYAN + "\n[*] Android Device Configuration:" + Fore.RESET)
        print(Fore.YELLOW + "   Run: adb shell settings put global http_proxy <PC_IP>:8080" + Fore.RESET)
        print(Fore.YELLOW + "   Or manually set WiFi proxy in Android settings" + Fore.RESET)
        
        print(Fore.CYAN + "\n[*] CA Certificate Installation:" + Fore.RESET)
        print(Fore.YELLOW + "   1. Export Burp CA cert (DER format)" + Fore.RESET)
        print(Fore.YELLOW + "   2. Push to device: adb push cacert.der /sdcard/" + Fore.RESET)
        print(Fore.YELLOW + "   3. Install via Settings → Security → Install certificate" + Fore.RESET)
        
        print(Fore.CYAN + "\n" + "="*60 + "\n" + Fore.RESET)
        
        input(Fore.YELLOW + "Press ENTER when Burp Suite is configured..." + Fore.RESET)
    
    def bypass_ssl_pinning_workflow(self, package_name, apk_path=None):
        """
        Complete workflow for SSL pinning bypass
        
        Args:
            package_name: Target app package name
            apk_path: Optional path to APK (will pull if not provided)
        
        Returns:
            Boolean indicating success
        """
        self.config["app"] = package_name
        
        print(Fore.CYAN + "\n" + "="*70 + Fore.RESET)
        print(Fore.GREEN + "    ReFlutter SSL Pinning Bypass Workflow" + Fore.RESET)
        print(Fore.CYAN + "="*70 + "\n" + Fore.RESET)
        
        # Step 1: Get APK if not provided
        if not apk_path:
            print(Fore.YELLOW + "[*] Pulling APK from device..." + Fore.RESET)
            # This would be handled by the MMSF framework now
            print(Fore.RED + "[-] APK pull functionality must be implemented in MMSF" + Fore.RESET)
            return False
        
        self.config["apk_path"] = apk_path
        self.config["output_path"] = os.path.dirname(apk_path)
        
        # Step 2: Setup Burp Suite
        self.setup_burp_proxy()
        
        # Step 3: Patch APK
        patched_apk = self.patch_apk(apk_path)
        
        if not patched_apk:
            return False
        
        print(Fore.GREEN + "[+] SSL pinning bypass completed!" + Fore.RESET)
        print(Fore.GREEN + "[+] Patched APK ready for installation: " + patched_apk + Fore.RESET)
        print(Fore.YELLOW + "[*] You can now install the patched APK using adb install" + Fore.RESET)
        
        return True
    
    def set_config(self, key, value):
        """
        Set configuration value for ReFlutter module
        
        Args:
            key: Configuration key to set
            value: Value to set for the key
        """
        if key in self.config:
            self.config[key] = value
        else:
            print(Fore.RED + f"[-] Unknown configuration key: {key}" + Fore.RESET)

    def get_config(self, key=None):
        """
        Get configuration value(s) for ReFlutter module
        
        Args:
            key: Specific configuration key to retrieve (optional)
        
        Returns:
            Configuration value or dictionary of all configs
        """
        if key:
            return self.config.get(key)
        return self.config