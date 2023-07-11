#!/usr/bin/env python
"""
    pyExcal.py

    A very basic fitter to the SDSS primed system photometric equations
    of the form:
      u_inst - u_std = a_u + b_u*( (u-g)_std - (u-g)_0 ) + k*X 
      g_inst - g_std = a_g + b_g*( (g-r)_std - (g-r)_0 ) + k*X 
      r_inst - r_std = a_r + b_r*( (r-i)_std - (r-i)_0 ) + k*X 
      i_inst - i_std = a_i + b_i*( (r-i)_std - (r-i)_0 ) + k*X 
      z_inst - z_std = a_z + b_z*( (i-z)_std - (i-z)_0 ) + k*X 

    Reads in a CSV file with the following columns and fits the data to
    the relevant photometric equation (u',g',r',i',z'): 
      Frame,Name,ra,dec,UT,F,X,mag,merr,u,g,r,i,z,ue,ge,re,ie,ze
    (order is not important, but spelling and case are important)   

    Example:
    
    pyExcal.py --help

    pyExcal.py --inputFile std-rguiz-test.g.csv --band g --verbose 1
    
    """

##################################

def main():

    import argparse

    supportedBandList = ['u','g','r','i','z']

    """Create command line arguments"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--inputFile', help='Name of input file', default='std-rguiz-test.g.csv')
    parser.add_argument('--band', help='comma-separated list of filter bands to consider', default='g,r,i,z,Y')
    parser.add_argument('--nsigma', help='number of sigma for sigma-clipping of outliers', default=3.0, type=float)
    parser.add_argument('--niter', help='number of iterations for sigma-clipping of outliers', default=3, type=int)
    parser.add_argument('--verbose', help='verbosity level of output to screen (0,1,2,...)', default=0, type=int)
    args = parser.parse_args()

    if args.verbose > 0: print args

    if args.band not in supportedBandList:
        print """Filter band %s is not found in the list of supported bands...""" % (band)
        print """The list of supported filter bands is %s""" % (supportedBandList)
        print """(Note that the filter band names in this list are case-sensitive.)"""
        print """Exiting now!..."""
        print 
        return 1
        
    status = pyExcal(args)

    print
    print
    print "That's all, folks!"
    print
    
    return 0


##################################


def pyExcal(args):

    # Based on a scripts at
    # http://linuxgazette.net/115/andreasen.html (by Anders Andreasen)
    # and at
    # http://www.phy.uct.ac.za/courses/python/examples/fitresonance.py (University of Cape Town)

    import numpy as np 
    import math
    import os
    import sys
    import matplotlib.pyplot as plt
    
    if args.verbose>0: 
        print 
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print 'pyExcal'
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print 


    inputFile = args.inputFile
    band = args.band
    niter = args.niter
    nsigma = args.nsigma
    
    # Check for the existence of the input file...
    if os.path.isfile(inputFile)==False:
        print """File %s does not exist...""" % (inputFile)
        print """Exiting now!"""
        print
        return 1

    # Extract file basename (to be used to name output qa files...)
    baseName = os.path.basename(inputFile)

    # Python dictionary of stdColor0's...
    stdColor0Dict = {'u':1.39,'g':0.53,'r':0.21,'i':0.21,'z':0.09}

    # Python dictionary of conjugate filter bands...
    cbandDict = {'u':'g','g':'r','r':'i','i':'r','z':'i'}

    # Python dictionary of signs for the cast of the (band-cband) colors...
    csignDict = {'u':1.,'g':1.,'r':1.,'i':-1.,'z':-1.}
    
    # Python dictionary of color names...
    colorNameDict = {'u':'u-g','g':'g-r','r':'r-i','i':'r-i','z':'i-z'}
    
    # Grab the correct conjugate filter band from the
    #  conjugate filter band Python dictionary...
    cband = cbandDict[band]
    
    # Grab the correct cast sign from the
    #  cast sign Python dictionary...
    csign = csignDict[band]

    # Read whole file into numpy arrays using np.genfromtxt...
    data = np.genfromtxt(inputFile,dtype=None,delimiter=',',names=True)

    # Extract relevant numpy arrays for fit....
    dmag = data['mag'] - data[band]
    X = data['X']
    dstdcolor = csign*(data[band]-data[cband])
    name = data['Name']
    ut = data['UT']


    # Create initial (and generous) mask...
    # 1. Mask out entries with bad instrumental mags...
    mask1 = ( (data['mag'] > -100.) & (data['mag'] < 100.) )
    # 2. Mask out entries with bad instrumental magerrs...
    mask2 = ( (data['merr'] >= 0.0) & (data['merr'] < 0.1) )
    # 3. Mask out entries with bad dstdcolors...
    mask3 = ( (dstdcolor > -5.) & (dstdcolor < 5.) )
    # Full mask:
    mask123 = ( mask1 & mask2 & mask3 )
    mask = mask123

    for i in range(niter):

        iiter = i + 1
        if args.verbose > 0:
            print """   iter%d...""" % ( iiter )

        # Remove bad entries before performing the fit...
        dmag_masked = dmag[np.where(mask)]
        X_masked = X[np.where(mask)]
        dstdcolor_masked = dstdcolor[np.where(mask)]
    
        # List bad entries that were removed...
        if args.verbose > 0:
            name_bad = name[np.where(~mask)]
            ut_bad = ut[np.where(~mask)]
            X_bad = X[np.where(~mask)]
            dmag_bad = dmag[np.where(~mask)]
            print 
            print "These entries are excluded from this iteration of the fit:"
            print 
            print "    N         Name                 UT      X        dmag"
            for j in range(len(name_bad)):
                print """%5d %-25s %7.4f %6.3f %10.3f""" % \
                    (j+1, name_bad[j], ut_bad[j], X_bad[j], dmag_bad[j])

            print 
            print 

        # Perform fit...
        p,perr,rms = pyExcal_fit(X_masked, dstdcolor_masked, dmag_masked, args.verbose)
        res_masked = residuals(p,X_masked,dstdcolor_masked,dmag_masked)
        stddev_masked = res_masked.std()

        # Calculate residuals for full (unmasked) data set and update mask...
        res = residuals(p,X,dstdcolor,dmag)
        mask4 = (np.abs(res) < nsigma*stddev_masked)
        mask = mask123 & mask4


    # Create QA plots...
    
    title="""%s_inst - %s_std = %.3f + %.3f*((%s) - %.3f) + %.3f*X""" % (band, band, p[0], p[1], colorNameDict[band], stdColor0Dict[band], p[2])
    xlabel = ''
    ylabel = """%s_inst - %s_std""" % (band, band)

    print
    print
    print """Your fit equation is:\n   %s""" % (title)
    print
    
    # output QA plot...
    qaPlot1a = """qa-%s_dmag_airmass.%s-band.png""" % (baseName, band)
    print """Outputting QA plot %s""" % (qaPlot1a)
    xlabel = 'airmass'
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    dmag_masked_min = np.min(dmag_masked)
    dmag_masked_max = np.max(dmag_masked)
    y_lo = dmag_masked_min - 0.5*(dmag_masked_max-dmag_masked_min)
    y_hi = dmag_masked_max + 0.5*(dmag_masked_max-dmag_masked_min)
    plt.ylim(y_lo, y_hi)
    plt.scatter(X, dmag, facecolors='none', edgecolors='r', s=10)
    plt.scatter(X_masked, dmag_masked)
    dstdcolorMean=np.zeros(dstdcolor_masked.size)+np.mean(dstdcolor_masked)
    plt.plot(X_masked, fp(p,X_masked,dstdcolorMean), '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot1a)
    plt.clf()

    qaPlot1b = """qa-%s_res_airmass.%s-band.png""" % (baseName, band)
    print """Outputting QA plot %s""" % (qaPlot1b)
    xlabel = 'airmass'
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('residuals [mag]')
    res_masked_min = np.min(res_masked)
    res_masked_max = np.max(res_masked)
    y_lo = res_masked_min - 0.5*(res_masked_max-res_masked_min)
    y_hi = res_masked_max + 0.5*(res_masked_max-res_masked_min)
    plt.ylim(y_lo, y_hi)
    plt.scatter(X, res, facecolors='none', edgecolors='r', s=10)
    plt.scatter(X_masked, res_masked)
    zero_line=np.zeros(dstdcolor_masked.size)
    plt.plot(X_masked, zero_line, '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot1b)
    plt.clf()

    qaPlot2a = """qa-%s_dmag_color.%s-band.png""" % (baseName, band)
    print """Outputting QA plot %s""" % (qaPlot2a)
    xlabel = """(%s) - %.3f""" % (colorNameDict[band], stdColor0Dict[band])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    y_lo = dmag_masked_min - 0.5*(dmag_masked_max-dmag_masked_min)
    y_hi = dmag_masked_max + 0.5*(dmag_masked_max-dmag_masked_min)
    plt.ylim(y_lo, y_hi)
    plt.scatter(dstdcolor, dmag, facecolors='none', edgecolors='r', s=10)
    plt.scatter(dstdcolor_masked,dmag_masked)
    XMean=np.zeros(X_masked.size)+np.mean(X_masked)
    plt.plot(dstdcolor_masked, fp(p,XMean,dstdcolor_masked), '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot2a)
    plt.clf()

    qaPlot2b = """qa-%s_res_color.%s-band.png""" % (baseName, band)
    print """Outputting QA plot %s""" % (qaPlot2b)
    xlabel = """(%s) - %.3f""" % (colorNameDict[band], stdColor0Dict[band])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('residuals [mag]')
    res_masked_min = np.min(res_masked)
    res_masked_max = np.max(res_masked)
    y_lo = res_masked_min - 0.5*(res_masked_max-res_masked_min)
    y_hi = res_masked_max + 0.5*(res_masked_max-res_masked_min)
    plt.ylim(y_lo, y_hi)
    plt.scatter(dstdcolor, res, facecolors='none', edgecolors='r', s=10)
    plt.scatter(dstdcolor_masked, res_masked)
    zero_line=np.zeros(dstdcolor_masked.size)
    plt.plot(dstdcolor_masked, zero_line, '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot2b)
    plt.clf()

    return 0


##################################

# Parametric function:
#  p is the parameter vector;
#  X is the airmass
#  dstdcolor is "stdColor-stdColor0"
def fp(p,X,dstdcolor):
    return p[0] + p[1]*dstdcolor + p[2]*X

##################################

# Error function:
def residuals(p,X,dstdcolor,dmag):
    err = (dmag-fp(p,X,dstdcolor))
    return err

##################################

# Fitting function:
def pyExcal_fit(X, dstdcolor, dmag, verbose=0):

    import numpy as np 
    import math
    from scipy.optimize import leastsq
    
    # Calculate the median of dmag for use as an initial guess
    # for the overall zeropoint offset..
    mdn = np.median( dmag, None )

    # Parameter names
    pname = (['a', 'b', 'k'])

    # Initial parameter values
    p0 = [mdn, 0.0, 0.0]

    print 
    print 'Initial parameter values:  ', p0


    # Perform fit
    p,cov,infodict,mesg,ier = leastsq(residuals, p0, args=(X, dstdcolor, dmag), maxfev=10000, full_output=1)
    if (ier >=1 and ier <=4):
	print "Converged"
    else:
	print "Not converged"
	print mesg


    # Calculate some descriptors of the fit 
    # (similar to the output from gnuplot 2d fits)
    chisq=sum(infodict['fvec']*infodict['fvec'])
    dof=len(dmag)-len(p)
    rms=math.sqrt(chisq/dof)

    if verbose > 0:
        print "Converged with chi squared ",chisq
        print "degrees of freedom, dof ", dof
        print "RMS of residuals (i.e. sqrt(chisq/dof)) ", rms
        print "Reduced chisq (i.e. variance of residuals) ", chisq/dof
        print


    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    perr = []
    if verbose > 0:
        print "Fitted parameters at minimum, with 68% C.I.:"
    for i,pmin in enumerate(p):
        if verbose > 0:
	    print "%-10s %13g +/- %13g   (%5f percent)" % (pname[i],pmin,math.sqrt(cov[i,i])*math.sqrt(chisq/dof),100.*math.sqrt(cov[i,i])*math.sqrt(chisq/dof)/abs(pmin))
        perr.append(math.sqrt(cov[i,i])*math.sqrt(chisq/dof))
    if verbose > 0:  print


    if verbose > 0:
        print "Correlation matrix:"
        # correlation matrix close to gnuplot
        print "               ",
        for i in range(len(pname)): print "%-10s" % (pname[i],),
        print
        for i in range(len(p)):
	    print "%-10s" % pname[i],
	    for j in range(i+1):
	        print "%10f" % (cov[i,j]/math.sqrt(cov[i,i]*cov[j,j]),),
	    #endfor
	    print
        #endfor
        print
        print
        print

        
    return p, perr, rms


##################################

if __name__ == "__main__":
    main()

##################################


