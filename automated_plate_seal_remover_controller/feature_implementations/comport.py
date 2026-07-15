# coding: utf-8
"""COM port module

Module for handling COM port
"""
import configparser
import threading
from logging import getLogger
from queue import Empty, Queue

import serial

logger = getLogger("automated_plate_seal_remover_controller")


class COMPort:
    def __init__(self, config: configparser.ConfigParser):
        """Initialize"""
        self.name = config["COMPORT"]["name"]
        self.baudrate = int(config["COMPORT"]["baudrate"])
        self.parity = config["COMPORT"]["parity"]
        self.bytesize = int(config["COMPORT"]["bytesize"])
        self.stopbits = int(config["COMPORT"]["stopbits"])
        self.timeout = int(config["COMPORT"]["timeout"])

    def start(self):
        """Start process

        Open the COM port and launch the message-receiving thread.
        """
        self.serial_port = serial.Serial(
            port=self.name,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout,
        )

        # Create the reading queue and launch the reading thread.
        self.read_queue = Queue()
        self.recv_thread = threading.Thread(target=self.__recv)
        self.recv_thread_canceled = False
        self.recv_thread.start()

    def send(self, message: str, reset_recv_buffer: bool = True):
        """Send a message

        Send a message over the COM port

        Args:
            message (str): The message string to send.
            reset_recv_buffer (bool): Whether to empty the reading queue before sending the message. If not specified, the default is True.
        """
        send_data = message.encode("ascii")
        if reset_recv_buffer:
            self.__clear_read_queue()
        self.serial_port.write(send_data)
        logger.debug(repr(f"Sent message : {message}"))

    def get_received_message(self):
        """Receive a message

        Get the latest message that is received from the COM port.
        If no messages have been received, wait until either a message arrives or the configured timeout is reached.
        If nothing is received within the timeout, return an empty string.
        """

        message = ""
        try:
            message = self.read_queue.get(True, self.timeout)
        except Empty as exc:
            logger.warning("Empty exception occurred.", exc_info=exc)
        return message

    def __recv(self):
        """Receive process

        Continue to enqueue messages received from the COM port into the reading queue.
        This method is expected to be called on another thread via the start method.
        """
        while not self.recv_thread_canceled:
            recv_data = self.serial_port.readline()
            if len(recv_data) > 0:
                recv_message = recv_data.decode(encoding="ascii")
                self.read_queue.put(recv_message)
                logger.debug(repr(f"Received message : {recv_message}"))

    def __clear_read_queue(self):
        """Clear the reading queue

        Clear the reading queue by reading all messages.
        """
        while not self.read_queue.empty():
            try:
                logger.debug(f"queue = {self.read_queue.queue}")
                self.read_queue.get(False)
            except Empty as exc:
                # Log the warning message just in case.
                logger.warning("Empty exception occurred.", exc_info=exc)
                return
