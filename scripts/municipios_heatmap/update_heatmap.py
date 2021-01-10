#!/usr/bin/env python
# coding: utf-8


import os
import glob
import itertools

import pandas as pd
import seaborn as sns
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import ticker, dates, rcParams
from matplotlib.colors import LogNorm, PowerNorm
import locale

np.warnings.filterwarnings('ignore')


def draw(fdata, pdata):
    
    ddata = (fdata.T / fdata.max(axis=1)).T.copy()

    color_text = '#9b9ba3'
    locale.setlocale(locale.LC_TIME, "es_US.UTF8")
    rcParams['font.family'] = 'Quicksand'

    f = plt.figure(figsize=(40,50), facecolor='#f9f9f9')
    plt.subplots_adjust(wspace=0.04)
    gs = f.add_gridspec(1, 6)
    heat_ax = f.add_subplot(gs[:, :-1])
    bar_ax = f.add_subplot(gs[:, -1])

    datelist = dates.date2num(ddata.columns.to_pydatetime())
    im = heat_ax.imshow(ddata, cmap='Spectral_r', aspect='auto', extent=[datelist[0], datelist[-1], len(ddata), 0], alpha=.8)
    heat_ax.yaxis.set_major_locator(ticker.FixedLocator([i + 0.5 for i in list(range(0,len(ddata)))]))
    heat_ax.yaxis.set_minor_locator(ticker.IndexLocator(1,0))
    heat_ax.set_yticklabels(ddata.index.tolist())
    heat_ax.xaxis.set_major_locator(dates.AutoDateLocator())
    heat_ax.xaxis.set_major_formatter(dates.DateFormatter('%B'))
    heat_ax.grid(axis='x', which='major', alpha=.8, color='white', linewidth=4, linestyle='-')
    heat_ax.grid(axis='y', which='minor', alpha=.1, color='white', linewidth=1, linestyle='-')
    heat_ax.tick_params(which='both', axis='both', labelcolor=color_text, labeltop=True, pad=12, rotation=0, width=0, length=0)
    heat_ax.tick_params(axis='x', labelsize=20)
    heat_ax.tick_params(axis='y', labelsize=15)
    heat_ax.set_ylabel('Municipios', fontdict={'size':100, 'family':'Charter'}, color=color_text, labelpad=35)
    heat_ax.annotate(text='Casos Activos Diarios', xy=(.5,0.94), xycoords='figure fraction', ha='center', va='bottom', color=color_text, fontsize=120, fontfamily='Charter')
    heat_ax.annotate(text='como proporción del valor máximo por municipio', xy=(.5,0.935), xycoords='figure fraction', ha='center', va='top', color=color_text, fontsize=50, fontfamily='Charter')
    heat_ax.annotate(text='El número de casos activos en un día corresponde al número de casos que han sido confirmados en los últimos 14 días.\nEn base a datos producidos por el Ministerio de Desarrollo Productivo y Economía Plural y almacenados en https://github.com/mauforonda/covid19bolivia-municipal', xy=(.5,0.040), xycoords='figure fraction', ha='center', va='bottom', color=color_text, fontsize=25, fontfamily='Charter', linespacing=1.6)
    
    pdata[::-1].plot(kind='barh', ax=bar_ax, color='#8f5383', alpha=.7, width=0.9)
    bar_ax.set_yticks([])
    bar_ax.tick_params(axis='x', labeltop=True, labelcolor=color_text, labelsize=20, pad=12, rotation=0, width=0, length=0)
    bar_ax.grid('x', 'major', alpha=.3, color=color_text, linewidth=2, linestyle='-')
    bar_ax.xaxis.set_major_locator(ticker.MaxNLocator(3))
    bar_ax.set_xlabel('Casos acumulados\npor 100 Mil habitantes', fontdict={'size':30, 'family':'Charter'}, color=color_text, labelpad=40, loc='left')
    bar_ax.xaxis.set_label_position('top')
    bar_ax.set_ylabel('')

    for ax in [heat_ax, bar_ax]:
        ax.set_frame_on(False)
    plt.savefig('plots/municipios_heatmap.jpg', bbox_inches='tight', dpi=100, pad_inches=0.8)
    plt.close()


def load_data():
    df = pd.DataFrame([])
    tdf = pd.DataFrame([])

    for file_name in glob.glob('./scripts/municipios_heatmap/data/*.csv'):
        dept_data = pd.read_csv(file_name)
        dept_data['fecha'] = pd.to_datetime(dept_data['fecha'])

        dept_data = dept_data.set_index(['cod_ine', 'fecha'])['confirmados'].unstack()
        tdf = pd.concat([tdf, dept_data])

        dept_data = dept_data.fillna(0).T
        dept_data = dept_data.rolling(window=14).sum().dropna(how='all').T.round()
        df = pd.concat([df, dept_data])

    return df, tdf


if __name__ == '__main__':
    muni = pd.read_csv('scripts/municipios_heatmap/sdsn.gen.csv')
    muni = muni.set_index('cod_ine')

    cmun = muni[['municipio']]
    cmun = cmun[~cmun.index.duplicated(keep='first')]

    df, tdf = load_data()

    fdata = df[df.T.max() > 15]
    fdata = fdata.T.interpolate(method='quadratic').T
    fdata = fdata.fillna(0).round()
    fdata[fdata < 1] = 1e-3

    fdata = fdata.loc[fdata.idxmax(axis=1).sort_values(ascending=False).index]
    pdata = (1e5 * tdf.loc[fdata.index].sum(axis=1).div(muni['poblacion']))
    pdata = pdata[~pdata.isnull()]
    pdata = pdata[fdata.index]

    fdata.index = [_ for _ in itertools.chain(*cmun.loc[fdata.index].to_numpy())]

    draw(fdata, pdata)

    print(fdata.columns[-1].strftime("%d de %B de %Y"))
