# Process states
IDLE = 0
COORDINATOR = 1
WAITING_FOR_OK = 2
ELECTING = 3
DEAD = 4
WAITING_FOR_COORDINATOR = 5

# Message types
ELECTION = 2
OK = 3
I_AM_COORDINATOR = 1
YOU_ARE_COORDINATOR = 4

# Time interval for becoming coordinator
THRESHOLD = 2
