#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
from scipy import signal


def calcular_fft(amostras, t_amost):
    n_amostras = len(amostras)    
    freq_naturais = np.fft.fftfreq(n_amostras, t_amost)
    espectro = np.fft.fft(amostras)/n_amostras 
    
    # Desloca frequência zero para origem.
    # espectro = np.fft.fftshift(espectro) 
    # freq_naturais = np.fft.fftshift(freq_naturais)
    
    return (freq_naturais, espectro)
    
def plotar_sinal(amostras, t_amost, titulo='Título'):
    n_amostras = len(amostras)
    
    # Calcula a FFT.
    espectro = np.fft.fft(amostras)/n_amostras 
    freq_naturais = np.fft.fftfreq(n_amostras, t_amost)
    
    # Desloca frequência zero para origem.
    # espectro = np.fft.fftshift(espectro) 
    # freq_naturais = np.fft.fftshift(freq_naturais)
    
    fig, ax = plt.subplots(2, 1)
    fig.canvas.set_window_title(titulo)
    
    t = np.arange(0, n_amostras * t_amost, t_amost, dtype='float64')

    ax[0].plot(t, amostras, 'r-')
    ax[0].set_xlabel(u't(s)')
    ax[0].set_ylabel(u'x(t)')
    ax[0].set_title(u'Sinal no domínio do tempo',
                                fontsize= 12, fontweight="bold")

    ax[1].plot(freq_naturais, np.abs(espectro), 'b-')
    ax[1].set_xlabel(u'f(Hz)')
    ax[1].set_ylabel('|X(f)|')
    ax[1].set_title(u'Sinal no domínio da frequência', 
                                fontsize= 12, fontweight="bold")
    
    fig.tight_layout()
    plt.show(block=False)
    
   
'''
Esta função plota a resposta em frequência de um filtro digital, com base nos
valores de b e a (numerador e denominador da função de transferência, 
respectivamente.
Parâmtros:
    b = Numerador do filtro linear
    a = Denominador do filtro linear
    freqs_corte = Array no formato [freq_corte_inferior, limite_corte_superior]
    freq_amost = Frequência de amostragem do sinal.
'''
def plotar_filtro_passa_faixa(b, a, freqs_corte, freq_amost):

    # Obtém a resposta em frequência do fitro digital definido por a e b.
    w, h = signal.freqz(b, a)
    
    # Plota a curva do filtro de Butterworth.
    plt.plot(0.5 * freq_amost * w / np.pi, np.abs(h), 'b')
    
    # Plota os pontos onde a queda da potência é 1/raizde(2) (50%).
    plt.plot(freqs_corte[0], 1.0/np.sqrt(2), 'ko')
    plt.plot(freqs_corte[1], 1.0/np.sqrt(2), 'ko')
    
    # Plota uma linha vertical mostrando os dois pontos de corte.
    plt.axvline(limite_inferior*banda, color='k')
    plt.axvline(limite_superior*banda, color='k')
    
    # Limita os eixos x e y na plotagem.
    plt.xlim(0, 0.5*freq_amost)
    plt.ylim(0, 1.2)
    
    # Alterando títulos e legendas.
    plt.title(u'Resposta em frequência do filtro passa-faixa')
    plt.xlabel(u'f(Hz)')
    plt.ylabel(u'|H(f)|')
    plt.grid()
    plt.tight_layout()
    plt.show()



sound = "audio-ruido-gaussiano.wav"

print('[1] Abrindo arquivo "%s"...' %sound)
(amostras, freq_amost) = sf.read(sound, dtype='float64')

t_amost = 1.0/freq_amost
n_amostras = len(amostras)
duracao = n_amostras * t_amost
banda = 0.5 * freq_amost

print("[2] Informações do áudio:")
print("  [2.1] Frequência de Amostragem: %d Hz" %freq_amost)
print("  [2.2] Período de Amostragem: %f s" %t_amost)
print("  [2.2] Número de amostras: %d" %n_amostras)
print("  [2.3] Duração do áudio: %f s" %duracao)
print("  [2.4] Banda base: %f Hz" %banda)


print("[3] Calculando FFT do áudio...")

# Calcula a FFT.
espectro = np.fft.fft(amostras)/n_amostras 
freq_naturais = np.fft.fftfreq(n_amostras, t_amost)

# Encontra a frequência com maior energia.

print("[4] Encontrando frequência do codigo morse...")

maior_potencia = espectro.max()
arg_maior_potencia = espectro.argmax()
freq_maior_potencia = np.round(np.abs(freq_naturais[arg_maior_potencia]))

print("[5] Realizando filtragem passa banda... ")

freq_maior_potencia_relativa = freq_maior_potencia/banda
limite_inferior = 0.8 * freq_maior_potencia_relativa
limite_superior = 1.2 * freq_maior_potencia_relativa
limites = [limite_inferior, limite_superior]
freq_corte_inferior = limite_inferior * banda
freq_corte_superior = limite_superior * banda
freqs_corte = [freq_corte_inferior, freq_corte_superior,]

# Cria o filtro linear do tipo Butterworth passa-faixa,
b, a = signal.butter(6, limites, 'band', analog=False)
                                                        
# Plota a resposta em frequência do filtro.
plotar_filtro_passa_faixa(b, a, freqs_corte, freq_amost)

# Aplica o filtro no sinal original.
sinal_filtrado = signal.lfilter(b, a, amostras)




#plotar_sinal(amostras, t_amost, titulo='Sinal original')
#plotar_sinal(sinal_filtrado, t_amost, titulo='Sinal filtrado')

sf.write('saida-filtrado.wav', sinal_filtrado, freq_amost)

raw_input()

        




#sf.write('saida.ogg', sinal_filtrado[:5000000], freq_amost)

