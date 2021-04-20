---
template: post.html
author: Karthik D
author_dp: /assets/dp2.png
title: Hosting a website / webserver on your PC / Laptop using Reverse SSH Tunnel on a custom domain name
url: /host-website-on-laptop
cover: /assets/code.jpg
published_date: 2021-04-20T09:00:00+05:30
modified_date: 2021-04-20T09:00:00+05:30
display_date: 20 April, 2021
---

The below setup was tried on a Linux machine. Windows users, please <a href="https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview" target="_blank">click here</a>.

## Requirements
- A cloud server with SSH access to be used as jump server (yes you still need one)
- Local PC or Laptop

> NOTE:
> If you do not have a cloud server, you can use [localhost.run](https://localhost.run/)

Step 1: Make sure you are able to SSH into your server
```
ssh -i <private_key_file> <username>@<your_domain_or_ip> 
```

Step 2: Setup the tunnel
```
ssh -i <private_key_file> -N -T -R <remote port>:localhost:<local port> <username>@<your_domain_or_ip>
# e.g.:
ssh -i private.key -N -T -R 2523:localhost:8000 user@kdnanmaga.xyz
```
The above example will tunnel port number 8000 on my local machine to port number 2523 on the remote machine

Step 3: Verify the tunnel is working
```
# On local machine
$ python3 -m http.server 8000 # Or any other test server

# On cloud machine
$ curl http://localhost:2523
# You must be able to see the contents of your local folder printed here
``` 

Step 4: Setup a reverse proxy using NGINX on the cloud server
```
# Install NGINX if not present
$ sudo apt install nginx

# Add server block as shown below
$ sudo nano /etc/nginx/sites-available/local

# Symlink and activate
$ sudo ln -s /etc/nginx/sites-available/local /etc/nginx/sites-enabled/
$ sudo systemctl restart nginx
```
```
# File contents for /etc/nginx/sites-available/local
server{
  server_name <your domain name>;
  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $http_host;
        
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
        
    proxy_pass http://localhost:2523/;
    proxy_redirect off;
    proxy_read_timeout 240s;
  }

  listen 80;
}    
```

Step 5: Make sure DNS for the domain name you used above has an A record poiting to your server IP

Step 6: Install SSL certificate using let's encrypt so you can access via https://
```
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt install python-certbot-nginx
$ sudo certbot --nginx -d <your domain name>
```
With the commands in Step 2 and Step 3 still running, you should be able to access your local machine via the domain name now! 

