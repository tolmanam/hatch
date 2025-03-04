from __future__ import annotations

import os
import pickle
import sys
from typing import Any


class InvokedApplication:
    def display(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display', *args, **kwargs)

    def display_info(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_info', *args, **kwargs)

    def display_waiting(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_waiting', *args, **kwargs)

    def display_success(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_success', *args, **kwargs)

    def display_warning(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_warning', *args, **kwargs)

    def display_error(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_error', *args, **kwargs)

    def display_debug(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_debug', *args, **kwargs)

    def display_mini_header(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('display_mini_header', *args, **kwargs)

    def abort(self, *args: Any, **kwargs: Any) -> None:
        send_app_command('abort', *args, **kwargs)
        sys.exit(kwargs.get('code', 1))

    def get_safe_application(self) -> SafeApplication:
        return SafeApplication(self)


class Application:
    """
    The way output is displayed can be [configured](../config/hatch.md#terminal) by users.

    !!! important
        Never import this directly; Hatch judiciously decides if a type of plugin requires
        the capabilities herein and will grant access via an attribute.
    """

    def __init__(self) -> None:
        self.__verbosity = int(os.environ.get('HATCH_VERBOSE', '0')) - int(os.environ.get('HATCH_QUIET', '0'))

    def display(self, message: str = '', **kwargs: Any) -> None:
        # Do not document
        print(message)

    def display_info(self, message: str = '', **kwargs: Any) -> None:
        """
        Meant to be used for messages conveying basic information.
        """
        if self.__verbosity >= 0:
            print(message)

    def display_waiting(self, message: str = '', **kwargs: Any) -> None:
        """
        Meant to be used for messages shown before potentially time consuming operations.
        """
        if self.__verbosity >= 0:
            print(message)

    def display_success(self, message: str = '', **kwargs: Any) -> None:
        """
        Meant to be used for messages indicating some positive outcome.
        """
        if self.__verbosity >= 0:
            print(message)

    def display_warning(self, message: str = '', **kwargs: Any) -> None:
        """
        Meant to be used for messages conveying important information.
        """
        if self.__verbosity >= -1:
            print(message)

    def display_error(self, message: str = '', **kwargs: Any) -> None:
        """
        Meant to be used for messages indicating some unrecoverable error.
        """
        if self.__verbosity >= -2:
            print(message)

    def display_debug(self, message: str = '', level: int = 1, **kwargs: Any) -> None:
        """
        Meant to be used for messages that are not useful for most user experiences.
        The `level` option must be between 1 and 3 (inclusive).
        """
        if not 1 <= level <= 3:  # noqa: PLR2004
            error_message = 'Debug output can only have verbosity levels between 1 and 3 (inclusive)'
            raise ValueError(error_message)
        elif self.__verbosity >= level:
            print(message)

    def display_mini_header(self, message: str = '', **kwargs: Any) -> None:
        if self.__verbosity >= 0:
            print(f'[{message}]')

    def abort(self, message: str = '', code: int = 1, **kwargs: Any) -> None:
        """
        Terminate the program with the given return code.
        """
        if message and self.__verbosity >= -2:
            print(message)

        sys.exit(code)

    def get_safe_application(self) -> SafeApplication:
        return SafeApplication(self)


class SafeApplication:
    def __init__(self, app: InvokedApplication | Application) -> None:
        self.abort = app.abort
        self.display = app.display
        self.display_info = app.display_info
        self.display_error = app.display_error
        self.display_success = app.display_success
        self.display_waiting = app.display_waiting
        self.display_warning = app.display_warning
        self.display_debug = app.display_debug
        self.display_mini_header = app.display_mini_header


def format_app_command(method: str, *args: Any, **kwargs: Any) -> str:
    procedure = pickle.dumps((method, args, kwargs), 4)

    return f"__HATCH__:{''.join('%02x' % i for i in procedure)}"


def get_application(*, called_by_app: bool) -> InvokedApplication | Application:
    return InvokedApplication() if called_by_app else Application()


def send_app_command(method: str, *args: Any, **kwargs: Any) -> None:
    _send_app_command(format_app_command(method, *args, **kwargs))


def _send_app_command(command: str) -> None:
    print(command)
