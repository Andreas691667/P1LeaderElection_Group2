import unittest
import sys
sys.path.insert(0, "./src")
from bully_orginal import ProcessOriginal
from bully_improved import ProcessImproved



class TestBullyOriginal(unittest.TestCase):
    """Test the methods in bully_original.py"""
    # create N processes and put them in a list

    def setUp(self) -> None:
        self.N = 10
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
        for p in self.all_processes:
            p.kill()

    def test_get_id(self):
        """Test get_id() method"""
        ids = [process.get_id() for process in self.all_processes]
        ids_expected = list(range(self.N))
        self.assertEqual(ids, ids_expected)

    def test_get_process(self):
        """Test get_process() method"""
        for i in range(self.N):
            process = self.all_processes[i]
            self.assertEqual(process.get_process(i), process)

    def test_enqueue_message(self):
        """Test enqueue_message() method"""
        for i in range(self.N):
            process = self.all_processes[i]
            process.enqueue_message(i, "msg_type")
            self.assertEqual(process.message_queue.get(), ("msg_type", i))

    def test_send_coordinator(self):
        """Test send_coordinator() method"""
        process_N = self.all_processes[self.N-1]
        process_N.send_coordinator()
        self.assertTrue(process_N.coordinator_msg_sent)
        for i in range(self.N-1):
            process = self.all_processes[i]
            self.assertEqual(process.message_queue.get(),
                             (1, self.N-1))
            self.assertEqual(process.state, 0)

# TODO: Are we able to write test for the 'start_election()' method?


# unit tests for the methods in 'bully_improved.py'
class TestBullyImproved(unittest.TestCase):
    """Test the methods in bully_improved.py"""

    def setUp(self) -> None:
        self.N = 10
        self.all_processes = []
        for i in range(self.N):
            self.all_processes.append(ProcessImproved(i))

        # inform each process of all the other processes
        for i in range(self.N):
            self.all_processes[i].processes = self.all_processes

        # start processes
        for p in self.all_processes:
            p.start_thread()

    def tearDown(self) -> None:
        for p in self.all_processes:
            p.kill()
        

    def test_get_id(self):
        """Test get_id() method"""
        ids = [process.get_id() for process in self.all_processes]
        ids_expected = list(range(self.N))
        self.assertEqual(ids, ids_expected)

    def test_get_process(self):
        """Test get_process() method"""
        for i in range(self.N):
            process = self.all_processes[i]
            self.assertEqual(process.get_process(i), process)

    def test_enqueue_message(self):
        """Test enqueue_message() method"""
        for i in range(self.N):
            process = self.all_processes[i]
            process.enqueue_message(i, "msg_type")
            self.assertEqual(process.message_queue.get(), ("msg_type", i))

    def test_send_coordinator(self):
        """Test send_coordinator() method"""
        process_N = self.all_processes[self.N-1]
        process_N.send_coordinator()
        self.assertTrue(process_N.coordinator_msg_sent)
        for i in range(self.N-1):
            process = self.all_processes[i]
            self.assertEqual(process.message_queue.get(),
                             (1, self.N-1))
            self.assertEqual(process.state, 0)


if __name__ == '__main__':
    unittest.main()
