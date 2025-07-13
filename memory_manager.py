class MemoryManager:
    def __init__(self):
        self.memory_blocks = [100, 500, 200, 300, 600]  # example memory blocks
        self.allocations = []

    def reset(self):
        self.allocations = []

    def allocate_first_fit(self, size):
        for i, block in enumerate(self.memory_blocks):
            if block >= size:
                self.allocations.append((i, size))
                self.memory_blocks[i] -= size
                return f"Allocated {size} to block {i}"
        return "Allocation failed"

    def allocate_best_fit(self, size):
        best_idx = -1
        min_diff = float("inf")
        for i, block in enumerate(self.memory_blocks):
            if block >= size and (block - size) < min_diff:
                best_idx = i
                min_diff = block - size
        if best_idx != -1:
            self.allocations.append((best_idx, size))
            self.memory_blocks[best_idx] -= size
            return f"Allocated {size} to block {best_idx}"
        return "Allocation failed"

    def allocate_worst_fit(self, size):
        worst_idx = -1
        max_diff = -1
        for i, block in enumerate(self.memory_blocks):
            if block >= size and (block - size) > max_diff:
                worst_idx = i
                max_diff = block - size
        if worst_idx != -1:
            self.allocations.append((worst_idx, size))
            self.memory_blocks[worst_idx] -= size
            return f"Allocated {size} to block {worst_idx}"
        return "Allocation failed"