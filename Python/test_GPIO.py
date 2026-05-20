#!/usr/bin/python3
''' 
-------------------------------------------------------------------------------

                        TOUCH MAKER LAB  -  Gpio Test

Touch Maker Lab est une carte d’extension pour Raspberry PI, 
pensée par des makers pour des makers, conçue pour faciliter la connexion et 
la programmation des entrées/sorties. 
Elle permet d’interagir avec le système grâce à ses 6 pads tactiles et de 
relier de 6 à 12 GPIO en quelques secondes grâce à ses 6 connecteurs jack.
Fini la prise de tête avec le câblage — 
concentrez-vous sur le code, que ce soit sur Scratch ou en Python. 

by SLmediation & F-ROBOTICS.FR                                        mai 2026             

-------------------------------------------------------------------------------
'''

import time
from datetime import datetime
import RPi.GPIO as GPIO
 
GPIOS = [16, 17, 18, 19, 20, 21]
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for gpio in GPIOS:
    GPIO.setup(gpio, GPIO.IN)
 
try:
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        states = " ".join(
                f" {'Low ' if not GPIO.input(g) else 'High'}"
                for g in GPIOS
            )
        print(f"{now}  | Gpio 16to21 : {states}")
        time.sleep(0.1)
 
except KeyboardInterrupt:
    print("\nTerminé.")
finally:
    GPIO.cleanup()
