#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Seção de imports
# =============================================================================

import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
from scipy import signal

# =============================================================================
# Configurações do receptor
# =============================================================================

ARQUIVO = "audio-ruido-gaussiano.wav"

DURACAO_PONTO = 0.060 # 60 ms
DURACAO_TRACO = 3*DURACAO_PONTO
DURACAO_INTERVALO = DURACAO_PONTO

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
# Funções do receptor.
# =============================================================================

def calcular_fft(amostras, t_amost):
    n_amostras = len(amostras)    
    freq_naturais = np.fft.fftfreq(n_amostras, t_amost)
    espectro = np.fft.fft(amostras)/n_amostras 
    
    # Desloca frequência zero para origem.
    # espectro = np.fft.fftshift(espectro) 
    # freq_naturais = np.fft.fftshift(freq_naturais)
    
    return (freq_naturais, espectro)
    
''' Plota um sinal no domínio do tempo e no domínio da frequência.'''
def plotar_sinal(amostras, t_amost, titulo='Título'):
    n_amostras = len(amostras)
    
    # Calcula a FFT.
    espectro = np.fft.fft(amostras)/n_amostras 
    freq_naturais = np.fft.fftfreq(n_amostras, t_amost)
    
    # Desloca frequência zero para origem.
    espectro = np.fft.fftshift(espectro) 
    freq_naturais = np.fft.fftshift(freq_naturais)
    
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
    ax[1].set_ylabel(u'|X(f)|')
    ax[1].set_title(u'Sinal no domínio da frequência', 
                                fontsize= 12, fontweight="bold")
    
    fig.tight_layout()
    plt.show(block=False)
    #plt.draw()
    
   
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

''' 
Esta função calcula a transformada Wavelet, do tipo Morlet, e plota o seu 
comportamento no tempo, mostrando exatamente onde há divisão entre som e 
silêncio.
'''
def plotat_wavelet(amostras, maior_ordem):

    larguras = np.arange(1, maior_ordem+1)
    cwtmatr = signal.cwt(amostras, signal.morlet, larguras)
            
    plt.figure()
    plt.title(u'Transformada Wavelet - primeira janela')
    plt.xlabel(u'Tempo (s)')
    plt.ylabel(u'Amplitudes')
    
    t = np.arange(0, n_amostras * t_amost, t_amost, dtype='float64')
    plt.plot(t, np.abs(cwtmatr[0]), 'k')
    plt.show(block=False)  
    
    plt.figure()
    plt.title(u'Transformada Wavelet - última janela')
    plt.xlabel(u'Tempo (s)')
    plt.ylabel(u'Amplitudes')
    
    t = np.arange(0, n_amostras * t_amost, t_amost, dtype='float64')
    plt.plot(t, np.abs(cwtmatr[maior_ordem-1]), 'r')
    plt.show(block=False)  
     
    
       
# =============================================================================
# Execução do programa.
# =============================================================================

if __name__ == "__main__":

    
    print('[1] Abrindo arquivo "%s"...' %ARQUIVO)
    (amostras, freq_amost) = sf.read(ARQUIVO, dtype='float64')

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
    
    plotar_sinal(amostras, t_amost, 'Áudio limpo')
    
    print("[4] Procurando frequências do código morse...")
     
    espectro_interesse = np.abs(espectro[0:(n_amostras/2-1)])
    freq_interesse = abs(freq_naturais[0:(n_amostras/2-1)])
    
    # Encontrando impulsos (vários).
    media_espectro = np.mean(espectro_interesse) 
    indices_impulsos = freq_interesse[
                    np.argwhere(espectro_interesse > 10*media_espectro)
    ]
    
    impulsos = []
    quantidade_impulsos = len(indices_impulsos)
    
    inicio_range = indices_impulsos[0]
    for i in range(0, quantidade_impulsos-1, 1):
    
        diferenca = indices_impulsos[i+1] - inicio_range 
    
        if diferenca > 200 or i == quantidade_impulsos-2:
        
            media = (indices_impulsos[i] + inicio_range)/2;
            impulsos.append(media)
            inicio_range = indices_impulsos[i+1];
        
        
    
    print impulsos 
  
    '''
    # Encontra a frequência com maior energia.

    print("[4] Encontrando frequência do codigo morse...")

    maior_potencia = espectro.max()
    arg_maior_potencia = espectro.argmax()
    freq_maior_potencia = np.round(np.abs(freq_naturais[arg_maior_potencia]))

    print("[5] Realizando filtragem passa banda... ")
    
    raw_input()
    exit()

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
           

    #sf.write('saida.ogg', sinal_filtrado[:5000000], freq_amost)
    '''
   
    plotat_wavelet(amostras, 10)
    
    raw_input()
    exit(0)

    maximo = np.max(np.abs(amostras))
    minimo = np.min(np.abs(amostras))

    morse = ''
    
    valor_anterior = np.abs(amostras)[0]
    contador_maximos = 0
    contador_minimos = 0
    estava_lendo_maximos = True
    
    n_amostras_intervalo = DURACAO_INTERVALO/t_amost
    
    morse += ''
    
    lendo_maximos = True
    
    for amostra in np.abs(amostras): 
        
        if lendo_maximos:
            contador_maximos += 1
   
        if amostra <= 0.3:
            contador_minimos += 1
        else:
            lendo_maximos = True
            contador_minimos = 0
        
        if contador_minimos == n_amostras_intervalo:
            
            if lendo_maximos:
                tempo_simbolo = (contador_maximos-contador_minimos)*t_amost
                if tempo_simbolo >= 0.9 * DURACAO_PONTO and tempo_simbolo <= 1.1 * DURACAO_PONTO:
                    morse += '.'
                elif tempo_simbolo >= 0.9 * DURACAO_TRACO and tempo_simbolo <= 1.1 * DURACAO_TRACO:
                    morse += '-'
                contador_maximos = 0
                contador_minimos = 0
                lendo_maximos = False
            else:
                 morse += ' '
                 contador_minimos = 0
                
       
    
    morse = morse.replace("  ", " ") 
    morse = morse.replace("   ", " / ")   
    
    CODIGO_INVERSO = {v: k for k, v in CODIGO.items()}  
    texto = ""
    
    simbolos = morse.split(" ")
    for simbolo in simbolos:
        if simbolo == '/':
            texto += " "
        else:
            texto += CODIGO_INVERSO[simbolo]
    
    print texto
    raw_input()
        
