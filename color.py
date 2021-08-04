#! python3

from colorama import init, Fore, Style
init(autoreset=True)

# Color bindings:
BLUE = Fore.CYAN # Really cyan on macOS
GREEN = Fore.GREEN
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW
YELLOW_BRIGHT = Fore.YELLOW + Style.BRIGHT # Bold on macOS?

ORANGE = YELLOW # TODO: improve with package 'termcolor'

RESET = Style.RESET_ALL
