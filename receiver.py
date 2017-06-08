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
    
    plt.plot(t, np.abs(cwtmatr[maior_ordem/2]), 'm')
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
    
    n_amostras_intervalo = DURACAO_INTERVALO/t_amost
    
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
       
    
    # Tratando eventuais espaços em exceço.    
    morse = morse.replace("  ", " ") 
    morse = morse.replace("   ", " / ")  

    return morse
    
     
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
    
    frequencias_tonais = []
    quantidade_impulsos = len(indices_impulsos)
    
    inicio_range = indices_impulsos[0]
    for i in range(0, quantidade_impulsos-1, 1):
        diferenca = indices_impulsos[i+1] - inicio_range 
        if diferenca > 200 or i == quantidade_impulsos-2:
            media = (indices_impulsos[i] + inicio_range)/2;
            frequencias_tonais.append(np.round(media[0]))
            inicio_range = indices_impulsos[i+1];
        
    print frequencias_tonais 
    
    freqs_corte = []
    for freq in frequencias_tonais:
        freqs_corte.append(freq - 40)
        freqs_corte.append(freq + 40)
    
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
        
    # Calculando SNR.
    
    ruido_restante = amostras - sinal_filtrado; 
    
    SNR = np.mean(sinal_filtrado ** 2)/np.mean(ruido_restante ** 2 ); 
    SNRdB = 10 * np.log10(SNR)
    
    print "Relação sinal ruído (em dB): ", SNRdB
    
    # Plotando filtro FIR.
    
    w, h = signal.freqz(coeficientes)
    plt.figure()
    plt.title(u'Filtro FIR')
    plt.xlabel(u'Frequência (Hz)')
    plt.ylabel(u'Amplitude do Filtro')
    plt.plot(w, 20 * np.log10(abs(h)), 'g')
    plt.show(block=False) 
  
  
    sf.write('audio-filtrado.wav', sinal_filtrado, freq_amost)
    
    
    # Plotando sinal filtrado.
    plotar_sinal(sinal_filtrado, t_amost, titulo='Sinal Filtrado')

    # Plota a transformada Wavelet.
    #plotat_wavelet(sinal_filtrado, 10)
  
    print("[4] Convertendo áudio para código morse.")
    
    #plotar_sinal(np.abs(sinal_filtrado), t_amost, titulo='Módulo do sinal filtrado')
    morse = audio_para_morse(sinal_filtrado)

    print morse
               
    print("[5] Convertendo morse para texto.")
    texto = morse_para_texto(morse)

    print "[6] Texto identificado: ", texto
    raw_input()
        
