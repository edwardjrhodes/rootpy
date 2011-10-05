#!/usr/bin/env python
from rootpy.tree import TreeModel
from rootpy.vector import LorentzVector, Vector2
from rootpy.types import *


class FourMomentum(TreeModel):
    """
    Base model for all four-momentum objects
    """
    fourmomentum = LorentzVector


class MatchedObject(TreeModel):
    """
    Base model for all objects which may be matched
    to other objects
    """
    matched = BoolCol()


class Jet(FourMomentum, MatchedObject):
    """
    A jet is a matchable four-momentum and
    a boolean flag signifying whether ot not it
    has been flagged as a b-jet
    """
    btagged = BoolCol()


class Tau(FourMomentum, MatchedObject):
    """
    A tau is a matchable four-momentum
    with a number of tracks and a charge
    """
    numtrack = IntCol()
    charge = IntCol()


class Event(Jet.prefix('jet1_'), Jet.prefix('jet2_'),
            Tau.prefix('tau1_'), Tau.prefix('tau2_')):
    """
    An event is composed of two jets and two taus
    an event number and some missing transverse energy
    """
    eventnumber = IntCol()
    missingET = Vector2

print Event