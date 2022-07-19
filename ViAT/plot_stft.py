from scipy import signal as sig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


class TimeFrequency(object):
    '''
    This processing is given by calculating the short-time Fourier transform.
    '''

    def __init__(self, id_Subject, cc_Subject, date, loc, save):
        '''
        Rec: ID of the subject registered in the database, ID of the subject
            registered in the database, date of registration, location of the 
            registration and location to save.
        Func: Define variables and locations of the delivered files.
        '''
        self.__subject = id_Subject
        self.__cc = cc_Subject
        self.__date = date
        self.loc = loc + '/' + str(self.__subject) + \
            '_'+str(self.__cc) + '/' + date
        self.path_save = save + '/' + \
            str(self.__subject)+'_'+str(self.__cc) + '/' + date

    def plot_stft(self):
        '''
        Reads the log on the Oz-FCz channel and applies short-time Fourier 
        transform stft from the scipy.signal library
        STFTs can be used as a way to quantify the change in the frequency of a
        non-stationary signal and the phase content over time.
        '''
        name = str(self.__subject)+'_'+str(self.__cc)
        signal = pd.read_csv(self.loc+'/'+'Record_' +
                             name + '.csv', sep=';', index_col=0)
        # signal = pd.read_csv(self.loc +'/'+ name +'.csv', header=None)
        fs = 250

        f, t, Zxx = sig.stft(signal['C2'], fs, nperseg=500)

        levels = MaxNLocator(nbins=15).tick_values(
            np.abs(abs(Zxx)).min(), np.abs(abs(Zxx)).max())

        cmap = plt.get_cmap('jet')
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        fig, ax0 = plt.subplots(nrows=1)
        im = ax0.pcolormesh(t, f, np.abs(abs(Zxx)), cmap=cmap, norm=norm)
        plt.ylim([0, 30])
        plt.title('STFT_'+name)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        # imagen ploteada y la figura donde esta en el subplot
        cbar = plt.colorbar(im, ax=ax0)
        cbar.set_label('Amplitude [uV]')
        img = ('Time-Frequency Oz-FCz')
        plt.savefig(self.path_save + '/' + img + '_' + name + '.jpg')
        ini = self.loc+'/'+'Record_' + name + '.csv'
        fig = self.path_save + '/' + img + '_' + name + '.jpg'
        return ini, fig, signal


if __name__ == '__main__':
    path_in = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
    path_out = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Processing'
    run = TimeFrequency('H1', '1152207135', '06-28-2020', path_in, path_out)
    ini, fig, signal2 = run.plot_stft()
