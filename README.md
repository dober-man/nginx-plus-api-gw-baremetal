# NGINX+ API Gateway Deploy & Config

## There are 3 sections to this guide. 

- NGINX+ App Protect Installation Script
- NGINX+ API GW config with Auth Script (basic or mTLS)
- NGINX+ API GW features - additional config examples

# NGINX+ App Protect Installation Script

## Overview

This Python script automates the installation and configuration of NGINX+ and NGINX App Protect on an Ubuntu 22.04 system. It sets up the necessary directories, copies the provided certificate and key files, installs required dependencies, and configures the repositories for NGINX+ and App Protect. Script could easily be modified to support a variety of host Operating Systems including RHEL, Debian or Alpine. 

## Prerequisites

Before running the script, ensure you have the following:

- A valid NGINX+ subscription or trial.
- The certificate and key files for NGINX+ repository access, named `nginx-repo.crt` and `nginx-repo.key`.
- An Ubuntu-based system (NAP supported and tested on Ubuntu 22.04).

**Note:** Always check NAP release notes to ensure OS support.


## Requirements

- Python 3.x
- `sudo` privileges on the system
- Internet access from Ubuntu server to download dependencies and repository keys

## Usage

### Step-by-Step Instructions

1. **Download the Script**: Save the `setup_nginx.py` script to the system you will be installing N+ and NAP on.

2. **Make the Script Executable**:
    ```bash
    chmod +x setup_nginx.py
    ```

3. **Run the Script**: Execute the script by providing the paths to your `nginx-repo.crt` and `nginx-repo.key` files.
    ```bash
    ./setup_nginx.py /path/to/nginx-repo.crt /path/to/nginx-repo.key
    ```

### Example

Assuming your certificate and key files are located in `/home/user/`, you would run:
```bash
./setup_nginx.py /home/user/nginx-repo.crt /home/user/nginx-repo.key
```
### Successful Completion

NGINX+ installation verification:
nginx version: nginx/1.25.5 (nginx-plus-r32)

# NGINX+ API GW basic config with Auth (basic or mTLS)

## Overview

This script sets up cryptographic components and configures NGINX as a Gateway for the Cats API. The user can choose between Basic Authentication and Mutual TLS (mTLS) for secure access. The script also provides an option to add other authentication methods if needed.

# Setup Script for NGINX Gateway with Authentication for Cats API

This Bash script sets up cryptographic configurations and configures NGINX as an API Gateway for the Cats API. It allows the user to select between Basic Authentication and Mutual TLS (mTLS) authentication.

## Prerequisites

- A Unix-based operating system (e.g., Ubuntu).
- NGINX installed and running.
- OpenSSL installed for cryptographic operations.
- Apache utilities installed for Basic Authentication (if chosen).

## Features

- **Certificate Management**: Creates directories and generates private keys and self-signed certificates.
- **Basic Authentication**: Option to secure the API using HTTP Basic Authentication.
- **Mutual TLS (mTLS)**: Option to secure the API using mTLS, which requires client certificates.
- **Configuration Backup**: Backups existing NGINX configuration before making changes.
- **Dynamic NGINX Configuration**: Configures NGINX based on user-selected authentication type.

## Usage

1. **Run the Script**:
    ```bash
    ./setup_nginx_gateway.sh
    ```

2. **Enter Domain**:
    - Enter your domain. This should be the FQDN that resolves to the host where NGINX is running.
    - Default: `your_domain.com`.

3. **Choose Authentication Type**:
    - Options: Basic Authentication (`a`) or mTLS Authentication (`b`).
    - Other methods like OAuth, OIDC, and LDAP can be added.

4. **Configure Upstream Server**:
    - Enter the upstream server address that NGINX will forward requests to.
    - Default: `api.thecatapi.com`.

## Script Breakdown

1. **Create Certificate Directory**:
    ```bash
    sudo mkdir -p /etc/nginx/ssl
    ```

2. **Generate Private Key**:
    ```bash
    sudo openssl genpkey -algorithm RSA -out /etc/nginx/ssl/nginx-selfsigned.key -aes256
    ```

3. **Create Self-Signed Certificate**:
    ```bash
    sudo openssl req -new -x509 -key /etc/nginx/ssl/nginx-selfsigned.key -out /etc/nginx/ssl/nginx-selfsigned.crt -days 365 -subj "/C=US/ST=New York/L=New York/O=Example Company/OU=Org/CN=$domain"
    ```

4. **Remove Key Passphrase**:
    ```bash
    sudo openssl rsa -in /etc/nginx/ssl/nginx-selfsigned.key -out /etc/nginx/ssl/nginx-selfsigned-nopass.key
    ```

5. **Backup Existing NGINX Configuration**:
    ```bash
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    ```

6. **Install Apache Utilities** (for Basic Auth):
    ```bash
    sudo apt-get install -y apache2-utils
    ```

7. **Create `.htpasswd` File** (for Basic Auth):
    ```bash
    sudo htpasswd -c /etc/nginx/.htpasswd <username>
    ```

8. **Generate Client Certificate** (for mTLS):
    ```bash
    sudo openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/client.key -out /etc/nginx/ssl/client.csr -subj "/C=US/ST=New York/L=New York/O=Client Company/OU=Org/CN=client"
    sudo openssl x509 -req -in /etc/nginx/ssl/client.csr -CA /etc/nginx/ssl/nginx-selfsigned.crt -CAkey /etc/nginx/ssl/nginx-selfsigned-nopass.key -CAcreateserial -out /etc/nginx/ssl/client.crt -days 365
    sudo openssl pkcs12 -export -out /etc/nginx/ssl/client.pfx -inkey /etc/nginx/ssl/client.key -in /etc/nginx/ssl/client.crt -certfile /etc/nginx/ssl/nginx-selfsigned.crt -password pass:your_password
    ```

9. **Set Permissions**:
    ```bash
    sudo chmod 644 /etc/nginx/ssl/client.crt
    sudo chmod 600 /etc/nginx/ssl/client.key
    sudo chown $(whoami):$(whoami) /etc/nginx/ssl/client.crt
    sudo chown $(whoami):$(whoami) /etc/nginx/ssl/client.key
    ```

10. **Configure NGINX**:
    ```bash
    sudo tee /etc/nginx/nginx.conf <<EOF
    # NGINX Configuration
    EOF
    ```

11. **Test NGINX Configuration**:
    ```bash
    sudo nginx -t
    ```

12. **Restart NGINX**:
    ```bash
    sudo systemctl restart nginx
    ```

## Testing

- **Basic Authentication**:
    ```bash
    curl -k https://$domain -u 'user:password'
    ```

- **mTLS Authentication**:
    ```bash
    curl -k --cert /etc/nginx/ssl/client.crt --key /etc/nginx/ssl/client.key https://$domain
    ```

## Notes

- Ensure that NGINX is correctly installed and that you have administrative privileges to run the script.
- The script assumes default installation paths and configurations for NGINX and OpenSSL. Adjust paths if your setup is different.
- Modify the script to add support for additional authentication methods as required.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Your Name**

---

Feel free to modify and extend this script to suit your specific needs. Contributions and suggestions are welcome!


## Future Enhancements

- The script can be extended to include additional authentication methods such as OAuth, OIDC, LDAP, or custom methods.
- More detailed logging and error handling can be added to improve usability and troubleshooting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
