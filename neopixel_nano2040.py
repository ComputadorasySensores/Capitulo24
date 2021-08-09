import board
import neopixel
import time

NUM_PIXELS = 8

pixels = neopixel.NeoPixel(board.D2, NUM_PIXELS)
pixels.brightness = 0.2

while True:
    pixels.fill(0)
    pixels.fill((255, 0, 0))    # rojo
    time.sleep(2)
    pixels.fill((0, 255, 0))    # verde
    time.sleep(2)
    pixels.fill((0, 0, 255))    # azul
    time.sleep(2)
    pixels.fill(0)
    for i in range(NUM_PIXELS):
        pixels[i] = 127,0,127   # violeta
        time.sleep(0.5)
    pixels.show()
