class AllocationSimulator:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def allocate(self, strategy, size):
        if strategy == "first_fit":
            return self.memory_manager.allocate_first_fit(size)
        elif strategy == "best_fit":
            return self.memory_manager.allocate_best_fit(size)
        elif strategy == "worst_fit":
            return self.memory_manager.allocate_worst_fit(size)
        else:
            return "Unknown strategy"