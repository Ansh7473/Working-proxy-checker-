import requests
import socks
import socket
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from urllib.parse import urlparse
import time

def parse_proxy(proxy_line):
    """Parse different proxy formats and return connection details"""
    proxy_line = proxy_line.strip()
    if not proxy_line:
        return None
    
    # Handle user:pass@ip:port format first
    if '@' in proxy_line and '://' not in proxy_line:
        try:
            auth, host_port = proxy_line.split('@')
            username, password = auth.split(':')
            host, port = host_port.split(':')
            return {
                'host': host,
                'port': int(port),
                'type': 'http',
                'username': username,
                'password': password
            }
        except (ValueError, IndexError):
            pass
    
    # Split by both : and / delimiters for other formats
    parts = proxy_line.replace('://', ':').replace('/', ':').split(':')
    
    # Handle different proxy formats
    try:
        if len(parts) == 2:  # ip:port
            return {
                'host': parts[0],
                'port': int(parts[1]),
                'type': 'http',
                'username': None,
                'password': None
            }
        elif len(parts) == 3:  # protocol:ip:port
            return {
                'host': parts[1],
                'port': int(parts[2]),
                'type': parts[0].lower(),
                'username': None,
                'password': None
            }
        elif len(parts) == 4:  # ip:port:username:password
            return {
                'host': parts[0],
                'port': int(parts[1]),
                'type': 'http',
                'username': parts[2],
                'password': parts[3]
            }
        elif len(parts) == 5:  # protocol:ip:port:username:password or protocol:user:password:ip:port
            if parts[1] in ['user', 'username']:  # http:user:password:ip:port format
                return {
                    'host': parts[3],
                    'port': int(parts[4]),
                    'type': parts[0].lower(),
                    'username': parts[1],
                    'password': parts[2]
                }
            return {  # protocol:ip:port:username:password
                'host': parts[1],
                'port': int(parts[2]),
                'type': parts[0].lower(),
                'username': parts[3],
                'password': parts[4]
            }
    except (ValueError, IndexError):
        return None
    return None

def check_proxy(proxy_info):
    """Check if a single proxy is working"""
    if not proxy_info:
        return None
        
    test_url = "https://www.google.com"
    timeout = 5
    
    try:
        if proxy_info['type'] in ['socks4', 'socks5']:
            # Set up SOCKS proxy
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
            # HTTP/HTTPS proxy
            proxies = {
                'http': f"{proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}",
                'https': f"{proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}"
            }
            if proxy_info['username'] and proxy_info['password']:
                proxies['http'] = f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
                proxies['https'] = f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
            
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
        
        if response.status_code == 200:
            # Reconstruct proxy string
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
    # Read proxies from file
    try:
        with open('proxies.txt', 'r') as f:
            proxy_lines = f.readlines()
    except FileNotFoundError:
        print("Error: proxies.txt not found")
        return

    # Parse all proxies
    proxy_info_list = [parse_proxy(line) for line in proxy_lines]
    proxy_info_list = [p for p in proxy_info_list if p is not None]

    if not proxy_info_list:
        print("No valid proxies found in the file")
        return

    # Split into batches for multiprocessing
    cpu_count = multiprocessing.cpu_count()
    batch_size = max(1, len(proxy_info_list) // (cpu_count * 2))
    batches = [proxy_info_list[i:i + batch_size] for i in range(0, len(proxy_info_list), batch_size)]

    print(f"Checking {len(proxy_info_list)} proxies using {len(batches)} batches...")

    # Process batches in parallel
    start_time = time.time()
    working_proxies = []
    
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.map(process_proxy_batch, batches)
        for batch_result in results:
            working_proxies.extend(batch_result)

    # Save working proxies
    with open('working_proxies.txt', 'w') as f:
        for proxy in working_proxies:
            f.write(f"{proxy}\n")

    end_time = time.time()
    print(f"Found {len(working_proxies)} working proxies")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main()
