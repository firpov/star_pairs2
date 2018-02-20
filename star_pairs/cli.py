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

# _Defining constants:
LONGITUDE = '-70d44m12.096s'  # WGS84
LATITUDE = '-30d14m26.700s'   # WGS84

#_Defining functions:
def format_decimal(string):
    "Change format, from a string 'HHhMMmSS.SSSs' to a float HH.H"
    print(string,type(string))
    if string[0] == '-':
        string = float(string[0:3]) - float(string[4:6]) / 60. - float(string[7:12]) / 3600.
    elif string[0] == '+':
        string = float(string[1:3]) + float(string[4:6]) / 60. + float(string[7:12]) / 3600.
    else:
        string = float(string[0:2]) + float(string[3:5]) / 60. + float(string[6:11]) / 3600.
    print string
    return


@click.command()
def main(args=None):
    """Console script for star_pairs."""

    try:
        import epics
        LST_epics = epics.caget("tcs:LST")
    except ImportError:
            LST_epics = "00:00:00.0"

    # _Defining location parameters (WGS84)
    #longitude = float(LONGITUDE[0:3]) - float(LONGITUDE[4:6]) / \
#        60. - float(LONGITUDE[7:12]) / 3600.  # Degrees
#    latitude = float(LATITUDE[0:3]) - float(LATITUDE[4:6]) / \
#        60. - float(LATITUDE[7:12]) / 3600.  # Degrees

    longitude = format_decimal(LONGITUDE)
    print(type(format_decimal(LONGITUDE)))

    print(longitude, type(longitude))

    quit()

    # _Defining local sidereal time (LST)
    LST = float(LST_epics[0:2]) + float(LST_epics[3:5]) / 60. + \
        float(LST_epics[6:10]) / 3600.  # Hours

    # _Celestial objects in equatorial coordinates (J2000)
    # ___Read from file
    file = pkg_resources.resource_stream(__name__, "data/pairs.txt")
    lines = file.readlines()
    file.close()

    ID = []
    ID_P1P2 = []
    RA = []
    Dec = []
    Vmag_AcqCam = []
    Vmag_P1P2 = []
    Sep = []
    Pangle = []

    for i in range((len(lines) / 3) + 1):
        ID.append(lines[3 * i].split()[0])
        ID_P1P2.append(lines[3 * i + 1].split()[0])
        RA.append(lines[3 * i].split()[1])
        Dec.append(lines[3 * i].split()[2])
        Vmag_AcqCam.append(lines[3 * i].split()[3])
        Vmag_P1P2.append(lines[3 * i + 1].split()[3])
        Sep.append(lines[3 * i].split()[4])
        Pangle.append(lines[3 * i + 1].split()[4])

    # ___Change the format of RA and Dec so it could be used in the code tuning
    for x in range(len(RA)):
        RA[x] = float(RA[x][:2]) + float(RA[x][3:5]) / 60. + \
            float(RA[x][6:11]) / 3600.  # Hours
        Dec[x] = float(Dec[x][:3]) - float(Dec[x][4:6]) / 60. - \
            float(Dec[x][7:11]) / 3600.  # Degrees

    # ___Calculate HA
    HA = []

    for a in range(len(RA)):
        HA.append((float(RA[a])))  # Hours (following calculi need HA in degrees)
        HA[a] = LST - HA[a]

    #__Calculating altazimuthal coordinates
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

    #__Plotting in polar coordiantes
    #____Setting altazimuthal coordinates
    # In a polar plot, Zenith would be 0 degrees, so we have to revert the
    # elevation axis.
    r = []
    theta = []  # For converting azimuth axis to degrees
    ID_f = []
    ID_P1P2_f = []
    Vmag_AcqCam_f = []
    Vmag_P1P2_f = []
    Sep_f = []
    Pangle_f = []
    size = []
    color_star = []
    alpha_star = []

    for i in range(len(RA)):
        if np.degrees(El[i]) > 30.:
            r.append(90.0 - np.degrees(El[i]))
            theta.append(Az[i])
            ID_f.append(ID[i])
            ID_P1P2_f.append(ID_P1P2[i])
            Vmag_AcqCam_f.append(Vmag_AcqCam[i])
            Vmag_P1P2_f.append(Vmag_P1P2[i])
            Sep_f.append(Sep[i])
            Pangle_f.append(Pangle[i])
            if (float(Vmag_AcqCam[i]) > 3. and float(Vmag_AcqCam[i]) < 5.5):
                size.append(22)
                color_star.append((1, 1, 0))
                alpha_star.append(1)
            elif (float(Vmag_AcqCam[i]) > 5.5 and float(Vmag_AcqCam[i]) < 7.):
                size.append(18)
                color_star.append((0.95, 0.95, 0))
                alpha_star.append(0.95)
            else:
                size.append(14)
                color_star.append((0.9, 0.9, 0))
                alpha_star.append(0.9)
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
