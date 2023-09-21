import unittest
from bully_orginal import Process

# unit tests for the methods in 'bully_original.py'


class TestBullyOriginal(unittest.TestCase):
    """Test the methods in bully_original.py"""
    # create N processes and put them in a list
    N = 10
    all_processes = []
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    for i in range(N):
        all_processes[i].processes = all_processes

    # start processes
    for p in all_processes:
        p.start_thread()

    def test_get_id(self):
        """Test get_id() method"""
        ids = [process.get_id() for process in self.__class__.all_processes]
        ids_expected = list(range(self.__class__.N))
        self.assertEqual(ids, ids_expected)

    def test_get_process(self):
        """Test get_process() method"""
        for i in range(self.__class__.N):
            process = self.__class__.all_processes[i]
            self.assertEqual(process.get_process(i), process)

    def test_enqueue_message(self):
        """Test enqueue_message() method"""
        for i in range(self.__class__.N):
            process = self.__class__.all_processes[i]
            process.enqueue_message(i, "msg_type")
            self.assertEqual(process.message_queue.get(), ("msg_type", i))

    def test_send_coordinator(self):
        """Test send_coordinator() method"""
        process_N = self.__class__.all_processes[self.__class__.N-1]
        process_N.send_coordinator()
        self.assertTrue(process_N.coordinator_msg_sent)
        for i in range(self.__class__.N-1):
            process = self.__class__.all_processes[i]
            self.assertEqual(process.message_queue.get(),
                             (1, self.__class__.N-1))
            self.assertEqual(process.state, 0)

# TODO: Are we able to write test for the 'start_election()' method?


# unit tests for the methods in 'bully_improved.py'
class TestBullyImproved(unittest.TestCase):
    """Test the methods in bully_improved.py"""
    N = 10
    all_processes = []
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other processes
    for i in range(N):
        all_processes[i].processes = all_processes

    # start processes
    for p in all_processes:
        p.start_thread()

    def test_get_id(self):
        """Test get_id() method"""
        ids = [process.get_id() for process in self.__class__.all_processes]
        ids_expected = list(range(self.__class__.N))
        self.assertEqual(ids, ids_expected)

    def test_get_process(self):
        """Test get_process() method"""
        for i in range(self.__class__.N):
            process = self.__class__.all_processes[i]
            self.assertEqual(process.get_process(i), process)

    def test_enqueue_message(self):
        """Test enqueue_message() method"""
        for i in range(self.__class__.N):
            process = self.__class__.all_processes[i]
            process.enqueue_message(i, "msg_type")
            self.assertEqual(process.message_queue.get(), ("msg_type", i))

    def test_send_coordinator(self):
        """Test send_coordinator() method"""
        process_N = self.__class__.all_processes[self.__class__.N-1]
        process_N.send_coordinator()
        self.assertTrue(process_N.coordinator_msg_sent)
        for i in range(self.__class__.N-1):
            process = self.__class__.all_processes[i]
            self.assertEqual(process.message_queue.get(),
                             (1, self.__class__.N-1))
            self.assertEqual(process.state, 0)


if __name__ == '__main__':
    unittest.main()
