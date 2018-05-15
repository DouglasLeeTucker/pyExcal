#!/usr/bin/env python

# Author:      Douglas Tucker
# Date:        15 May 2018
#
# Description: 
#              
#              

"""
    copyAstrometryNetWCSpyExcal.py

    Copy the Astrometry.net WCS from the header from one file (wcsFromFile) 
    to the header of another file (wcsToFile).

    By default, overwrite the original wcsToFile.
    To avoid overwriting the original wcsToFile, provide the name of an outputFile.
 

    EXAMPLES:

    copyAstrometryNetWCS.py --help

    copyAstrometryNetWCS.py --wcsFromFile new-dec18.1090.fits --wcsToFile dec18.1092.fits --outputFile wcs-dec18.1092.fits --verbose 1


"""

##################################

def main():

    import argparse

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--wcsFromFile', help='Name of input file *from* which the Astrometry.net WCS info will be copied.', default='None')
    parser.add_argument('--wcsToFile', help='Name of input file *to* which the Astrometry.net WCS info will be copied.', default='None')
    parser.add_argument('--outputFile', help='Name of new file (if not overwriting original wcsToFile)', default='None')
    parser.add_argument('--verbose', help='verbosity level of output to screen (0,1,2,...)', default=0, type=int)
    args = parser.parse_args()

    if args.verbose > 0: print args

    if args.wcsFromFile == 'None':
        print 'No wcsFromFile specified...'
        print 'Exiting now!...'
        return 1

    if args.wcsToFile == 'None':
        print 'No wcsToFile specified...'
        print 'Exiting now!...'
        return 1

    if args.outputFile == 'None':
        print """No outputFile specified...  Original %s will be updated.""" % (args.wcsToFile)
        
    status = copyAstrometryNetWCS(args)

    print
    print
    print "That's all, folks!"
    print

    return 0

##################################


def copyAstrometryNetWCS(args):

    # Initial setup...
    import numpy as np
    import pandas as pd
    from astropy.io import fits
    import math
    import os
    import datetime

    if args.verbose>0:
        print
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print 'copyAstrometryNetWCS'
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print

    inputFile1 = args.wcsFromFile
    inputFile2 = args.wcsToFile
    outputFile = args.outputFile
    verbose = args.verbose

    # Check for the existence of the inputFile1...
    if os.path.isfile(inputFile1)==False:
        print """Input file %s does not exist...""" % (inputFile1)
        print """Exiting now!"""
        print
        return 1

    # Check for the existence of the inputFile2...
    if os.path.isfile(inputFile2)==False:
        print """Input file %s does not exist...""" % (inputFile2)
        print """Exiting now!"""
        print
        return 1

    hdulist1 = fits.open(inputFile1)
    hdulist2 = fits.open(inputFile2)

    hdr1 = hdulist1[0].header
    hdr2 = hdulist2[0].header
    
    iflag = 0
    hdr1_keys = hdr1.keys()
    for i in range(len(hdr1)):
        if hdr1[i] == "--Start of Astrometry.net WCS solution--":
            if verbose > 0:
                print 'Copying the following Astrometry.net WCS entries:'
            tstamp = str(datetime.datetime.now())
            historyLine = """Astrometry.net WCS keywords copied from %s (%s)""" % (inputFile1, tstamp)
	    #hdr2.add_history(historyLine)
	    hdr2.append( ('HISTORY', historyLine), end=True)
            iflag = 1
        if hdr1[i] == "--End of Astrometry.net WCS--":
            break
        if iflag == 1:
            #key = hdr1.keys()[i]
            key = hdr1_keys[i]
            value = hdr1[i]
            comment = hdr1.comments[i]
            if verbose > 0:
                print i, key, value, comment
            hdr2.append((key, value, comment), end=True)

    hdulist2.writeto(outputFile,clobber=True)
  
    return 0


##################################

if __name__ == "__main__":
    main()

##################################
