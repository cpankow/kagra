import glob
import os
from collections import defaultdict
from argparse import ArgumentParser

import numpy as np

from mpl_toolkits import basemap
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt
from matplotlib import cm as mpl_cm
from matplotlib import lines as mpl_lines
from matplotlib import colorbar
from matplotlib import colors
from matplotlib.ticker import MaxNLocator
import matplotlib.gridspec as gridspec

from skyutils import *

# Determine which plots to make
argp = ArgumentParser()
argp.add_argument("-n", "--network", default=None, help="Choices are all, 'HLV_to_HKLV', and 'HKLV_to_HIKLV'")
args = argp.parse_args()

network_to_plot = args.network

runs_kagra = np.loadtxt('err_snr_antenna_HKLV')
runs_nokagra = np.loadtxt('err_snr_antenna_HLV')
runs_india = np.loadtxt('err_snr_antenna_HIKLV')

#outlier_list = np.loadtxt('outliers_HIKLV')
outlier_list = np.loadtxt('outliers_HLV')

if network_to_plot == 'all':
    runs_to_plot = [runs_nokagra, runs_kagra, runs_india]
    names = ['HLV', 'HKLV', 'HIKLV']
    scatter_config = 'HIKLV'
elif network_to_plot == 'HLV_to_HKLV':
    runs_to_plot = [runs_nokagra, runs_kagra]
    names = ['HLV', 'HKLV']
    scatter_config = 'HKLV'
elif network_to_plot == 'HKLV_to_HIKLV':
    runs_to_plot = [runs_kagra, runs_india]
    names = ['HKLV', 'HIKLV']
    scatter_config = 'HIKLV'
elif network_to_plot == 'HLV':
    runs_to_plot = [runs_nokagra]
    names = ['HLV']
    scatter_config = 'HLV'



# Set up plots
plt.figure(1)
gs = gridspec.GridSpec(3, 3)
gs.update(hspace=0.0, wspace=0.0)
ax1 = plt.subplot(gs[1:, :-1])
ax2 = plt.subplot(gs[0, :-1], sharex=ax1)
ax3 = plt.subplot(gs[1:, 2], sharey=ax1)

#print outlier_list
#print outlier_list[0]

scatter_shape = ['o', '+', 's']
colors_options = ['gray', 'cyan', 'white']
colors_stats = ['black', 'blue', 'red']


for runs in runs_to_plot:

    #print runs[0, :]

    err_reg = runs[:, 0]
    snr = runs[:, 1]
    antenna_pattern = runs[:, 2]
    run_numbers = runs[:, 3]
    hist_color = colors_options.pop(0)
    statistics_color = colors_stats.pop(0)
    label = names.pop(0)

    # Find points that aren't outliers for histograms
    err_reg_noout = []
    antenna_pattern_noout = []

    # FIXME: list comprehension
    for index, enum in enumerate(run_numbers):
        if enum not in outlier_list:
            err_reg_noout.append(err_reg[index])
            antenna_pattern_noout.append(antenna_pattern[index])



    #Scatter plot of SNR vs. Error Regions
    if label == scatter_config:

        norm = colors.Normalize(vmin=min(snr), vmax=max(snr))
        smap = mpl_cm.ScalarMappable(norm=norm, cmap=plt.get_cmap("viridis"))

        nonoutlier_marker = scatter_shape.pop(0)
        outlier_marker = scatter_shape.pop(0)
        for index, enum in enumerate(run_numbers):
            if enum in outlier_list:
                marker = outlier_marker
            #elif err_reg[index] > 1000:
            #    print str(int(enum)) + ' has an error region of ' + str(err_reg[index]) + ' and is not on the blacklist'
            #    print runs[index, :]
            #    marker = 's'
            else:
                marker = nonoutlier_marker
            scatter = ax1.scatter(err_reg[index], antenna_pattern[index], marker=marker, c=smap.to_rgba(snr[index]), edgecolors='None', cmap='viridis')

        ax1.set_xlabel('Error Region (squared degrees)')
        ax1.set_ylabel('Network Antenna Pattern')
        ax1.set_xlim(1e-1, 1e5)
        ax1.set_ylim(0.0, 1.4)
        ax1.set_xscale('log')

    # Histogram of Error Regions
    ax2.hist(err_reg_noout, color=hist_color, histtype='stepfilled', bins=np.logspace(-1, 5, 20), alpha=0.5, label=label)
    ax2.tick_params(axis='x', top='on', bottom='on', labelbottom='off', labeltop='off')
    ax2.set_ylabel('Count')
    nbins = len(ax1.get_xticklabels())
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='lower', integer=True))

    # Find the median and 90% interval of Error Region histograms
    err_med = np.percentile(err_reg_noout, 50)
    err_95 = np.percentile(err_reg_noout, 95)
    err_5 = np.percentile(err_reg_noout, 5)
    ax2.axvline(x=err_med, color=statistics_color, linewidth=2)
    ax2.axvline(x=err_95, color=statistics_color, linewidth=2, ls='-.')
    ax2.axvline(x=err_5, color=statistics_color, linewidth=2, ls='-.')

    # Histogram of Antenna Patterns
    ax3.hist(antenna_pattern, color=hist_color, histtype='stepfilled', bins=np.linspace(0, 1, 20), orientation='horizontal', alpha=0.5)
    ax3.tick_params('y', left='on', right='on', labelleft='off', labelright='off')
    ax3.set_xlabel('Count')
    ax3.xaxis.set_major_locator(MaxNLocator(integer=True))
    xticks = ax3.xaxis.get_major_ticks()
    xticks[0].label1.set_visible(False)


    # Find the mean and standard deviation of antenna pattern histograms
    #net_mean = np.mean(antenna_pattern)
    #net_stdev = np.std(antenna_pattern)
    #ax3.axhline(y=net_mean, color=statistics_color, linewidth=2)
    #ax3.axhline(y=(net_mean + net_stdev), color=statistics_color, linewidth=2, ls='dashed')
    #ax3.axhline(y=(net_mean - net_stdev), color=statistics_color, linewidth=2, ls='dashed')

    net_med = np.percentile(antenna_pattern_noout, 50)
    net_95 = np.percentile(antenna_pattern_noout, 95)
    net_5 = np.percentile(antenna_pattern_noout, 5)
    ax3.axhline(y=net_med, color=statistics_color, linewidth=2, label=(label + ' Median'))
    ax3.axhline(y=net_95, color=statistics_color, linewidth=2, ls='-.', label=(label + ' 90% Conf.'))
    ax3.axhline(y=net_5, color=statistics_color, linewidth=2, ls='-.')


# Overall plot features

if network_to_plot == 'all':
    plt.suptitle('SNR, Error Regions, and Network Antenna Pattern for HLV, HKLV, and HIKLV with Scatterplot of HIKLV')
elif network_to_plot == 'HLV_to_HKLV':
    plt.suptitle('SNR, Error Regions, and Network Antenna Pattern for HLV and HKLV with Scatterplot of HKLV')
elif network_to_plot == 'HKLV_to_HIKLV':
    plt.suptitle('SNR, Error Regions, and Network Antenna Pattern for HKLV and HIKLV with Scatterplot of HIKLV')
elif network_to_plot == 'HLV':
    plt.suptitle('SNR, Error Regions, and Network Antenna Pattern for HLV')
smap.set_array([0, 1])
cbar = plt.colorbar(smap, label='Network SNR')  # FIXME: this is not a common scale
cbar.ax.tick_params(labelsize=10)
#ax1.legend(loc='upper left', fontsize=7)
ax2.legend(loc='upper left', fontsize=7)
ax3.legend(fontsize=7)

if network_to_plot == 'all':
    plt.savefig("figures/snr_vs_err_allconfigs.png")
elif network_to_plot == 'HLV_to_HKLV':
    plt.savefig("figures/snr_vs_err_HLV_to_HKLV.png")
elif network_to_plot == 'HKLV_to_HIKLV':
    plt.savefig("figures/snr_vs_err_HKLV_to_HIKLV.png")
elif network_to_plot == 'HLV':
    plt.savefig('figures/snr_vs_err_HLV.png')
