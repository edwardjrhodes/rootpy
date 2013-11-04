# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
from __future__ import absolute_import

import ROOT

from . import log; log = log[__name__]
from .. import QROOT, asrootpy
from ..base import NamedObject
from .fit import minimize

__all__ = [
    'Workspace',
]


class Workspace(NamedObject, QROOT.RooWorkspace):

    _ROOT = QROOT.RooWorkspace

    def __call__(self, *args):
        """
        Need to provide an alternative to RooWorkspace::import since import is
        a reserved word in Python and would be a syntax error.
        """
        return getattr(super(Workspace, self), 'import')(*args)

    def __getitem__(self, name):
        thing = super(Workspace, self).obj(name)
        if thing == None:
            raise ValueError(
                "object named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return asrootpy(thing, warn=False)

    def __contains__(self, name):
        thing = super(Workspace, self).obj(name)
        if thing:
            return True
        return False

    def obj(self, name, cls=None):
        thing = super(Workspace, self).obj(name)
        if thing == None:
            raise ValueError(
                "object named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        thing = asrootpy(thing, warn=False)
        if cls is not None and not isinstance(thing, cls):
            raise TypeError(
                "object named '{0}' is not of the correct type: "
                "{1} does not subclass {2}".format(name, thing.__class__, cls))
        return thing

    @property
    def category_functions(self):
        return asrootpy(self.allCatFunctions())

    @property
    def categories(self):
        return asrootpy(self.allCats())

    @property
    def datas():
        return self.allData()

    @property
    def functions(self):
        return asrootpy(self.allFunctions())

    @property
    def generic_objects(self):
        return self.allGenericObjects()

    @property
    def pdfs(self):
        return asrootpy(self.allPdfs())

    @property
    def resolution_models(self):
        return asrootpy(self.allResolutionModels())

    @property
    def vars(self):
        return asrootpy(self.allVars())

    def arg(self, name):
        thing = super(Workspace, self).arg(name)
        if thing == None:
            raise ValueError(
                "RooAbsArg named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def argset(self, name):
        thing = super(Workspace, self).argSet(name)
        if thing == None:
            raise ValueError(
                "RooArgSet named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def category(self, name):
        thing = super(Workspace, self).cat(name)
        if thing == None:
            raise ValueError(
                "RooCategory named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def category_function(self, name):
        # Dear RooStats, use camelCase consistently...
        thing = super(Workspace, self).catfunc(name)
        if thing == None:
            raise ValueError(
                "RooAbsCategory named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def data(self, name):
        thing = super(Workspace, self).data(name)
        if thing == None:
            raise ValueError(
                "RooAbsData named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def function(self, name):
        thing = super(Workspace, self).function(name)
        if thing == None:
            raise ValueError(
                "RooAbsReal named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def pdf(self, name):
        thing = super(Workspace, self).pdf(name)
        if thing == None:
            raise ValueError(
                "RooAbsPdf named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return thing

    def set(self, name):
        thing = super(Workspace, self).set(name)
        if thing == None:
            raise ValueError(
                "RooArgSet named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return asrootpy(thing)

    def var(self, name):
        thing = super(Workspace, self).var(name)
        if thing == None:
            raise ValueError(
                "RooRealVar named '{0}' does not exist "
                "in the workspace '{1}'".format(name, self.name))
        return asrootpy(thing)

    def fit(self,
            data_name='obsData',
            model_config_name='ModelConfig',
            param_const=None,
            param_values=None,
            param_ranges=None,
            poi_const=False,
            poi_value=None,
            poi_range=None,
            print_level=None,
            **kwargs):
        """
        Fit a pdf to data in a workspace

        Parameters
        ----------

        workspace : RooWorkspace
            The workspace

        data_name : str, optional (default='obsData')
            The name of the data

        model_config_name : str, optional (default='ModelConfig')
            The name of the ModelConfig in the workspace

        param_const : dict, optional (default=None)
            A dict mapping parameter names to booleans setting
            the const state of the parameter

        param_values : dict, optional (default=None)
            A dict mapping parameter names to values

        param_ranges : dict, optional (default=None)
            A dict mapping parameter names to 2-tuples defining the ranges

        poi_const : bool, optional (default=False)
            If True, then make the parameter of interest (POI) constant

        poi_value : float, optional (default=None)
            If not None, then set the POI to this value

        poi_range : tuple, optional (default=None)
            If not None, then set the range of the POI with this 2-tuple

        print_level : int, optional (default=None)
            The verbosity level for the minimizer algorithm.
            If None (the default) then use the global default print level.
            If negative then all non-fatal messages will be suppressed.

        kwargs : dict, optional
            Remaining keyword arguments are passed to the minimize function

        Returns
        -------

        result : RooFitResult
            The fit result

        See Also
        --------

        minimize

        """
        model_config = self.obj(
            model_config_name, cls=ROOT.RooStats.ModelConfig)
        data = self.data(data_name)
        pdf = model_config.GetPdf()

        pois = model_config.GetParametersOfInterest()
        if pois.getSize() > 0:
            poi = pois.first()
            poi.setConstant(poi_const)
            if poi_value is not None:
                poi.setVal(poi_value)
            if poi_range is not None:
                poi.setRange(*poi_range)

        if param_const is not None:
            for param_name, const in param_const.items():
                var = self.var(param_name)
                var.setConstant(const)
        if param_values is not None:
            for param_name, param_value in param_values.items():
                var = self.var(param_name)
                var.setVal(param_value)
        if param_ranges is not None:
            for param_name, param_range in param_ranges.items():
                var = self.var(param_name)
                var.setRange(*param_range)

        if print_level < 0:
            msg_service = ROOT.RooMsgService.instance()
            msg_level = msg_service.globalKillBelow()
            msg_service.setGlobalKillBelow(ROOT.RooFit.FATAL)
        func = pdf.createNLL(data)
        if print_level < 0:
            msg_service.setGlobalKillBelow(msg_level)
        return minimize(func, print_level=print_level, **kwargs)