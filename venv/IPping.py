import os

hostname = '192.168.0.6'
response = os.system("ping -c 1" + hostname)

print response