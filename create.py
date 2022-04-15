import sys

# You may need to run `pip3 install hcloud`
from hcloud import Client
from hcloud.images.domain import Image
from hcloud.server_types.domain import ServerType
from hcloud.firewalls.domain import FirewallRule
from hcloud.ssh_keys.domain import SSHKey

# Email address is used for LetsEncrypt in Caddy
owner_email = input("Enter your email address: ")

if(owner_email == ""):
    sys.exit()

# Collect Hetzner Cloud auth token
hcloud_api_token = input("Enter your Hetzner Cloud auth token: ")

if(hcloud_api_token == ""):
    sys.exit()

# Collect Tailscale auth key
ts_auth_token =  input("Enter your Tailscale auth key: ")

if(ts_auth_token == ""):
    sys.exit()

# Collect SSH Public Key for connecting
ssh_public_key_path = input("Enter the absolute path of your SSH Public Key: ")

if(ssh_public_key_path == ""):
    sys.exit()

ssh_public_key_file = open(ssh_public_key_path, "r")
ssh_public_key = ssh_public_key_file.read()

if(ssh_public_key == ""):
    sys.exit()

# Collect domains to proxy
# Format is `some.domain.com:3006,another.domain.com:80`
domains_to_proxy = input("Enter the ingress domain and egress port you wish to proxy separated by a colon. You can combine multiple records separated by a comma: ")

if(domains_to_proxy == ""):
    sys.exit()

domains_to_proxy = domains_to_proxy.split(",")
domains_to_proxy_string = ""

# parse domains to proxy for Caddyfile
for domain_to_proxy in domains_to_proxy:
    domain = domain_to_proxy.split(":")[0]
    port = domain_to_proxy.split(":")[1]

    if(len(domains_to_proxy_string) > 0):
        domains_to_proxy_string += "      "

    domains_to_proxy_string += domain + " {\n            reverse_proxy {ADDRESS_TO_PROXY}:" + port + "\n      }\n\n"


# copy variables to the cloud-config yaml file
user_data_file = open("./user_data.yml", "r")
user_data = user_data_file.read()
user_data = user_data.replace("{OWNER_EMAIL_ADDRESS}", owner_email)
user_data = user_data.replace("{TS_AUTH_KEY}", ts_auth_token)
user_data = user_data.replace("{SSH_PUBLIC_KEY}", ssh_public_key)
user_data = user_data.replace("{DOMAINS_TO_PROXY}", domains_to_proxy_string)

# Hetzner cloud client
client = Client(
    token=hcloud_api_token
)

# Create firewall in Hetzner that allows ports 22,80,443 only
firewallResponse = client.firewalls.create(
    name="http-s-ssh-firewall",
    rules=[
        FirewallRule(
            direction="in",
            protocol="tcp",
            port="22",
            source_ips=[
                "0.0.0.0/0",
            ],
            description="SSH"
        ),
        FirewallRule(
            direction="in",
            protocol="tcp",
            port="80",
            source_ips=[
                "0.0.0.0/0",
            ],
            description="HTTP"
        ),
        FirewallRule(
            direction="in",
            protocol="tcp",
            port="443",
            source_ips=[
                "0.0.0.0/0",
            ],
            description="HTTPS"
        ),
    ]
)

# Create a SSH Key in Hetzner
sshKeyResponse = client.ssh_keys.create(
    name="local-ssh-key",
    public_key=ssh_public_key,
)

# Create a Server in Hetzner using the created firewall and SSH key
serverResponse = client.servers.create(
    name="umbrel-ssl-proxy", 
    server_type=ServerType("cpx11"), 
    image=Image(name="ubuntu-20.04"),
    ssh_keys=[SSHKey(name=sshKeyResponse.name, id=sshKeyResponse.id)],
    firewalls=[firewallResponse.firewall],
    user_data=user_data
)

server = serverResponse.server

# done!
print("Server IP Address is " + server.public_net.ipv4.ip)
print("Update your domain's DNS A record to this IP address!")
print("Then, SSH into the machine by running `ssh ubuntu@" + server.public_net.ipv4.ip + "`")
print("Right now, the machine is installing all the required software. It will then reboot once. After reboot, your site will be accessible!")
