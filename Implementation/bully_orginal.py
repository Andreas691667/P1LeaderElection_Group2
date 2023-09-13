from enum import Enum
from dataclasses import dataclass
from threading import Event, Thread
from queue import Empty, Queue


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
        self.message_queue = Queue() # tuple[sender_id, type]
        
        self._id = _id
        self.state = ProcessStates.ALIVE
        self.processes = []
        self.oks = 0
        
    def start_thread(self):
        """Start the message handler thread"""
        self.message_thread.start()

    def kill(self):
        """Kill the process"""
        self.state = ProcessStates.DEAD
    
    def get_id(self):
        return self._id
    
    def get_process(self, _id):
        return self.processes[_id]
    
    def enqueue_message(self, sender_id, msg_type):
        self.message_queue.put((sender_id, msg_type))        
    
    def message_handler(self):
        """"Receive message from another process"""
        #worker method for thread
        while not self.stop_worker.is_set():
            try:
                process_id, msg_type = self.message_queue.get(timeout=1)
            except Empty:
                pass
            else:
                match msg_type:                     
                    case MessageTypes.ELECTION:
                        print(f"{self.get_id} received election from {process_id}")
                        process = self.get_process(process_id)
                        process.enqueue_message(self.get_id(), MessageTypes.OK)
                        self.start_election()

                    case MessageTypes.OK:
                        print(f"{self.get_id} received OK from {process_id}")
                        
                    case MessageTypes.COORDINATOR:
                        print(f"{self.get_id} received coordinator from {process_id}")

                    case _:
                        pass

    def send_coordinator(self):
        """Send coordinator message to all processes"""
        for process in self.processes:
            process.enqueue_message(self.get_id(), MessageTypes.COORDINATOR)

    # Starts an elec
    def start_election (self):
        # Send election msg to processes with higher id's
        for process in self.processes:
            if process.get_id() > self.get_id():
                process.enqueue_message(self.get_id, MessageTypes.ELECTION)
        
        # check for OKs
        # if no OKs, send coordinator msg to all processes
        if self.oks == 0:
            self.send_coordinator()
      
if __name__ == "__main__":
    #create 5 processes as threads and start them
    processes = []
    for i in range(5):
        processes.append(Process(i))

    # inform each process of all the other processes by adding them to the process list
    for i in range(5):
        processes[i].processes = processes
        
    
    for p in processes:
        p.start_thread()
    
    # simulate a process dying and sending an election message
    processes[2].kill()
    processes[2].enqueue_message(processes[2].get_id(), MessageTypes.ELECTION)

    while True:
        pass


# Implement messages/oks with a state machine for each process