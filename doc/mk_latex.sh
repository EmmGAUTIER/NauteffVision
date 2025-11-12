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

cd latex/src

for fic in $Fichiers
do
    echo
    echo ##############################################################################
    echo #
    echo #           $fic.tex
    echo #
    echo ##############################################################################
    echo
    echo "Fichier : " $fic
    pwd
    read rep

    pdflatex  -halt-on-error  -output-directory=../build  ${fic}.tex
    cp ../build/${fic}.pdf ../pdf
done

