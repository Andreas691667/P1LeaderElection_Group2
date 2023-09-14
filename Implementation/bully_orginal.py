# from enum import Enum
# from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, Queue
import time

# Time interval for becoming coordinator
TIMEOUT = 2

# Process states
ALIVE = 0
COORDINATOR = 1
WAITING_FOR_OK = 2
ELECTING = 3
DEAD = 4


# Message types
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
        self.state = ALIVE
        self.processes = []
        self.oks = 0
        self.coordinater = False    #what is this for?
        self.coordinator_msg_sent = False

    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process"""
        self.coordinater = False
        self.state = DEAD

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
                if msg_type == ELECTION:
                    print(f"{self._id} received election from {process_id} \n")
                    if not self.state == DEAD:
                        process = self.get_process(process_id)
                        process.enqueue_message(self._id, OK)
                        print(f"{self._id} sent OK to {process_id} \n")
                        self.start_election()
                    elif msg_type == OK:
                        self.oks += 1
                        print(f"{self._id} received OK from {process_id}")

                    elif msg_type == COORDINATOR:
                        print(f"{self._id} received coordinator from {process_id}")

                    else:
                        pass

    def state_machine(self):
        """State machine for process"""
        while not self.stop_worker.is_set():
            if self.state == ALIVE:
                pass

            elif self.state == COORDINATOR:
                if not self.coordinator_msg_sent:
                    self.send_coordinator()

            elif self.state == WAITING_FOR_OK:
                start = time.time()
                while self.state == WAITING_FOR_OK and self.oks == 0:
                    end = time.time()
                    if end - start > TIMEOUT:
                        self.state = COORDINATOR
                        break

            elif self.state == ELECTING:
                self.start_election()

            elif self.state == DEAD:
                pass
            
            else:
                pass

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        print(f"{self._id} sending coordinator to all processes")
        for process in self.processes:
            process.enqueue_message(self._id, COORDINATOR)
        self.coordinator_msg_sent = True

    # Starts an election
    def start_election(self):
        """Send election msg to processes with higher id's"""
        for process in self.processes:
            if process.get_id() > self._id:
                print(f"{self._id} sending election to {process.get_id()}")
                process.enqueue_message(self._id, ELECTION)

        self.state = WAITING_FOR_OK

        # check for oks in a while loop for a maximum of TIMEOUT seconds
        # if no oks, send coordinator msg to all processes
        start = time.time()
        while self.oks == 0:
            end = time.time()
            if end - start > TIMEOUT:
                self.coordinater = True
                self.send_coordinator()
                break

        # if we received any oks, do nothing. somebody else took over
        # reset oks
        self.oks = 0

if __name__ == "__main__":
    # create N processes and put them in a list
    N = 3
    all_processes = []
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    # pass them as references to each process
    for i in range(N):
        all_processes[i].processes = all_processes

    # set process N as coordinator
    all_processes[N].state = COORDINATOR

    # start all all_processes
    for p in all_processes:
        p.start_thread()

    # simulate a process dying and sending an election message
    all_processes[2].kill()           # process 1 dies
    all_processes[0].start_election() # process 2 starts election

    while True:
        pass