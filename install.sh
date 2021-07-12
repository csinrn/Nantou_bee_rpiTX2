#!/bin/sh

#### install awsiotpythonsdk ####
export LC_ALL=en_US.utf8
sudo apt-get install python3-pip
pip3 install awsiotpythonsdk

#### move crediential ####
mv ~/Documents/pems/* ./Nantou_bee_rpiTX2/
rm -r ~/Documents/pems

#### move files ####
# service and autostart
mkdir -p ~/.config/systemd/user
mkdir ~/.config/autostart
cp ~/Documents/Nantou_bee_rpiTX2/qtBee.service ~/.config/systemd/user
cp ~/Documents/Nantou_bee_rpiTX2/tx2code.desktop ~/.config/autostart
cp ~/Documents/Nantou_bee_rpiTX2/qtBeeservice.sh ~/Documents/tracking_pollen_demo_code/release/
# network
sudo cp ~/Documents/Nantou_bee_rpiTX2/eth0:1 /etc/network/interface.d/ 


#### enable systemctl ####
systemctl --user enable qtBee.service