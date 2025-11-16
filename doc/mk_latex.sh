#!/bin/bash
##############################################################################
# Latex compilation                                                          #
#----------------------------------------------------------------------------#
#                                                                            # 
##############################################################################

Fichiers="Nauteff-Vision-Conception
Nauteff-Vision-Spec"

if [ "$NAUTEFFVISION_PATH" != "" ]
then
    cd $NAUTEFFVISION_PATH/doc
fi

set -x
cd latex/graph
for fic in *.dia
do

    base="${fic%.dia}"
    echo "Conversion de $fic vers $base.svg et $base.pdf ..."
    dia --nosplash --export="$base.svg" --filter=svg "$fic"
    dia --nosplash --export="$base.pdf" --filter=pdf "$fic"
done

exit

cd ../src

for fic in $Fichiers
do
    echo
    echo ##############################################################################
    echo #
    echo #           $fic.tex
    echo #
    echo ##############################################################################
    echo

    pdflatex  -halt-on-error  -output-directory=../build  ${fic}.tex
    cp ../build/${fic}.pdf ../../pdf
done

