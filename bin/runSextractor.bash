#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# This script will likely eventually be replaced by a 
# python script.
# 
# To run:
# 1. Clone from GitHub (or update your copy) of the 
#    pyExcal package from 
#    https://github.com/DouglasLeeTucker/pyExcal
#
# 2. Edit your $PYEXCAL_DIR/bin/setup.bash or setup.csh 
#    file.  (Should only need to do this once per 
#    pyExcal package clone/update.)
#
# 3. Update the values for SEXTRACTOR_DIR, STILTS_DIR, and 
#    STILTS_DIR list in the runSextractor.bash script (see
#    these variables below).  (Should only need to do this 
#    once per pyExcal package clone/update.)
#
# 4. Copy runSextractor.sh to the directory where you want
#    to run it.
#
# 5. Copy/create to the directly where you just copied 
#    runSextractor.sh the sextractor files from your 
#    $PYEXCAL_DIR/etc directory, or from GitHub:
#    https://github.com/DouglasLeeTucker/pyExcal/tree/master/etc
#
# 6. Create a file containing the list of wcs'ed files you 
#    want to run sextractor on and match with the standard
#    star catalog.  E.g., in IRAF or pyraf, 
#    --> hselect wcs_*.fits $I 'FILTER2=="r"' > fileList_r.txt
#
# 7. source your $PYEXCAL_DIR/bin/setup.bash (or setup.csh) file.
#    (run in an environment that contains the astropy package.)
#    (do this in the terminal where you plan to run the code.)
#
# 8. Run runSextractor.sh; e.g.:
#
#    bash-4.1$ runSextractor.sh fileList_r.txt
# 
#
# REMAINING ISSUES:
# 
# 1. Still need to make header of the combined matched file
#    robust for times when we use sextractor to extract
#    MAG_APERs (FLUX_APERs) from multiple apertures...
# 
# 2. Still not fully compliant with the format required 
#    by $PYEXCAL/bin/pyExcal.py.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Location of the sextractor executable:
SEXTRACTOR_DIR=/sdss/ups/prd/sextractor/v2_18_10/Linux/binx86_64

# Location of the STILTS executable:
STILTS_DIR=/usrdevel/dp0/dtucker/STILTS/latest

# Location of the main pyExcal directory: 
PYEXCAL_DIR=/usrdevel/dp0/dtucker/GitHub/pyExcal

# The file containing the list of files to run sextractor on
#  is the first (and, currently, the only) argument that was 
#  passed to runSextractor.sh on the command line...
FILELISTNAME=$1

# Loop through list of files in FILELISTNAME:
while read fname; do

    echo $fname

    # Grab exptime, airmass, and jd from the FITS header of $fname...
    #  (A bit slow, but it seems to work...)
    exptime=`getFITSKeyValue.py --inputFile $fname --keyword EXPTIME`
    airmass=`getFITSKeyValue.py --inputFile $fname --keyword AIRMASS`
    jd=`getFITSKeyValue.py --inputFile $fname --keyword JD`

    echo "Running sextractor..."
    # if there is currently a file called $fname.cat.ascii, delete it...
    rm -f $fname.cat.ascii
    # now run sextractor (output file is called $fname.cat.ascii)...
    $SEXTRACTOR_DIR/sex $fname -c sextractor.pyexcal.config -CATALOG_NAME $fname.cat.ascii

    echo "Running stilts..."
    # if there is currently a file called $fname.cat.ascii.matched.tmp, delete it...
    rm -f $fname.cat.ascii.matched.tmp
    # Now match sextractor catalog $fname.cat.ascii against the standard stars catalog...
    #  We use the stilts command "tmatch2".
    #  It is assumed that the RA and DEC of the sextractor catalog $fname.cat.ascii
    #  are in columns 8 and 9, respectively.  A 3.0-arcsec search radius is used.
    $STILTS_DIR/stilts tmatch2 \
	matcher=sky params="3.0" find=best \
	in1=$fname.cat.ascii ifmt1=ascii values1="col8 col9" \
	in2=$PYEXCAL_DIR/data/stdstars_ugriz_prime.v4.csv ifmt2=csv values2="ra dec" \
	out=$fname.cat.ascii.matched.tmp ofmt=csv

    echo "Adding FNAME, JD, EXPTIME, and AIRMASS to file..."
    # if there is currently a file called $fname.cat.ascii.matched, delete it...
    rm -f $fname.cat.ascii.matched
    # Add header...
    awk 'NR==1 {print "FNAME,JD,EXPTIME,AIRMASS,"$0}' $fname.cat.ascii.matched.tmp > $fname.cat.ascii.matched
    # Add fname, JD, exptime, and airmass...
     awk -v f=$fname -v j=$jd -v e=$exptime -v a=$airmass 'NR>1&&NR<6 {print f","j","e","a","$0}' $fname.cat.ascii.matched.tmp >> $fname.cat.ascii.matched

    # Delete the extraneous $fname.cat.ascii.matched.tmp file...
    rm $fname.cat.ascii.matched.tmp


done < $FILELISTNAME


# Create an empty file to contained the matches from all the files...
rm -f $FILELISTNAME.cat.ascii.matched.combined
touch $FILELISTNAME.cat.ascii.matched.combined

# Create header for combined matches file...
# (This won't work perfectly if multiple apertures are used in sextractor.)
firstFile=$(head -n 1 $FILELISTNAME)
firstFile=$firstFile.cat.ascii
echo -n "FNAME,JD,EXPTIME,AIRMASS," >> $FILELISTNAME.cat.ascii.matched.combined
awk '$1=="#" {printf("%s,", $3)}' $firstFile >> $FILELISTNAME.cat.ascii.matched.combined
awk 'NR==1 {printf("%s,", $0)}' $PYEXCAL_DIR/data/stdstars_ugriz_prime.v4.csv >> $FILELISTNAME.cat.ascii.matched.combined
echo "Separation" >> $FILELISTNAME.cat.ascii.matched.combined

# Copy (non-header) contents of each match file into the combined match file...
while read fname; do
    awk 'NR>1' $fname.cat.ascii.matched >> $FILELISTNAME.cat.ascii.matched.combined
done < $FILELISTNAME


echo 
echo 
echo "Combined matched file is "$FILELISTNAME.cat.ascii.matched.combined

echo
echo
echo "That's all, folks!"
echo 
