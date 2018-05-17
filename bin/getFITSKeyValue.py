#!/usr/bin/env python

# Author:      Douglas Tucker
# Date:        17 May 2018
#
# Description: 
#              
#              

"""
    getFITSKeyValue.py

    Return the value of a header keyword from a FITS file.

    EXAMPLES:

    getFITSKeyValue.py --help

    getFITSKeyValue.py --inputFile new-dec18.1090.fits --keyword EXPTIME --hdrNumber 0

    getFITSKeyValue.py --inputFile new-dec18.1090.fits --keyword GAIN --hdrNumber 1


"""

##################################

def main():

    # Initial setup...
    from astropy.io import fits
    import argparse

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--inputFile', help='Name of input FITS file from which to grab the header keyword value.')
    parser.add_argument('--keyword', help='Name of the FITS header keyword')
    parser.add_argument('--hdrNumber', help='Number of the header in which the keyword resides', default=0, type=int)
    parser.add_argument('--verbose', help='verbosity level of output to screen (0,1,2,...)', default=0, type=int)
    args = parser.parse_args()

    if args.verbose > 0: print args

    # Extract arguments...
    inputFile = args.inputFile
    keyword = args.keyword.upper()
    hdrNumber = args.hdrNumber
    verbose = args.verbose

    # Open FITS file, read header, and grab value for the specified keyword...
    hdulist = fits.open(inputFile)
    hdr = hdulist[hdrNumber].header
    value = hdr[keyword]
    hdulist.close()

    # Return value...
    print value


##################################

if __name__ == "__main__":
    main()

##################################
