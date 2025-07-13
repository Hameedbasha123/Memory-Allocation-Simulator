from flask import Flask, render_template_string, request, jsonify
import random
import json
from datetime import datetime

app = Flask(__name__)

class MemoryBlock:
    def __init__(self, start, size, allocated=False, process_id=None):
        self.start = start
        self.size = size
        self.allocated = allocated
        self.process_id = process_id
        self.timestamp = datetime.now()

class MemoryBlockManager:
    def __init__(self, total_size=1024):
        self.total_size = total_size
        self.blocks = [MemoryBlock(0, total_size)]
        self.allocation_history = []
    
    def first_fit(self, size, process_id):
        for block in self.blocks:
            if not block.allocated and block.size >= size:
                if block.size > size:
                    new_block = MemoryBlock(block.start + size, block.size - size)
                    self.blocks.insert(self.blocks.index(block) + 1, new_block)
                block.size = size
                block.allocated = True
                block.process_id = process_id
                self.allocation_history.append(f"Allocated {size}KB to P{process_id} at {block.start}")
                return True
        return False
    
    def best_fit(self, size, process_id):
        best_block = None
        best_size = float('inf')
        
        for block in self.blocks:
            if not block.allocated and block.size >= size and block.size < best_size:
                best_block = block
                best_size = block.size
        
        if best_block:
            if best_block.size > size:
                new_block = MemoryBlock(best_block.start + size, best_block.size - size)
                self.blocks.insert(self.blocks.index(best_block) + 1, new_block)
            best_block.size = size
            best_block.allocated = True
            best_block.process_id = process_id
            self.allocation_history.append(f"Allocated {size}KB to P{process_id} at {best_block.start}")
            return True
        return False
    
    def worst_fit(self, size, process_id):
        worst_block = None
        worst_size = 0
        
        for block in self.blocks:
            if not block.allocated and block.size >= size and block.size > worst_size:
                worst_block = block
                worst_size = block.size
        
        if worst_block:
            if worst_block.size > size:
                new_block = MemoryBlock(worst_block.start + size, worst_block.size - size)
                self.blocks.insert(self.blocks.index(worst_block) + 1, new_block)
            worst_block.size = size
            worst_block.allocated = True
            worst_block.process_id = process_id
            self.allocation_history.append(f"Allocated {size}KB to P{process_id} at {worst_block.start}")
            return True
        return False
    
    def deallocate(self, process_id):
        for block in self.blocks:
            if block.allocated and block.process_id == process_id:
                block.allocated = False
                block.process_id = None
                self.allocation_history.append(f"Deallocated P{process_id}")
                self.merge_free_blocks()
                return True
        return False
    
    def merge_free_blocks(self):
        i = 0
        while i < len(self.blocks) - 1:
            if not self.blocks[i].allocated and not self.blocks[i + 1].allocated:
                self.blocks[i].size += self.blocks[i + 1].size
                self.blocks.pop(i + 1)
            else:
                i += 1
    
    def get_stats(self):
        allocated = sum(b.size for b in self.blocks if b.allocated)
        free = self.total_size - allocated
        fragmentation = len([b for b in self.blocks if not b.allocated])
        return {
            'allocated': allocated,
            'free': free,
            'utilization': (allocated / self.total_size) * 100,
            'fragmentation': fragmentation,
            'total_blocks': len(self.blocks)
        }

memory_manager = MemoryBlockManager()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Memory Allocation Visualizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f7fa; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; font-size: 2.5em; }
        .controls { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .control-group { display: flex; gap: 15px; align-items: center; margin-bottom: 15px; flex-wrap: wrap; }
        label { font-weight: 600; min-width: 120px; }
        input, select, button { padding: 8px 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        button { background: #3498db; color: white; border: none; cursor: pointer; transition: all 0.3s; }
        button:hover { background: #2980b9; transform: translateY(-1px); }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .memory-visual { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .memory-bar { height: 60px; border: 2px solid #34495e; border-radius: 5px; display: flex; overflow: hidden; }
        .block { height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px; transition: all 0.3s; }
        .block:hover { opacity: 0.8; transform: scaleY(1.1); }
        .allocated { background: linear-gradient(45deg, #e74c3c, #c0392b); }
        .free { background: linear-gradient(45deg, #2ecc71, #27ae60); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #3498db; margin-bottom: 5px; }
        .stat-label { color: #7f8c8d; font-size: 14px; }
        .history { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-height: 300px; overflow-y: auto; }
        .history h3 { margin-bottom: 15px; color: #2c3e50; }
        .history-item { padding: 8px; background: #ecf0f1; margin-bottom: 5px; border-radius: 3px; font-size: 13px; }
        .legend { display: flex; gap: 20px; justify-content: center; margin-top: 10px; }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .legend-color { width: 20px; height: 20px; border-radius: 3px; }
        @media (max-width: 768px) {
            .control-group { flex-direction: column; align-items: stretch; }
            .legend { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Memory Allocation Visualizer</h1>
        
        <div class="controls">
            <div class="control-group">
                <label for="algorithm">Algorithm:</label>
                <select id="algorithm">
                    <option value="first_fit">First Fit</option>
                    <option value="best_fit">Best Fit</option>
                    <option value="worst_fit">Worst Fit</option>
                </select>
                
                <label for="size">Size (KB):</label>
                <input type="number" id="size" value="64" min="1" max="512">
                
                <label for="processId">Process ID:</label>
                <input type="number" id="processId" value="1" min="1">
                
                <button onclick="allocate()">Allocate</button>
            </div>
            
            <div class="control-group">
                <label for="deallocateId">Deallocate Process:</label>
                <input type="number" id="deallocateId" value="1" min="1">
                <button onclick="deallocate()" class="btn-danger">Deallocate</button>
                
                <button onclick="reset()" class="btn-danger">Reset Memory</button>
                <button onclick="simulate()">Auto Simulate</button>
            </div>
        </div>
        
        <div class="memory-visual">
            <h3>Memory Layout (1024 KB Total)</h3>
            <div class="memory-bar" id="memoryBar"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color allocated"></div>
                    <span>Allocated</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color free"></div>
                    <span>Free</span>
                </div>
            </div>
        </div>
        
        <div class="stats" id="stats"></div>
        
        <div class="history">
            <h3>Allocation History</h3>
            <div id="historyList"></div>
        </div>
    </div>

    <script>
        function updateDisplay() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update memory bar
                    const memoryBar = document.getElementById('memoryBar');
                    memoryBar.innerHTML = '';
                    
                    data.blocks.forEach(block => {
                        const div = document.createElement('div');
                        div.className = `block ${block.allocated ? 'allocated' : 'free'}`;
                        div.style.width = `${(block.size / 1024) * 100}%`;
                        div.textContent = block.allocated ? 
                            `P${block.process_id} (${block.size}KB)` : 
                            `Free (${block.size}KB)`;
                        div.title = `${block.allocated ? 'Allocated' : 'Free'} - Start: ${block.start}, Size: ${block.size}KB`;
                        memoryBar.appendChild(div);
                    });
                    
                    // Update stats
                    const stats = data.stats;
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${stats.allocated}</div>
                            <div class="stat-label">Allocated (KB)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.free}</div>
                            <div class="stat-label">Free (KB)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.utilization.toFixed(1)}%</div>
                            <div class="stat-label">Utilization</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.fragmentation}</div>
                            <div class="stat-label">Free Fragments</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.total_blocks}</div>
                            <div class="stat-label">Total Blocks</div>
                        </div>
                    `;
                    
                    // Update history
                    const historyList = document.getElementById('historyList');
                    historyList.innerHTML = data.history.slice(-10).reverse().map(item => 
                        `<div class="history-item">${item}</div>`
                    ).join('');
                });
        }
        
        function allocate() {
            const algorithm = document.getElementById('algorithm').value;
            const size = parseInt(document.getElementById('size').value);
            const processId = parseInt(document.getElementById('processId').value);
            
            fetch('/api/allocate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({algorithm, size, process_id: processId})
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) alert('Allocation failed: ' + data.message);
                updateDisplay();
                document.getElementById('processId').value = processId + 1;
            });
        }
        
        function deallocate() {
            const processId = parseInt(document.getElementById('deallocateId').value);
            
            fetch('/api/deallocate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({process_id: processId})
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) alert('Deallocation failed: Process not found');
                updateDisplay();
            });
        }
        
        function reset() {
            fetch('/api/reset', {method: 'POST'})
                .then(() => updateDisplay());
        }
        
        function simulate() {
            const algorithms = ['first_fit', 'best_fit', 'worst_fit'];
            const sizes = [32, 64, 128, 256];
            
            for (let i = 0; i < 5; i++) {
                setTimeout(() => {
                    const algorithm = algorithms[Math.floor(Math.random() * algorithms.length)];
                    const size = sizes[Math.floor(Math.random() * sizes.length)];
                    const processId = i + 1;
                    
                    fetch('/api/allocate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({algorithm, size, process_id: processId})
                    }).then(() => updateDisplay());
                }, i * 1000);
            }
        }
        
        // Initial display update
        updateDisplay();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    blocks = []
    for block in memory_manager.blocks:
        blocks.append({
            'start': block.start,
            'size': block.size,
            'allocated': block.allocated,
            'process_id': block.process_id
        })
    
    return jsonify({
        'blocks': blocks,
        'stats': memory_manager.get_stats(),
        'history': memory_manager.allocation_history
    })

@app.route('/api/allocate', methods=['POST'])
def allocate_memory():
    data = request.json
    algorithm = data['algorithm']
    size = data['size']
    process_id = data['process_id']
    
    if algorithm == 'first_fit':
        success = memory_manager.first_fit(size, process_id)
    elif algorithm == 'best_fit':
        success = memory_manager.best_fit(size, process_id)
    elif algorithm == 'worst_fit':
        success = memory_manager.worst_fit(size, process_id)
    else:
        success = False
    
    return jsonify({
        'success': success,
        'message': 'Not enough memory' if not success else 'Allocated successfully'
    })

@app.route('/api/deallocate', methods=['POST'])
def deallocate_memory():
    data = request.json
    process_id = data['process_id']
    success = memory_manager.deallocate(process_id)
    
    return jsonify({'success': success})

@app.route('/api/reset', methods=['POST'])
def reset_memory():
    global memory_manager
    memory_manager = MemoryBlockManager()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)