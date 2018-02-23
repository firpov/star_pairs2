# -*- coding: utf-8 -*-

"""Console script for star_pairs."""

import click

import readline
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
from time import localtime
from time import strftime
import math
import os
import pkg_resources

# _Define constants:
LATITUDE = '-30d14m26.700s'   # WGS84

# _Define functions:
def format_decimal(s):
    "Format HH:MM:SS strings in decimal HH.H floats"
    if len(s) == 14:  # For latitude and longitude (degress)
        return float(s[0:3]) - float(s[4:6]) / 60. - float(s[7:12]) / 3600.
    elif len(s) == 10:  # For LST (hours)
        return float(s[0:2]) + float(s[3:5]) / 60. + float(s[6:10]) / 3600.
    else:
        print 'Wrong len(string), see format_decimal function'

def format_Dec(s):
    "Format from a string DD:MM:SS.S to DD.D float the Dec values from pairs.txt"
    for x in range(len(s)):
        s[x] = float(s[x][:3]) - float(s[x][4:6]) / 60. - \
                float(s[x][7:11]) / 3600.
    return s

def format_RA(s):
    "Format from a string HH:MM:SS.S to DD.D float the RA values from pairs.txt"
    for x in range(len(s)):
        s[x] = float(s[x][:2]) + float(s[x][3:5]) / 60. + \
                float(s[x][6:11]) / 3600.
    return s

def fill_list(l):
    "Introducing the file pairs.txt, with columns and lines, it creates lists and fill them with data"
    ID = []
    ID_P1P2 = []
    RA = []
    Dec = []
    Vmag_AcqCam = []
    Vmag_P1P2 = []
    Sep = []
    Pangle = []
    for i in range((len(l) / 3) + 1):
        ID.append(l[3 * i].split()[0])
        ID_P1P2.append(l[3 * i + 1].split()[0])
        RA.append(l[3 * i].split()[1])
        Dec.append(l[3 * i].split()[2])
        Vmag_AcqCam.append(l[3 * i].split()[3])
        Vmag_P1P2.append(l[3 * i + 1].split()[3])
        Sep.append(l[3 * i].split()[4])
        Pangle.append(l[3 * i + 1].split()[4])
    return ID, ID_P1P2, RA, Dec, Vmag_AcqCam, Vmag_P1P2, Sep, Pangle

def cal_HA(LST, RA):
    "Calculate HA introducing RA and LST"
    HA = []
    for a in range(len(RA)):
        HA.append(LST - RA[a])
    return HA

def cal_altaz(RA, Dec, HA, latitude):
    "Convert from equatorial to altazimuthal coordinares (radians)"
    El = []
    Az = []
    for i in range(len(RA)):
        El.append(
            np.arcsin(
                np.sin(
                    np.radians(
                        Dec[i])) *
                np.sin(
                    np.radians(latitude)) +
                np.cos(
                    np.radians(
                        Dec[i])) *
                np.cos(
                    np.radians(latitude)) *
                np.cos(
                    np.radians(
                        HA[i] *
                        15.))))  # Radians
        Az.append(
            np.arccos(
                (np.sin(
                    np.radians(
                        Dec[i])) -
                np.sin(
                    El[i]) *
                    np.sin(
                    np.radians(latitude))) /
                (
                    np.cos(
                        El[i]) *
                    np.cos(
                        np.radians(latitude)))))  # Radians
        if np.sin(np.radians(HA[i] * 15.)) > 0.:
            Az[i] = 2. * np.pi - Az[i]
    return Az, El

def set_altaz(El, Az, ID, ID_P1P2, Vmag_AcqCam, Vmag_P1P2, Sep, Pangle):
    "Set format for displaying altazimuthal coordinates. Besides, it only takes"
    "pairs which are higher than 30 degrees in elevation. Plus it has to invert"
    "the elevation to be displayed right (issues about polar projection?)"
    r = []
    theta = []
    ID_f = []
    ID_P1P2_f = []
    Vmag_AcqCam_f = []
    Vmag_P1P2_f = []
    Sep_f = []
    Pangle_f = []
    size = []
    color_star = []
    alpha_star = []
    for i in range(len(El)):
        if np.degrees(El[i]) > 30.:
            r.append(90.0 - np.degrees(El[i]))
            theta.append(Az[i])
            ID_f.append(ID[i])
            ID_P1P2_f.append(ID_P1P2[i])
            Vmag_AcqCam_f.append(Vmag_AcqCam[i])
            Vmag_P1P2_f.append(Vmag_P1P2[i])
            Sep_f.append(Sep[i])
            Pangle_f.append(Pangle[i])
    return r, theta, ID_f, ID_P1P2_f, Vmag_AcqCam_f, Vmag_P1P2_f, Sep_f, Pangle_f

@click.command()
def main(args=None):
    """Console script for star_pairs."""

    # _Extract LST from computer, format LST
    try:
        import epics
        LST_epics = epics.caget("tcs:LST")
    except ImportError:
            LST_epics = "00:00:00.0"

    LST = format_decimal(LST_epics)

    # _Format latitude
    latitude = format_decimal(LATITUDE)

    # _Pairs from equatorial coordinates (J2000) to altazimuthal
    # ___Read from file
    file = pkg_resources.resource_stream(__name__, "data/pairs.txt")
    lines = file.readlines()
    file.close()

    # ___Fill lists with data from pairs.txt
    ID, ID_P1P2, RA, Dec, Vmag_AcqCam, Vmag_P1P2, Sep, Pangle = fill_list(lines)

    # ___Format RA and Dec: so it could be used in the code tuning
    RA = format_RA(RA)
    Dec = format_Dec(Dec)

    # ___Calculate HA
    HA = cal_HA(LST, RA)

    #__Calculate altazimuthal coordinates
    Az, El = cal_altaz(RA, Dec, HA, latitude)

    #__Plotting in polar coordiantes
    #____Format altazimuthal coordinates
    r, theta, ID_f, ID_P1P2_f, Vmag_AcqCam_f, Vmag_P1P2_f, Sep_f, Pangle_f = set_altaz(El, Az, ID, ID_P1P2, Vmag_AcqCam, Vmag_P1P2, Sep, Pangle)

    #____Plot, in a polar projection, the coordinates
    fig = plt.figure(figsize=(11, 11))
    fig.set_facecolor((0.8, 0.8, 0.8))
    ax = plt.subplot(111, polar=True)
    ax.set_axis_bgcolor((0.0, 0.0, 0.3))
    ax.set_alpha(0.9)
    ax.plot(
        theta,
        r,
        linestyle='None',
        label='Stars pairs',
        marker='o',
        color='yellow',
        markeredgecolor=(
            (0,
            0,
            0.3)),
        markersize=6,
        alpha=1,
        markeredgewidth=0.1,
        picker=3)  # theta (radians),radii (degrees)
    ax.set_title(
        'LST ' +
        LST_epics,
        verticalalignment='bottom',
        horizontalalignment='center',
        weight='bold')
    ax.set_rmax(90.0)
    plt.thetagrids([theta * 15 for theta in range(360 // 15)])
    ax.set_xticklabels(['N',
                        '',
                        '',
                        '',
                        '',
                        '',
                        'E',
                        '',
                        '',
                        '',
                        '',
                        '',
                        'S',
                        '',
                        '',
                        '',
                        '',
                        '',
                        'W',
                        ''],
                    verticalalignment='top')
    ax.set_rgrids([0.01, 10, 20, 30, 40, 50, 60, 70, 80, 90],
                angle=67.5, color='grey', alpha='0.7')  # Display options
    ax.set_yticklabels(['90$^\circ$',
                        '80$^\circ$',
                        '70$^\circ$',
                        '60$^\circ$',
                        '50$^\circ$',
                        '40$^\circ$',
                        '30$^\circ$',
                        '20$^\circ$',
                        '10$^\circ$'])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.grid(color='white', linestyle='-', linewidth=0.6, alpha=0.3)
    ax.grid(True)
    ax.legend(loc='lower right')

    # ___Some display
    os.system('clear')
    print '__________________________________________________________________________'
    print ''
    print '                 TUNING STARS MAP, GEMINI SOUTH OBSERVATORY               '
    print '                        ', 'Actual LST:', LST_epics, '          '
    print '__________________________________________________________________________'
    print ''
    print 'Pairs library file in: perm/staff/mgomez/project_tuning/pairs.txt '
    print ''
    print 'Click on any star to display the information...'

    # ___Events with mouse click


    def onpick(event):
        ind = event.ind
        print '__________________________________________________________________________'
        print ''
        print ' AcqCam star ', 'ID:', ID_f[ind], 'Vmag:', Vmag_AcqCam_f[ind][0:3]
        print ' PWFS star   ', 'ID:', ID_P1P2_f[ind], 'Vmag:', Vmag_P1P2_f[ind][0:3]
        print ' Separation (arcmin): ', Sep_f[ind][0:4], 'PA (degrees):', Pangle_f[ind][0:5]
        print '__________________________________________________________________________'


    fig.canvas.mpl_connect('pick_event', onpick)
    fig.canvas.set_window_title('tuning.py')

    plt.show()

    print ''
    print '*** Please send any comment to mgomez@gemini.edu'
    print ''

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
