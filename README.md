# Proxy Checker

A fast and efficient Python script to check and filter working proxies from a list. Supports multiple proxy formats and protocols.

## Features
- Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies
- Handles multiple proxy formats
- Uses multiprocessing and threading for faster checking
- Saves working proxies to a separate file

## Supported Proxy Formats


user:pass@192.168.1.1:8080
192.168.1.1:8080
http://192.168.1.1:8080
socks5://192.168.1.1:1080
192.168.1.1:8080:user:pass
https://192.168.1.1:443:user:pass
http/user/pass/192.168.1.1/8080


## Installation
1. Clone the repository:
```bash
git clone https://github.com/Ansh7473/proxy-checker.git
cd proxy-checker



Install dependencies:


bash


pip install -r requirements.txt



Usage

Create a proxies.txt file with your proxy list (see example in proxies.txt.example)



Run the script:


bash


python proxy_checker.py




