import unittest
from bully_orginal import Process

# unit tests for the methods in 'bully_original.py'
class TestBullyOriginal(unittest.TestCase):
    """Test the methods in bully_original.py"""    
    N = 10      # number of processes
    all_processes = []  # list of all processes
    for i in range(N):
        all_processes.append(Process(i))

    # inform each process of all the other all_processes by adding them to the process list and remove self from list
    for i in range(N):
        all_processes[i].processes = all_processes

    def test_get_id(self):
        """Test get_id() method"""
        self.assertEqual(self.process.get_id(), 0)
    
    def test_get_process(self):
        """Test get_process() method"""
        self.assertEqual(self.process.get_process(0), self.__class__.process)


# unit tests for the methods in 'bully_improved.py'
class TestBullyImproved(unittest.TestCase):
    """Test the methods in bully_improved.py"""
    def test_get_id(self):
        """Test get_id() method"""
        self.assertEqual(Process(0).get_id(), 0)

if __name__ == '__main__':
    unittest.main()
