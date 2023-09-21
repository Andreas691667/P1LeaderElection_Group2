# from enum import Enum
# from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, PriorityQueue
import time

# Time interval for becoming coordinator
THRESHOLD = 2

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


class Process:
    """Processes in the system"""

    def __init__(self, _id):
        self.message_thread = Thread(target=self.state_machine, daemon=True)
        self.stop_worker = Event()
        self.message_queue = PriorityQueue()  # tuple[sender_id, type]
        self._id = _id
        self.state = IDLE  # initial state
        self.processes = []
        self.oks = []  # vector oks: Each entry is an id corresponding to a OK from that process
        self.coordinator_msg_sent = False
        self.election_msg_sent = False
        self.msg_count = 0  # number of messages sent, metric for performance
        # Improved bully attributes
        self.election_in_progess = False
        self.current_coordinator = 0
        self.election_start_time = 0

    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process by setting state and stopiing worker thread"""
        self.state = DEAD
        self.stop_worker.set()
        print(f"{self._id} is dead \n")

    def get_id(self):
        """Get process id"""
        return self._id

    def get_process(self, _id):
        """Get process object by id"""
        return self.processes[_id]

    def enqueue_message(self, sender_id, msg_type):
        """Enqueue message to be processed by the state machine"""
        self.msg_count += 1
        self.message_queue.put((msg_type, sender_id))

    def message_handler(self, process_id, msg_type):
        """"Handle message from another process"""
        # respond to election message by sending OK
        if msg_type == ELECTION:
            print(f"{self._id} received ELECTION from {process_id} \n")
            process = self.get_process(process_id)
            process.enqueue_message(self._id, OK)
            self.election_in_progess = True
            print(
                f"{self._id} sent OK to {process_id} and election is in progress: {self.election_in_progess} \n")

        # respond to OK message by incrementing OK count
        elif msg_type == OK:
            self.oks.append(process_id)
            if process_id > self.current_coordinator:
                self.current_coordinator = process_id
            print(
                f"{self._id} received OK from {process_id} and current oks is: {self.oks} \n")

        # accept coordinator message and do nothing
        elif msg_type == I_AM_COORDINATOR:
            print(f"{self._id} received I_AM_COORDINATOR from {process_id} \n")
            self.state = IDLE

        elif msg_type == YOU_ARE_COORDINATOR:
            print(f'{self._id} received YOU_ARE_COORDINATOR from {process_id} \n')
            self.current_coordinator = self._id
            self.start_election()

    def state_machine(self):
        """State machine for process. Worker method"""
        # try to get message from queue, if empty, check state and do something
        while not self.stop_worker.is_set():
            try:
                msg_type, process_id = self.message_queue.get(timeout=1)

            except Empty:
                # if state is IDLE, do nothing
                if self.state == IDLE or self.state == WAITING_FOR_COORDINATOR:
                    pass
                # if state is COORDINATOR, send coordinator message to all processes if not already sent
                elif self.state == COORDINATOR:
                    if not self.coordinator_msg_sent:
                        self.send_coordinator()
                # if state is WAITING_FOR_OK, check if OK count is > 0, if so, change state to IDLE, else send coordinator message
                # TODO: Maybe this is superfluous, since we change state to IDLE when we receive OK message but this is not ideal
                elif self.state == WAITING_FOR_OK:
                    # Threshold calculation
                    time_passed = time.time() - self.election_start_time
                    time_expired = time_passed > THRESHOLD

                    # Pick new coordinator
                    if len(self.oks) == len(self.processes)-self._id or time_expired:
                        self.oks.clear()

                        # if process has not received any oks, and time has expired, then itself becomes coordinator
                        if self.current_coordinator == -1:
                            print(f'{self._id} is taking over ')
                            self.current_coordinator = self._id
                            self.state = COORDINATOR

                        else:
                            # get the new coordinator object
                            new_coordinator = self.get_process(
                                self.current_coordinator)
                            # tell coordinator that it is the new coordinator
                            new_coordinator.enqueue_message(
                                self._id, YOU_ARE_COORDINATOR)
                            self.state = WAITING_FOR_COORDINATOR

            # if message queue is not empty, handle message
            else:
                self.message_handler(process_id, msg_type)

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        print(f"{self._id} sending coordinator to all processes \n")
        other_processes = [
            process for process in self.processes if process.get_id() != self._id]
        for process in other_processes:
            process.enqueue_message(self._id, I_AM_COORDINATOR)
        self.coordinator_msg_sent = True

    # Starts an election
    def start_election(self):
        """Send election msg to processes with higher id's"""
        self.election_start_time = time.time()
        self.current_coordinator = -1
        self.coordinator_msg_sent = False
        higher_priority_processes = [
            process for process in self.processes if process.get_id() > self._id]
        for process in higher_priority_processes:
            print(f"{self._id} sending ELECTION to {process.get_id()} \n")
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

    # start election at highest priority process
    # all_processes[N-1].start_election()

    # all_processes[N-1].state = COORDINATOR

    # wait for convergence
    # time.sleep(2)
    # simulate process failure and new election
    # all_processes[4].kill()           # process 2 dies
    # time.sleep(2)
    all_processes[0].start_election()  # process 1 starts election

    # wait for 5 seconds and then stop all all_processes
    start = time.sleep(10)

    msg_count = 0
    for p in all_processes:
        msg_count += p.msg_count
        p.stop_worker.set()

    print(f"Total messages sent: {msg_count}")