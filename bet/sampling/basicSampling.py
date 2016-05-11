# Copyright (C) 2014-2015 The BET Development Team

# Lindley Graham 4/15/2014
"""
This module contains functions for sampling. We assume we are given access to a
model, a parameter space, and a data space. The model is a map from the
paramter space to the data space. We desire to build up a set of samples to
sovle an inverse problem this guving use information about the inverse mapping.
Each sample consists for a paramter coordinate, data coordinate pairing. We
assume the measure on both spaces in Lebesgue.
"""

import numpy as np
import scipy.io as sio
from pyDOE import lhs
from bet.Comm import comm
import bet.sample as sample

def loadmat(save_file, disc_name=None, model=None):
    """
    Loads data from ``save_file`` into a
    :class:`~bet.basicSampling.sampler` object.

    :param string save_file: file name
    :param string disc_name: name of :class:`~bet.sample.discretization` in
        file
    :param model: runs the model at a given set of parameter samples and
        returns data 
    :type model: callable

    :rtype: tuple
    :returns: (sampler, discretization)

    """
    # load the data from a *.mat file
    mdat = sio.loadmat(save_file)
    num_samples = mdat['num_samples']
    # load the discretization
    discretization = sample.load_discretization(save_file, disc_name)
    loaded_sampler = sampler(model, num_samples)    
    return (loaded_sampler, discretization)

class sampler(object):
    """
    This class provides methods for adaptive sampling of parameter space to
    provide samples to be used by algorithms to solve inverse problems. 

    num_samples
        total number of samples OR list of number of samples per dimension such
        that total number of samples is prob(num_samples)
    lb_model
        callable function that runs the model at a given set of input and
        returns output
    """
    def __init__(self, lb_model, num_samples=None):
        """
        Initialization
        
        :param lb_model: Interface to physics-based model takes an input of
            shape (N, ndim) and returns an output of shape (N, mdim)
        :type lb_model: callable function
        :param int num_samples: N, number of samples (optional)
        """
        #: int, total number of samples OR list of number of samples per
        #: dimension such that total number of samples is prob(num_samples)
        self.num_samples = num_samples
        #: callable function that runs the model at a given set of input and
        #: returns output
        # parameter samples and returns data

        self.lb_model = lb_model

    def save(self, mdict, save_file, discretization=None):
        """
        Save matrices to a ``*.mat`` file for use by ``MATLAB BET`` code and
        :meth:`~bet.sampling.loadmat`

        :param dict mdict: dictonary of sampling data and sampler parameters
        :param string save_file: file name

        """
        sio.savemat(save_file, mdict, do_compression=True)
        if discretization is not None:
            sample.save_discretization(discretization, save_file)

    def update_mdict(self, mdict):
        """
        Set up references for ``mdict``

        :param dict mdict: dictonary of sampler parameters

        """
        mdict['num_samples'] = self.num_samples

    def random_samples_set(self, sample_type, input_sample_set,
            num_samples=None, criterion='center', parallel=False):
        """
        Sampling algorithm with three basic options

            * ``random`` (or ``r``) generates ``num_samples`` samples in
                ``lam_domain`` assuming a Lebesgue measure.
            * ``lhs`` generates a latin hyper cube of samples.

        Note: This function is designed only for generalized rectangles and
        assumes a Lebesgue measure on the parameter space.
       
        :param string sample_type: type sampling random (or r),
            latin hypercube(lhs), regular grid (rg), or space-filling
            curve(TBD)
        :param input_sample_set: samples to evaluate the model at
        :type input_sample_set: :class:`~bet.sample.sample_set` with
            num_smaples
        :param string savefile: filename to save discretization
        :param int num_samples: N, number of samples (optional)
        :param string criterion: latin hypercube criterion see 
            `PyDOE <http://pythonhosted.org/pyDOE/randomized.html>`_
        :param bool parallel: Flag for parallel implementation.  Default value
            is ``False``.  
        
        :rtype: :class:`~bet.sample.discretization`
        :returns: :class:`~bet.sample.discretization` object which contains
            input and output of ``num_samples`` 

        """
        # Create N samples
        dim = input_sample_set.get_dim()

        if num_samples is None:
            num_samples = self.num_samples

        if input_sample_set.get_domain() is None:
            input_left = np.repeat(np.zeros([1, dim]), num_samples, 0)
            input_right = np.repeat(np.ones([1, dim]), num_samples, 0)
            input_values = (input_right-input_left)
        else:
            input_left = np.repeat([input_sample_set.get_domain()[:, 0]], num_samples, 0)
            input_right = np.repeat([input_sample_set.get_domain()[:, 1]], num_samples, 0)
            input_values = (input_right - input_left)
         
        if sample_type == "lhs":
            input_values = input_values * lhs(dim,
                    num_samples, criterion)
        elif sample_type == "random" or "r":
            input_values = input_values * np.random.random(input_left.shape) 
        input_values = input_values + input_left
        input_sample_set.set_values(input_values)

        return input_sample_set

    def random_samples_domain(self, sample_type, input_domain,
                           num_samples=None, criterion='center', parallel=False):
        """
        Sampling algorithm with three basic options

            * ``random`` (or ``r``) generates ``num_samples`` samples in
                ``lam_domain`` assuming a Lebesgue measure.
            * ``lhs`` generates a latin hyper cube of samples.

        Note: This function is designed only for generalized rectangles and
        assumes a Lebesgue measure on the parameter space.

        :param string sample_type: type sampling random (or r),
            latin hypercube(lhs), regular grid (rg), or space-filling
            curve(TBD)
        :param input_domain: min and max bounds for the input values,
            ``min = input_domain[:, 0]`` and ``max = input_domain[:, 1]``
        :type input_domain: :class:`numpy.ndarray` of shape (ndim, 2)
        :param string savefile: filename to save discretization
        :param int num_samples: N, number of samples (optional)
        :param string criterion: latin hypercube criterion see
            `PyDOE <http://pythonhosted.org/pyDOE/randomized.html>`_
        :param bool parallel: Flag for parallel implementation.  Default value
            is ``False``.

        :rtype: :class:`~bet.sample.discretization`
        :returns: :class:`~bet.sample.discretization` object which contains
            input and output of ``num_samples``

        """
        # Create N samples
        input_sample_set = sample.sample_set(input_domain.shape[0])
        input_sample_set.set_domain(input_domain)

        return self.random_samples_set(sample_type, input_sample_set,
                                       num_samples, criterion, parallel)

    def random_samples_dimension(self, sample_type, input_dim,
                              num_samples=None, criterion='center', parallel=False):
        """
        Sampling algorithm with three basic options

            * ``random`` (or ``r``) generates ``num_samples`` samples in
                ``lam_domain`` assuming a Lebesgue measure.
            * ``lhs`` generates a latin hyper cube of samples.

        Note: A default input space of a hypercube is created and the
        Lebesgue measure is assumed on a space of dimension specified
        by ``input_dim``

        :param string sample_type: type sampling random (or r),
            latin hypercube(lhs), regular grid (rg), or space-filling
            curve(TBD)
        :param int input_dim: the dimension of the input space
        :param string savefile: filename to save discretization
        :param int num_samples: N, number of samples (optional)
        :param string criterion: latin hypercube criterion see
            `PyDOE <http://pythonhosted.org/pyDOE/randomized.html>`_
        :param bool parallel: Flag for parallel implementation.  Default value
            is ``False``.

        :rtype: :class:`~bet.sample.discretization`
        :returns: :class:`~bet.sample.discretization` object which contains
            input and output of ``num_samples``

        """
        # Create N samples
        input_sample_set = sample.sample_set(input_dim)

        return self.random_samples_set(sample_type, input_sample_set,
                                       num_samples, criterion, parallel)

    def compute_QoI_and_create_discretization(self, input_sample_set, savefile=None, parallel=False):
        """
        Samples the model at ``input_sample_set`` and saves the results.

        Note: There are many ways to generate samples on a regular grid in
        Numpy and other Python packages. Instead of reimplementing them here we
        provide sampler that utilizes user specified samples.

        :param input_sample_set: samples to evaluate the model at
        :type input_sample_set: :class:`~bet.sample.sample_set` with
            num_smaples
        :param string savefile: filename to save samples and data
        :param bool parallel: Flag for parallel implementation. Default value
            is ``False``.  
        
        :rtype: :class:`~bet.sample.discretization` 
        :returns: :class:`~bet.sample.discretization` object which contains
            input and output of ``num_samples`` 

        """
        
        # Update the number of samples
        self.num_samples = input_sample_set.check_num()

        # Solve the model at the samples
        if not(parallel) or comm.size == 1:
            output_values = self.lb_model(\
                    input_sample_set.get_values())
            # figure out the dimension of the output
            if len(output_values.shape) == 1:
                output_dim = 1
            else:
                output_dim = output_values.shape[1]
            output_sample_set = sample.sample_set(output_dim)
            output_sample_set.set_values(output_values)
        elif parallel:
            input_sample_set.global_to_local()
            local_output_values = self.lb_model(\
                    input_sample_set.get_values_local())
            # figure out the dimension of the output
            if len(output_values.shape) == 0:
                output_dim = 1
            else:
                output_dim = output_values.shape[1]
            output_sample_set = sample.sample_set(output_dim)
            output_sample_set.set_values_local(local_output_values)
            input_sample_set.local_to_global()
            output_sample_set.local_to_global()
        
        discretization = sample.discretization(input_sample_set,
                output_sample_set)

        mdat = dict()
        self.update_mdict(mdat)

        if comm.rank == 0 and savefile is not None:
            self.save(mdat, savefile, discretization)
        
        return discretization


def create_random_discretization(self, sample_type, input_obj, savefile = None,
                   num_samples=None, criterion='center', parallel=False):
    """
    Sampling algorithm with three basic options
        * ``random`` (or ``r``) generates ``num_samples`` samples in
            ``lam_domain`` assuming a Lebesgue measure.
        * ``lhs`` generates a latin hyper cube of samples.
    Note: This function is designed only for generalized rectangles and
    assumes a Lebesgue measure on the parameter space.

    :param string sample_type: type sampling random (or r),
        latin hypercube(lhs), regular grid (rg), or space-filling
        curve(TBD)
    :param input_obj: Either a sample set object for an input space,
    an array of min and max bounds for the input values with
    ``min = input_domain[:, 0]`` and ``max = input_domain[:, 1]``,
    or the dimension of an input space
    :type input_obj: :class: `~bet.sample.sample_set`,
    :class:`numpy.ndarray` of shape (ndim, 2), or :class: `int`
    :param string savefile: filename to save discretization
    :param int num_samples: N, number of samples (optional)
    :param string criterion: latin hypercube criterion see
        `PyDOE <http://pythonhosted.org/pyDOE/randomized.html>`_
    :param bool parallel: Flag for parallel implementation.  Default value
        is ``False``.

    :rtype: :class:`~bet.sample.discretization`
    :returns: :class:`~bet.sample.discretization` object which contains
        input and output sample sets with ``num_samples`` total samples
    """
    # Create N samples
    if num_samples is None:
        num_samples = self.num_samples

    if isinstance(input_obj, sample.sample_set):
        input_sample_set = self.random_samples_set(sample_type, input_obj,
                                       num_samples, criterion, parallel)
    elif isinstance(input_obj, np.array):
        input_sample_set = self.random_samples_domain(sample_type, input_obj,
                                       num_samples, criterion, parallel)
    else:
        input_sample_set = self.random_samples_dimension(sample_type, input_obj,
                                       num_samples, criterion, parallel)

    return self.compute_QoI_and_create_discretization(input_sample_set, savefile, parallel)
