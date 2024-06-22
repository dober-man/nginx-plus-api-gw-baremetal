# NGINX+ API Gateway Deploy & Config

## There are 4 sections to this guide. 

1. NGINX+ App Protect Installation Script
2. NGINX+ API GW config with Auth Script (basic or mTLS)
3. NGINX+ API GW features - additional config examples
     -Load Balancing
     -Rate Limiting
     -Caching
     -Allow List
4. NGINX+ App Protect (Bot & WAF Policy)
  
-----------------------------------------**SECTION 1**-----------------------------------------

# NGINX+ App Protect Installation Script

## Overview

This Python script automates the installation and configuration of NGINX+ and NGINX App Protect on an Ubuntu 22.04 system. It sets up the necessary directories, copies the provided certificate and key files, installs required dependencies, and configures the repositories for NGINX+ and App Protect. This script could easily be modified to support a variety of supported host Operating Systems including RHEL, Debian or Alpine. 

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

-----------------------------------------**SECTION 2**-----------------------------------------

# NGINX+ API GW basic config with Auth (basic or mTLS)

## Overview

This script sets up cryptographic components and configures NGINX as a Gateway for an API. The user can choose between Basic Authentication and Mutual TLS (mTLS) for secure access. The script also provides an option to add other authentication methods if needed.

## Prerequisites

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

1. **Download the Script**: Save the `setup_nginx_gateway.sh` script to the system you will already installed N+ and NAP on.

2. **Make the Script Executable**:
    ```bash
    chmod +x setup_nginx_gateway.sh

3. **Run the Script**:
    ```bash
    ./setup_nginx_gateway.sh
    ```

4. **Enter Domain**:
    - Enter your domain. This should be the FQDN that resolves to the host where NGINX is running.
    - Default: `your_domain.com`.

5. **Choose Authentication Type**:
    - Options: Basic Authentication (`a`) or mTLS Authentication (`b`).
    - Other methods like OAuth, OIDC, and LDAP can be added.

6. **Configure Upstream Server**:
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

- ## Future Enhancements

- The script can be extended to include additional authentication methods such as OAuth, OIDC, LDAP, or custom methods.
- More detailed logging and error handling can be added to improve usability and troubleshooting.


-----------------------------------------**SECTION 3**-----------------------------------------

# Adding features to the API Gateway

This section provides instructions for configuring NGINX to load balance traffic for the API and how to test the configuration.

## Load Balancing

To distribute traffic across multiple backend servers, you can configure NGINX with an upstream block. Follow these steps:

1. **Edit your NGINX configuration file** (e.g., `/etc/nginx/nginx.conf` or a specific site configuration file under `/etc/nginx/sites-available/`).

2. **Add or modify the upstream block** to define the backend servers:
    ```nginx
    http {
        upstream catapi {
            server api.thecatapi.com;
            server api2.thecatapi.com;
        }
    ```

3. **Save and close the configuration file**.

4. **Test the NGINX configuration** to ensure there are no syntax errors:
    ```bash
    sudo nginx -t
    ```

5. **Reload or restart NGINX** to apply the changes:
    ```bash
    sudo systemctl reload nginx
    ```

## Testing Load Balancing

To verify that the load balancing configuration is working:

1. **Send multiple requests** to your NGINX server using a tool like `curl`:
    ```bash
    curl -k https://your_domain.com -o /dev/null -s -w "%{http_code}\n"
    ```

2. **Observe the backend servers** to check if the requests are distributed. You can use server logs or monitoring tools to verify that traffic is reaching all specified servers.

3. **Check NGINX logs** for any issues or confirmations that requests are being handled properly:
    ```bash
    sudo tail -f /var/log/nginx/access.log
    sudo tail -f /var/log/nginx/error.log
    ```

This guide will help you set up and test load balancing for your API using NGINX. Adjust the configuration as necessary to suit your specific requirements.

## Adding Rate Limiting
This section provides instructions for configuring NGINX to limit the rate of requests to the API and how to test the configuration.
To prevent abuse and manage traffic effectively, you can configure NGINX to limit requests to 5 requests per second (rps).

1. **Edit your NGINX configuration file** (e.g., `/etc/nginx/nginx.conf` or a specific site configuration file under `/etc/nginx/sites-available/`).

2. **Add the rate limiting configuration**:
    ```nginx
    http {
        limit_req_zone $binary_remote_addr zone=mylimit:10m rate=5r/s;

        server {
            listen 443 ssl;
            server_name your_domain.com;

            ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
            ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned-nopass.key;

            location / {
                limit_req zone=mylimit burst=10 nodelay;
                proxy_pass https://api.thecatapi.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }
    ```

3. **Save and close the configuration file**.

4. **Test the NGINX configuration** to ensure there are no syntax errors:
    ```bash
    sudo nginx -t
    ```

5. **Reload or restart NGINX** to apply the changes:
    ```bash
    sudo systemctl reload nginx
    ```

## Testing Rate Limiting

To verify that the rate limiting configuration is working:

1. **Send multiple requests** to your NGINX server using a tool like `curl` or `ab` (Apache Benchmark):
    ```bash
    ab -n 100 -c 10 https://your_domain.com/
    ```

2. **Observe the response status codes** to check if requests beyond the limit are being throttled. You should see `503 Service Unavailable` errors when the rate limit is exceeded.

3. **Check NGINX logs** for any issues or confirmations that requests are being limited as expected:
    ```bash
    sudo tail -f /var/log/nginx/access.log
    sudo tail -f /var/log/nginx/error.log
    ```

This guide will help you set up and test rate limiting for your API using NGINX. Adjust the configuration as necessary to suit your specific requirements.


## Adding Caching
This section provides instructions for configuring NGINX to cache responses for the API and how to test the configuration.
Caching helps to reduce the load on backend servers and improve response times by storing copies of responses. Follow these steps to set up caching:

1. **Edit your NGINX configuration file** (e.g., `/etc/nginx/nginx.conf` or a specific site configuration file under `/etc/nginx/sites-available/`).

2. **Add the caching configuration**:
    ```nginx
    http {
        proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;

        server {
            listen 443 ssl;
            server_name your_domain.com;

            ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
            ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned-nopass.key;

            location / {
                proxy_cache my_cache;
                proxy_cache_valid 200 1h;
                proxy_pass https://api.thecatapi.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }
    ```

3. **Save and close the configuration file**.

4. **Test the NGINX configuration** to ensure there are no syntax errors:
    ```bash
    sudo nginx -t
    ```

5. **Reload or restart NGINX** to apply the changes:
    ```bash
    sudo systemctl reload nginx
    ```

## Testing Caching

To verify that the caching configuration is working:

1. **Send a request** to your NGINX server and observe the response headers:
    ```bash
    curl -I -k https://your_domain.com/
    ```
    - You should see headers like `X-Cache-Status` indicating if the response was served from the cache.

2. **Check the cache directory** to see if files are being stored:
    ```bash
    ls /var/cache/nginx
    ```

3. **Monitor NGINX logs** for cache hit or miss information and ensure caching is operating as expected:
    ```bash
    sudo tail -f /var/log/nginx/access.log
    sudo tail -f /var/log/nginx/error.log
    ```

This guide will help you set up and test caching for your API using NGINX. Adjust the configuration as necessary to suit your specific requirements.



## Adding an IP Allow List
This section provides instructions for configuring NGINX to restrict access to the API based on an IP allow list and how to test the configuration.
To restrict access to specific IP addresses, you can configure an IP allow list in NGINX. Follow these steps:

1. **Edit your NGINX configuration file** (e.g., `/etc/nginx/nginx.conf` or a specific site configuration file under `/etc/nginx/sites-available/`).

2. **Add the IP allow list configuration**:
    ```nginx
    http {
        server {
            listen 443 ssl;
            server_name your_domain.com;

            ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
            ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned-nopass.key;

            location / {
                allow 192.168.1.0/24;  # Example: Allow all IPs from 192.168.1.x subnet
                allow 203.0.113.42;     # Example: Allow specific IP address
                deny all;              # Deny all other IP addresses

                proxy_pass https://api.thecatapi.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }
    ```

3. **Save and close the configuration file**.

4. **Test the NGINX configuration** to ensure there are no syntax errors:
    ```bash
    sudo nginx -t
    ```

5. **Reload or restart NGINX** to apply the changes:
    ```bash
    sudo systemctl reload nginx
    ```

## Testing the IP Allow List

To verify that the IP allow list configuration is working:

1. **Test access from an allowed IP address**:
    ```bash
    curl -k https://your_domain.com/
    ```
    - The request should succeed if you're accessing from an allowed IP address.

2. **Test access from a disallowed IP address**:
    - You can do this by accessing the site from a different network or using a tool like `curl` from a server with a disallowed IP.
    ```bash
    curl -k https://your_domain.com/
    ```
    - You should receive a `403 Forbidden` response if you're accessing from a disallowed IP.

3. **Check NGINX logs** for entries indicating access attempts and whether they were allowed or denied:
    ```bash
    sudo tail -f /var/log/nginx/access.log
    sudo tail -f /var/log/nginx/error.log
    ```

This guide will help you set up and test an IP allow list for your API using NGINX. Adjust the IP ranges and addresses to match your specific security requirements.

-----------------------------------------**SECTION 4**-----------------------------------------
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Brad Scherer**

---

Feel free to modify and extend this script to suit your specific needs. Contributions and suggestions are welcome!


---
