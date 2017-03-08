# <a name="top"></a>pyExcal
A Python standard star fitter inspired by the SDSS mtpipe excal code.

## FAQ

* [How to run pyExcal?](#howtorun)
* [How to request updates to the code or to the FAQ?](#requests)

----------------------------------------------------------------------
#### <a name="howtorun"></a>How to run pyExcal?

<ol>
<li> Ensure that you have the necessary dependencies installed on your computer:
     <ul>
     <li> Python 2.7 or higher
     <li> The numpy python module (pyExcal definitely works with numpy 1.11.1; other versions should work, too.)
     <li> The scipy python module (pyExcal definitely works with numpy 0.18.0; other versions should work, too.)
     </ul>
     A fairly recent version of Ureka (run "ur_setup") or astroconda should set up all the necessary versions 
     of Python, numpy, and scipy.
<li> Run the appropriate setup script in the pyExcal bin directory, dependind on which shell you are using (bash or tcsh):
     <pre> source pyExcal/bin/setup.bash</pre> or <pre> source pyExcal/bin/setup.csh</pre>
     **Note:  you will need to modify the value for PYEXCAL_DIR in the setup script before the first time you ever run it.**
<li> Run the following command:
     <pre> pyExcal.py --inputFile $PYEXCAL_DIR/test/std-rguiz-test.g.csv --band g</pre>
</ol>
You should get the following output to the screen, as well as two
QA plots in png form:

<pre>
bash$ pyExcal.py --inputFile $PYEXCAL_DIR/test/std-rguiz-test.g.csv --band g

Initial parameter values:   [1.6509999999999998, 0.0, 0.0]
Converged
Converged with chi squared  0.481103286398
degrees of freedom, dof  40
RMS of residuals (i.e. sqrt(chisq/dof))  0.109670334001
Reduced chisq (i.e. variance of residuals)  0.01202758216

Fitted parameters at minimum, with 68% C.I.:
a                1.34904 +/-     0.0629574   (4.666840 percent)
b            -0.00829816 +/-     0.0502757   (605.865115 percent)
k               0.214706 +/-     0.0391504   (18.234481 percent)

Correlation matrix:
                 a          b          k
a            1.000000
b           -0.101816   1.000000
k           -0.904639  -0.244643   1.000000


Your fit equation is:
    g_inst - g_std = 1.349 + -0.008*((g-r) - 0.530) + 0.215*X

Outputting QA plot qa-std-rguiz-test.g.csv_airmass.g-band.png
Outputting QA plot qa-std-rguiz-test.g.csv_color.g-band.png


That's all, folks!
</pre>

The a, b, and k parameters are the familiar a, b, and k from
the mtpipe photometric equations.  Currently, I have ignored
the "c" term coefficient (a.k.a., the second-order extinction),
but that could be added if needed.  (The concern is that it is
so small that we won't get a significant fit for it, and will
just end up adding noise to the fit.)


[Back to top.](#top)

----------------------------------------------------------------------
#### <a name="requests"></a>How to request additions or other updates to the FAQ?

Please use the [issues](https://github.com/DouglasLeeTucker/pyExcal/issues) to post requests for additions or other updates 
to this FAQ .


[Back to top.](#top)
