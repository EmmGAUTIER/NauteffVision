#!/bin/bash

# DIALOG=${DIALOG=dialog}
DIALOG=dialog

SCRIPT_DIR=$(dirname "$(realpath "$0")")
export NAUTEFFVISION_PATH=`dirname $SCRIPT_DIR`
cd  $NAUTEFFVISION_PATH
export TARGET_DIR=$NAUTEFFVISION_PATH/build

main_menu() {
    while true; do
        CHOICE=$($DIALOG --clear --backtitle "Menu Principal" \
            --title "Menu" \
            --menu "Sélectionnez une option :" 15 50 5 \
            d "Documentation Auto doxygen" \
            l "Documentation latex" \
            t "tests" \
            z "Fin" \
            2>&1 >/dev/tty)

        case $CHOICE in

            s)  echo "Génération de documentation (sphynx)"
                #${NAUTEFFVISION_PATH}/scripts/mk_doxy.sh
                read -p "Appuyez sur <Return> pour continuer" rep
                ;;

            l)  echo "Génération de documentation (latex)"
                ${NAUTEFFVISION_PATH}/doc/mk_latex.sh
                read -p "Appuyez sur <Return> pour continuer" rep
                ;;

            t) CHO "Éxécution des tests"
                ${NAUTEFFVISION_PATH}/tests/tests.sh
		read -p "Appuyez sur une touche pour continuer" rep
                ;;

            z) clear
               exit 0
                ;;

            *) break ;;
        esac
    done
}

main_menu
clear

