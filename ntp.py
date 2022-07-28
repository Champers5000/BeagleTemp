import ntplib
import socket
from datetime import datetime, timezone



c = ntplib.NTPClient()
# Provide the respective ntp server ip in below function
try:
    response = c.request('us.pool.ntp.org', version=3)
    response.offset
    utcdatetime = datetime.fromtimestamp(response.tx_time, None) # Passing in None object for timezone parameter defaults to local timezone
    print (utcdatetime)
    print(datetime.now())
except (ntplib.NTPException, socket.gaierror):
    print("Unable to find server")
