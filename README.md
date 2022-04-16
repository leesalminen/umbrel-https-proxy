# umbrel-https-proxy

You can use this tool to set up a clearnet HTTPS proxy to multiple apps running on your Umbrel node.

YouTube demo video: https://youtu.be/pFIothCfT3Y

# Pre-requisites

- Umbrel node fully configured
- Tailscale account
- Tailscale installed and configured on your Umbrel node
- Hetzner Cloud account
- Ownership of a domain name
- Ability to modify DNS records for your domain name
- MacOS or Linux computer (probably works on Windows, dunno, I don't use it)

# What does this do?

This tool will create a server in Hetzner cloud (cost is 4 EUR / mo) along with appropriate firewall rules and your SSH public key. Once the server is up, it will automatically install and configure Docker, Docker Compose, Tailscale, and Caddy. Once complete, you'll be able to navigate to https://my.domain.com in any web browser from anywhere and access your Umbrel node.

# Instructions

- go to https://hetzner.cloud and log in
- create a new project, name it whatever you want
- click into the project
- click security -> api tokens -> generate api token
- set description -> stand up environment, permissions -> read & write, click generate api token
- save the auth token for later use!
- go to https://tailscale.com and log in
- click settings -> personal settings -> keys -> auth keys -> generate auth key
- set pre-authorized -> yes, click generate key
- save the auth key for later use!
- on your computer clone this repository
- `cd umbrel-https-proxy`
- `pip3 install hcloud`
- `python3 create.py`
- follow the on-screen prompts
- be sure to update the DNS records for the domain(s) you entered to the IP Address shown in the on-screen prompt
