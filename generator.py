#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Seção de imports
# =============================================================================

import random
import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# =============================================================================
# Configurações do gerador
# =============================================================================

# Cada tonal é uma nota musical A, iniciando em A4.
TONAIS = [440.0, 880.0, 1760.0, 3520.0]

#TONAIS = range(300, 18000, 1200)
          
BANDA = 4000 # 
FREQ_AMOST = 2 * BANDA # Frequência de amostragem seguindo Nyquist.
T_AMOST = 1.0/FREQ_AMOST # Período de amostragem.
 
DURACAO_PONTO = 0.060 # 60 ms
DURACAO_TRACO = 3*DURACAO_PONTO
DURACAO_INTERVALO = DURACAO_PONTO

SNRdB = 3
SNR = 10.0 ** (SNRdB/10.0)
#SNRdB = 10.0 * np.log10(SNRdB)

CODIGO = {
    'a': '.-',     'b': '-...',   'c': '-.-.', 
    'd': '-..',    'e': '.',      'f': '..-.',
    'g': '--.',    'h': '....',   'i': '..',
    'j': '.---',   'k': '-.-',    'l': '.-..',
    'm': '--',     'n': '-.',     'o': '---',
    'p': '.--.',   'q': '--.-',   'r': '.-.',
    's': '...',    't': '-',      'u': '..-',
    'v': '...-',   'w': '.--',    'x': '-..-',
    'y': '-.--',   'z': '--..',

    '0': '-----',  '1': '.----',  '2': '..---',
    '3': '...--',  '4': '....-',  '5': '.....',
    '6': '-....',  '7': '--...',  '8': '---..',
    '9': '----.' 
}

# =============================================================================
# Funções do gerador.
# =============================================================================

''' Converte de texto para ASCII. '''
def produzir_morse(texto):
    saida = ''
    for caractere in texto:
        # Verifica se é um caractere ASCII válio.
        if caractere.isalnum():
            saida += CODIGO[caractere.lower()] + ' '
        # Verifica se é um espaço em branco.
        elif caractere == ' ':
            saida += '/ '
            
    return saida[:-1]

''' Produz um tonal, com frequência aleatória, e duração estabelecida. '''
def produzir_tonal(duracao, tonal):    
    # Gera o intervalo de amostras.
    n_amostras = duracao/T_AMOST
    t = np.arange(0, duracao, T_AMOST, dtype='float64')
    
    # Gera o sinal digital no tonal.
    amostras = np.cos(2*np.pi*tonal*t)
    
    return amostras

''' Produz um período de silêncio com duração fornecida. '''
def produzir_silencio(duracao):
    n_amostras = int(duracao/T_AMOST)
    amostras = np.zeros(shape=(1, n_amostras), dtype='float64')
    return amostras

''' Produz o som de um ponto.'''
def ponto(tonal):
    return produzir_tonal(DURACAO_PONTO, tonal)

''' Produz o som de um traço.'''
def traco(tonal):
    return produzir_tonal(DURACAO_TRACO, tonal)

''' Produz o som de um intervalo.'''
def intervalo():
    return produzir_silencio(DURACAO_INTERVALO)

''' Converte uma string com código morse em um áudio. '''
def produzir_audio(morse):

    resultado = np.zeros(shape=(0,0))
    
    for caractere in morse:
        tonal = random.choice(TONAIS)
        if caractere == '.':
            resultado = np.append(resultado, ponto(tonal))
            resultado = np.append(resultado, intervalo())
        elif caractere == '-':
            resultado = np.append(resultado, traco(tonal))
            resultado = np.append(resultado, intervalo())
        elif caractere == ' ':
            resultado = np.append(resultado, intervalo())
            resultado = np.append(resultado, intervalo())
        elif caractere == '/':
            resultado = np.append(resultado, intervalo())
            resultado = np.append(resultado, intervalo())
            
    return resultado
    
''' Plota um sinal no domínio do tempo e no domínio da frequência.'''
def plotar_sinal(amostras, titulo='Título'):
    n_amostras = len(amostras)
    
    # Calcula a FFT.
    espectro = np.fft.fft(amostras)/n_amostras 
    freq_naturais = np.fft.fftfreq(n_amostras, T_AMOST)
    
    # Desloca frequência zero para origem.
    espectro = np.fft.fftshift(espectro) 
    freq_naturais = np.fft.fftshift(freq_naturais)
    
    fig, ax = plt.subplots(2, 1)
    fig.canvas.set_window_title(titulo)
    
    t = np.arange(0, n_amostras * T_AMOST, T_AMOST, dtype='float64')

    ax[0].plot(t, amostras, 'r-')
    ax[0].set_xlabel(u't(s)')
    ax[0].set_ylabel(u'x(t)')
    ax[0].set_title(u'Sinal no domínio do tempo',
                                fontsize= 12, fontweight="bold")

    ax[1].plot(freq_naturais, np.abs(espectro), 'b-')
    ax[1].set_xlabel(u'f(Hz)')
    ax[1].set_ylabel(u'|X(f)|')
    ax[1].set_title(u'Sinal no domínio da frequência', 
                                fontsize= 12, fontweight="bold")
    
    fig.tight_layout()
    plt.show(block=False)
    #plt.draw()
    
# =============================================================================
# Execução do programa.
# =============================================================================
    
if __name__ == "__main__":
    
    texto = "perigo fogo terceiro andar"

    print('[1] Convertendo texto para morse.')
    morse = produzir_morse(texto)
    print('  [1.1] Texto em ASCII: %s' %texto)
    print('  [1.2] Código morse: %s' %morse)
    
    
    print('[2] Transformando o código morse em áudio.')
    audio = produzir_audio(morse)
    n_amostras = len(audio)
    duracao = n_amostras * T_AMOST
    
    print("  [2.1] Frequência de Amostragem: %d Hz" %FREQ_AMOST)
    print("  [2.2] Período de Amostragem: %f s" %T_AMOST)
    print("  [2.2] Número de amostras: %d" %n_amostras)
    print("  [2.3] Duração do áudio: %f s" %duracao)
    print("  [2.4] Banda base: %f Hz" %BANDA)

   
    print('[3] Criando ruído gaussiano branco, de modo que a SNR = %d dB.' %SNRdB)
    
    # Teorema de Parserval para calcular potência do sinal (áudio).
    potencia_sinal = np.sum(np.square(audio))/n_amostras;

    # Gerando ruído gaussiano branco (média = 0, variancia = potencia do awgn).
    media = 0
    potencia_ruido = potencia_sinal/SNR
    desvio_padrao = np.sqrt(potencia_ruido)
    ruido_gaussiano = np.random.normal(media, desvio_padrao, n_amostras)
    
    # Adicionando o ruído no áudio gerado anteriormente.
    audio_gaussiano = audio + ruido_gaussiano
    
    print ('[4] Plotando resultado.')

    plotar_sinal(audio, 'Áudio limpo')
    plotar_sinal(audio_gaussiano, 'Áudio com ruído gaussiano branco')

    print('[5] Armazenando resultado.')

    sf.write('audio-limpo.wav', audio, FREQ_AMOST)
    sf.write('audio-ruido-gaussiano.wav', audio_gaussiano, FREQ_AMOST)

    #print("[5] Tocando resultado final...")
    #sd.play(audio, FREQ_AMOST)
    #sd.wait() 

    print("[5] Pressione qualquer tecla para sair...")
    raw_input()
    






