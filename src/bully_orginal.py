# from enum import Enum
# from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, Queue
from types_ import *
import time


class ProcessOriginal:
    """Processes in the system"""

    def __init__(self, _id):
        self.message_thread = Thread(target=self.state_machine, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()  # tuple[sender_id, type]
        self._id = _id
        self.state = NORMAL  # initial state
        self.processes = []
        self.oks = 0
        self.coordinator_msg_sent = False
        self.election_msg_sent = False
        self.msg_count = 0  # number of messages sent, metric for performance
        self.coordinator = None
        self.election_start_time = 0

    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process by setting state and stopiing worker thread"""
        self.state = DEAD
        self.stop_worker.set()

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
            process = self.get_process(process_id)
            process.enqueue_message(self._id, OK)
            if not self.election_msg_sent:
                self.start_election()
                self.election_msg_sent = True

        # respond to OK message by incrementing OK count
        elif msg_type == OK:
            self.oks += 1

        # accept coordinator message and do nothing
        elif msg_type == I_AM_COORDINATOR:
            self.state = NORMAL
            self.coordinator = process_id
            self.election_msg_sent = False

    def state_machine(self):
        """State machine for process. Worker method"""
        # try to get message from queue, if empty, check state and do something
        while not self.stop_worker.is_set():
            try:
                msg_type, process_id = self.message_queue.get(timeout=1)

            except Empty:
                # if state is NORMAL, do nothing
                if self.state == NORMAL or self.state == WAITING_FOR_COORDINATOR:
                    pass
                # if state is COORDINATOR, send coordinator message to all processes if not already sent
                elif self.state == COORDINATOR:
                    if not self.coordinator_msg_sent:
                        self.send_coordinator()
                # if state is WAITING_FOR_OK, check if OK count is > 0.
                # If so, change state to NORMAL, else send coordinator message
                elif self.state == WAITING_FOR_OK:
                    time_passed = time.time() - self.election_start_time
                    time_expired = time_passed > THRESHOLD

                    if self.oks > 0:
                        self.oks = 0
                        self.state = WAITING_FOR_COORDINATOR
                    elif time_expired:
                        self.send_coordinator()
                    else:
                        pass

            # if message queue is not empty, handle message
            else:
                self.message_handler(process_id, msg_type)

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        other_processes = [
            process for process in self.processes if process.get_id() != self._id]
        for process in other_processes:
            process.enqueue_message(self._id, I_AM_COORDINATOR)
        self.coordinator_msg_sent = True
        self.state = COORDINATOR

    # Starts an election
    def start_election(self):
        """Send election msg to processes with higher id's"""
        self.election_start_time = time.time()
        higher_priority_processes = [
            process for process in self.processes if process.get_id() > self._id]
        for process in higher_priority_processes:
            process.enqueue_message(self._id, ELECTION)

        self.election_msg_sent = True
        self.state = WAITING_FOR_OK