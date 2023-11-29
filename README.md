# azure-acquire
Acquiring MoSeq data using Kinect Azure. This package is a simple CLI tool that facilitates acquiring data using Kinect Azure on an Ubuntu machine.

# Installation

## Step 0: Install Ubuntu 18.04 on your acquisiton machine
Currently Ubuntu 18.04 is the only supported distribution listed in the [official installation instruction](https://learn.microsoft.com/en-us/azure/kinect-dk/sensor-sdk-download#linux-installation-instructions). **Please click `Don't Upgrade` to decline when you are prompted to upgrade to a new version of Ubuntu.**

## Step 1: Install `curl`
`curl` is used to download necessary files in the installation process. You can skip this step is `curl` is already installed.

Check if you have `curl` installed in the environment by running the following commands:
```
which curl
```

If you have `curl`, it should print out a path like `/usr/bin/curl` and you can go to the next step. Otherwise, you will see `curl not found`, and will need to install `curl` by running the following commands:
```
sudo apt update
sudo apt upgrade
sudo apt install curl
```

## Step 2: Install `build-essential` and `ffmpeg`
`build-essential` and `ffmpeg` are used to compile and write videos in the `azure_acquire` package. You can skip this step is `build-essential` and `ffmpeg` are already installed. When in doubt, install them.
```
sudo apt install build-essential
sudo apt install ffmpeg
```

## Step 3: Configure Microsoft's package repository
```
sudo apt-get update
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository https://packages.microsoft.com/ubuntu/18.04/prod
```
Find more information at the [official instruction](https://learn.microsoft.com/en-us/windows-server/administration/linux-package-repository-for-microsoft-software).

## Step 4: Install Azure Kinect packages
Install the Kinect Azure packages to control the Kinect Azure camera. The `k4a-tools` include [Azure Kinect viewer](https://learn.microsoft.com/en-us/azure/kinect-dk/azure-kinect-viewer), [Azure Kinect recorder](https://learn.microsoft.com/en-us/azure/kinect-dk/azure-kinect-recorder), and [Azure Kince firmware tool](https://learn.microsoft.com/en-us/azure/kinect-dk/azure-kinect-firmware-tool).

```
sudo apt install libk4a1.3-dev
sudo apt install libk4abt1.0-dev
sudo apt install k4a-tools=1.3.0
```
Find more information at the [official instruction](https://learn.microsoft.com/en-us/azure/kinect-dk/sensor-sdk-download#linux-installation-instructions). The version number for `libk4a` must match that of `k4a-tools` (in the case above the version number is `1.3`)

## Step 5: Finish the device setup
Add `99-k4a.rules` to the udev rules to use Azure Kinect as non-root.

```
wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/develop/scripts/99-k4a.rules
sudo mv 99-k4a.rules /etc/udev/rules.d/
```
Disconnect and reconnect Azure Kinect device for the changes to be effective.

## Step 6: Check if the set up runs correctly
Open Terminal and run the following command:
`k4aviewer`

<!---add k4aviwer images--->

## Step 7: Configure the camera setting
1. Select the device from the drop down list
2. Choose the device and note down the serial number. If you have multiple devices, place an object or wave you hand under the camera, click start to start test recording to figure out which serial number maps to which camera. After that, click stop to stop.
3. Select the device to configure and click Open device button to open the device.
4. Check Enable Depth Camera stream and select NFOV (Near Field of View) Unbinned for Depth mode.
5. [Recommended] Uncheck Enalbe color camera.
6. Select 30 FPS for framerate.
7. Click Save to save the settings.
8. Click close device. You must close device before you exsit the program.

## Step 8: Install and configure `git`
`git` is used to download the `azure_acquire` repository from GitHub.

Check if you have `git` installed in the environment by running the following commands:
```bash
which git
```
If you have `git`, it should print out a path like `/usr/bin/git` and you can go to the next step. Otherwise, you will see `git not found` and will need to install `git` by running the following commands:
```bash
sudo apt install git
```

If the installation code block above fails, visit the [official documentation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git/) for more information and alternative ways of installing `git`.

## Step 9: Install Anaconda/Miniconda
Anaconda is a distribution of python and Miniconda is a minimal version of Anaconda. Conda is the package and virtual environment management component of Anaconda/Miniconda. It allows users to install python packages and set up virtual environments more reproducibly.

Miniconda is sufficient for the MoSeq2 package suite because we don't need all the extra packages Anaconda provides. You can skip this step if Anaconda/Miniconda is already installed.

Check if you have `conda` (the package manager in Anaconda/Miniconda program) installed in the environment by running the following commands:
```bash
conda info
```

If you have `conda`, it should print out information about your environment and you can go to the next step. Otherwise, you will see `conda not found` and will need to download and install `conda` by running the following commands:
```bash
curl -L https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o "$HOME/miniconda3_latest.sh"
chmod +x $HOME/miniconda3_latest.sh
$HOME/miniconda3_latest.sh
```
We recommend that you say **yes** when the installation prompt asks if you want to initialize Miniconda3. If you decide to say no (not recommended) you can manually initialize conda by running `conda init`.

:exclamation: :grey_exclamation: **STOP!** :exclamation: :grey_exclamation: You must restart the terminal before continuing. Close the window, open a new one and move on to step 4. Restarting the terminal allows the new conda and python packages to be accessible by the terminal. This is important for [step 6](#step-6-create-a-conda-environment-using-moseq2-envyaml) and beyond. 

## Step 10: Clone (download) the `azure-acquire` repository
Clone `azure-acquire` repository from GitHub by running:
```bash
git clone https://github.com/versey-sherry/azure-acquire.git
```
Navigate to the `azure-acquire` directory by running:
```bash
cd azure-acquire
```

## Step 11: Create a new Conda environment and installed relevant packages
Please make sure you are in `azure-qcquire` directory for the following steps.

Create a conda environment called `azure-acquire` with `python 3.8` by running:
```
conda create -n azure-acquire python=3.8
```
Activate the eonvironment by running:
```
conda activate azure-acquire
```
Install the relevant package by running:
```
pip install -r requirements.txt
```
Install this package by running:
```
pip install .
```

Once you have finished setting up the environment, you should be able to verify the installation by running:
```
azure-acquire --version
```

# Acquiring data
Check the version of the package by running:
```
azure-acquire --version
```
Example acquisition command saving recording at `./data`:
```
azure-acquire ./data --subject-name mouse1 --session-name saline --serial-number xxx -recording-length 20
```

Options for the acquisition command:

`session-name`: This field can be an indicator of the date, cohort, experimental condition and/or environment type.
`subject-name`: This field can be an indicator of the rodent strain, sex, age and/or additional identifiers. The subject name should uniquely identify each mouse.
`recording-length`: The length of the recording time. Default is 30 mins if this option is not specified. Alternatively, the option could be specified using `-t 20`.
`serial-number`: The device the session records from. The device serial number could be found using `k4aviewer`.


```
sudo apt update
sudo apt install curl

sudo apt install build-essential
sudo apt install ffmpeg
sudo apt-add-repository -y -n 'deb http://archive.ubuntu.com/ubuntu focal main'
sudo apt-add-repository -y 'deb http://archive.ubuntu.com/ubuntu focal universe'
sudo apt-get update
sudo apt-get install -y libsoundio1

curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository https://packages.microsoft.com/ubuntu/18.04/prod

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.3/libk4a1.3_1.3.0_amd64.deb > /tmp/libk4a1.3_1.3.0_amd64.deb
echo 'libk4a1.3 libk4a1.3/accepted-eula-hash string 0f5d5c5de396e4fee4c0753a21fee0c1ed726cf0316204edda484f08cb266d76' | sudo debconf-set-selections
sudo dpkg -i /tmp/libk4a1.3_1.3.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.3-dev/libk4a1.3-dev_1.3.0_amd64.deb > /tmp/libk4a1.3-dev_1.3.0_amd64.deb
sudo dpkg -i /tmp/libk4a1.3-dev_1.3.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4abt1.0/libk4abt1.0_1.0.0_amd64.deb > /tmp/libk4abt1.0_1.0.0_amd64.deb
echo 'libk4abt1.0 libk4abt1.0/accepted-eula-hash string	03a13b63730639eeb6626d24fd45cf25131ee8e8e0df3f1b63f552269b176e38' | sudo debconf-set-selections
sudo dpkg -i /tmp/libk4abt1.0_1.0.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4abt1.0-dev/libk4abt1.0-dev_1.0.0_amd64.deb > /tmp/libk4abt1.0-dev_1.0.0_amd64.deb
sudo dpkg -i /tmp/libk4abt1.0-dev_1.0.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/k/k4a-tools/k4a-tools_1.3.0_amd64.deb > /tmp/k4a-tools_1.3.0_amd64.deb
sudo dpkg -i /tmp/k4a-tools_1.3.0_amd64.deb

wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/develop/scripts/99-k4a.rules
sudo mv 99-k4a.rules /etc/udev/rules.d/

curl -L https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o "$HOME/miniconda3_latest.sh"
chmod +x $HOME/miniconda3_latest.sh
$HOME/miniconda3_latest.sh
```

```
sudo apt-add-repository -y -n 'deb http://archive.ubuntu.com/ubuntu focal main'
sudo apt-add-repository -y 'deb http://archive.ubuntu.com/ubuntu focal universe'
sudo apt-get install -y libsoundio1
sudo apt-add-repository -r -y -n 'deb http://archive.ubuntu.com/ubuntu focal universe'
sudo apt-add-repository -r -y 'deb http://archive.ubuntu.com/ubuntu focal main'

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.3/libk4a1.3_1.3.0_amd64.deb > /tmp/libk4a1.3_1.3.0_amd64.deb
echo 'libk4a1.3 libk4a1.3/accepted-eula-hash string 0f5d5c5de396e4fee4c0753a21fee0c1ed726cf0316204edda484f08cb266d76' | sudo debconf-set-selections
sudo dpkg -i /tmp/libk4a1.3_1.3.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.3-dev/libk4a1.3-dev_1.3.0_amd64.deb > /tmp/libk4a1.3-dev_1.3.0_amd64.deb
sudo dpkg -i /tmp/libk4a1.3-dev_1.3.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4abt1.0/libk4abt1.0_1.0.0_amd64.deb > /tmp/libk4abt1.0_1.0.0_amd64.deb
echo 'libk4abt1.0	libk4abt1.0/accepted-eula-hash	string	03a13b63730639eeb6626d24fd45cf25131ee8e8e0df3f1b63f552269b176e38' | sudo debconf-set-selections
sudo dpkg -i /tmp/libk4abt1.0_1.0.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4abt1.0-dev/libk4abt1.0-dev_1.0.0_amd64.deb > /tmp/libk4abt1.0-dev_1.0.0_amd64.deb
sudo dpkg -i /tmp/libk4abt1.0-dev_1.0.0_amd64.deb

curl -sSL https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/k/k4a-tools/k4a-tools_1.3.0_amd64.deb > /tmp/k4a-tools_1.3.0_amd64.deb
sudo dpkg -i /tmp/k4a-tools_1.3.0_amd64.deb
```
