#!/usr/bin/bash

ttyAP=/dev/ttyACM0

echo commande
while true
do
    read rep

    case $rep in

    "h") echo "mode heading"            > $ttyAP;;
    "i") echo "mode idle"               > $ttyAP;;
    "+") echo "turn starboard 1"        > $ttyAP;;
    "-") echo "turn port 1"             > $ttyAP;;
    +[0-9]*) echo "turn starboard ${rep//[^0-9]/}"  > $ttyAP;;
    -[0-9]*) echo "turn port ${rep//[^0-9]/}"       > $ttyAP;;

    "dac")    echo "display AP config"    > $ttyAP;;
    "dmc")    echo "display motor config" > $ttyAP;;
    "dec")    echo "display MEMS config"  > $ttyAP;;
    "hwms")   echo "display hwms"         > $ttyAP;;
    "simple") echo "AHRS select simple"   > $ttyAP;;
    "quat")   echo "AHRS select quat"     > $ttyAP;;
    "DT0058") echo "AHRS select DT0058"   > $ttyAP;;

    Kp=[.0-9]* | Kp=\-[.0-9]* | Kp=\+[.0-9]) echo set Kp ${rep//[^0-9.-]/}  > $ttyAP;;
    Kd=[.0-9]* | Kd=\-[.0-9]* | Kd=\+[.0-9]) echo set Kd ${rep//[^0-9.-]/}  > $ttyAP;;
    Ki=[.0-9]* | Ki=\-[.0-9]* | Ki=\+[.0-9]) echo set Ki ${rep//[^0-9.-]/}  > $ttyAP;;

    
    thr=[.0-9]* | thr=\-[.0-9]* | thr=\+[.0-9]) echo set motor_threshold ${rep//[^0-9.-]/}  > $ttyAP;;
    cvt=[.0-9]* | cvt=\-[.0-9]* | cvt=\+[.0-9]) echo set motor_angletime ${rep//[^0-9.-]/}  > $ttyAP;;
    hpf=[.0-9]* | hpf=\-[.0-9]* | hpf=\+[.0-9]) echo set motor_hpf_coeff ${rep//[^0-9.-]/}  > $ttyAP;;
    mvg=[.0-9]* | mvg=\-[.0-9]* | mvg=\+[.0-9]) echo set mag_vs_gyr ${rep//[^0-9.-]/}  > $ttyAP;;

    "q") exit ;;
    esac

done
