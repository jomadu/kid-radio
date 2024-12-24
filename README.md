# Kid Radio

I'm making a radio for my kid for her first christmas.

Taking an old radio, connecting the tuner to a raspberry pi zero 2 w, and using it to switch between different spotify playlists that I manage with a specific naming convention.

## Hardware

- Raspberry Pi Zero 2 W 
- IQaudIO Codec Zero
- HiLetgo ADS1115 16 Bit 16 Byte 4 Channel ADC

## Setup for IQaudIO-Codec-Zero

- [Raspberry Pi Configuration](https://www.raspberrypi.com/documentation/accessories/audio.html#configuration)
- [Re: Pi Zero W with Codec Zero not working, help needed](https://forums.raspberrypi.com/viewtopic.php?t=351641#p2108752)

`/boot/firmware/config.txt`

```
#dtparam=audio=on

dtoverlay=
dtoverlay=iqaudio-codec
```

```
sudo apt install git
git clone https://github.com/raspberrypi/Pi-Codec.git
```

```
sudo alsactl restore -f /home/<username>/Pi-Codec/Codec_Zero_OnboardMIC_record_and_SPK_playback.state
```

`/etc/rc.local`

```
#!/bin/sh
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

sudo alsactl restore -f /home/<username>/Pi-Codec/Codec_Zero_OnboardMIC_record_and_SPK_playback.state

exit 0
```

`.asoundrc`

```
pcm.!default {
  type hw
  card IQaudIOCODEC
}
ctl.!default {
  type hw
  card IQaudIOCODEC
}
```

```
sudo reboot
```

```
speaker-test -c2
```

## Raspotify Setup

- [Basic Setup Guide](https://github.com/dtcooper/raspotify/wiki/Basic-Setup-Guide)

- [Change name of spotify connect name](https://github.com/dtcooper/raspotify/issues/667)

`/etc/raspotify/conf`

```
LIBRESPOT_NAME="Kid Radio"
```

## Spotify Creds

https://developer.spotify.com/dashboard