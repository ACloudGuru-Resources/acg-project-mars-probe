## Hardware List

- Pi Zero W
- Voltaic 3.4W 6V Solar Panel
- Sixfab Cellular IoT Hat
- Twilio SuperSIM sim card and service
- Pi Camera v2.1
- Zero2Go Omini Power Controller
- Adafruit USB/DC/Solar LiPo Charger
- 4400mAh LiPo battery
- Sandisk Ultra 32GB microSD card
- DHT22 Temperature and Humidity Sensor
- Waterproof Case ($6 from local big box store)
- Small transparent plastic square from a clamshell cookie container
- Cyanoacrylate glue (Super Glue)
- Heavy duty velcro with adhesive backing
- Spray paint (Optional but if the case is transparent, recommended to keep the heat down)
- Silicone sealant
- USB cables to connect Pi to Cellular Hat

Also used
- Soldering Iron and Solder
- Drill for camera hole and solar charging port


## Hardware Setup

1. Added (soldered) 4700uF capacitor to the USB/DC/Solar LiPo Charger
2. Added (soldered) the GPIO pin-outs to the Pi Zero
3. Install jumper wire on Cellular Hat to force it to use USB power rather than GPIO power.  Consult documentation for specific jumpers.  This allowed me to place the Cellular Hat on the other side of the enclosure rather than having to stack it on top of the Pi and Power Controller.
4. Install the Pi Camera into the ribbon connector on the Pi Zero.
5. Stack power controller on top 40pin socket riser header.
6. Connect DHT22 to GPIO pins 1 (3v3 Power), 6 (Ground) and 37 (GPIO26) with jumper wires.  Note that GPIO4 (1Wire) is used by the Zero2Go Power Controller and will constantly power cycle your Pi if you try to use GPIO4 for anything else.
7. Twilio SuperSIM card goes into the Cellular Hat.  LTE and GPS antennas connect to respective ports on the hat.
8. Provision the SuperSIM on Twilio website for appropriate geography and providers.
9. USB cables connect the Pi to the Cellular Hat.
10. 4400mAh LiPo battery connects to the Adafruit USB/DC/Solar LiPo Charger
11. Solar panel connects to the solar port on the Charger
12. Zero2Go Omni Power Controller connects to the Load port on the Charger
13. Drill holes for camera and solar port.
14. Glue transparent plastic square over top of camera hole, ensuring even glue coverage around the hole.
15. Place small piece of tape over camera porthole and paint you desired color.
16. Mount components in the container with heavy duty velcro.  Make sure the solar port sticks out slightly.
17. Use silicone sealant around the solar port to seal out the weather.  Hot glue could also work and be less permanent.
18. Button everything up.
19. Work out a solar panel mounting arrangement that works for you.  Optimal direction and angle will vary based on your latitude and the season.
20. Profit!  Err...no power.
21. Open the container back up, hit the power button on the Power Controller and on the Cellular Hat.  Watch all the LEDs blink nicely.
22. Button everything up.
23. Profit!


## Software Setup

1. Download and image microSD card with Raspberry Pi OS Lite.
2. Add empty ```ssh``` file and ```wpa_supplicant.conf``` containing your wifi network info to boot partition.
3. SSH into Pi and copy over you SSH public key into ```~/.ssh/authorized_keys```.  Saves LOTS of password typing.
4. Change Pi default password and/or disable password login in ```/etc/ssh/sshd_config```.
5. ```sudo apt update && sudo apt upgrade -y && sudo reboot```
6. (Optional) Disable HDMI and Audio to save power and CPU.  Google it.
7. Use ```raspi-config``` to expand SD card and enable Pi Camera.  If you stacked your cellular modem on the GPIO pins rather than use the USB cable method, you'll also need to enable the serial port (but say no to allowing login via serial).
8. Edit the ```/boot/config.txt``` to enable 1-Wire on GPIO26 for our DHT22 sensor by adding ```dtoverlay=w1-gpio,gpiopin=26```.  You can use any available pin though except the default 1-Wire pin of GPIO4.  The Zero2Go board uses that pin.
9. Install [Zero2Go Omini softwre](https://www.uugear.com/doc/Zero2Go_Omini_UserManual.pdf) per manual.  This will allow the Pi to gracefully shutdown if the battery gets too low and will restart when the battery is recharged enough.
10. Install the Sixfab Cellular IoT Hat software and configure for PPP connection per their [documentation](https://docs.sixfab.com/docs/raspberry-pi-cellular-iot-hat-introduction).  Suggest using the auto-connect configuration.
11. Proceed through AWS Greengrass IoT Core setup and config.
12. Profit!

## Issues and Tips


### Access In the Field
When I took the device out into the field, I wanted to be able to SSH into it to make sure the cellular modem was connected and the PPP connection was good.  Apparently, with the Twilio SuperSIM, it's a proxied connection (through AWS might I add...so a ```traceroute 8.8.8.8``` and you'll see an EC2 instance pop up there...hehe).  This means that it's not real easy to initiate a remote SSH connection into the device.  Good for security but kind of a hassle for me.  I could have setup a VPN connection from the Pi, but that would consume valuable memory and CPU.  Instead, I setup the Pi to use the hotspot on my phone as a secondary connection in my ```/etc/wpa_supplicant/wpa_supplicant.conf```.  So, if my home wifi was unavailable, it would failover to my mobile phone hotspot if that's available.  (Do note that the Pi Zero W does not support 5GHz, only 2.4Ghz.)

  
### IPv6 No-Go
By default, IPv6 is enabled along with IPv4 on the Pi.  My mobile hotspot (see above) was issuing both an IPv4 and IPv6 address.  The Pi was trying to resolve my Greengrass IoT endpoint via IPv6 and it couldn't get to it.  Not sure if the endpoint doesn't support IPv6 by default or if my mobile hotspot was just not forwarding IPv6.  Seems like the IoT endpoint would surely support this so my bet is that it's something in the mobile hotspot or mobile network.  Anyhow, I disabled IPv6 on the Pi by adding the following lines to ```/etc/sysctl.conf``` and restarted:
```
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
```


### Credentials Issue?

At one point, I was getting this very cryptic error in the Greengrass log and my program was reporting that it couldn't upload the file to S3.  The inline exception thrown by the ```upload_file``` method weren't that helpful either.
```
2021-09-12T21:41:59.747Z [INFO] (pool-2-thread-14) com.aws.greengrass.tes.CredentialRequestHandler: Received IAM credentials that will be cached until 2021-09-12T22:36:58Z. {iotCredentialsPath=/role-aliases/GreengrassV2TokenExchangeRoleAlias/credentials}
2021-09-12T21:42:01.298Z [INFO] (pool-2-thread-14) com.aws.greengrass.tes.CredentialRequestHandler: Request failed. {}
java.io.IOException: Broken pipe
	at java.base/sun.nio.ch.FileDispatcherImpl.write0(Native Method)
	at java.base/sun.nio.ch.SocketDispatcher.write(SocketDispatcher.java:47)
	at java.base/sun.nio.ch.IOUtil.writeFromNativeBuffer(IOUtil.java:113)
	at java.base/sun.nio.ch.IOUtil.write(IOUtil.java:79)
	at java.base/sun.nio.ch.IOUtil.write(IOUtil.java:50)
	at java.base/sun.nio.ch.SocketChannelImpl.write(SocketChannelImpl.java:463)
	at jdk.httpserver/sun.net.httpserver.Request$WriteStream.write(Request.java:391)
    <snip>
```
Initially, I thought it was related to Greengrass not getting the proper credentials, but eventually, I stumbled across the root cause.  In my code, I'm trying to put the image with an ACL of ```public-read```, however I had left the 'Block public access' restriction on in my bucket.  After turning off that, the uploads were functioning as desired.  After verifying that was the issue and that in fact everything was working properly, I ultimately remove the ```public-read``` and reinstated the restriction on the S3 bucket.  I'd recommend you do the same once you get things working.


### Power Drain
After a few days of running the cellular modem full time, I hit a day where the sun wasn't as bright.  This resulted in an incomplete charge on the battery for that day and caused the modem to power down.  Because I am using the USB connection method, I had no way of triggering the modem to start back up after it was shut down.  After consulting the Sixfab docs, I figured out that my particular modem version uses GPIO11 as the Power Key.  I jumpered the GPIO11 pin on the Pi Zero to the corresponding GPIO11 port on the HAT and also wrote a little Python program that would cycle GPIO11 to High for 0.5 seconds then go back to Low.  This simulated pressing the physical power button and now I was able to power on and off the modem.

This also allowed me to create a "phone home" schedule that I could include in ```crontab``` such that I wouldn't need to have the modem on constantly consuming power.  I created two scripts.  One script powered on the modem (via my Python script) and issued the ```sudo pon``` command to start a PPP connection.  The other script issued the ```sudo poff``` command to close the PPP connection and also powered off the modem (same script as power-on...its a toggle).  I set these scripts to execute in cron every 15 minutes offset by 5 minutes.  So, my Pi would phone the Greengrass IoT queues once every 15 minutes and stay connected for 5 minutes.  In that time, it would pickup any retained messages on the ```picam/request``` topic and do what it needed to do.  Then, after 5 minutes, it would drop the connection.

I could get better battery milage by adding on a [Witty Pi 3 Mini Realtime Clock and Power Manager](https://www.uugear.com/product/witty-pi-3-mini-realtime-clock-and-power-management-for-raspberry-pi/) that I also had on hand, but I ran out of stacking room in the case.  The Witty Pi 3 Mini has a little clock and battery on it that can keep up with time all by itself.  It can power on the Pi Zero at a certain time and power it back off after some time.  This would have consumed the least power and might be a needed change as I go into the darker months of the year.



