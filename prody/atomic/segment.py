# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2012 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module defines classes to handle segments in an atom group.

.. currentmodule:: prody.atomic"""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

from subset import AtomSubset, MCAtomSubset

__all__ = ['Segment', 'MCSegment']

class Segment(AtomSubset):
    
    """Instances are generated by :class:`HierView` class.
    
    Indexing a :class:`Segment` instance by chain identifier returns 
    :class:`Chain` instances."""

    def __init__(self, ag, indices, **kwargs):
        
        AtomSubset.__init__(self, ag, indices, **kwargs)
        self._dict = dict()
        self._list = list()
    
    def __repr__(self):

        return ('<Segment: {0:s} from {1:s} ({2:d} atoms)>').format(
                self.getSegname(), self._ag.getTitle(), 
                self.numAtoms())

    def __str__(self):

        return 'Segment {0:s}'.format(self.getSegname())

    def __getitem__(self, chid):
        
        return self._dict.get(chid)
    
    def __len__(self):

        return len(self._list)
    
    def __iter__(self):
        
        return self._list.itervalues()

    def getSegname(self):
        """Return segment name."""
        
        return self._ag._data['segments'][self._indices[0]]
    
    def setSegname(self, segname):
        """Set segment name."""
        
        self.setSegnames(segname)
    
    def numChains(self):
        """Return number of residues."""
        
        return len(self._list)
    
    def getChain(self, chid):
        """Return chain with identifier *chid*."""
        
        index = self._dict.get(chid)
        if index is not None:
            return self._list[index]
    
    def iterChains(self):
        """Iterate chains in the segment."""
        
        return self._list.__iter__()

    def getSelstr(self):
        """Return selection string that selects atoms in this segment."""
        
        if self._selstr:
            return 'segname {0:s} and ({1:s})'.format(self.getSegname(), 
                                                        self._selstr)
        else:
            return 'segname {0:s}'.format(self.getSegname())


class MCSegment(Segment, MCAtomSubset):
    
    def __init__(self, ag, indices, acsi, **kwargs):
        
        MCAtomSubset.__init__(self, ag, indices, acsi, **kwargs)
        self._dict = dict()
        self._list = list()

    def __repr__(self):
        
        n_csets = self._ag.numCoordsets()
        if n_csets:
            return ('<MCSegment: {0:s} from {1:s} ({2:d} chains, {3:d} atoms; '
                    '{4:d} coordsets, active {5:d})>').format(
                    self.getSegname(), self._ag.getTitle(), self.numChains(),
                    self.numAtoms(), n_csets, self._acsi)
        else:
            return ('<MCSegment: {0:s} from {1:s} ({2:d} chains, {3:d} atoms; '
                    '0 coordsets)>').format(self.getSegname(), 
                    self._ag.getTitle(), self.numAtoms(), self.numChains())

    def __str__(self):
    
        return 'MCSegment {0:s}'.format(self.getSegname())