from enum import Enum
from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, Queue
import time


@dataclass
class ProcessStates(Enum):
    """states that processes can take on"""""
    ALIVE = 1
    DEAD = 2


@dataclass
class MessageTypes(Enum):
    """types of messages that can be sent"""
    ELECTION = 1
    OK = 2
    COORDINATOR = 3


class Process:
    """Processes in the system"""

    def __init__(self, _id):
        self.message_thread = Thread(target=self.message_handler, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()  # tuple[sender_id, type]

        self._id = _id
        self.state = ProcessStates.ALIVE
        self.processes = []
        self.oks = 0
        self.coordinater = False

    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process"""
        self.coordinater = False
        self.state = ProcessStates.DEAD

    def get_id(self):
        return self._id

    def get_process(self, _id):
        return self.processes[_id]

    def enqueue_message(self, sender_id, msg_type):
        self.message_queue.put((sender_id, msg_type))

    def message_handler(self):
        """"Receive message from another process"""
        # worker method for thread
        while not self.stop_worker.is_set():
            try:
                process_id, msg_type = self.message_queue.get(timeout=1)
            except Empty:
                pass
            else:
                match msg_type:
                    case MessageTypes.ELECTION:
                        print(f"{self._id} received election from {process_id} \n")
                        if not self.state == ProcessStates.DEAD:
                            process = self.get_process(process_id)
                            process.enqueue_message(self._id, MessageTypes.OK)
                            self.start_election()

                    case MessageTypes.OK:
                        self.oks = self.oks + 1
                        print(f"{self._id} received OK from {process_id}")

                    case MessageTypes.COORDINATOR:
                        print(
                            f"{self._id} received coordinator from {process_id}")

                    case _:
                        pass

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        for process in self.processes:
            process.enqueue_message(self._id, MessageTypes.COORDINATOR)

    # Starts an election
    def start_election(self):
        """Send election msg to processes with higher id's"""
        for process in self.processes:
            if process.get_id() > self._id:
                print(f"{self._id} sending election to {process.get_id()}")
                process.enqueue_message(self._id, MessageTypes.ELECTION)

        # Change state to waitForOks

        # check for oks in a while loop for a maximum of 5 seconds
        # if no oks, send coordinator msg to all processes
        start = time.time()
        while self.oks == 0:
            end = time.time()
            if end - start > 5:
                self.coordinater = True
                self.send_coordinator()
                break

        # if we received any oks, do nothing. somebody else took over
        # print(f"{self._id} received no oks")


if __name__ == "__main__":
    # create 5 processes and put them in a list
    N = 3
    all_processes = []
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    # pass them as references to each process
    for i in range(N):
        all_processes[i].processes = all_processes

    # start all all_processes
    for p in all_processes:
        p.start_thread()

    # simulate a process dying and sending an election message
    all_processes[2].kill()           # process 1 dies
    all_processes[0].start_election() # process 2 starts election

    while True:
        pass


# Implement messages/oks with a state machine for each process
