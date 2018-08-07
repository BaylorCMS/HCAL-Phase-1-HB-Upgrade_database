#!/bin/bash

# step12.sh: This script manages the caching of database files.
#
# Author:   Andrew Baas
# Credits:  Shaun Hogan, Mason Dorseth, John Lawrence, Jordan Potarf,
#                Andrew Baas
# 
# Version:  1.0
# Maintainer:   Caleb Smith
# Email:    caleb_smith2@baylor.edu
# Status:   Live

###################################################
#               Run Caching scripts               #
###################################################

#/usr/local/bin/python2.7 /home/django/testing_database_hb/web_update/summary_json.py
/usr/local/bin/python2.7 /home/django/testing_database_hb/web_update/plots_json.py
#/usr/local/bin/python2.7 /home/django/testing_database_hb/web_update/stats_json.py
/usr/local/bin/python2.7 /home/django/testing_database_hb/media/summary_plots/dqmplots.py
