# Config Manager
Configuration Tracker and Change detection

This repo will showcase an use case of how to detect and notify changes made to devices managed by DNA Center

## The Challenge: 
 - 70% of policy violations are due to user errors
 - Configuration drifting 

## The Goal: 
 - Detect and alert on all network configuration changes


## The Solution:
 - Integration between Cisco DNA Center, git, github and Webex Teams
 - The application may run on demand, scheduled or continuously


## The Results: 
 - Non compliant configuration changes are mitigated in minutes
 - Troubleshooting assistance by providing a real time view of all device configuration changes

 
## Setup and Configuration
 - The requirements.txt file include all the Python libraries needed for this application
 - This application requires:
   - Cisco DNA Center
   - GitHub account configured on local machine
   - Git setup locally
   - Webex Teams Bot account
 - The **config.py** requires customization with your instance  of Cisco DNA-Center and more
 