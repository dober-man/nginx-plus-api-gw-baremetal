#!/usr/bin/env python3

import os
import subprocess
import sys

def run_command(command):
    """ Run a shell command and print its output """
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)
    return result.stdout, result.stderr

def main(cert_file, key_file):
    # Step 1: Create the /etc/ssl/nginx directory
    run_command("sudo mkdir -p /etc/ssl/nginx")

    # Step 2: Copy cert and key to the /etc/ssl/nginx directory
    run_command(f"sudo cp {cert_file} /etc/ssl/nginx/nginx-repo.crt")
    run_command(f"sudo cp {key_file} /etc/ssl/nginx/nginx-repo.key")

    # Step 3: Install the prerequisite packages
    run_command("sudo apt-get install -y apt-transport-https lsb-release ca-certificates wget ubuntu-keyring")

    # Step 4: Download and add NGINX signing key
    run_command("wget -qO - https://cs.nginx.com/static/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null")

    # Step 5: Download and add App Protect security updates signing key
    run_command("wget -qO - https://cs.nginx.com/static/keys/app-protect-security-updates.key | gpg --dearmor | sudo tee /usr/share/keyrings/app-protect-security-updates.gpg >/dev/null")

    # Step 6: Add NGINX+ Repo
    run_command("printf \"deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://pkgs.nginx.com/plus/ubuntu `lsb_release -cs` nginx-plus\n\" | sudo tee /etc/apt/sources.list.d/nginx-plus.list")

    # Step 7: Add NGINX App Protect Repo
    run_command("printf \"deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://pkgs.nginx.com/app-protect/ubuntu `lsb_release -cs` nginx-plus\n\" | sudo tee /etc/apt/sources.list.d/nginx-app-protect.list")
    run_command("printf \"deb [signed-by=/usr/share/keyrings/app-protect-security-updates.gpg] https://pkgs.nginx.com/app-protect-security-updates/ubuntu `lsb_release -cs` nginx-plus\n\" | sudo tee -a /etc/apt/sources.list.d/nginx-app-protect.list")

    # Step 8: Download the nginx-plus apt configuration
    run_command("sudo wget -P /etc/apt/apt.conf.d https://cs.nginx.com/static/files/90pkgs-nginx")

    # Step 9: Update repository information
    run_command("sudo apt-get update")

    # Step 10: Install NGINX+
    run_command("sudo apt-get install -y nginx-plus")

    # Step 11: Install App Protect & Signatures
    run_command("sudo apt-get install -y app-protect app-protect-attack-signatures")

    # Step 12: Check NGINX+ version
    stdout, stderr = run_command("nginx -v 2>&1")
    print("NGINX+ installation verification:")
    print(stdout or stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./setup_nginx.py <path_to_cert_file> <path_to_key_file>")
        sys.exit(1)
    
    cert_file = sys.argv[1]
    key_file = sys.argv[2]

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Error: Certificate or key file does not exist.")
        sys.exit(1)
    
    main(cert_file, key_file)
