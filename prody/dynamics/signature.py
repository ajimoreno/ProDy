# -*- coding: utf-8 -*-
"""This module defines functions for analyzing normal modes obtained 
for conformations in an ensemble."""

import numpy as np

from prody import LOGGER, SETTINGS
from prody.utilities import showFigure
from prody.ensemble import Ensemble

from .nma import NMA
from .modeset import ModeSet
from .mode import Mode, Vector
from .functions import calcENM
from .compare import calcSpectralOverlap, matchModes
from .analysis import calcSqFlucts
from .anm import ANM
from .gnm import GNM

__all__ = ['calcEnsembleENMs', 'getSignatureProfile', 'calcSpectralDistances',
           'showSignatureProfile']

def calcEnsembleENMs(ensemble, model='gnm', trim='trim', n_modes=20):
    """Description"""

    if model is GNM:
        model_type = 'GNM'
    elif model is ANM:
        model_type = 'ANM'
    else:
        model_type = str(model).strip().upper()

    atoms = ensemble.getAtoms()
    select = None
    if ensemble._indices is not None:
        select = atoms
        atoms = atoms.getAtomGroup()
        
    labels = ensemble.getLabels()

    verb = LOGGER.verbosity
    LOGGER.verbosity = 'info'
    ### ENMs ###
    ## ENM for every conf
    enms = []
    n_confs = ensemble.numConfs()
    LOGGER.progress('Calculating {0} {1} modes for {2} conformations...'
                    .format(n_modes, model_type, n_confs), n_confs)

    for i in range(n_confs):
        atoms.setCoords(ensemble.getCoordsets(i, selected=False))
        enm, _ = calcENM(atoms, select, model=model, trim=trim, 
                            n_modes=n_modes, title=labels[i])
        enms.append(enm)

        lbl = labels[i] if labels[i] != '' else '%d-th conformation'%(i+1)
        LOGGER.update(i)
    
    LOGGER.update(n_confs, 'Finished.')
    LOGGER.verbosity = verb

    LOGGER.info('{0} {1} modes were calculated for each of the {2} conformations.'
                        .format(n_modes, model_type, n_confs))
    return enms

def _getEnsembleENMs(ensemble, **kwargs):
    if isinstance(ensemble, Ensemble):
        enms = calcEnsembleENMs(ensemble, **kwargs)
    else:
        try:
            enms = []
            for enm in ensemble:
                if not isinstance(enm, (Mode, NMA, ModeSet)):
                    raise TypeError('ensemble can be a list of Mode, '
                                    'NMA, or ModeSet instances, '
                                    'not {0}'.format(type(enm)))
                enms.append(enm)
        except TypeError:
            raise TypeError('ensemble must be an Ensemble instance, '
                            'or a list of NMA, Mode, or ModeSet instances.')
    return enms

def calcSpectralDistances(ensemble, **kwargs):
    """Description"""

    enms = _getEnsembleENMs(ensemble, **kwargs)
    
    overlaps = np.zeros((len(enms), len(enms)))
    for i, enmi in enumerate(enms):
        for j, enmj in enumerate(enms):
            covlap = calcSpectralOverlap(enmi, enmj)
            overlaps[i, j] = covlap

    ### build tree based on similarity matrix ###
    dist_mat = np.arccos(overlaps)

    return dist_mat

def getSignatureProfile(ensemble, index, **kwargs):
    """Description"""

    enms = _getEnsembleENMs(ensemble, **kwargs)
    
    matches = matchModes(*enms)

    if np.isscalar(index):
        modes = matches[index]
        V = []
        v0 = modes[0].getEigvec()
        for mode in modes:
            v = mode.getEigvec()
            c = np.dot(v, v0)
            if c < 0:
                v *= -1
            V.append(v)
    else:
        V = []
        for j in range(len(matches)):
            modes = []
            for i in index:
                mode = matches[i][j]
                modes.append(mode)
            sqfs = calcSqFlucts(modes)
            V.append(sqfs)
    V = np.vstack(V); V = V.T

    meanV = V.mean(axis=1)
    stdV = V.std(axis=1)

    return V, (meanV, stdV)
    
def showSignatureProfile(ensemble, index, linespec='-', **kwargs):
    """Description"""

    from matplotlib.pyplot import figure, plot, fill_between, gca
    from .signature import getSignatureProfile

    V, (meanV, stdV) = getSignatureProfile(ensemble, index, **kwargs)
    minV = V.min(axis=1)
    maxV = V.max(axis=1)

    x = range(meanV.shape[0])

    new_fig = kwargs.pop('new_fig', True)

    if new_fig:
        figure()
    line = plot(x, meanV, linespec)[0]
    color = line.get_color()
    fill_between(x, minV, maxV,
                alpha=0.3, facecolor=color,
                linewidth=1, antialiased=True)
    fill_between(x, meanV-stdV, meanV+stdV,
                alpha=0.5, facecolor=color,
                linewidth=1, antialiased=True)
    
    if SETTINGS['auto_show']:
        showFigure()
    return gca()
    
def calcAverageCrossCorr(modes, *args, **kwargs):
    """Calculate average cross-correlations for a list of modes."""
    matches = matchModes(*modes)

    CCs = []
    for mode_i in matches[0]:
        CC = calcCrossCorr(mode_i)
        CCs.append(CC)
    C = np.vstack(CCs)

    n_atoms = modes[0].numAtoms()
    C = C.reshape(len(CCs), n_atoms, n_atoms)
    mean = C.mean(axis=0)
    std = C.std(axis=0)
    return mean, std

def showAverageCrossCorr(modes, *args, **kwargs):
    """Show average cross-correlations using :func:`~matplotlib.pyplot.imshow`.  By
    default, *origin=lower* and *interpolation=bilinear* keyword  arguments
    are passed to this function, but user can overwrite these parameters.
    See also :func:`.calcAverageCrossCorr`."""

    import matplotlib.pyplot as plt
    if kwargs.pop('new_fig', True):
        plt.figure()

    arange = np.arange(modes[0].numAtoms())
    mean, std = calcAverageCrossCorr(modes)
    # cross_correlations = np.zeros((arange[-1]+2, arange[-1]+2))
    # cross_correlations[arange[0]+1:,
                       # arange[0]+1:] = calcCrossCorr(modes)
    if not 'interpolation' in kwargs:
        kwargs['interpolation'] = 'bilinear'
    if not 'origin' in kwargs:
        kwargs['origin'] = 'lower'
    show = plt.imshow(mean, *args, **kwargs), plt.colorbar()
    plt.axis([arange[0]+0.5, arange[-1]+1.5, arange[0]+0.5, arange[-1]+1.5])
    plt.title('Average Cross-correlations')
    plt.xlabel('Indices')
    plt.ylabel('Indices')
    if SETTINGS['auto_show']:
        showFigure()
    return show
