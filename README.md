# KlipperScreen
KlipperScreen is an idea based from [OctoScreen](https://github.com/Z-Bolt/OctoScreen/), but instead of needing OctoPrint or ot compile go, KlipperScreen is python based and interacts directly with Moonraker, Klipper's API service, so that it can be run with no dependecies besides Klipper.


More details to come...


### Installation
``` sudo apt install -y xserver-xorg-video-fbturbo xinit xinput x11-xserver-utils python-gi python-gi-cairo gir1.2-gtk-3.0 python-requests python-websocket
```

Add the following to _/boot/config.text_
``` hdmi_cvt=800 533 60 6
hdmi_group=2
hdmi_mode=87
hdmi_drive=2
```

As an option to do development or interact with KlipperScreen from your computer, you may install tigervnc-scraping-server and VNC to your pi instance. Follow tigervnc server setup procedures for details on how to do that.
