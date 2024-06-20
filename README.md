# NGINX Plus and App Protect Installation Script

## Overview

This Python script automates the installation and configuration of NGINX Plus and NGINX App Protect on an Ubuntu system. It sets up the necessary directories, copies the provided certificate and key files, installs required dependencies, and configures the repositories for NGINX Plus and App Protect.

## Prerequisites

Before running the script, ensure you have the following:

- A valid NGINX Plus subscription.
- The certificate and key files for NGINX Plus repository access, named `nginx-repo.crt` and `nginx-repo.key`.
- An Ubuntu-based system (tested on Ubuntu 22.04).
- Note: Always check NAP release notes to ensure OS support.


## Requirements

- Python 3.x
- `sudo` privileges on the system
- Internet access to download dependencies and repository keys

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
