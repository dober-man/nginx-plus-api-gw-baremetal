# NGINX+ API Gateway Deploy & Config

## There are 3 sections to this guide. 

- NGINX+ App Protect Installation Script
- NGINX+ API GW basic config with Auth (basic or mTLS)
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

## Prerequisites

- `openssl` must be installed on your system for generating certificates.
- `nginx` must be installed and running.
- `apache2-utils` must be installed to use Basic Authentication.

## Script Workflow

1. **Create Certificate Directory**: The script creates a directory for storing SSL certificates at `/etc/nginx/ssl`.

2. **Generate Private Key**: Generates a secure private key for the server.

3. **Create Self-Signed Certificate**: Generates a self-signed SSL certificate.

4. **Remove Passphrase from Key**: Removes the passphrase from the private key for easier access by NGINX.

5. **Backup NGINX Configuration**: Backs up the existing NGINX configuration file to avoid any data loss.

6. **Choose Authentication Type**: Prompts the user to select either Basic Authentication or mTLS.

7. **Install Apache Utils**: Installs Apache utilities for creating a `.htpasswd` file if Basic Authentication is chosen.

8. **Create `.htpasswd` File**: Creates a `.htpasswd` file for Basic Authentication.

9. **Generate Client Certificate for mTLS**: Generates a client certificate for mTLS and sets appropriate permissions.

10. **Configure NGINX**: Configures NGINX based on the chosen authentication method.

11. **Test NGINX Configuration**: Tests the NGINX configuration for errors.

12. **Restart NGINX**: Restarts the NGINX service to apply the new configuration.

## Usage Instructions

### Running the Script

1. Make the script executable:
    ```bash
    chmod +x setup_nginx_gw.sh
    ```

2. Run the script:
    ```bash
    sudo ./setup_nginx_gw.sh
    ```

### Choosing an Authentication Type

- **Basic Authentication**:
  - The script will prompt you to enter a username for creating a `.htpasswd` file.
  - You will be asked for your domain, which is used for the NGINX server configuration.

- **Mutual TLS (mTLS) Authentication**:
  - The script will generate a client certificate and set the necessary permissions.
  - You will be prompted to enter your domain.

### Testing the Configuration

**Note:** Make sure to add a host file entry or update DNS to point your_domain.com to the Ubuntu server. 

- **Basic Authentication**:
  - Use the following `curl` command to test:
    ```bash
    curl -k https://your_domain.com -u 'user:password'
    ```

- **Mutual TLS**:
  - Use the following `curl` command to test:
    ```bash
    curl -k --cert /etc/nginx/ssl/client.crt --key /etc/nginx/ssl/client.key https://your_domain.com
    ```

## Script Details

### Certificate Generation

The script generates an RSA private key and a self-signed certificate with a validity of 365 days. The certificate's subject details (such as country, state, and organization) are pre-configured but can be adjusted in the script.

### NGINX Configuration

The script configures NGINX to use the generated SSL certificates and sets up the server to forward requests to the Cats API. It includes configurations for both Basic Authentication and mTLS, and prompts the user to choose between them.

### Error Handling

The script includes checks to ensure that NGINX configurations are valid before restarting the service. It also provides feedback on the success or failure of the operations.

## Troubleshooting

- Ensure that you have the necessary permissions to execute the script and make changes to the `/etc/nginx` directory.
- Check for typos or incorrect domain entries during the prompts.
- Review the NGINX test output for any configuration errors if the script reports issues.

## Future Enhancements

- The script can be extended to include additional authentication methods such as OAuth, OIDC, LDAP, or custom methods.
- More detailed logging and error handling can be added to improve usability and troubleshooting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
