# from enum import Enum
# from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, Queue
# import time

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
        self.message_thread = Thread(target=self.state_machine, daemon=True)

        self.stop_worker = Event()
        self.message_queue = Queue()  # tuple[sender_id, type]
        self._id = _id
        self.state = ALIVE
        self.processes = []
        self.oks = 0
        self.coordinator_msg_sent = False

    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process"""
        self.state = DEAD
        print(f"{self._id} is dead \n")

    def get_id(self):
        """Get process id"""
        return self._id

    def get_process(self, _id):
        """Get process object by id"""
        return self.processes[_id]

    def enqueue_message(self, sender_id, msg_type):
        """Enqueue message to be processed by the state machine"""
        self.message_queue.put((sender_id, msg_type))

    def message_handler(self, process_id, msg_type):
        """"Receive message from another process"""
        if msg_type == ELECTION:
            if not self.state == DEAD:
                print(f"{self._id} received election from {process_id} \n")
                process = self.get_process(process_id)
                process.enqueue_message(self._id, OK)
                print(f"{self._id} sent OK to {process_id} \n")
                self.start_election()
        elif msg_type == OK:
            self.oks += 1
            print(
                f"{self._id} received OK from {process_id} and current oks is {self.oks} \n")

        elif msg_type == COORDINATOR:
            print(f"{self._id} received coordinator from {process_id} \n")

    def state_machine(self):
        """State machine for process"""
        while not self.stop_worker.is_set():
            try:
                process_id, msg_type = self.message_queue.get(timeout=1)

            except Empty:
                if self.state == ALIVE or self.state == DEAD:
                    pass
                elif self.state == COORDINATOR:
                    if not self.coordinator_msg_sent:
                        self.send_coordinator()
                elif self.state == WAITING_FOR_OK:
                    if self.oks > 0:
                        self.oks = 0
                        self.state = ALIVE
                    else:
                        self.send_coordinator()

                elif self.state == ELECTING:
                    self.start_election()

            else:
                self.message_handler(process_id, msg_type)

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        print(f"{self._id} sending coordinator to all processes \n")
        other_processes = [
            process for process in self.processes if process.get_id() != self._id]
        for process in other_processes:
            process.enqueue_message(self._id, COORDINATOR)
        self.coordinator_msg_sent = True
        self.state = COORDINATOR

    # Starts an election
    def start_election(self):
        """Send election msg to processes with higher id's"""
        higher_priority_processes = [
            process for process in self.processes if process.get_id() > self._id]
        for process in higher_priority_processes:
            print(f"{self._id} sending election to {process.get_id()} \n")
            process.enqueue_message(self._id, ELECTION)

        self.state = WAITING_FOR_OK


if __name__ == "__main__":
    # create N processes and put them in a list
    N = 5
    all_processes = []
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    # pass them as references to each process
    for i in range(N):
        all_processes[i].processes = all_processes

    # set process N as coordinator
    # all_processes[N-1].state = COORDINATOR

    # start all all_processes
    for p in all_processes:
        p.start_thread()

    # simulate a process dying and sending an election message
    # all_processes[4].kill()           # process 1 dies
    all_processes[0].start_election()  # process 2 starts election

    while True:
        pass
