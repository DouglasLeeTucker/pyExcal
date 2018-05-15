# You will want to set up a Python environment that contains
#  the Python numpy, scipy, and astropy  modules.

# Also, you will want to edit the PYEXCAL_DIR below to point to
#  your pyExcal directory, and edit the STILTS_DIR to point to 
#  your stilts directory,  and then source this script (if you 
#  are running tcsh) or the equivalent setup.sh script (if you 
#  are running bash)...
setenv PYEXCAL_DIR /Users/dtucker/GitHub/pyExcal
setenv PATH ${PYEXCAL_DIR}/bin:$PATH
setenv PYTHONPATH ${PYEXCAL_DIR}/python:$PYTHONPATH

setenv STILTS_DIR /Users/dtucker/Software/STILTS/latest/stilts
