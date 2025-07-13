class StatsGenerator:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def generate_stats(self):
        total_blocks = len(self.memory_manager.memory_blocks)
        remaining_space = self.memory_manager.memory_blocks
        return {
            "total_blocks": total_blocks,
            "remaining_space": remaining_space,
            "allocations": self.memory_manager.allocations
        }