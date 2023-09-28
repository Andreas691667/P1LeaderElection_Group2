import unittest
import sys
sys.path.insert(0, "./src")
from bully_orginal import ProcessOriginal
from bully_improved import ProcessImproved
from types_ import *



class TestBullyOriginal(unittest.TestCase):
    """Test the methods in bully_original.py"""
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

    def test_init(self):
        """Test the init method"""
        for i in range(self.N):
            process = self.all_processes[i]
            self.assertEqual(process._id, i)
            self.assertEqual(process.state, IDLE)
            self.assertEqual(process.processes, self.all_processes)
            self.assertEqual(process.oks, 0)
            self.assertFalse(process.coordinator_msg_sent)
            self.assertFalse(process.election_msg_sent)
            self.assertEqual(process.msg_count, 0)
            self.assertIsNone(process.coordinator)

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
            self.assertEqual(process.state, IDLE)

    def test_kill(self):
        """Test kill() method"""
        process = self.all_processes[0]
        process.kill()
        self.assertEqual(process.state, DEAD)
        self.assertTrue(process.stop_worker.is_set())

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
        
    def test_init(self):
        """Test the init method"""
        for i in range(self.N):
            process = self.all_processes[i]
            self.assertEqual(process._id, i)
            self.assertEqual(process.state, IDLE)
            self.assertEqual(process.processes, self.all_processes)
            self.assertEqual(process.oks, [])
            self.assertFalse(process.coordinator_msg_sent)
            self.assertFalse(process.election_msg_sent)
            self.assertEqual(process.msg_count, 0)
            self.assertEqual(process.current_coordinator, 0)
            self.assertFalse(process.election_in_progess)
            self.assertEqual(process.current_coordinator, 0)
            self.assertEqual(process.election_start_time, 0)

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
            self.assertEqual(process.state, IDLE)

    def test_kill(self):
        """Test kill() method"""
        process = self.all_processes[0]
        process.kill()
        self.assertEqual(process.state, DEAD)
        self.assertTrue(process.stop_worker.is_set())


if __name__ == '__main__':
    unittest.main()
