# */
# * @author John Heber Mendoza
# * @Henry Medina
# * @Universidad del Area Andina
# */

import network, time, urequests, framebuf, utime
from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from hcsr04 import HCSR04
from utime import sleep, sleep_ms
from dht import DHT11

def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True

# Led Indicadores
led1 = Pin(15, Pin.OUT) # Alerta de 00-10%  Capacidad
led2 = Pin(4, Pin.OUT)  # Alerta de 10-30%  Capacidad
led3 = Pin(16, Pin.OUT) # Alerta de 30-50%  Capacidad
led4 = Pin(17, Pin.OUT) # Alerta de 50-70%  Capacidad
led5 = Pin(5, Pin.OUT)  # Alerta de 70-90%  Capacidad
led6 = Pin(18, Pin.OUT)  # Alerta de 90-100% Capacidad
led7 = Pin(23, Pin.OUT) # Led sensor aire

def leds (a, b, c, d, e, f):
    led1.value(a)
    led2.value(b)
    led3.value(c)
    led4.value(d)
    led5.value(e)
    led6.value(f)

def aire() : 
    if calidadAire >1200:
        led7.value(1)
        utime.sleep_ms(100)
        led7.value(0)
        utime.sleep_ms(100)
        led7.value(1)
        utime.sleep_ms(100)
        led7.value(0)
        utime.sleep_ms(100)

#Sensores & Variables
sensorDHT= DHT11(Pin(32)) # Variable sensor DHT11
medidor = HCSR04 (trigger_pin = 27 , echo_pin = 14 ) #Variable Sensor HCSRR04
mq135 = ADC(Pin(35))# Variable sensor mq135
alturaC = 226 # Medida altura contenedor

#OLED
def open_icon(routh):
    doc = open(routh, "rb")
    doc.readline()
    xy = doc.readline()
    x = int(xy.split()[0])
    y = int(xy.split()[1])
    icon = bytearray(doc.read())
    doc.close()
    return framebuf.FrameBuffer(icon, x, y, framebuf.MONO_HLSB)

ancho = 128
alto = 64
i2c = I2C(1, scl = Pin(22), sda = Pin(21), freq = 200000)
oled = SSD1306_I2C(ancho, alto, i2c)
oled.fill(0)
oled.blit(open_icon("img/img2.pbm"),0, 0)
sleep_ms(300)
oled.show()

if conectaWifi ("JMEN715", "12345678"):
#if conectaWifi ("CONEXIONDIGITAL MONROY", "Mendoza.715@"):
    print ("Conexión exitosa!")
    print ('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())      
    url = "https://api.thingspeak.com/update?api_key=NFCRGS7MA708G8NR"
     
    while True:
        sleep(60)
        sensorDHT.measure()
        temp = sensorDHT.temperature()     # Evalua Temperatura
        hum = sensorDHT.humidity()         # Evalua Humedad
        distancia = medidor.distance_mm () # Evalua Distancia
        capacidadC = int(100- ((distancia*10)/alturaC)) # Evalua Porcentaje
        calidadAire = mq135.read() # Lee sensor de aire mq135
        aire()
        
        # Calcula volumen y conviente a litros 
        alturaCont = alturaC - (distancia*0.1)
        radioC= 70
        npi = 3.14159265
        volumenC = npi*((radioC**2)*alturaCont)
        litrosC = volumenC*0.001
        
# mostrar en pantalla        
        oled.fill(0)
        oled.rect(0, 0, 128, 64, 1)     
        oled.text("Capacidad", 3, 4)
        oled.text("lt=", 3, 14)
        oled.text(str(litrosC), 25, 14)
        oled.text(str(capacidadC), 3, 24)
        oled.text("%", 22, 24)
        oled.text("Gases", 4, 43,)
        oled.text(str(calidadAire), 4, 53)
        oled.text("ppm", 40, 53)
        oled.text("Temp", 90, 43)
        oled.text(str(temp), 98, 53)   
        oled.show()
        
        print ("\nT={:02d}C H={:02d}%".format(temp, hum))
        #print ("Distancia = ", distancia, "cm")
        print ("Capacidad =", capacidadC, "%")
        print ("Calidad Aire ",calidadAire, "ppm")
        print ("T litros ",litrosC)
        
# Envia Datos a thingspeak
        respuesta = urequests.get(url+"&field1="+str(temp)+"&field2="+str(calidadAire)+"&field3="+str(capacidadC)+"&field4="+str(litrosC))
        print(respuesta.text)
        print(respuesta.status_code)
        respuesta.close ()

# Condicional Encendido de Leds
        
        if capacidadC >= 90: #10cm
            leds(0,1,1,1,1,1)
            aire()
        elif capacidadC >= 70: #20cm
            leds(0,1,1,1,1,0)
            aire()
        elif capacidadC >= 50: #30cm
            leds(0,1,1,1,0,0)
            aire()
        elif capacidadC >= 30: #40cm
            leds(0,1,1,0,0,0)
            aire()
        elif capacidadC >= 20: #40cm
            leds(0,1,0,0,0,0)
            aire()
        else:
            leds(1,0,0,0,0,0)
            aire()
            
else:
    print ("Imposible conectar")
    miRed.active (False)
    
