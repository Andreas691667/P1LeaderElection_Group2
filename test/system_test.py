import sys
sys.path.insert(0, "./src")
from types_ import *
from time import sleep
import unittest
from bully_orginal import ProcessOriginal
from bully_improved import ProcessImproved

class SystemTestsOriginal(unittest.TestCase):
    """Testing simulations of the bully algorithm"""

    def setUp(self) -> None:
        self.N = 5 
        self.all_processes = []
        for i in range(self.N):
            self.all_processes.append(ProcessOriginal(i))

        # inform each process of all the other all_processes by adding them to the process list and remove self from list
        for i in range(self.N):
            self.all_processes[i].processes = self.all_processes

        # start processes
        for p in self.all_processes:
            p.start_thread()

    def tearDown(self) -> None:
        msg_count = 0
        for p in self.all_processes:
            msg_count += p.msg_count
            p.kill()
        print(f"Total messages sent in original: {msg_count}")

    def test_election(self):
        """Test election"""
        # start election at lowest priority process
        self.all_processes[0].start_election()

        # wait for convergence
        sleep(5)

        # check that all all_processes have the correct state
        for i in range(self.N-2):
            self.assertEqual(self.all_processes[i].state, NORMAL)
        self.assertEqual(self.all_processes[self.N-1].state, COORDINATOR)

        # check that all all_processes have the correct coordinator
        for i in range(self.N-1):
            self.assertEqual(self.all_processes[i].coordinator, self.N-1)

    # def test_coordinator_death(self):
    #     """Test coordinator death"""
    #     # start election at lowest priority process
    #     self.all_processes[self.N-1].kill()
    #     self.all_processes[0].start_election()

    #     # wait for convergence
    #     # sleep(5)

    #     # kill coordinator
        
    #     # self.all_processes[0].start_election()

    #     # wait for convergence
    #     # sleep(5)

    #     # check that all all_processes have the correct state
    #     for i in range(self.N-3):
    #         self.assertEqual(self.all_processes[i].state, NORMAL)
    #     self.assertEqual(self.all_processes[self.N-2].state, COORDINATOR)

    #     # check that all all_processes have the correct coordinator
    #     for i in range(self.N-2):
    #         self.assertEqual(self.all_processes[i].coordinator, self.N-2)


class SystemTestsImproved(unittest.TestCase):
    """Testing simulations of the improved bully algorithm"""

    def setUp(self) -> None:
        self.N = 5 
        self.all_processes = []
        for i in range(self.N):
            self.all_processes.append(ProcessImproved(i))

        # inform each process of all the other all_processes by adding them to the process list and remove self from list
        for i in range(self.N):
            self.all_processes[i].processes = self.all_processes

        # start processes
        for p in self.all_processes:
            p.start_thread()

    def tearDown(self) -> None:
        msg_count = 0
        for p in self.all_processes:
            msg_count += p.msg_count
            p.kill()
        print(f"Total messages sent in improved: {msg_count}")

    def test_election(self):
        """Test election"""
        # start election at lowest priority process
        self.all_processes[0].start_election()

        # wait for convergence
        sleep(10)

        # check that all all_processes have the correct state
        for i in range(self.N-2):
            self.assertEqual(self.all_processes[i].state, NORMAL)
        self.assertEqual(self.all_processes[self.N-1].state, COORDINATOR)

        # check that all all_processes have the correct coordinator
        for i in range(self.N-1):
            self.assertEqual(
                self.all_processes[i].current_coordinator, self.N-1)


# system test for 'bully_improved.py'
if __name__ == "__main__":
    unittest.main()
