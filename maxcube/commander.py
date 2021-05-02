import base64
import logging
from time import sleep
from typing import List

from .connection import Connection
from .deadline import Deadline, Timeout
from .message import Message

logger = logging.getLogger(__name__)

QUIT_MSG = Message("q")
L_MSG = Message("l")
L_REPLY_CMD = L_MSG.reply_cmd()

UPDATE_TIMEOUT = Timeout("update", 3.0)
CONNECT_TIMEOUT = Timeout("connect", 3.0)
FLUSH_INPUT_TIMEOUT = Timeout("flush-input", 0)
SEND_RADIO_MSG_TIMEOUT = Timeout("send-radio-msg", 30.0)
CMD_REPLY_TIMEOUT = Timeout("cmd-reply", 2.0)


class Commander(object):
    def __init__(self, host: str, port: int):
        self.__host: str = host
        self.__port: int = port
        self.use_persistent_connection = True
        self.__connection: Connection = None
        self.__unsolicited_messages: List[Message] = []

    def disconnect(self):
        if self.__connection:
            try:
                self.__connection.send(QUIT_MSG)
            except Exception:
                logger.debug(
                    "Unable to properly shutdown MAX Cube connection. Resetting it..."
                )
            finally:
                self.__close()

    def get_unsolicited_messages(self) -> List[Message]:
        result = self.__unsolicited_messages
        self.__unsolicited_messages = []
        return result

    def update(self) -> List[Message]:
        deadline = Deadline(UPDATE_TIMEOUT)
        if self.__is_connected():
            try:
                response = self.__call(L_MSG, deadline)
                if response:
                    self.__unsolicited_messages.append(response)
            except Exception:
                self.__connect(deadline)
        else:
            self.__connect(deadline)
        if not self.use_persistent_connection:
            self.disconnect()
        return self.get_unsolicited_messages()

    def send_radio_msg(self, hex_radio_msg: str) -> bool:
        deadline = Deadline(SEND_RADIO_MSG_TIMEOUT)
        request = Message(
            "s", base64.b64encode(bytearray.fromhex(hex_radio_msg)).decode("utf-8")
        )
        while not deadline.is_expired():
            if self.__cmd_send_radio_msg(request, deadline):
                return True
        return False

    def __cmd_send_radio_msg(self, request: Message, deadline: Deadline) -> bool:
        try:
            response = self.__call(request, deadline)
            duty_cycle, status_code, free_slots = response.arg.split(",", 3)
            if status_code == "0":
                return True
            logger.debug(
                "Radio message %s was not send [DutyCycle:%s, StatusCode:%s, FreeSlots:%s]"
                % (request, duty_cycle, status_code, free_slots)
            )
            if int(duty_cycle, 16) == 100 and int(free_slots, 16) == 0:
                sleep(deadline.remaining(upper_bound=10.0))
        except Exception as ex:
            logger.error("Error sending radio message to Max! Cube: " + str(ex))
        return False

    def __call(self, msg: Message, deadline: Deadline) -> Message:
        already_connected = self.__is_connected()
        if not already_connected:
            self.__connect(deadline.subtimeout(CONNECT_TIMEOUT))
        else:
            # Protection in case some late answer arrives for a previous command
            self.__wait_for_reply(None, deadline.subtimeout(FLUSH_INPUT_TIMEOUT))

        try:
            self.__connection.send(msg)
            subdeadline = deadline.subtimeout(CMD_REPLY_TIMEOUT)
            result = self.__wait_for_reply(msg.reply_cmd(), subdeadline)
            if result is None:
                raise TimeoutError(str(subdeadline))
            return result

        except Exception:
            self.__close()
            if already_connected:
                return self.__call(msg, deadline)
            else:
                raise

        finally:
            if not self.use_persistent_connection:
                self.disconnect()

    def __is_connected(self) -> bool:
        return self.__connection is not None

    def __connect(self, deadline: Deadline):
        self.__unsolicited_messages = []
        self.__connection = Connection(self.__host, self.__port)
        reply = self.__wait_for_reply(
            L_REPLY_CMD, deadline.subtimeout(CMD_REPLY_TIMEOUT)
        )
        if reply:
            self.__unsolicited_messages.append(reply)

    def __wait_for_reply(self, reply_cmd: str, deadline: Deadline) -> Message:
        while True:
            msg = self.__connection.recv(deadline)
            if msg is None:
                return None
            elif reply_cmd and msg.cmd == reply_cmd:
                return msg
            else:
                self.__unsolicited_messages.append(msg)

    def __close(self):
        self.__connection.close()
        self.__connection = None
