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
    #         self.assertEqual(self.all_processes[i].state, IDLE)
    #     self.assertEqual(self.all_processes[self.N-2].state, COORDINATOR)

    #     # check that all all_processes have the correct coordinator
    #     for i in range(self.N-2):
    #         self.assertEqual(self.all_processes[i].coordinator, self.N-2)