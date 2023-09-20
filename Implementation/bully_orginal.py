# from enum import Enum
# from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, PriorityQueue
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
ELECTION = 2
OK = 3
COORDINATOR = 1


class Process:
    """Processes in the system"""
    def __init__(self, _id):
        self.message_thread = Thread(target=self.state_machine, daemon=True)
        self.stop_worker = Event()
        self.message_queue = PriorityQueue()  # tuple[sender_id, type]
        self._id = _id
        self.state = ALIVE  # initial state
        self.processes = []
        self.oks = 0
        self.coordinator_msg_sent = False
        self.msg_count = 0  # number of messages sent, metric for performance

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
            print(f"{self._id} received election from {process_id} \n")
            process = self.get_process(process_id)
            process.enqueue_message(self._id, OK)
            print(f"{self._id} sent OK to {process_id} \n")
            self.start_election()
        
        # respond to OK message by incrementing OK count and changing state (TODO: Should maybe not change here...)
        elif msg_type == OK and self.state == WAITING_FOR_OK:
            self.oks += 1
            print(
                f"{self._id} received OK from {process_id} and current oks is {self.oks} \n")
            self.state = ALIVE

        # accept coordinator message and do nothing
        elif msg_type == COORDINATOR:
            print(f"{self._id} received coordinator from {process_id} \n")

    def state_machine(self):
        """State machine for process. Worker method"""
        # try to get message from queue, if empty, check state and do something
        while not self.stop_worker.is_set():
            try:
                msg_type, process_id = self.message_queue.get(timeout=1)

            except Empty:
                # if state is ALIVE, do nothing
                if self.state == ALIVE:
                    pass
                # if state is COORDINATOR, send coordinator message to all processes if not already sent
                elif self.state == COORDINATOR:
                    if not self.coordinator_msg_sent:
                        self.send_coordinator()
                # if state is WAITING_FOR_OK, check if OK count is > 0, if so, change state to ALIVE, else send coordinator message
                # TODO: Maybe this is superfluous, since we change state to ALIVE when we receive OK message but this is not ideal
                elif self.state == WAITING_FOR_OK:
                    if self.oks > 0:
                        self.oks = 0
                        self.state = ALIVE
                    else:
                        self.send_coordinator()

                # if state is ELECTING, start election
                elif self.state == ELECTING:
                    self.start_election()

            # if message queue is not empty, handle message
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

    # start election at highest priority process
    all_processes[N-1].start_election()
    # wait for convergence
    time.sleep(2)
    # simulate process failure and new election
    all_processes[4].kill()           # process 2 dies
    time.sleep(2)
    all_processes[0].start_election()  # process 1 starts election

    # wait for 5 seconds and then stop all all_processes
    start = time.time()
    while True:
        time.sleep(.1)
        if time.time() - start > 5:
            break

    msg_count = 0
    for p in all_processes:
        msg_count += p.msg_count
        p.stop_worker.set()

    print(f"Total messages sent: {msg_count}")

    # while True:
    #     pass
