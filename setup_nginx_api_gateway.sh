#!/bin/bash
#Script sets up crypto and configures NGINX as GW for cats api. User can 
#select between basic auth and mtls (other options could be added)

# Function to create a certificate directory
create_certificate_directory() {
    echo "Creating certificate directory..."
    sudo mkdir -p /etc/nginx/ssl && cd /etc/nginx/ssl
}

# Function to generate a private key
generate_private_key() {
    echo "Generating private key..."
    sudo openssl genpkey -algorithm RSA -out nginx-selfsigned.key -aes256
}

# Function to create a self-signed certificate
create_self_signed_certificate() {
    echo "Creating self-signed certificate..."
    sudo openssl req -new -x509 -key nginx-selfsigned.key -out nginx-selfsigned.crt -days 365 \
        -subj "/C=US/ST=New York/L=New York/O=Example Company/OU=Org/CN=your_domain.com"
}

# Function to remove the passphrase from the key
remove_passphrase_from_key() {
    echo "Removing passphrase from key..."
    sudo openssl rsa -in nginx-selfsigned.key -out nginx-selfsigned-nopass.key
}

# Function to back up the existing nginx configuration
backup_nginx_configuration() {
    echo "Backing up existing nginx configuration..."
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
}

# Function to install Apache utilities
install_apache_utils() {
    echo "Installing Apache utilities to create .htpasswd file..."
    sudo apt-get install -y apache2-utils
}

# Function to create .htpasswd file for Basic Authentication
create_htpasswd() {
    echo "Creating .htpasswd file for Basic Authentication..."
    read -p "Enter username for basic authentication: " username
    sudo htpasswd -c /etc/nginx/.htpasswd "$username"
}

# Function to generate a client certificate for mTLS
generate_client_certificate() {
    echo "Generating client certificate for mTLS..."
    sudo openssl req -newkey rsa:2048 -nodes -keyout client.key -out client.csr \
        -subj "/C=US/ST=New York/L=New York/O=Client Company/OU=Org/CN=client"
    sudo openssl x509 -req -in client.csr -CA nginx-selfsigned.crt -CAkey nginx-selfsigned-nopass.key \
        -CAcreateserial -out client.crt -days 365
    sudo openssl pkcs12 -export -out client.pfx -inkey client.key -in client.crt \
        -certfile nginx-selfsigned.crt -password pass:your_password
}

# Function to set permissions and ownership
set_permissions() {
    echo "Setting file permissions and ownership..."
    sudo chmod 644 /etc/nginx/ssl/client.crt
    sudo chmod 600 /etc/nginx/ssl/client.key
    sudo chown $(whoami):$(whoami) /etc/nginx/ssl/client.crt
    sudo chown $(whoami):$(whoami) /etc/nginx/ssl/client.key
}

# Function to configure nginx based on user choice
configure_nginx() {
    echo "Configuring NGINX Plus as an API Gateway..."
    cat <<EOF | sudo tee /etc/nginx/nginx.conf
# Main context
user www-data;
worker_processes auto;
pid /run/nginx.pid;

# Events block
events {
    worker_connections 1024;
}

# HTTP block
http {
    # DNS resolver configuration, prefer IPv4
    resolver 8.8.8.8 ipv6=off;
    resolver_timeout 10s;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;

    server {
        listen 443 ssl;
        server_name $1;

        ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned-nopass.key;
EOF

    if [[ $2 == "a" ]]; then
        cat <<EOF | sudo tee -a /etc/nginx/nginx.conf
        location / {
            auth_basic "Restricted Area";
            auth_basic_user_file /etc/nginx/.htpasswd;
            proxy_pass https://api.thecatapi.com;
            proxy_set_header Host api.thecatapi.com;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_ssl_verify off;
            proxy_ssl_server_name on;
            proxy_connect_timeout 60s;
            proxy_read_timeout 60s;
            proxy_send_timeout 60s;
        }
EOF
    elif [[ $2 == "b" ]]; then
        cat <<EOF | sudo tee -a /etc/nginx/nginx.conf
        ssl_client_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
        ssl_verify_client on;

        location / {
            proxy_pass https://api.thecatapi.com;
            proxy_set_header Host api.thecatapi.com;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_ssl_verify off;
            proxy_ssl_server_name on;
            proxy_connect_timeout 60s;
            proxy_read_timeout 60s;
            proxy_send_timeout 60s;
        }
EOF
    fi

    echo "    }" | sudo tee -a /etc/nginx/nginx.conf
    echo "}" | sudo tee -a /etc/nginx/nginx.conf
}

# Function to test nginx configuration
test_nginx_configuration() {
    echo "Testing NGINX configuration..."
    sudo nginx -t
    if [[ $? -eq 0 ]]; then
        echo "NGINX configuration is valid."
    else
        echo "NGINX configuration has errors."
        sudo nginx -t 2>&1 | tee /tmp/nginx_test_output.log
    fi
}

# Function to restart nginx
restart_nginx() {
    echo "Restarting NGINX..."
    sudo systemctl restart nginx
}

# Main script execution
create_certificate_directory
generate_private_key
create_self_signed_certificate
remove_passphrase_from_key
backup_nginx_configuration

echo "Choose an Authentication Type - other methods supported and could be added to this script:"
echo " Other options could include oAuth, OIDC, LDAP & Custom"
echo "a. Please Choose"
echo "a. Basic Authentication"
echo "b. Mutual TLS (mTLS) Authentication"

read -p "Enter your choice (a/b): " auth_choice

if [[ $auth_choice == "a" ]]; then
    install_apache_utils
    create_htpasswd
elif [[ $auth_choice == "b" ]]; then
    generate_client_certificate
    set_permissions
    echo "Client certificate created for mTLS. The files client.key and client.crt are located in /etc/nginx/ssl."
    echo "You can convert client.crt and client.key to a format compatible with your client, such as PFX, using the following command:"
    echo "  sudo openssl pkcs12 -export -out client.pfx -inkey /etc/nginx/ssl/client.key -in /etc/nginx/ssl/client.crt -certfile /etc/nginx/ssl/nginx-selfsigned.crt -password pass:your_password"
else
    echo "Invalid option. Exiting."
    exit 1
fi

read -p "Enter your domain (e.g., your_domain.com): " domain
configure_nginx $domain $auth_choice
test_nginx_configuration
restart_nginx

if [[ $auth_choice == "b" ]]; then
    echo "To test the site with mTLS, use the following curl command:"
    echo "  curl -k --cert /etc/nginx/ssl/client.crt --key /etc/nginx/ssl/client.key https://$domain"
else
    echo "To test the site with Basic Authentication, use the following curl command:"
    echo "  curl -k https://$domain -u 'user1:password'"
fi

echo "Done."
