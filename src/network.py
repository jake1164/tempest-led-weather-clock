## Class for handling networking. 
import os
import gc
import ssl
import wifi
import socketpool
import adafruit_ntp
import adafruit_requests

WEATHERFLOW_ROOT_CERT = u"""
-----BEGIN CERTIFICATE-----
MIIHJDCCBgygAwIBAgIQDuFgA3khLEDnd1hthCChxTANBgkqhkiG9w0BAQsFADA8
MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRwwGgYDVQQDExNBbWF6b24g
UlNBIDIwNDggTTAxMB4XDTIzMDMwMjAwMDAwMFoXDTI0MDEwODIzNTk1OVowHDEa
MBgGA1UEAwwRKi53ZWF0aGVyZmxvdy5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IB
DwAwggEKAoIBAQCowoLO18WV+jb9bxP51s5zW6t6r4rqz+5K2Fn/b6lPvrBwtlkR
nnWFu9e4JXcN2ZevLTRkTj+838Jj28pUf40A8eel1QEjeXmbwWkY69xuVisFZnDS
Q5tCYNeWqQyOwhji/BVmrlZuDEfTtlOYajyUIqR2X2LxILpcukiklC64kII3H3xd
3Z+8Mte8Hljx8cLKJ8s3sWDJTfk7zQ5wKUR6MtNQZSXfwE6c7PShh4plzw9J4+A9
UJ3q6AxnJIIbH1Oh+7mi2K0LXQSS0l7467ith2SsSalSp5HPM6UdbqYjbNaiAoi/
N940JV4VdkRQsOOIlprd1x/5AkJOX2De4GJxAgMBAAGjggRAMIIEPDAfBgNVHSME
GDAWgBSBuA5jiokSGOX6OztQlZ/m5ZAThTAdBgNVHQ4EFgQUXsBGrwrEF4+IwJjO
hbojoFtccxUwggFvBgNVHREEggFmMIIBYoIRKi53ZWF0aGVyZmxvdy5jb22CDnN0
b3JtcHJpbnQuY29tghJ0ZW1wZXN0d2VhdGhlci5jb22CFCoudGVtcGVzdHdlYXRo
ZXIuY29tgg9maXNod2VhdGhlci5jb22CDyouaXdpbmRzdXJmLmNvbYIQKi5zdG9y
bXByaW50LmNvbYIMc2FpbGZsb3cuY29tggl3aW5keC5jb22CDWlraXRlc3VyZi5j
b22CGXRlbXBlc3R3ZWF0aGVybmV0d29yay5jb22CD3dlYXRoZXJmbG93LmNvbYIO
Ki5zYWlsZmxvdy5jb22CGyoudGVtcGVzdHdlYXRoZXJuZXR3b3JrLmNvbYIPKi53
aW5kYWxlcnQuY29tgg8qLmlraXRlc3VyZi5jb22CESouZmlzaHdlYXRoZXIuY29t
ggsqLndpbmR4LmNvbYINd2luZGFsZXJ0LmNvbYINaXdpbmRzdXJmLmNvbTAOBgNV
HQ8BAf8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMDsGA1Ud
HwQ0MDIwMKAuoCyGKmh0dHA6Ly9jcmwucjJtMDEuYW1hem9udHJ1c3QuY29tL3Iy
bTAxLmNybDATBgNVHSAEDDAKMAgGBmeBDAECATB1BggrBgEFBQcBAQRpMGcwLQYI
KwYBBQUHMAGGIWh0dHA6Ly9vY3NwLnIybTAxLmFtYXpvbnRydXN0LmNvbTA2Bggr
BgEFBQcwAoYqaHR0cDovL2NydC5yMm0wMS5hbWF6b250cnVzdC5jb20vcjJtMDEu
Y2VyMAwGA1UdEwEB/wQCMAAwggF/BgorBgEEAdZ5AgQCBIIBbwSCAWsBaQB2AO7N
0GTV2xrOxVy3nbTNE6Iyh0Z8vOzew1FIWUZxH7WbAAABhp/Zkj0AAAQDAEcwRQIh
AN+2gJe4S7FMsR9Jrkh3O0KY0kH2WuvNE7m0pq+h0iUQAiBNdtmymNMMOkNkpga7
C5VVGNCPC78c3pGhzeiIUDCmgwB3AHPZnokbTJZ4oCB9R53mssYc0FFecRkqjGuA
EHrBd3K1AAABhp/ZkmMAAAQDAEgwRgIhAOJcs8JdUjhEZP0wBLSaKwxDvPpOC8gn
i8KsFDSH1iS6AiEAx98w1LFWqEwBDs9J8aDp2JwMwWyXTVySw1TxD8zAhbIAdgBI
sONr2qZHNA/lagL6nTDrHFIBy1bdLIHZu7+rOdiEcwAAAYaf2ZIlAAAEAwBHMEUC
IEx2n9MTZ1vjdU/FW+5T1z5D9w1DhoKgDieX0RsVzEmXAiEA59G2qOOhkc9ZkJUy
9/zLm/boiMsnCNz2NnJKfAx4oVUwDQYJKoZIhvcNAQELBQADggEBANOmLhYXjO/j
AETJez0lKxKAWMb6ppPCUGWq7WjcvmHl0lnoWNkmIkie4/RfuZZyAthRPDK8Q8bB
bZcqux76LT6g3Lx4agr3+mIitM2Zo7axG8kzqchV9qkxhH/m1IV/m/xt7b41oARX
+3G+BuLV901/Fc19N8AdldjTMi9dmGPKl9P4U/CjUZIZoemcSAkCla0ZqeQ7sfiG
maQGLIJec19lRHHmPF6RFkhHqZxJWf1m0UCZ2mykaKDutfueeQUQB2K0QYiseTS6
cweA+cWWVAmu0m7v24IWP9X1MP94KBa583r6Xmj3wGgtvY1vNSFIPcaqINHt5q6w
NjaM33Jl0Y4=
-----END CERTIFICATE-----
"""

class WifiNetwork:
    def __init__(self) -> None:
        self.RETRY_WIFI = 5 # Number of times to attempt to connect to wifi
        self.SSID = os.getenv('WIFI_SSID')
        self.PASS = os.getenv('WIFI_PASSWORD')

        if self.SSID is None or self.PASS is None or len(self.SSID) == 0 or len(self.PASS) == 0:
            raise Exception("WIFI_SSID & WIFI_PASSWORD are stored in settings.toml, please add them")

        # NTP specific constants
        self.TZ = os.getenv('TZ_OFFSET')
        self.NTP_HOST = os.getenv('NTP_HOST')
        self.INTERVAL = os.getenv('NTP_INTERVAL')

        if self.TZ is None or self.NTP_HOST is None or self.INTERVAL is None:
            raise Exception("NTP_HOST, NTP_INTERVAL & TZ_OFFSET are stored in settings.toml, please add them")
        
        self.connect()


    def connect(self) -> bool:
        """ If not connected connect to the network."""
        print("connecting to: {}".format(self.SSID))
        # TODO: async methods?
        attempt = 1
        while(attempt <= self.RETRY_WIFI):
            try:
                # TODO: async methods?
                wifi.radio.connect(self.SSID, self.PASS)                        
                return True
            except Exception as e:
                print(e)
            attempt += 1
        
        raise Exception('Unable to connect')



    def get_time(self):
        # Need better connection testing
        # has IP before connecting.
        #if wifi.radio.ipv4_address is None:
        #self.connect() # This just feels wrong to connect every time.
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=self.TZ, server=self.NTP_HOST)
        return ntp.datetime
                    

    def getJson(self, url):
        try:
            pool = socketpool.SocketPool(wifi.radio)
            context = ssl.create_default_context()
            if 'weatherflow.com' in url:
                context.load_verify_locations(cadata=WEATHERFLOW_ROOT_CERT)
                print('Added Certificate')
            requests = adafruit_requests.Session(pool, context)
            #requests = adafruit_requests.Session(pool, ssl.create_default_context())
            print('getting url:', url)
            gc.collect()
            print('free memory', gc.mem_free())

            #response = requests.get(url, stream=True) 
            response = requests.get(url) 
            print('free memory after', gc.mem_free())
            return response.json()
        except Exception as e:
            print('response.json Exception:', e)
            gc.collect()
        return {}        

    def get_interval(self):
        return int(self.INTERVAL)


    def get_pool(self):
        pass


