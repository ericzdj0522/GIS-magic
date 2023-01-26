import os

hostname = '192.168.0.6'
response = os.system("ping -c 3 " + hostname)

print response