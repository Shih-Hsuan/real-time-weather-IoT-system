from machine import UART, Pin, RTC
import network
import urequests, ujson
import ntptime, utime

# Configurations
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

def connect_wifi(ssid, passwd):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print("Connecting to network...")
        sta.connect(ssid, passwd)
        while not sta.isconnected():
            pass
    print("Network config:", sta.ifconfig())

def build_weather_url(city, country="TW", lang="en", units="metric"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&units={units}&lang={lang}&appid={API_KEY}"
    return url

# Format datetime helper function (simplified)
def format_datetime(t):
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

# Initialize Wi-Fi and UART
connect_wifi(SSID, PASSWORD)
uart = UART(2, baudrate=9600, tx=17, rx=16)

print("System Ready. Waiting for STM32 commands...")

while True:
    if uart.any():
        # Setup NTP Time
        ntptime.settime()
        utc = utime.mktime(utime.localtime())
        
        # Read command from STM32
        line = uart.readline()
        place = line.decode('utf-8').strip()
        print("Decoded command:", place)
        
        url = ""
        local_time = ""
        
        # Determine City and Timezone Offset
        if place == "K":
            url = build_weather_url("Keelung")
            local_time = format_datetime(utime.localtime(utc + 28800)) # UTC+8
        elif place == "M":
            url = build_weather_url("Miaoli")
            local_time = format_datetime(utime.localtime(utc + 28800)) # UTC+8
        elif place == "N":
            url = build_weather_url("Tainan")
            local_time = format_datetime(utime.localtime(utc + 28800)) # UTC+8
        elif place == "O":
            url = build_weather_url("Osaka", country="JP")
            local_time = format_datetime(utime.localtime(utc + 32400)) # UTC+9
        elif place == "S":
            url = build_weather_url("Seoul", country="KR")
            local_time = format_datetime(utime.localtime(utc + 32400)) # UTC+9
        elif place == "L":
            url = build_weather_url("London", country="GB")
            local_time = format_datetime(utime.localtime(utc))         # UTC+0
        else:
            print("Invalid location code.")
            continue
            
        # Fetch and Parse API Data
        try:
            response = urequests.get(url)
            data = ujson.loads(response.text)
            
            if data:
                desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                
                # Format Payload: "Description (Temp C)"
                weather_info = f"{desc} ({temp:.1f} C)"
                
                # Pad string to 40 bytes for consistent HMI display
                weather_fixed = weather_info
                while len(weather_fixed.encode('utf-8')) < 40:
                    weather_fixed += " "
                    
                time_str = local_time[:19]
                result = weather_fixed + time_str + "\r\n"
                
                # Send back to STM32
                uart.write(result.encode('utf-8'))
                print("Sent to STM32:", result)
            else:
                print("No weather data found.")
        except Exception as e:
            print("API Request Failed:", e)
