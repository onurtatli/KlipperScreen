#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
KSPATH=$(sed 's/\/scripts//g' <<< $SCRIPTPATH)
echo "Installing KlipperScreen unit file from ${KSPATH}"
echo ""

SERVICE=$(<$SCRIPTPATH/KlipperScreen.service)
KSPATH_ESC=$(sed "s/\//\\\\\//g" <<< $KSPATH)
SERVICE=$(sed "s/KS_DIR/$KSPATH_ESC/g" <<< $SERVICE)


echo "$SERVICE" > /etc/systemd/system/KlipperScreen.service
