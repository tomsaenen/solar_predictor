#! python3

from colorama import init, Fore, Style
init(autoreset=True)

# Color bindings:
BLUE = Fore.CYAN
GREEN = Fore.GREEN
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW
YELLOW_BRIGHT = Fore.YELLOW + Style.BRIGHT

ORANGE = YELLOW # TODO: improve with package 'termcolor'

RESET = Style.RESET_ALL
