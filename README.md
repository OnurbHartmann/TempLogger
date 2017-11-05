# TempLogger
This is my first Raspberry Pi project to monitor temps and efficency of my house ventilation system (Vaillant RecoVair 350).
Baiscally I use 5 temperature sensor and a Raspi to send data to Microsoft Azure IoT hub. From there the Azure Streamanalytics calculates 
the efficency and forwards to Microsoft streaming dataset where PowerBI shows up the data on a dashboard. 
Additionally I add the CPU temperature and and a virtuell GPS position by reading the ISS position on each sample.
Samples where send each minute by using cron job.


![Alt text](/documentation/IMG_5912.JPG?raw=true "general setup")

![Alt text](/documentation/IMG_5943.JPG?raw=true "Optional Title")

![Alt text](/documentation/IMG_5944.JPG?raw=true "Optional Title")

![Alt text](/documentation/IMG_5945.JPG?raw=true "Optional Title")
