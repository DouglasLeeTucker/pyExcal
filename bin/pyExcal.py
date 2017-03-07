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
    (order is not important, but spelling is important)   

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
        
    status = pyExcal_fit(args)

    print
    print
    print "That's all, folks!"
    print
    
    return 0


##################################


def pyExcal_fit(args):

    import numpy as np 
    import math
    import os
    import sys
    from scipy.optimize import leastsq
    import matplotlib.pyplot as plt
    
    if args.verbose>0: 
        print 
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print 'pyExcal_fit'
        print '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
        print 


    inputFile = args.inputFile
    band = args.band

    # Check for the existence of the input file...
    if os.path.isfile(inputFile)==False:
        print """File %s does not exist...""" % (inputFile)
        print """Exiting now!"""
        print
        return 1
        

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
    

    # Mask out bad data...
    # 1. Mask out entries with bad instrumental mags...
    mask1 = ( (data['mag'] > -100.) & (data['mag'] < 100.) )
    # 2. Mask out entries with bad instrumental magerrs...
    mask2 = ( (data['merr'] >= 0.0) & (data['merr'] < 0.1) )
    # 3. Mask out entries with bad dstdcolors...
    mask3 = ( (dstdcolor > -5.) & (dstdcolor < 5.) )
    # Full mask:
    mask = ( mask1 & mask2 & mask3 )

    # Remove bad entries before performing the fit...
    dmag = dmag[np.where(mask)]
    X = X[np.where(mask)]
    dstdcolor = dstdcolor[np.where(mask)]
    
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
    print "Converged with chi squared ",chisq
    print "degrees of freedom, dof ", dof
    print "RMS of residuals (i.e. sqrt(chisq/dof)) ", math.sqrt(chisq/dof)
    print "Reduced chisq (i.e. variance of residuals) ", chisq/dof
    print


    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    print "Fitted parameters at minimum, with 68% C.I.:"
    for i,pmin in enumerate(p):
	print "%-10s %13g +/- %13g   (%5f percent)" % (pname[i],pmin,math.sqrt(cov[i,i])*math.sqrt(chisq/dof),100.*math.sqrt(cov[i,i])*math.sqrt(chisq/dof)/abs(pmin))
    print


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

    title="""%s_inst - %s_std = %.3f + %.3f*((%s) - %.3f) + %.3f*X""" % (band, band, p[0], p[1], colorNameDict[band], stdColor0Dict[band], p[2])
    xlabel = ''
    ylabel = """%s_inst - %s_std""" % (band, band)

    print
    print
    print """Your fit equation is:\n   %s""" % (title)
    print
    
    # output QA plot...
    qaPlot1 = """qa-%s_airmass.png""" % (inputFile)
    print """Outputting QA plot %s""" % (qaPlot1)
    xlabel = 'airmass'
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(X,dmag)
    dstdcolorMean=np.zeros(dstdcolor.size)+np.mean(dstdcolor)
    plt.plot(X, fp(p,X,dstdcolorMean), '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot1)
    plt.clf()
    qaPlot2 = """qa-%s_color.png""" % (inputFile)
    print """Outputting QA plot %s""" % (qaPlot2)
    xlabel = """(%s) - %.3f""" % (colorNameDict[band], stdColor0Dict[band])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(dstdcolor,dmag)
    XMean=np.zeros(X.size)+np.mean(X)
    plt.plot(dstdcolor, fp(p,XMean,dstdcolor), '-', linewidth=2)
    plt.grid(True)
    plt.savefig(qaPlot2)
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

if __name__ == "__main__":
    main()

##################################

