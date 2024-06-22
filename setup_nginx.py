#!/usr/bin/env python3

import os
import subprocess

# Function to run a shell command
def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        exit(1)

# Create the /etc/ssl/nginx/ directory with sudo
ssl_dir = '/etc/ssl/nginx'
if not os.path.exists(ssl_dir):
    print(f"Creating directory: {ssl_dir}")
    run_command(f'sudo mkdir -p {ssl_dir}')
else:
    print(f"Directory already exists: {ssl_dir}")

# Paths to the certificate and key files in the current directory
current_dir = os.getcwd()
cert_file = os.path.join(current_dir, 'nginx-repo.crt')
key_file = os.path.join(current_dir, 'nginx-repo.key')

# Check if the files exist
if not os.path.isfile(cert_file):
    print(f"Certificate file not found: {cert_file}")
    exit(1)

if not os.path.isfile(key_file):
    print(f"Key file not found: {key_file}")
    exit(1)

# Copy nginx-repo.crt and nginx-repo.key files to the /etc/ssl/nginx/ directory with sudo
print(f"Copying {cert_file} to {ssl_dir}")
run_command(f'sudo cp {cert_file} {ssl_dir}')

print(f"Copying {key_file} to {ssl_dir}")
run_command(f'sudo cp {key_file} {ssl_dir}')

# Remove any previous NGINX repository and apt configuration files
print("Removing old NGINX repository and configuration files")
run_command('sudo rm -f /etc/apt/sources.list.d/nginx*.list')
run_command('sudo rm -f /etc/apt/sources.list.d/*app-protect*.list')
run_command('sudo rm -f /etc/apt/apt.conf.d/90pkgs-nginx')

# Install prerequisite packages
print("Installing prerequisite packages")
run_command('sudo apt-get update && sudo apt-get install -y apt-transport-https lsb-release ca-certificates gnupg2 ubuntu-keyring curl')

# Download and add the NGINX signing key using curl
print("Downloading and adding the NGINX signing key")
nginx_key_url = 'https://cs.nginx.com/static/keys/nginx_signing.key'
keyring_path = '/usr/share/keyrings/nginx-archive-keyring.gpg'
run_command(f'curl -s {nginx_key_url} | gpg --dearmor | sudo tee {keyring_path} >/dev/null')

# Download the apt configuration to /etc/apt/apt.conf.d using curl
print("Downloading the apt configuration")
config_url = 'https://cs.nginx.com/static/files/90pkgs-nginx'
config_path = '/etc/apt/apt.conf.d/90pkgs-nginx'
run_command(f'sudo curl -s -o {config_path} {config_url}')

# Verify that the downloaded key contains the proper fingerprint
print("Verifying the downloaded key")
fingerprint = "573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62"
command = f'gpg --dry-run --quiet --no-keyring --import --import-options import-show {keyring_path}'
result = subprocess.run(command, shell=True, capture_output=True, text=True)
if fingerprint in result.stdout:
    print(f"Key verification successful. Fingerprint: {fingerprint}")
else:
    print(f"Key verification failed. Removing {keyring_path}")
    run_command(f'sudo rm {keyring_path}')
    exit(1)

# Add the NGINX Plus repository
print("Adding the NGINX Plus repository")
run_command(f'printf "deb [signed-by={keyring_path}] https://pkgs.nginx.com/plus/ubuntu `lsb_release -cs` nginx-plus\\n" | sudo tee /etc/apt/sources.list.d/nginx-plus.list')

# Add the NGINX App Protect WAF v5 repository
print("Adding the NGINX App Protect WAF v5 repository")
run_command(f'printf "deb [signed-by={keyring_path}] https://pkgs.nginx.com/app-protect-x-plus/ubuntu `lsb_release -cs` nginx-plus\\n" | sudo tee /etc/apt/sources.list.d/nginx-app-protect.list')

# Install the NGINX App Protect WAF v5 package
print("Updating package list and installing NGINX App Protect WAF v5")
run_command('sudo apt-get update')
run_command('sudo apt-get install -y app-protect-module-plus')

print("Starting NGINX+ with App Protect.")
run_command('sudo systemctl start nginx')


# Function to run a shell command and return its output
def run_command(command, capture_output=False):
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            return result.stdout.strip()
        else:
            subprocess.check_call(command, shell=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        exit(1)

# Function to return app protect version
def get_app_protect_version():
    try:
        # Query the package management system for the installed version of app-protect-module-plus
        version_output = run_command('dpkg -l | grep app-protect-module-plus', capture_output=True)
        if version_output:
            version = version_output.split()[2]
            return version
        else:
            return "App Protect version not found"
    except Exception as e:
        print(f"Failed to get App Protect version: {e}")
        return "App Protect version not found"

# Display versions and status
app_protect_version = get_app_protect_version()


print("\n--- NGINX App Protect Version Information ---")
print(f"App Protect Version: {app_protect_version}")



