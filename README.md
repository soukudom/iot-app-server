# IoT App

Fog computing app to gather and visualize data. This repository has two parts, server and edge. Server part is built on Cisco EFM that receives incoming data, processes them and visualizes them. Edge part gathers data from OPC/UA server and sends them via MQTT. The edge application is prepared for Cisco Fog computing devices as IOx package.
All deployment tasks are done via Ansible. Below you can see a description of the build process.
## Getting started
In order to get everything working as intended you first need to:
* Download EFM 1.7.2 Windows and Linux Install packages from Cisco CCO (they come bundled in one .zip file)
* Download and install Ansible
## Prerequisites
The following must be present on the target hosts before installation can proceed:
* RHEL CentOS 7 (fresh installation is preferred) 
* An user with sudo privileges named "efm" (the same sudo password must pe present on all the target hosts)
* Access to any of the target hosts through ssh
* A ssh rsa key-pair (ssh-keygen) generated and copied to each target host, so that you won't need to enter the ssh password
on every login
## Ansible Setup
Now that Ansible is downloaded and installed the next steps are:
1. Populate the "hosts" file in the main folder with the target hosts IPs, and aliases for ease of use
(there is an example is the hosts file provided in the repo)
2. Place the following folders: "playbooks" and "roles" in your Ansible installation folder 
(default installation place is /etc/ansible for Linux)
3. For privacy reasons, any username and password that will be used in the installation have been placed in a file
named "credentials.yml" - this file is located in "roles/efm17x/vars/" and is encrypted using Ansible-Vault
4. The file structure must remain exacty as provided in the entire "roles" folder for Ansible to understand it correctly
## EFM 1.7.2 Installation
In order to correctly run the Ansible playbook and commence the EFM 1.7.2 installation:
1. Create a vault password file, so that you won't have to enter the password everytime you run the playbook on a target host 
and place the file in roles/efm17x/files
2. In the roles/efm17x/tasks folder please go through the "main.yml" and "dglux.yml" files and make the necessary changes
in each TODO section
3. In order to run the Ansible playbook the following command must be used:
"$ ansible-playbook --vault-password-file roles/efm17x/files/.vault_pass -K playbooks/efm17x_playbook.yml"
4. The -K argument will prompt you to enter the sudo password for the target hosts
## (Optional) Demo Dashboard installation
In order to install the demo Dashboard the steps are:
1. Download the "server.zip" file from the provided Box link - this file is encrypted using Ansible Vault (the password is the same as for the "credentials.yml" file)
2. Modify the Ansible playbook in order to have to correct paths to the files
3. Run the playbook
4. In the EFM DGLux Dashboard select: "Project" (the between "File" and "Edit") -> "Open Project" -> "Open/Import" tab -> select the project and open it
5. In the EFM DGLux Dashboard select: "Data" -> expand "sys" -> right-click "links" -> "Rescan" and "Start All Links" 
6. In the EFM DGLux Dashboard select: "Data" -> expand "conns" -> expand "Refinery-Simulator" -> right-click "simulator" -> select "start"
7. You can now navigate to the "Project" tab and view the demo Dashboard with simulated data
## OPC/UA IOx plugin
Edge application for gathering data from OPC/UA server and send them to a MQTT broker. To specify input parameters, use a configuration file in INI format (e.g. package_config.ini). To launch this module just run opcPlugin.py without any parameter and configuration file in the same location. Verbose mode is controlled by global variable 'VERBOSE'.

To compile and run this app on Cisco IoT gateways use 'ioxclient'. Further monitoring and control can be done by Cisco GMM, FND or Fog director