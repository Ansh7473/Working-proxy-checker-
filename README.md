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
git clone https://github.com/yourusername/proxy-checker.git
cd proxy-checker



Install dependencies:


bash


pip install -r requirements.txt



Usage

Create a proxies.txt file with your proxy list (see example in proxies.txt.example)



Run the script:


bash


python proxy_checker.py



Working proxies will be saved to working_proxies.txt


Requirements

Python 3.6+



See requirements.txt for Python package dependencies


License

MIT License - feel free to use and modify as needed


`proxies.txt.example` (example proxy file):



Example proxy formats

user:pass@192.168.1.1:8080
192.168.1.1:8080
http://192.168.1.1:8080
socks5://192.168.1.1:1080
192.168.1.1:8080:user:pass
https://192.168.1.1:443:user:pass
http/user/pass/192.168.1.1/8080


`.gitignore` (to ignore unnecessary files):



pycache/
*.pyc
working_proxies.txt
proxies.txt


To create this repository on GitHub:

1. Create a new repository on GitHub:
   - Go to GitHub.com
   - Click "New repository"
   - Name it "proxy-checker" (or whatever you prefer)
   - Choose "Public" or "Private"
   - Don't initialize with README (we'll add our own)

2. On your local machine:
```bash
# Create directory and initialize git
mkdir proxy-checker
cd proxy-checker
git init

# Create all files with the content above
# (You can copy-paste each into respective files)

# Add and commit files
git add .
git commit -m "Initial commit with proxy checker script"

# Connect to your GitHub repo and push
git remote add origin https://github.com/yourusername/proxy-checker.git
git branch -M main
git push -u origin main


