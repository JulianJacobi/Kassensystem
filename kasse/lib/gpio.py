from django.conf import settings
import time

if settings.GPIO_AVAILABLE:
    import RPi.GPIO


def general_gpio_config():
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    if settings.GPIO_OPEN is not None:
        RPi.GPIO.setup(settings.GPIO_OPEN, RPi.GPIO.OUT)
    if settings.GPIO_DETECTION is not None:
        RPi.GPIO.setup(settings.GPIO_DETECTION, RPi.GPIO.IN)


def cleanup_gpio():
    RPi.GPIO.cleanup()


def open_drawer():
    general_gpio_config()
    RPi.GPIO.output(settings.GPIO_OPEN, RPi.GPIO.HIGH)
    time.sleep(0.2)
    RPi.GPIO.output(settings.GPIO_OPEN, RPi.GPIO.LOW)
    while RPi.GPIO.input(settings.GPIO_DETECTION) == RPi.GPIO.LOW:
        time.sleep(0.5)
    cleanup_gpio()
