# Automated Plate Seal Remover Controller

A Python SiLA Server for controlling the Automated Plate Seal Remover (formerly known as Xpeel) made by Azenta Life Sciences.  

## About

This server allows you to control the Automated Plate Seal Remover using the following features.  

* Commands
  * Peel
  * GetTapeLeft
  * ResetInstrument
  * Reset
* Property
  * Status

## Command Details

### Peel

Peel the seal attached to the plate.

#### Parameters

| Identifier | Type | Description |
| -- | -- | -- |
| BeginPeelLocation | Integer | Parameter for the beginning location and peeling speed.<br><br>1: Default -2 mm / fast<br>2: Default -2 mm / slow<br>3: Default / fast<br>4: Default / slow<br>5: Default +2 mm / fast<br>6: Default +2 mm / slow<br>7: Default +4 mm / fast<br>8: Default +4 mm / slow<br>9: custom / custom |
| AdhesionTime | Integer | Adhesion time between the peeler and the seal.<br><br>1: 2.5 seconds<br>2: 5.0 seconds<br>3: 7.5 seconds<br>4: 10.0 seconds |

#### Response

| Identifier | Type | Description |
| -- | -- | -- |
| InstrumentWarningMessage | String |  Warning message corresponded to the error code returned by the instrument.<br>If there is no error code that indicates an instrument warning<br>(i.e., all error codes indicate "No error" or non-warning error),<br>the empty string will be returned. |

#### Status condition

* Status required to execute this command: Idle
* Status while this command is running: Running
* Status after this command finishes
  * If it completes normally: Idle
  * If an error occurs: Error

#### Remarks

Depending on the plate and the specified parameters, the instrument may return an error even if the seal is successfully removed.  
Please try different parameters to find a combination that allows the result to be recognized correctly.

### GetTapeLeft

Get the amount of tape left on the supply spool and the available capacity on the take-up spool.

#### Parameters

None.

#### Response

| Identifier | Type | Description |
| -- | -- | -- |
| SupplySpoolRemaining | Integer | The number of seal removals remaining on the supply spool. |
| TakeUpSpoolRemaining | Integer | The number of seal removals that can be accommodated by the remaining space on the take-up spool. |
| InstrumentWarningMessage | String |  Warning message corresponded to the error code returned by the instrument.<br>If there is no error code that indicates an instrument warning<br>(i.e., all error codes indicate "No error" or non-warning error),<br>the empty string will be returned. |

#### Status condition

* Status required to execute this command: Idle
* Status while this command is running: Same as the status at the start of execution
* Status after this command finishes
  * If it completes normally: Same as the status at the start of execution
  * If an error occurs: Error

### ResetInstrument

Move the spool forward a few inches to access fresh tape, return the elevator and conveyor to their home positions, and prepare the plate for pickup. Variables such as error codes and remaining tape information will be preserved.

#### Parameters

None.

#### Response

| Identifier | Type | Description |
| -- | -- | -- |
| InstrumentWarningMessage | String |  Warning message corresponded to the error code returned by the instrument.<br>If there is no error code that indicates an instrument warning<br>(i.e., all error codes indicate "No error" or non-warning error),<br>the empty string will be returned. |

#### Status condition

* Status required to execute this command: Idle
* Status while this command is running: Running
* Status after this command finishes
  * If it completes normally: Idle
  * If an error occurs: Error

### Reset

Reset the server to its Idle state. This command is common to all instruments.

#### Parameters

None.

#### Response

| Identifier | Type | Description |
| -- | -- | -- |
| InstrumentWarningMessage | String |  Warning message corresponded to the error code returned by the instrument.<br>If there is no error code that indicates an instrument warning<br>(i.e., all error codes indicate "No error" or non-warning error),<br>the empty string will be returned. |

#### Status condition

* Status required to execute this command: Idle, Error
* Status while this command is running: Same as the status at the start of execution
* Status after this command finishes
  * If it completes normally: Idle
  * If an error occurs: Error

## Property Details

### Status

Returns the status of the instrument. This property is common to all instruments.  

* 0: Not Connected  
* 1: Idle  
* 2: Running  
* 3: Error  

## Getting Started

### Cabling

Use a USB-to-serial (RS-232) conversion cable to connect the PC running this server to the Automated Plate Seal Remover.

### Prerequisites

* Python 3.10 or later

### Installation

1. Create/Activate a virtual environment

    In the directory where you checked out this repository, run the following commands to create and activate a virtual environment.  

    ```sh
    python -m venv venv
    source ./venv/bin/activate
    ```

2. Install packages

    Run the following commands to install the packages required to launch the SiLA Server.  

    ```sh
    pip install -r requirements.txt
    ```

3. Install SiLA Server

    Install the SiLA Server itself as a module.  

    ```sh
    pip install .
    ```

### Usage

Configure the settings required for running the application. The parameters are stored in `config.ini`.

In `app.env`, the launch parameters used when starting the application via `launch.sh` are stored. Edit `app.env` according to the environment in which the application will be launched.  
Once you finish editing `app.env`, run `launch.sh` to start the SiLA Server. If a `Permission denied` message appears, run the following command.

```sh
chmod +x launch.sh
```

## Launching in WSL2

When you run the SiLA Server in WSL, you must make the USB port used to connect the instrument visible to WSL. Follow the procedure described in "USB Passthrough" to configure this.  
Additionally, if you need to send requests from other PCs on the same network, you must configure Windows (Host OS) so that requests can be received by WSL (Guest OS). Configure this by following "Setting Up Request Routing from Windows to WSL".

### USB Passthrough

When you connect the instrument to the PC using a USB-to-serial (RS-232) conversion cable, the instrument is recognized only by Windows (Host OS). If you run the SiLA Server in WSL, the server cannot detect or communicate with the instrument unless USB passthrough is configured. The following procedure describes how to perform USB passthrough from Windows (host) to WSL (guest) using usbipd-win.

Note:
  While USB passthrough is active, the instrument will no longer be detected by Windows. If you need Windows to recognize the instrument again, perform the operation described in "Detach from WSL".

#### Setup usbipd-win

Follow the procedure in this chapter only the first time.  

1. (Operate on Windows) Install usbipd-win

    Launch PowerShell as Administrator and run the following command:

    ```ps1
    winget install --interactive --exact dorssel.usbipd-win
    ```

2. (Operate on Windows) Check device information

    Open "Device Manager" -> "Ports (COM & LPT)" and identify the port used by the instrument.  
    Right-click the device -> "Properties" -> "Details" tab, then select "Device instance bus" from the dropdown menu.  
    Make note of the VID and PID shown in the "Value" field.  

3. (Operate on Windows) Bind the instrument

    Launch Powershell as Administrator. If you kept PowerShell open, close it and reopen it as Administrator so that usbipd-win is available.  
    Run the following command to list device BUSIDs. Using the VID and PID from step 2, identify the corresponding device:  

    ```ps1
    usbipd list
    ```

    Next, bind the device to usbipd-win using the following commands.  

    ```ps1
    usbipd bind --busid <BUSID>
    ```

#### Attach to WSL

Follow the procedure in this chapter every time you configure USB passthrough.

1. (Operate on Windows) Check device information

    Open "Device Manager" -> "Ports (COM & LPT)" and identify the port used by the instrument.  
    Right-click the device -> "Properties" -> "Details" tab, then select "Device instance bus" from the dropdown menu.  
    Make note of the VID and PID shown in the "Value" field.  

2. (Operate on Windows) Attach the instrument to WSL

    Launch Powershell and run the following command to list device BUSIDs.  
    Using the VID and PID from step 1, identify the corresponding device:  

    ```ps1
    usbipd list
    ```

    Next, attach the device to WSL using the following command.  

    ```ps1
    usbipd attach --wsl --busid <BUSID>
    ```

3. (Operate on WSL) Check the passthrough virtual serial port

    Run the following commands to confirm the virtual serial port.  
    A name such as `ttyUSB0` will appear, so make note of it.

    ```ps1
    lsusb
    dmesg | grep -i tty
    ```

4. (Operate on WSL) Communicate using the passthrough virtual serial port

    Set the virtual serial port name (e.g., `ttyUSB0`) to the `name` parameter in the `COMPORT` section of config.ini.  
    After doing so, start the SiLA Server to establish communication.  

    Note:
      Be sure to specify the full path (e.g., `/dev/ttyUSB0`).

#### Detach from WSL

1. (Operate on Windows) Detach the instrument from WSL

    Launch Powershell and run the following command:

    ```ps1
    usbipd detach --busid <BUSID>
    ```

### Setting Up Request Routing from Windows to WSL

When you need to send requests from other PCs on the same network, you must configure Windows (Host OS) so that requests can be received by WSL (Guest OS).  
In this chapter, two methods are described for applying the above configuration. Follow either one of the procedures.  

#### Enabling WSL Mirrored Mode

WSL Mirrored Mode is a feature that allows WSL2 to share the same network and use the same IP address as Windows. You can enable WSL Mirrored Mode by following the procedure below.  

1. Open the "WSL Settings" on the machine where the SiLA Server will run.
2. Select "Network" from the menu on the left side of the window.
3. Configure as follows:

    * Network mode: Mirrored
    * Host address loopback: ON

4. Restart WSL.

    Open a Command Prompt and run the following command.

    ```cmd
    wsl --shutdown
    ```

5. Run the SiLA Server with the following configuration:

    * IP_ADDRESS: 0.0.0.0

#### Windows -> WSL Port Forwarding Setup

The following procedure allows you to forward traffic sent to a specified port on Windows to WSL.

1. Launch PowerShell as Administrator.
2. Configure inbound and outbound firewall exception rules for the specified port number.

    run the following commands.

    ```ps1
    New-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock' -Direction Outbound -RemoteAddress LocalSubnet -LocalPort <Port Number> -Action Allow -Protocol TCP
    New-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock' -Direction Inbound -RemoteAddress LocalSubnet -LocalPort <Port Number> -Action Allow -Protocol TCP
    ```

3. Allow connections via IP address to the specified port number.

    run the following commands.

    ```ps1
    netsh interface portproxy add v4tov4 listenport=<Port Number> listenaddress=* connectport=<Port Number> connectaddress=<WSL2 IP Address>
    ```

Note: Remove the firewall exception rules when they are no longer needed by executing the following command.

```ps1
Remove-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock'
netsh interface portproxy delete v4tov4 listenport=<Port Number> listenaddress=*
```
#### Encryption

You can configure whether to enable TLS.  

If you want to enable it, follow the procedure below:
- Set the items in app.env to the values as follows:
  - ENABLE_TLS: TRUE
  - CERT_FILE: Public key path
  - PRIVATE_KEY: Private key path 
- If the software is already running, quit it and relaunch it

Note:
- The file names and paths of the public and private keys are not restricted.
- For other certificate requirements, refer to the SiLA2 Documentation (especially *Encryption* in Part B).

If you want to disable it (i.e., run the SiLA Server in insecure mode), follow the procedure below:
- Set "ENABLE_TLS" in app.env to FALSE
- If the software is already running, quit it and relaunch it

### Sample Scripts

You can find a simple script at `automated_plate_seal_remover_controller/examples/snip_xpeel.py` that can be used to verify the basic operation of this software. The script contains example usage for each command and property. To test a specific command or property, follow the procedure below:
- Copy and paste the corresponding region from the script into your own script. Make sure your script is placed in the same directory as snip_xpeel.py
- Set "host", "port", and "cert_path" in  `automated_plate_seal_remover_controller/examples/snip_xpeel.py`
- Activate a virtual environment
- Run your script