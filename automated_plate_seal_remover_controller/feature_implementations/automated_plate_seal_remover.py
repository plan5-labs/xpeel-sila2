# -*- coding: utf-8 -*-
"""The module of the implementations of automated plate seal remover features."""
import configparser
from logging import getLogger
import re

from distutils.util import strtobool

from .comport import COMPort
from .constants import NO_ERROR, ERROR_MESSAGES, WARNING_CODES

from ..generated.automatedplatesealremovercontroller import (
    SerialCommunicationError,
    UnexpectedReturnValue,
    InstrumentErrorDetected
)

logger = getLogger("automated_plate_seal_remover_controller")

class AutomatedPlateSealRemover:
    def __init__(self, app_config: configparser.ConfigParser):
        self.app_config = app_config
        self.treat_warnings_as_errors = strtobool(self.app_config["APPLICATION"]["treat_warnings_as_errors"])

    def connect(self):
        """Connect to the instrument."""
        self.com_port = COMPort(self.app_config)
        self.com_port.start()

    def request_xpeel(self, begin_peel_location: int, adhesion_time: int) -> str:
        """Remove seal

        Send an "xpeel" request to the instrument and wait for an acknowledgement and then the response.

        Args:
            begin_peel_location (int): Parameters for the beginning location and peeling speed. Specified from 1 to 9.
            adhesion_time (int): Adhesion time between the peeler and the seal. Specified from 1 to 4.

        Returns:
            str: Warning message for the error code included in the completion response.

        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
            UnexpectedReturnValue: Received unexpected return value from the instrument.
            InstrumentErrorDetected: Received any error codes from the instrument.
        """
        logger.info("Start \"xpeel\" command.")

        # Send a request.
        send_str = f"*xpeel:{begin_peel_location}{adhesion_time}\r\n"
        self.com_port.send(send_str)

        # Receive Acknowledgement.
        self.receive_and_check_message("*ack")

        warning_msg = self.receive_completion_response("xpeel")

        logger.info("Complete \"xpeel\" command.")
        return warning_msg

    def request_tapeleft(self) -> tuple[int, int, str]:
        """Get the tape left

        Send a "tapeleft" request to the instrument and return the remaining tape value.
        This process wait until the "ready" response is received.

        Returns:
            Tuple: 
            * int: The number of seal removals remaining on the supply spool.
            * int: The number of seal removals that can be accommodated
                    by the remaining space on the take-up spool.
            * str: Warning message for the error code included in the completion response.

        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
            UnexpectedReturnValue: Received unexpected return value from the instrument.
            InstrumentErrorDetected: Received any error codes from the instrument.
        """
        logger.info("Start \"tapeleft\" command.")

        # Send a request.
        self.com_port.send(f"*tapeleft\r\n")

        # Receive Acknowledgement.
        self.receive_and_check_message("*ack")
        
        # Get the response.
        tape_str = self.com_port.get_received_message()
        logger.info(f"Response to the \"tapeleft\" request: \"{tape_str}\"")
        if len(tape_str) <= 0:
            error_msg = "No response to the \"tapeleft\" request received."
            logger.error(error_msg)
            raise SerialCommunicationError(error_msg)
        tape_pattern = r"^\*tape:\d{2},\d{2}$"
        # Remove leading and trailing whitespace and line breaks before comparing.
        if re.fullmatch(tape_pattern, tape_str.strip(), flags=0) is not None:
            m = re.findall(r"\d+", tape_str)
            supply_spool_remaining: int = int(m[0]) * 10
            take_up_spool_remaining: int = int(m[1]) * 10
            logger.info(f"Supply spool remaining: {supply_spool_remaining}, Take up spool remaining: {take_up_spool_remaining}")
        else:
            error_msg = "The format of the response to the \"tapeleft\" request is invalid."
            logger.error(error_msg)
            raise UnexpectedReturnValue(error_msg)

        warning_msg = self.receive_completion_response("tapeleft")

        logger.info("Complete \"tapeleft\" command.")
        return supply_spool_remaining, take_up_spool_remaining, warning_msg

    def request_reset(self) -> str:
        """Reset

        Send a "reset" request to the instrument, and wait for an acknowledgement and then the response.

        Returns:
            str: Warning message for the error code included in the completion response.

        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
            UnexpectedReturnValue: Received unexpected return value from the instrument.
            InstrumentErrorDetected: Received any error codes from the instrument.
        """
        logger.info("Start \"reset\" command.")

        # Send a request.
        self.com_port.send(f"*reset\r\n")

        # Receive Acknowledgement.
        self.receive_and_check_message("*ack")

        # Get the "homing" message.
        # Although it is not documented, the "homing" response is sent after acknowledgement.
        self.receive_and_check_message("*homing")

        warning_msg = self.receive_completion_response("reset")

        logger.info("Complete \"reset\" command.")
        return warning_msg

    def request_restart(self) -> str:
        """Send "restart" request.

        Send a "restart" request to the instrument, and wait until an Acknowledgement and Response are received.

        Returns:
            str: Warning message for the error code included in the completion response.

        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
            UnexpectedReturnValue: Received unexpected return value from the instrument.
            InstrumentErrorDetected: Received any error codes from the instrument.
        """
        logger.info("Start \"restart\" command.")

        # Send a request.
        self.com_port.send(f"*restart\r\n")

        # The order of instrument responses in the manual is following:
        #   "ack" → "poweron" → "homing" → "ready"
        # In practice, "ack" and "poweron" responses were sent concurrently.
        self.receive_and_check_message("*ack\r\n*poweron")
        self.receive_and_check_message("*homing")
        warning_msg = self.receive_completion_response("restart")

        logger.info("Complete \"restart\" command.")
        return warning_msg

    def receive_and_check_message(self, expected_msg: str):
        """Receive the message and check it is valid

        Receive the message, and check whether it matches the expected value.

        Args:
            expected_msg (str): Expected message.

        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
            UnexpectedReturnValue: Received unexpected return value from the instrument.
        """
        received_str = self.com_port.get_received_message()
        logger.info(f"Expected msg: \"{expected_msg}\"")
        logger.info(f"Received msg: \"{received_str}\"")
        if len(received_str) <= 0:
            error_msg = "No response received."
            logger.error(error_msg)
            raise SerialCommunicationError(error_msg)

        # Remove any unexpected leading or trailing spaces/line breaks, then compare the strings.
        if self.normalize_newlines(received_str.strip()) != self.normalize_newlines(expected_msg):
            error_msg = f"The received message does not match the expected value."
            logger.error(error_msg)
            raise UnexpectedReturnValue(error_msg)

    def receive_completion_response(self, command_name: str) -> str:
        """Receive the command completion message

        Receive the command completion message from the instrument.

        Args:
            command_name (str): Executed command name.
        
        Returns:
            str: Message for the error code included in the completion response.
        
        Raises:
            SerialCommunicationError: Failed to perform serial communication with the instrument.
        """
        response_str = self.com_port.get_received_message()
        logger.info(f"Received msg: \"{response_str}\"")
        if len(response_str) <= 0:
            error_msg = f"The specified time has elapsed since the \"{command_name}\" request was sent, but no completion response has been received."
            logger.error(error_msg)
            raise SerialCommunicationError(error_msg)

        m = self.check_completion_response_format(response_str, command_name)
        # The leftmost code is the latest.
        msg = self.check_error_codes_of_the_completion_response(int(m.group(1)), int(m.group(2)), int(m.group(3)))

        return msg

    def check_completion_response_format(self, response: str, command_name: str) -> re.Match[str] | None:
        """Check the format of the completion response

        Check the format of the command completion response.

        Args:
            response (str): The response message to be checked.
            command_name (str): Executed command name.

        Returns:
            Match[str]: The match object between the response and the correct pattern.

        Raises:
            UnexpectedReturnValue: Received unexpected return value from the instrument.
        """
        # Error codes must only contain ASCII numeric characters.
        response_pattern = r'^\*ready:([0-9]{2}),([0-9]{2}),([0-9]{2})$'
        # Remove any unexpected leading or trailing spaces/line breaks, then compare the strings.
        m = re.fullmatch(response_pattern, response.strip())
        if not m:
            error_msg = f"The format of the completion response to the \"{command_name}\" request is invalid."
            logger.error(error_msg)
            raise UnexpectedReturnValue(error_msg)
        return m

    def check_error_codes_of_the_completion_response(self, *error_codes: int) -> str:
        """Check the error codes of the completion response

        Check the error codes included in the completion response.
        If any errors are detected, the exception for the latest error is raised.

        Args:
            error_codes (int): The error codes in descending order by time.
        
        Returns:
            str: Message for the error code if any errors detected.

        Raises:
            InstrumentErrorDetected: Received any error codes from the instrument.
        """
        ex: InstrumentErrorDetected | None = None
        latest_msg: str = ""
        # Check error codes in ASCENDING order by time.
        for code in reversed(error_codes):
            if code == NO_ERROR:
                continue
            elif self.is_instrument_warning(code):
                logger.warning(f"Instrument warning detected. Returned error code: {code}")
                msg = self.get_message_from_error_code(code)
                logger.warning(msg)
                if not self.treat_warnings_as_errors:
                    # Do not raise an exception for warnings in case of this setting.
                    latest_msg = msg
                    continue
                # Update the exception to be raised; only the exception corresponding to the latest error code will be raised.
                # Do not raise here; iterate all error codes and log them.
                ex = InstrumentErrorDetected(msg)
            else: # error
                logger.error(f"Instrument error detected. Returned error code: {code}")
                msg = self.get_message_from_error_code(code)
                logger.error(msg)
                # Update the exception to be raised; only the exception corresponding to the latest error code will be raised.
                # Do not raise here; iterate all error codes and log them.
                ex = InstrumentErrorDetected(msg)

        # Raise an exception if exists.
        if ex is not None:
            raise ex

        return latest_msg

    def is_instrument_warning(self, code: int) -> bool:
        return True if code in WARNING_CODES else False

    def get_message_from_error_code(self, code: int) -> str:
        """Return the message for the given error code.

        Return the error or warning message for the given error code returned by the instrument.

        Args:
            code (int): An error code returned from the instrument.

        Returns:
            str: An error or warning message.
        """
        try:
            return ERROR_MESSAGES[code]
        except KeyError:
            error_msg = f"Unexpected error code {code:02d} returned from the instrument."
            logger.error(error_msg)
            # Suppress the original KeyError to hide internal details.
            raise UnexpectedReturnValue(error_msg) from None

    def normalize_newlines(self, s: str) -> str:
        """Normalize newline codes.
        
        Normalize newline characters to LF to ensure string comparison ignores newline differences.
        
        Args:
            s (str): String to be normalized.
        
        Returns:
            str: Normalized string.
        """
        # Convert CRLF into LF
        s = s.replace('\r\n', '\n')
        # Convert CR into LF
        s = s.replace('\r', '\n')
        
        return s
