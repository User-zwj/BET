BET
===
[![Build Status](https://travis-ci.org/UT-CHG/BET.svg?branch=master)](https://travis-ci.org/UT-CHG/BET) [![DOI](https://zenodo.org/badge/18813599.svg)](https://zenodo.org/badge/latestdoi/18813599) [![codecov](https://codecov.io/gh/UT-CHG/BET/branch/master/graph/badge.svg)](https://codecov.io/gh/UT-CHG/BET)


BET is in active development. Hence, some features are still being added and you may find bugs we have overlooked. If you find something please report these problems to us through GitHub so that we can fix them. Thanks! 

Please note that we are using continuous integration and issues for bug tracking.

## Butler, Estep, Tavener method

This code has been documented with sphinx. the documentation is available online ta http://ut-chg.github.io/bet. to build documentation run 
``make html`` in the ``doc/`` folder.

To build/update the documentation use the following commands::

    sphinx-apidoc -f -o doc bet
    cd doc/
    make html
    make html

This creates the relevant documentation at ``bet/gh-pages/html``. 
To change the build location of the documentation you will need to update ``doc/makefile``.

You will need to run sphinx-apidoc and reinstall bet anytime a new module or method in the source code has been added. 
If only the `*.rst` files have changed then you can simply run ``make html`` twice in the doc folder.

Useful scripts and Jupyter Notebooks are contained in ``examples/``

Tests
-----

To run tests in serial call::

    nosetests

To run tests in parallel call::

    mpirun -np nproc nosetests

Make you to have a working MPI environment (we recommend [mpich](http://www.mpich.org/downloads/)).


Dependencies
------------

`bet` requires the following packages:

1. [numpy](http://www.numpy.org/)
2. [scipy](http://www.scipy.org/)
3. [nose](https://nose.readthedocs.org/en/latest/)
4. [pyDOE](https://pythonhosted.org/pyDOE/)
5. [matplotlib](http://matplotlib.org/)

(Note: you may need to set `~/.config/matplotlib/matplotlibrc` to include `backend:agg` if there is no `DISPLAY` port in your environment). 
