import requests
import socks
import socket
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from urllib.parse import urlparse
import time
import os
import sys
import subprocess

def install_dependencies():
    """Install required dependencies from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please run 'pip install -r requirements.txt' manually")
        sys.exit(1)

def parse_proxy(proxy_line):
    """Parse different proxy formats and return connection details"""
    proxy_line = proxy_line.strip()
    if not proxy_line:
        return None

    # Handle standard URL-like format (e.g., http://username:password@host:port)
    if '://' in proxy_line:
        result = urlparse(proxy_line)
        host = result.hostname
        port = result.port
        type = result.scheme if result.scheme else 'http'
        username = result.username
        password = result.password
    # Handle username:password@host:port by adding default scheme
    elif '@' in proxy_line and '://' not in proxy_line:
        result = urlparse('http://' + proxy_line)
        host = result.hostname
        port = result.port
        type = 'http'
        username = result.username
        password = result.password
    # Handle formats without scheme (e.g., host:port, host:port:username:password)
    else:
        parts = proxy_line.split(':')
        if len(parts) == 2:  # host:port
            return {
                'host': parts[0],
                'port': int(parts[1]),
                'type': 'http',
                'username': None,
                'password': None
            }
        elif len(parts) == 4:  # host:port:username:password
            return {
                'host': parts[0],
                'port': int(parts[1]),
                'type': 'http',
                'username': parts[2],
                'password': parts[3]
            }
        else:
            return None

    # Validate required fields
    if not host or not port:
        return None

    try:
        port = int(port)
    except (ValueError, TypeError):
        return None

    return {
        'host': host,
        'port': port,
        'type': type,
        'username': username,
        'password': password
    }

def check_proxy(proxy_info):
    """Check if a single proxy is working"""
    if not proxy_info:
        return None
        
    test_url = "https://www.google.com"
    timeout = 5
    
    try:
        if proxy_info['type'] in ['socks4', 'socks5']:
            socks.set_default_proxy(
                socks.SOCKS5 if proxy_info['type'] == 'socks5' else socks.SOCKS4,
                proxy_info['host'],
                proxy_info['port'],
                username=proxy_info['username'],
                password=proxy_info['password']
            )
            socket.socket = socks.socksocket
            response = requests.get(test_url, timeout=timeout)
        else:
            proxies = {
                'http': f"{proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}",
                'https': f"{proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}"
            }
            if proxy_info['username'] and proxy_info['password']:
                proxies['http'] = f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
                proxies['https'] = f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            if proxy_info['username'] and proxy_info['password']:
                return f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
            return f"{proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}"
    except Exception:
        return None
    return None

def process_proxy_batch(proxy_batch):
    """Process a batch of proxies"""
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(check_proxy, proxy_batch))
    return [r for r in results if r is not None]

def main():
    # Check for --install flag or missing dependencies
    if '--install' in sys.argv or not os.path.exists('requirements.txt'):
        if not os.path.exists('requirements.txt'):
            with open('requirements.txt', 'w') as f:
                f.write("requests\npysocks")
        install_dependencies()

    # Import check after potential installation
    try:
        import requests
        import socks
    except ImportError:
        print("Required packages not found. Attempting to install...")
        install_dependencies()

    if not os.path.exists('proxies.txt'):
        print("proxies.txt not found, creating one with example proxies...")
        with open('proxies.txt', 'w') as f:
            f.write("# Example proxy formats - replace with your own proxies\n")
            f.write("user:pass@192.168.1.1:8080\n")
            f.write("192.168.1.1:8080\n")
            f.write("http://192.168.1.1:8080\n")
            f.write("socks5://192.168.1.1:1080\n")
            f.write("185.199.228.220:7300:qtnqianv:wzm29ynj809f\n")
            f.write("https://192.168.1.1:443:user:pass\n")
            f.write("http://wfmlbfgy:or54xe5i15dt@38.154.227.167:5868\n")

    with open('proxies.txt', 'r') as f:
        proxy_lines = f.readlines()

    proxy_info_list = [parse_proxy(line) for line in proxy_lines]
    proxy_info_list = [p for p in proxy_info_list if p is not None]

    if not proxy_info_list:
        print("No valid proxies found in proxies.txt")
        print("Please add your own proxies to proxies.txt and run again")
        return

    # Use 1 batch for every 3 proxies
    fixed_batch_size = 3
    batches = [proxy_info_list[i:i + fixed_batch_size] for i in range(0, len(proxy_info_list), fixed_batch_size)]

    print(f"Checking {len(proxy_info_list)} proxies using {len(batches)} batches...")

    start_time = time.time()
    working_proxies = []
    
    # Use multiprocessing to process batches, limiting processes to CPU cores or number of batches
    cpu_count = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=min(cpu_count, len(batches))) as pool:
        results = pool.map(process_proxy_batch, batches)
        for batch_result in results:
            working_proxies.extend(batch_result)

    if working_proxies:
        print("Creating working_proxies.txt with working proxies...")
        with open('working_proxies.txt', 'w') as f:
            for proxy in working_proxies:
                f.write(f"{proxy}\n")
    else:
        print("No working proxies found, creating empty working_proxies.txt...")
        with open('working_proxies.txt', 'w') as f:
            f.write("# No working proxies found\n")

    end_time = time.time()
    print(f"Found {len(working_proxies)} working proxies")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main()
