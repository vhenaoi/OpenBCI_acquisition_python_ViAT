# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 08:36:44 2019

@author: john.ochoa
"""
import numpy as np;
import scipy.signal as signal
import matplotlib.pyplot as plt

#%%

# Compute filter kernel
def fkernel(m, f, w):
    m = np.arange(-m/2, (m/2)+1)
    b = np.zeros((m.shape[0]))
    b[m==0] = 2*np.pi*f # No division by zero
    b[m!=0] = np.sin(2*np.pi*f*m[m!=0]) / m[m!=0] # Sinc
    b = b * w # Windowing
    b = b / np.sum(b) # Normalization to unity gain at DC
    return b

def firws(m, f , w , t = None):
    """
    Designs windowed sinc type I linear phase FIR filter.
    Parameters:        
        m: filter order.
        f: cutoff frequency/ies (-6 dB;pi rad / sample).
        w: vector of length m + 1 defining window. 
        t: 'high' for highpass, 'stop' for bandstop filter. {default low-/bandpass}
    Returns:
        b: numpy.ndarray
            filter coefficients 
    """
    f = np.squeeze(f)
    f = f / 2; 
    w = np.squeeze(w)
    if (f.ndim == 0): #low pass
        b = fkernel(m, f, w)
    else:
        b = fkernel(m, f[0], w) #band
    
    if (f.ndim == 0) and (t == 'high'):
        b = fspecinv(b)
    elif (f.size == 2):
        b = b + fspecinv(fkernel(m, f[1], w)) #reject
        if t == None or (t != 'stop'):
            b = fspecinv(b) #bandpass        
    return b

## Spectral inversion
def fspecinv(b):
    b = -b
    b[int((b.shape[0]-1)/2)] = b[int((b.shape[0]-1)/2)]+1
    return b
#%%
def mfreqz(b,a,order,nyq_rate = 1):
    
    """
    Plot the impulse response of the filter in the frequency domain

    Parameters:
        
        b: numerator values of the transfer function (coefficients of the filter)
        a: denominator values of the transfer function (coefficients of the filter)
        
        order: order of the filter 
                
        nyq_rate = nyquist frequency
    """
    
    w,h = signal.freqz(b,a);
    h_dB = 20 * np.log10 (abs(h));
    
    plt.figure();
    plt.subplot(311);
    plt.plot((w/max(w))*nyq_rate,abs(h));
    plt.ylabel('Magnitude');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Frequency response. Order: ' + str(order));
    [xmin, xmax, ymin, ymax] = plt.axis();
    plt.grid(True);
    
    plt.subplot(312);
    plt.plot((w/max(w))*nyq_rate,h_dB);
    plt.ylabel('Magnitude (db)');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Frequency response. Order: ' + str(order));
    plt.grid(True)
    plt.grid(True)
    
    
    plt.subplot(313);
    h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)));
    plt.plot((w/max(w))*nyq_rate,h_Phase);
    plt.ylabel('Phase (radians)');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Phase response. Order: ' + str(order));
    plt.subplots_adjust(hspace=0.5);
    plt.grid(True)
    plt.show()

#%%
def filter_design(srate, locutoff = 0, hicutoff = 0, revfilt = 0):
    #Constants
    TRANSWIDTHRATIO = 0.25;
    fNyquist = srate/2;  
    
    #The prototipical filter is the low-pass, we design a low pass and transform it
    if hicutoff == 0: #Convert highpass to inverted lowpass
        hicutoff = locutoff
        locutoff = 0
        revfilt = 1 #invert the logic for low-pass to high-pass and for
                    #band-pass to notch
    if locutoff > 0 and hicutoff > 0:
        edgeArray = np.array([locutoff , hicutoff])
    else:
        edgeArray = np.array([hicutoff]);
    
    #Not negative frequencies and not frequencies above Nyquist
    if np.any(edgeArray<0) or np.any(edgeArray >= fNyquist):
        print('Cutoff frequency out of range')
        return False  
    
    # Max stop-band width
    maxBWArray = edgeArray.copy() # Band-/highpass
    if revfilt == 0: # Band-/lowpass
        maxBWArray[-1] = fNyquist - edgeArray[-1];
    elif len(edgeArray) == 2: # Bandstop
        maxBWArray = np.diff(edgeArray) / 2;
    maxDf = np.min(maxBWArray);
    
    # Default filter order heuristic
    if revfilt == 1: # Highpass and bandstop
        df = np.min([np.max([maxDf * TRANSWIDTHRATIO, 2]) , maxDf]);
    else: # Lowpass and bandpass
        df = np.min([np.max([edgeArray[0] * TRANSWIDTHRATIO, 2]) , maxDf]);
    
    print(df)
    
    filtorder = 3.3 / (df / srate); # Hamming window
    filtorder = np.ceil(filtorder / 2) * 2; # Filter order must be even.
    
    # Passband edge to cutoff (transition band center; -6 dB)
    dfArray = [[df, [-df, df]] , [-df, [df, -df]]];
    cutoffArray = edgeArray + np.array(dfArray[revfilt][len(edgeArray) - 1]) / 2;
    print('pop_eegfiltnew() - cutoff frequency(ies) (-6 dB): '+str(cutoffArray)+' Hz\n');
    # Window
    winArray = signal.hamming(int(filtorder) + 1);
    # Filter coefficients
    if revfilt == 1:
        filterTypeArray = ['high', 'stop'];
        b = firws(filtorder, cutoffArray / fNyquist, winArray, filterTypeArray[len(edgeArray) - 1]);
    else:
        b = firws(filtorder, cutoffArray / fNyquist, winArray);

    return filtorder, b;    

#fs = 250;
##design
#order, lowpass = filter_design(fs, locutoff = 0, hicutoff = 50, revfilt = 0);
##plot
#mfreqz(lowpass,1,order, fs/2);
#
#order, highpass = filter_design(fs, locutoff = 4, hicutoff = 0, revfilt = 1);
##plot
#mfreqz(highpass,1,order, fs/2);
#
#order, bandpass = filter_design(fs, locutoff = 4, hicutoff = 50, revfilt = 0);
##plot
#mfreqz(bandpass,1,order, fs/2);
#
#order, notch = filter_design(fs, locutoff = 50, hicutoff = 70, revfilt = 1);
##plot
#mfreqz(notch,1,order, fs/2);

##%%load signal and apply filter
#import scipy.io as sio;
##carga de los datos
#mat_contents = sio.loadmat('senal_anestesia.mat')
##los datos se cargan como un diccionario, se puede evaluar los campos que contiene
#print("Los campos cargados son: " + str(mat_contents.keys()));
##la senal esta en el campo data
#senal_org = mat_contents['data'];
#senal_org = senal_org[0,:];
#
#senal_filtrada_pasaaltas = signal.filtfilt(highpass, 1, senal_org);
#senal_filtrada_pasabajas = signal.filtfilt(lowpass, 1, senal_org);
#senal_filtrada_pasabanda = signal.filtfilt(bandpass, 1, senal_org);
#senal_filtrada_rechazabanda = signal.filtfilt(notch, 1, senal_org);
#
#plt.subplot(2,2,1);
#plt.plot(senal_org[0:250]);
#plt.plot(senal_filtrada_pasaaltas[0:250]);
#plt.title('Pasa-altas');
#plt.subplot(2,2,2);
#plt.plot(senal_org[0:250]);
#plt.plot(senal_filtrada_pasabajas[0:250]);
#plt.title('Pasa-bajas');
#plt.subplot(2,2,3);
#plt.plot(senal_org[0:250]);
#plt.plot(senal_filtrada_pasabanda[0:250]);
#plt.title('Pasa-banda');
#plt.subplot(2,2,4);
#plt.plot(senal_org[0:250]);
#plt.plot(senal_filtrada_rechazabanda[0:250]);
#plt.title('Rechaza-banda');
#
#plt.show();
#
##%%analisis espectral
#import scipy.signal as pds
#
#f, Pxx = pds.welch(senal_org, fs, 'hanning', fs*2, fs)
#plt.title('Espectro original');
#plt.plot(f, Pxx);
#plt.show()
#
#f, Pxx = pds.welch(senal_filtrada_pasaaltas, fs, 'hanning', fs*2, fs)
#plt.title('Espectro original - pasaaltas');
#plt.plot(f, Pxx);
#plt.show()
#
#f, Pxx = pds.welch(senal_filtrada_pasabajas, fs, 'hanning', fs*2, fs)
#plt.title('Espectro original - pasabajas');
#plt.plot(f, Pxx);
#plt.show()
#
#f, Pxx = pds.welch(senal_filtrada_rechazabanda, fs, 'hanning', fs*2, fs)
#plt.title('Espectro original - rechazabandas');
#plt.plot(f, Pxx);
#plt.show()
#
#
#f, Pxx = pds.welch(senal_filtrada_pasabanda, fs, 'hanning', fs*2, fs)
#plt.title('Espectro original - pasabanda');
#plt.plot(f, Pxx);
#plt.show()
#
##%%
#f, Pxx = pds.welch(senal_filtrada_pasabajas, fs, 'hanning', fs*2, fs)
#plt.subplot(2,2,1);
#plt.title('Espectro original - pasaaltas');
#plt.xlim([0,50]);
#plt.plot(f, Pxx);
#
#f, Pxx = pds.welch(senal_filtrada_pasabajas, fs, 'hanning', fs*4, fs*2)
#plt.subplot(2,2,2);
#plt.title('Espectro original - pasaaltas');
#plt.xlim([0,50]);
#plt.plot(f, Pxx);
#
#f, Pxx = pds.welch(senal_filtrada_pasabajas, fs, 'hanning', fs*8, fs*4)
#plt.subplot(2,2,3);
#plt.title('Espectro original - pasaaltas');
#plt.xlim([0,50]);
#plt.plot(f, Pxx);
#
#f, Pxx = pds.welch(senal_filtrada_pasabajas, fs, 'hanning', fs*10, fs*5)
#plt.subplot(2,2,4);
#plt.title('Espectro original - pasaaltas');
#plt.plot(f, Pxx);
#plt.xlim([0,50]);
#plt.show()
#
##This function applies a linear digital filter twice, once forward and once 
##backwards. The combined filter has zero phase and a filter order twice that of the original.
##signal_filtered = signal.filtfilt(b, 1, senal);#
#
##Filter a data sequence, x, using a digital filter. This works for many
##fundamental data types (including Object type). The filter is a direct form II
## transposed implementation of the standard difference equation (see Notes).
##y = signal.lfilter(b, 1, senal)
#
###%%
##from numpy import array, ones
##from scipy.signal import lfilter, lfilter_zi, butter
##b, a = butter(5, 0.25)
##zi = lfilter_zi(b, a)
##y, zo = lfilter(b, a, ones(10), zi=zi)
##print(y)
#y = lfilter(b, a, ones(10))
#print(y)
