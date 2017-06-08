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

ARQUIVO_AUDIO_RUIDO = "audio-ruido-gaussiano.wav"
ARQUIVO_AUDIO_FILTRADO = "audio-filtrado.wav"

DURACAO_PONTO = 0.060 # 60 ms
DURACAO_TRACO = 3*DURACAO_PONTO
DURACAO_INTERVALO = DURACAO_PONTO
INTERVALO_FILTRAGEM = 40.0

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

CODIGO_INVERSO = {v: k for k, v in CODIGO.items()}  

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
Esta função plota a resposta em frequência de um filtro digital.
'''
def plotar_filtro_fir(coeficientes, freqs_corte):

    w, h = signal.freqz(coeficientes)
    w = (w/np.pi) * banda
    
    hDb = 20 * np.log10(abs(h))
    
    
    # Resposta no tempo (sinc).
    
    fig1 = plt.figure()
    fig1.canvas.set_window_title("Filtro FIR no domínio do tempo")
    
    plt.plot(coeficientes, 'k-', linewidth=1)
    plt.title(u'Filtro FIR, com %d coeficientes.' %len(coeficientes))
    plt.xlabel(u'Tempo (s)')
    plt.ylabel(u'Amplitude do Filtro FIR')
    plt.grid(True)
    plt.show(block=False)
    
    # Resposta em frequência do filtro
    
    fig2 = plt.figure()
    fig2.canvas.set_window_title("Resposta em frequência do filtro FIR")
    plt.title(u'Filtro FIR')
    plt.xlabel(u'Frequência (Hz)')
    plt.ylabel(u'Atenuação do Filtro (em dB)')
    plt.plot(w, hDb, 'g')
    plt.grid(True)
    plt.show(block=False) 
    
    # Plota os locais das frequências de corte e onde a atenuação é de 70dB.
    for freq in freqs_corte:
        plt.axvline(freq, color='k', linewidth=1)
        plt.plot(freq, -70, 'ko', linewidth=1)

    
''' 
Esta função calcula a transformada Wavelet, do tipo Morlet, e plota o seu 
comportamento no tempo, mostrando exatamente onde há divisão entre som e 
silêncio.
'''
def plotat_wavelet(amostras, maior_ordem):
    
    larguras = np.arange(1, maior_ordem+1)
    cwtmatr = signal.cwt(amostras, signal.morlet, larguras)
    
    t = np.arange(0, n_amostras * t_amost, t_amost, dtype='float64')
            
    plt.figure()
    plt.title(u'Transformada Wavelet - primeira janela')
    plt.xlabel(u'Tempo (s)')
    plt.ylabel(u'Amplitudes')
    plt.plot(t, np.abs(cwtmatr[0]), 'k')
    plt.show(block=False)  
    

    plt.figure()
    plt.title(u'Transformada Wavelet - última janela')
    plt.xlabel(u'Tempo (s)')
    plt.ylabel(u'Amplitudes')
    plt.plot(t, np.abs(cwtmatr[maior_ordem-1]), 'r')
    plt.show(block=False)  
     
     
def morse_para_texto(morse):

    simbolos = morse.split(" ")
    texto = ""
    for simbolo in simbolos:
        if simbolo == '/':
            texto += " "
        elif simbolo in CODIGO_INVERSO.keys():
            texto += CODIGO_INVERSO[simbolo]
        else:
            pass
    return texto
    

def audio_para_morse(audio):

    maximo = np.max(np.abs(audio))
    minimo = np.min(np.abs(audio))
    
    valor_anterior = np.abs(audio)[0]
    contador_maximos = 0
    contador_minimos = 0
    estava_lendo_maximos = True
    
    # Define os limites máximos de duração.
    
    duracao_ponto_inferior = 0.85 * DURACAO_PONTO
    duracao_ponto_superior = 1.15 * DURACAO_PONTO
    duracao_traco_inferior = 0.85 * DURACAO_TRACO
    duracao_traco_superior = 1.15 * DURACAO_TRACO
    
    n_amostras_intervalo = DURACAO_INTERVALO/t_amost
    
    # Algoritmo para procurar por pontos, traços e intervalos.
    
    morse = ""
    lendo_maximos = True
    for amostra in np.abs(audio): 
        
        if lendo_maximos:
            contador_maximos += 1
   
        if amostra <= 0.5 * maximo:
            contador_minimos += 1
        else:
            lendo_maximos = True
            contador_minimos = 0
        
        if contador_minimos == n_amostras_intervalo:
  
            if lendo_maximos:
                tempo_simbolo = np.abs(contador_maximos-contador_minimos)*t_amost
                if tempo_simbolo >= duracao_ponto_inferior and tempo_simbolo <= duracao_ponto_superior:
                    morse += '.'
                elif tempo_simbolo >= duracao_traco_inferior and tempo_simbolo <= duracao_traco_superior:
                    morse += '-'
                contador_maximos = 0
                contador_minimos = 0
                lendo_maximos = False
            else:
                 morse += ' '
                 contador_minimos = 0
       
    
    # Tratando eventuais espaços em exceço.    
    morse = morse.replace("  ", " ") 
    morse = morse.replace("   ", " / ")  
    
    return morse

    
def filtrar_sinal(amostras):
 
    frequencias_tonais = []
 
    # Calcula a FFT.
    espectro = np.fft.fft(amostras)/n_amostras 
    freq_naturais = np.fft.fftfreq(n_amostras, t_amost)
    
    # Obtém apenas a parte positiva do espectro.
    espectro_interesse = np.abs(espectro[0:(n_amostras/2-1)])
    freq_interesse = abs(freq_naturais[0:(n_amostras/2-1)])
    
    # Encontrando impulsos (vários).
    media_espectro = np.mean(espectro_interesse) 
    indices_impulsos = freq_interesse[
                    np.argwhere(espectro_interesse > 10 * media_espectro)
    ]
    
    quantidade_impulsos = len(indices_impulsos)
    
    inicio_range = indices_impulsos[0]
    for i in range(0, quantidade_impulsos-1, 1):
        diferenca = indices_impulsos[i+1] - inicio_range 
        if diferenca > 200 or i == quantidade_impulsos-2:
            media = (indices_impulsos[i] + inicio_range)/2;
            frequencias_tonais.append(np.round(media[0]))
            inicio_range = indices_impulsos[i+1];
            
    freqs_corte = []
    for freq in frequencias_tonais:
        freqs_corte.append(freq - INTERVALO_FILTRAGEM)
        freqs_corte.append(freq + INTERVALO_FILTRAGEM)
    
    # Construindo filtro FIR.
    faixa_transicao = 5.0/banda
    atenuacao = 70.0 # Em dB.
        
    # Encontrando parâmetros de Kaiser.
    num_coeficientes, beta = signal.kaiserord(atenuacao, faixa_transicao)
    
    # Calculando o atraso do FIR.
    ordem = (num_coeficientes-1)
    num_amostras_atrasadas = int(0.5 * ordem)
    atraso = num_amostras_atrasadas * t_amost # Em segundos.
    
    # Corrigindo atraso.
    amostras_maior = np.append(amostras, np.zeros(num_amostras_atrasadas))
    
    # Criando o filtro FIR.
    coeficientes = signal.firwin(num_coeficientes, freqs_corte, window=('kaiser', beta), pass_zero=False, nyq = banda)
    
    # Filtrando o sinal original.
    sinal_filtrado = signal.lfilter(coeficientes, 1.0, amostras_maior)
    
    # Remova o atraso do início do sinal filtrado.
    sinal_filtrado = np.delete(sinal_filtrado, range(0, num_amostras_atrasadas, 1))
    
    # Plotando filtro FIR.
    plotar_filtro_fir(coeficientes, freqs_corte)

    
    return sinal_filtrado
       
     
# =============================================================================
# Execução do programa.
# =============================================================================

if __name__ == "__main__":

    
    print('[1] Abrindo arquivo "%s"...' %ARQUIVO_AUDIO_RUIDO)
    (amostras, freq_amost) = sf.read(ARQUIVO_AUDIO_RUIDO, dtype='float64')

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
    
    plotar_sinal(amostras, t_amost, 'Áudio limpo')
    
    print("[3] Filtrando sinal.")
    sinal_filtrado = filtrar_sinal(amostras)
    plotar_sinal(sinal_filtrado, t_amost, titulo='Sinal Filtrado')
    
    # Calculando SNR.
    ruido_restante = amostras - sinal_filtrado; 
    SNR = np.mean(sinal_filtrado ** 2)/np.mean(ruido_restante ** 2 ); 
    SNRdB = 20 * np.log10(SNR)
    
    print("  [3.1] Foram atenuados %f dB de ruído" %SNRdB)
    
    # Plota a transformada Wavelet.
    #plotat_wavelet(amostras, 10)
  
    print("[4] Convertendo áudio para código morse.")
    morse = audio_para_morse(sinal_filtrado)
    print("  [4.1] Código morse: %s" %morse)
            
    print("[5] Convertendo morse para texto.")
    texto = morse_para_texto(morse)

    print("  [5.1] Texto identificado: %s" %texto)
    
    print("[6] Salvando resultado em %s" %ARQUIVO_AUDIO_FILTRADO)
    
    sf.write(ARQUIVO_AUDIO_FILTRADO, sinal_filtrado, freq_amost)
    
    print("[7] Pressione qualquer tecla para sair...")
    raw_input()
        
