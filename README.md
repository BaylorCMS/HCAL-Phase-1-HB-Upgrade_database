# CMS HB Phase 1 Upgrade database.
A web-framework for the CMS HB Phase 1 Upgrade database.
Initial QIE Card testing was performed at Fermilab, Summer 2018. QIE stands for "charge integrator and encoder."
Readout Modules (RM) and Calibration Units (CU) were assembled at CERN, Fall 2018.
* New website: The website will be hosted at Baylor... once done, the new URL can be posted here. (FIXME)
* Old website: https://nbay11.fnal.gov/hb/cards/catalog
* Username/password: Please email Jay Dittmann (Jay_Dittmann@baylor.edu) to request access.
* Questions: Contact Jay Dittmann (Jay_Dittmann@baylor.edu)

## Initial Teststands at Fermilab
### 1. Firmware programming of Bridge and Igloo Field Programable Gate Arrays (FPGA).
### 2. Quality control (QC) tests of read/writes to all registers and micro HCAL Trigger and Readout (uHTR) tests.
### 3. Calibration of QIE Chips using DC current charge injection.
## Reaout Box (RBX)
Each Readout Box (RBX) contains 4 Readout Modules (RM), 17 QIE Cards, 4 SiPM Control Cards, 1 Pulser Card and 1 Calibration Unit (CU).
Each RBX has 4 MTP cabels, 32 data fibers, 192 channels, 192 Silicon Photomultipliers (SiPM), and 192 Bias Voltages (BV).
There are 4 "dark SiPM channels" that do not receive data.
## Readout Modules (RM)
There are 4 Reaout Modules (RM) per Readout Box (RBX). Each RM contains 4 QIE Cards and 1 SiPM Control Card. Thus each RM has 48 QIE Chips, 48 channels, 8 fibers within 1 MTP cable, and 48 Bias Voltages (BV) which are set by the SiPM Control Card.
## QIE Cards
There are 4 QIE Cards per Readout Module (RM) and 16 QIE Cardsin in RMs per Readout Box (RBX). Each QIE Card has 12 QIE Chips, 12 channels, and 2 fibers. Note that each fiber has 6 channels.
## SiPM Control Cards
There is 1 SiPM Control Card per Readout Module (RM) and 4 SiPM Control Cards per Readout Box (RBX). Each SiPM Control Card controls 48 Bias Voltages (BV) for 48 Silicon Photomultipliers (SiPM).
## Calibrations Units (CU)
There is 1 Calibration Unit (CU) per Readout Box (RBX). Each CU contains 1 Pulser Board and 1 QIE Card. The CU has 6 pindioes and 5 laster inputs. The center quatz fiber input provides light for 2 pindioes as well as all SiPMs in RBX for a laser run.

## Database uploading scripts for adding or modifying information.
#### backup                      
Stores 2-hourly, daily, and weekly backups.
#### bv_uploader                 
Uploads bias voltage measurements for SiPMs in RM.
#### cal_uploader
Upload QIE card calibrations done at FNAL.
#### card_db
The main database directory.
#### csv_files
Generates CSV files from database.
#### db_edits
Database edits.
#### firmware_update
Update QIE card firmware using RBXLogger output dictionary.
#### LICENSE
License.
#### location_update
Update locations of QIE cards based on CU and RM locations.
#### media
Stores beaucoup data.
#### query
Ask the database a question... and get an answer!
#### rm_update
Set RM and CU unique ids based on QIE card unique ids.
#### sipm_control_uploader
Upload SiPM Control Card calibrations. One set is from Mandakini, and another set is from CERN B904.
#### uploader
Upload FNAL test results to the database.
#### web_update
Store a cached version of the website every hour.
