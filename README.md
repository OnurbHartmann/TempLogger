# TempLogger
This is my first Raspberry Pi project to monitor my house ventilation system.
Baiscally I use 5 temperature sensor and a Raspi to send data to Microsoft Azure IoT hub. From there the Azure Streamanalytics calculates 
the efficency and forwards to Microsoft streaming dataset where PowerBI shows up the data on a dashboard. 
Additionally I add the CPU temperature and and a virtuell GPS position by reading the ISS position on each sample.
Samples where send each minute by using cron job.

