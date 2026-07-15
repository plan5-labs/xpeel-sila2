import time
import sys
import yaml

from pathlib import Path

from automated_plate_seal_remover_controller import Client as XpeelClient
from automated_plate_seal_remover_controller.generated.automatedplatesealremovercontroller.automatedplatesealremovercontroller_errors import SerialCommunicationError, UnexpectedReturnValue, InvalidInstrumentStatusError, InstrumentErrorDetected

with open("config.yml", 'r') as file:
    config = yaml.safe_load(file)

host, port, cert = config["Xpeel"]["host"], config["Xpeel"]["port"], config["Xpeel"]["cert_path"]
print(f"Connect to Xpeel Server. host: {host} port: {port} cert file: {cert}")
xpeel_client = XpeelClient(host, port, root_certs=Path(cert).read_bytes())

# region peel command
print("Peel command start!")
peel_instance = xpeel_client.AutomatedPlateSealRemoverController.Peel(4, 1)
while not peel_instance.done:
    time.sleep(1)
    print("peel command is still running...")
print("Peel command complete!")

try:
    peel_warning = peel_instance.get_responses()
    print("Peel succeeded.")
    if peel_warning.InstrumentWarningMessage:
        print(f"Warning message: {peel_warning.InstrumentWarningMessage}")
except SerialCommunicationError:
    print("Serial Communication between Server and the instrument failed.")
    sys.exit()
except UnexpectedReturnValue:
    print("Unexpected value returned from the instrument.")
    sys.exit()
except InvalidInstrumentStatusError:
    print("Invalid status.")
    sys.exit()
except InstrumentErrorDetected:
    print("Instrument detected. Please confirm the instrument state.")
    sys.exit()
except:
    print("Undefined error occurred.")
    sys.exit()
#endregion

# region GetTapeLeft command
print("GetTapeLeft command start!")
get_tape_left_instance = xpeel_client.AutomatedPlateSealRemoverController.GetTapeLeft()
while not get_tape_left_instance.done:
    time.sleep(1)
    print("GetTapeLeft command is still running...")
print("GetTapeLeft command complete!")

try:
    supply_spool_remaining, takeup_spool_remaining, get_tape_left_warning = get_tape_left_instance.get_responses()
    print(f"GetTapeLeft succeeded. Supply spool: {supply_spool_remaining} Takeup Spool: {takeup_spool_remaining}")
    if get_tape_left_warning:
        print(f"Warning message: {get_tape_left_warning}")
except SerialCommunicationError:
    print("Serial Communication between Server and the instrument failed.")
    sys.exit()
except UnexpectedReturnValue:
    print("Unexpected value returned from the instrument.")
    sys.exit()
except InvalidInstrumentStatusError:
    print("Invalid status.")
    sys.exit()
except InstrumentErrorDetected:
    print("Instrument detected. Please confirm the instrument state.")
    sys.exit()
except:
    print("Undefined error occurred.")
    sys.exit()
# endregion

#region ResetInstrument command
xpeel_client.AutomatedPlateSealRemoverController.ResetInstrument()

print("ResetInstrument command start!")
reset_instrument_instance = xpeel_client.AutomatedPlateSealRemoverController.ResetInstrument()
while not reset_instrument_instance.done:
    time.sleep(1)
    print("ResetInstrument command is still running...")
print("ResetInstrument command complete!")

try:
    reset_instrument_warning = reset_instrument_instance.get_responses().InstrumentWarningMessage
    print("ResetInstrument succeeded.")
    if reset_instrument_warning:
        print(f"Warning message: {reset_instrument_warning}")
except SerialCommunicationError:
    print("Serial Communication between Server and the instrument failed.")
    sys.exit()
except UnexpectedReturnValue:
    print("Unexpected value returned from the instrument.")
    sys.exit()
except InvalidInstrumentStatusError:
    print("Invalid status.")
    sys.exit()
except InstrumentErrorDetected:
    print("Instrument detected. Please confirm the instrument state.")
    sys.exit()
except:
    print("Undefined error occurred.")
    sys.exit()
#endregion

# region reset command
print("Reset command start!")
reset_instance = xpeel_client.AutomatedPlateSealRemoverController.Reset()
while not reset_instance.done:
    time.sleep(1)
    print("Reset command is still running...")
print("Reset command complete!")

try:
    reset_warning = reset_instance.get_responses().InstrumentWarningMessage
    print("Reset succeeded.")
    if reset_warning:
        print(f"Warning message: {reset_warning}")
except SerialCommunicationError:
    print("Serial Communication between Server and the instrument failed.")
    sys.exit()
except UnexpectedReturnValue:
    print("Unexpected value returned from the instrument.")
    sys.exit()
except InvalidInstrumentStatusError:
    print("Invalid status.")
    sys.exit()
except InstrumentErrorDetected:
    print("Instrument detected. Please confirm the instrument state.")
    sys.exit()
except:
    print("Undefined error occurred.")
    sys.exit()
#endregion

#region Status property
print("Subscribe Status property start.")
print(f"Current status: {xpeel_client.AutomatedPlateSealRemoverController.Status.get()}")
status_subscription = xpeel_client.AutomatedPlateSealRemoverController.Status.subscribe()

print("New status:")
status_subscription.add_callback(print)

time.sleep(5)

status_subscription.cancel()
print("Subscribe Status property complete.")
#endregion
