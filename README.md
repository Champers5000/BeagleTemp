# BeagleTemp
An automatic way to collect temperature readings on a BeagleBone with a fancy webpage


Install instructions: The python program has several dependencies that need to be installed. Run these commands
```
#install necessary packages
sudo apt install python3 python3-pip cron git
sudo systemctl enable cron
```
```
#make sure you are in your home directory
cd ~/
```
```
git clone https://github.com/Champers5000/BeagleTemp.git
cd bgltemp
#give the startup script execute rights
chmod +x start.sh
#modify crontab
crontab -e
```
Add the following line to the file
```
@reboot /home/[username]/bgltemp/start.sh
```
Save and exit

Test if everything works by running the start script. There is a delay between the script running and the program starting, so wait about 40 seconds.
```
bash start.sh
```
If the script works fine, then restart your beagle and see if it still works. 
