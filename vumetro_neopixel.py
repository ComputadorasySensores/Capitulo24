# The MIT License (MIT)
#
# Copyright (c) 2017 Dan Halbert for Adafruit Industries
# Copyright (c) 2017 Kattni Rembor, Tony DiCola for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Partes de codigo de Circuit Playground Sound Meter
# Modificacion por Computadoras y Sensores

import array
import math
import audiobusio
import board
import neopixel

# Cantidad total de elementos de la tira de Neopixel
NUM_PIXELS = 8

# Factor de escala exponencial.
# Debe ser en el rango de -10 a 10 de forma razonable.
CURVE = 2
SCALE_EXPONENT = math.pow(10, CURVE * -0.1)

# Cantidad de muestras a tomar.
NUM_SAMPLES = 160


# Restringe el valor entre el piso y el techo.
def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))


# Escala input_value entre output_min y output_max, de forma exponencial.
def log_scale(input_value, input_min, input_max, output_min, output_max):
    normalized_input_value = (input_value - input_min) / \
                             (input_max - input_min)
    return output_min + \
        math.pow(normalized_input_value, SCALE_EXPONENT) \
        * (output_max - output_min)


# Elimina el bias DC antes de calcular el RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))


def mean(values):
    return sum(values) / len(values)


def volume_color(volume):
    return 0, 255, 0 # verde



# Crea objeto y apaga todo los elementos de la tira.
pixels = neopixel.NeoPixel(board.D2, NUM_PIXELS, brightness=0.1, auto_write=False)
pixels.fill(0)
pixels.show()

mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)

# Graba una muestra inicial para la calibracion. Asume un relativo silencia al principio.
samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))
# Establece el valor inferior esperado, adicionando algo mas.
input_floor = normalized_rms(samples) + 10
# Opcion de usar un valor establecido de forma estatica
# input_floor = 50

# Ajuste de sensibilidad: valores mas bajos iluminan una mayor cantidad de elementos
input_ceiling = input_floor + 300

peak = 0
while True:
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    # Imprime en consola el valor de magnitud para visualizar con plotter.
    print(magnitude)

    # Calcula escala logaritmica leyende en el rango de 0 a NUM_PIXELS
    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_PIXELS)

    # Iluminar elementos debajo de la escala y magnitud interpolada.
    pixels.fill(0)
    for i in range(NUM_PIXELS):
        if i < c:
            pixels[i] = volume_color(i)
        # Iluminar el valor de pico y animar una lenta caida.
        if c >= peak:
            peak = min(c, NUM_PIXELS - 1)
        elif peak > 0:
            peak = peak - 1
    pixels.show()
