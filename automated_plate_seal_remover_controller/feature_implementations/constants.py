from typing import Dict

"""Definitions of the error codes returned by the instrument."""
NO_ERROR = 0
CONVEYOR_MOTOR_STALLED = 1
ELEVATOR_MOTOR_STALLED = 2
TAKE_UP_SPOOL_STALLED = 3
SEAL_NOT_REMOVED = 4
ILLEGAL_COMMAND = 5
NO_PLATE_FOUND = 6
OUT_OF_TAPE = 7
PARAMETERS_NOT_SAVED = 8
STOP_BUTTON_PRESSED = 9
SEAL_SENSOR_UNPLUGGED = 10
SEALS_LOW_ON_THE_ROLL = 20
TAKE_UP_SPOOL_SPACE_LOW = 21
EMERGENCY_STOP = 51
CIRCUITRY_FAULT = 52

"""Error messages for the error codes returned by the instrument."""
ERROR_MESSAGES: Dict[int, str] = {
    NO_ERROR: "No error.",
    CONVEYOR_MOTOR_STALLED: "Conveyor motor stalled.",
    ELEVATOR_MOTOR_STALLED: "Elevator motor stalled.",
    TAKE_UP_SPOOL_STALLED: "Take up spool stalled.",
    SEAL_NOT_REMOVED: "Seal not removed.",
    ILLEGAL_COMMAND: "Illegal command executed. Please contact the SiLA Server developer.",
    NO_PLATE_FOUND: "No plate found.",
    OUT_OF_TAPE: "Out of tape, or tape broke.",
    PARAMETERS_NOT_SAVED: "Parameters not saved.",
    STOP_BUTTON_PRESSED: "Stop button pressed while running.",
    SEAL_SENSOR_UNPLUGGED: "Seal Sensor unplugged or broke.",
    SEALS_LOW_ON_THE_ROLL: "Less than 30 seals left on the supply roll.",
    TAKE_UP_SPOOL_SPACE_LOW: "Room for less than 30 seals on take up spool.",
    EMERGENCY_STOP: "Emergency Stop: Close the cover. If it is already closed, contact the manufacturer as there may be a hardware malfunction.",
    CIRCUITRY_FAULT: "Circuitry Fault Detected: Remove power."
}

"""Error codes treated as instrument warnings."""
WARNING_CODES: list[int] = [
    SEALS_LOW_ON_THE_ROLL,
    TAKE_UP_SPOOL_SPACE_LOW
]