import sys
sys.path.append('../')
from src.bully_improved import Process as ProcessImproved
from src.bully_orginal import Process as ProcessOriginal
import unittest


class SystemTests(unittest.TestCase):
    """Testing simulations of the bully algorithm"""

    def __init__(self, processes):
        self.processes = processes
        self.N = len(processes)

    def start_processes(self):
        """Start all processes"""
        for p in self.processes:
            p.start_thread()

    def test_election(self):
        """Test election"""
        # start election at highest priority process
        self.processes[self.N-1].start_election()

        # check that all processes have the correct state
        for i in range(self.N-1):
            self.assertEqual(self.processes[i].state, 0)
        self.assertEqual(self.processes[self.N-1].state, 1)

        # check that all processes have the correct message queue
        for i in range(self.N-1):
            self.assertEqual(self.processes[i].message_queue.get(),
                             (1, self.N-1))
    


# system test for 'bully_original.py'


# system test for 'bully_improved.py'
if __name__ == "__main__":

    N = 10
    processes_original = []
    processes_improved = []
    for i in range(N):
        processes_original.append(ProcessOriginal(i))
        processes_improved.append(ProcessImproved(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    for i in range(N):
        processes_original[i].processes = processes_original
        processes_improved[i].processes = processes_improved

    system_test_original = SystemTests(processes_original)
    system_test_improved = SystemTests(processes_improved)
