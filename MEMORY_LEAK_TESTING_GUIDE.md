# 💾 Memory Leak Testing Guide

**Ziel**: Sicherstellen dass long-running trading sessions keine Memory Leaks haben  
**Status**: 📝 Implementation Guide  
**Priorität**: 🟡 Medium

---

## 📋 Warum Memory Leak Tests?

### Problem
Trading Bots laufen oft für Tage/Wochen ohne Restart. Memory Leaks führen zu:
- 💥 System Crashes (Out of Memory)
- 🐌 Performance Degradation
- 🔄 Häufige Restarts nötig
- 💸 Server Costs steigen

### Lösung
Proaktive Memory Leak Tests mit `tracemalloc` und bounded data structures.

---

## 🛠️ Implementation

### 1. Basis Memory Leak Test

```python
"""
tests/test_memory_leaks.py - Memory leak tests for long-running sessions
"""

import unittest
import tracemalloc
from utils import generate_sample_data


class TestMemoryLeaks(unittest.TestCase):
    """Test for memory leaks in long-running sessions"""
    
    def test_no_memory_leak_10k_candles(self):
        """Test processing 10,000 candles doesn't leak memory"""
        tracemalloc.start()
        
        # Import here to get accurate initial memory
        from main import LiveTradingBot
        
        # Record initial memory
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Create bot instance
        bot = LiveTradingBot(
            symbol='BTCUSDT',
            strategy_name='MA_CROSSOVER',
            initial_capital=10000,
            dry_run=True,
            use_simulation=True
        )
        
        # Process 10,000 candles
        for i in range(10000):
            candle_data = generate_sample_data(1)
            bot.run_simulation_step(candle_data)
            
            # Periodic memory check
            if i % 1000 == 0:
                current, peak = tracemalloc.get_traced_memory()
                print(f"Candle {i}: Current={current/10**6:.1f}MB, Peak={peak/10**6:.1f}MB")
        
        # Record final memory
        final_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate memory growth
        memory_growth_mb = (final_memory - initial_memory) / 10**6
        peak_mb = peak_memory / 10**6
        
        print(f"\n📊 Memory Report:")
        print(f"Initial: {initial_memory/10**6:.1f} MB")
        print(f"Final: {final_memory/10**6:.1f} MB")
        print(f"Growth: {memory_growth_mb:.1f} MB")
        print(f"Peak: {peak_mb:.1f} MB")
        
        # Assert reasonable limits
        # 10k candles should use < 100MB
        self.assertLess(memory_growth_mb, 100, 
                       f"Memory leak detected: {memory_growth_mb:.1f}MB growth")
        
        # Peak should be < 200MB
        self.assertLess(peak_mb, 200,
                       f"Peak memory too high: {peak_mb:.1f}MB")
    
    def test_session_store_bounded(self):
        """Test that session store doesn't grow unbounded"""
        from core.session_store import SessionStore
        
        tracemalloc.start()
        
        store = SessionStore(max_size=1000)  # Bounded cache
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Add 10,000 sessions (should only keep last 1000)
        for i in range(10000):
            store.add_session(f"session_{i}", {
                'data': f"test_data_{i}",
                'timestamp': i,
                'metrics': {'value': i * 100}
            })
        
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        memory_growth_mb = (final_memory - initial_memory) / 10**6
        
        # Verify only max_size sessions exist
        self.assertEqual(len(store.sessions), 1000)
        
        # Memory growth should be bounded
        self.assertLess(memory_growth_mb, 50,
                       f"Session store memory not bounded: {memory_growth_mb:.1f}MB")
    
    def test_trade_history_bounded(self):
        """Test that trade history doesn't grow unbounded"""
        from binance_integration import PaperTradingExecutor
        
        tracemalloc.start()
        
        executor = PaperTradingExecutor(initial_capital=100000)
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Execute 1000 trades
        for i in range(1000):
            # Buy and sell cycle
            executor.buy('BTCUSDT', 0.01, 50000 + i)
            executor.sell('BTCUSDT', 50100 + i)
        
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        memory_growth_mb = (final_memory - initial_memory) / 10**6
        
        print(f"Trade history size: {len(executor.trade_history)}")
        print(f"Memory growth: {memory_growth_mb:.1f}MB")
        
        # 1000 trades should use < 50MB
        self.assertLess(memory_growth_mb, 50,
                       f"Trade history leak: {memory_growth_mb:.1f}MB")


if __name__ == '__main__':
    unittest.main()
```

---

## 🔍 Memory Profiling Tools

### 1. tracemalloc (Built-in)

```python
import tracemalloc

# Start tracking
tracemalloc.start()

# Your code here
# ...

# Get current memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 10**6:.1f}MB")
print(f"Peak: {peak / 10**6:.1f}MB")

# Get top memory allocations
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

tracemalloc.stop()
```

### 2. memory_profiler (External)

```bash
# Install
pip install memory_profiler

# Usage
python -m memory_profiler your_script.py
```

```python
from memory_profiler import profile

@profile
def process_candles():
    """Function to profile"""
    bot = LiveTradingBot(...)
    for i in range(10000):
        bot.run_simulation_step(...)
```

### 3. objgraph (Object tracking)

```bash
pip install objgraph
```

```python
import objgraph

# Show most common types
objgraph.show_most_common_types(limit=20)

# Growth tracking
objgraph.show_growth(limit=10)

# Reference chain
objgraph.show_chain(
    objgraph.find_backref_chain(
        random.choice(objgraph.by_type('dict')),
        objgraph.is_proper_module
    ),
    filename='chain.png'
)
```

---

## 🏗️ Bounded Data Structures

### 1. Bounded Session Store

```python
from collections import OrderedDict

class BoundedSessionStore:
    """Session store with maximum size limit"""
    
    def __init__(self, max_size: int = 1000):
        self.sessions = OrderedDict()
        self.max_size = max_size
    
    def add_session(self, session_id: str, data: dict):
        """Add session, remove oldest if exceeds max_size"""
        if len(self.sessions) >= self.max_size:
            # Remove oldest entry (FIFO)
            self.sessions.popitem(last=False)
        
        self.sessions[session_id] = data
    
    def get_session(self, session_id: str) -> dict:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def clear_old_sessions(self, keep_last: int = 100):
        """Clear all but last N sessions"""
        while len(self.sessions) > keep_last:
            self.sessions.popitem(last=False)
```

### 2. Bounded Trade History

```python
from collections import deque

class BoundedTradeHistory:
    """Trade history with maximum size"""
    
    def __init__(self, max_trades: int = 10000):
        self.trades = deque(maxlen=max_trades)
    
    def add_trade(self, trade: dict):
        """Add trade (oldest removed if full)"""
        self.trades.append(trade)
    
    def get_recent_trades(self, n: int = 100):
        """Get N most recent trades"""
        return list(self.trades)[-n:]
    
    def clear_old_trades(self, keep_last: int = 1000):
        """Keep only last N trades"""
        if len(self.trades) > keep_last:
            self.trades = deque(
                list(self.trades)[-keep_last:],
                maxlen=self.max_trades
            )
```

### 3. Circular Buffer for Metrics

```python
import numpy as np

class CircularBuffer:
    """Fixed-size circular buffer for metrics"""
    
    def __init__(self, size: int = 10000):
        self.buffer = np.zeros(size)
        self.size = size
        self.index = 0
        self.is_full = False
    
    def append(self, value: float):
        """Add value to buffer"""
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        if self.index == 0:
            self.is_full = True
    
    def get_all(self):
        """Get all values (in order)"""
        if self.is_full:
            return np.concatenate([
                self.buffer[self.index:],
                self.buffer[:self.index]
            ])
        return self.buffer[:self.index]
    
    def get_recent(self, n: int):
        """Get N most recent values"""
        all_values = self.get_all()
        return all_values[-n:] if len(all_values) > n else all_values
```

---

## 🚨 Common Memory Leak Patterns

### ❌ BAD: Unbounded List Growth

```python
class TradingBot:
    def __init__(self):
        self.all_candles = []  # ❌ Grows forever!
    
    def process_candle(self, candle):
        self.all_candles.append(candle)  # Memory leak!
```

### ✅ GOOD: Bounded with deque

```python
from collections import deque

class TradingBot:
    def __init__(self):
        self.recent_candles = deque(maxlen=1000)  # ✅ Max 1000
    
    def process_candle(self, candle):
        self.recent_candles.append(candle)  # Auto-removes oldest
```

---

### ❌ BAD: Circular References

```python
class Node:
    def __init__(self):
        self.children = []
        self.parent = None  # ❌ Can create cycles

# Creates circular reference
node1 = Node()
node2 = Node()
node1.children.append(node2)
node2.parent = node1  # Circular!
```

### ✅ GOOD: Weak References

```python
import weakref

class Node:
    def __init__(self):
        self.children = []
        self.parent = None
    
    def set_parent(self, parent):
        self.parent = weakref.ref(parent)  # ✅ Weak ref
```

---

### ❌ BAD: Global Caches

```python
# Global cache that never clears
PRICE_CACHE = {}  # ❌ Grows forever

def get_price(symbol, timestamp):
    key = f"{symbol}_{timestamp}"
    if key not in PRICE_CACHE:
        PRICE_CACHE[key] = fetch_price(symbol, timestamp)
    return PRICE_CACHE[key]
```

### ✅ GOOD: LRU Cache with Size Limit

```python
from functools import lru_cache

@lru_cache(maxsize=1000)  # ✅ Max 1000 entries
def get_price(symbol, timestamp):
    return fetch_price(symbol, timestamp)
```

---

## 📊 Monitoring in Production

### 1. Memory Metrics to Track

```python
import psutil
import os

def get_memory_metrics():
    """Get current process memory metrics"""
    process = psutil.Process(os.getpid())
    
    return {
        'rss_mb': process.memory_info().rss / 10**6,  # Resident Set Size
        'vms_mb': process.memory_info().vms / 10**6,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'num_threads': process.num_threads(),
        'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
    }

# Usage in monitoring loop
import time

while True:
    metrics = get_memory_metrics()
    logger.info(f"Memory: {metrics['rss_mb']:.1f}MB ({metrics['percent']:.1f}%)")
    
    if metrics['rss_mb'] > 1000:  # Alert if > 1GB
        logger.warning("⚠️ High memory usage!")
    
    time.sleep(60)  # Check every minute
```

### 2. Automatic Cleanup

```python
import gc

class TradingBot:
    def __init__(self):
        self.cleanup_interval = 1000  # Every 1000 candles
        self.candle_count = 0
    
    def process_candle(self, candle):
        self.candle_count += 1
        
        # Periodic cleanup
        if self.candle_count % self.cleanup_interval == 0:
            self._cleanup()
    
    def _cleanup(self):
        """Periodic memory cleanup"""
        # Clear old data
        self.clear_old_trades(keep_last=1000)
        self.clear_old_sessions(keep_last=100)
        
        # Force garbage collection
        gc.collect()
        
        # Log memory status
        metrics = get_memory_metrics()
        logger.info(f"Cleanup: {metrics['rss_mb']:.1f}MB")
```

---

## ✅ Checklist

### Development
- [ ] Add memory leak tests to test suite
- [ ] Use bounded data structures (deque, LRU cache)
- [ ] Implement periodic cleanup
- [ ] Profile memory usage with tracemalloc
- [ ] Test with 10k+ candles

### CI/CD
- [ ] Run memory tests in CI pipeline
- [ ] Set memory thresholds
- [ ] Fail build if memory leak detected
- [ ] Generate memory reports

### Production
- [ ] Monitor memory metrics
- [ ] Set up alerts for high memory usage
- [ ] Implement automatic restart on OOM
- [ ] Log memory statistics periodically
- [ ] Review memory usage weekly

---

## 📚 Resources

- [Python tracemalloc docs](https://docs.python.org/3/library/tracemalloc.html)
- [memory_profiler](https://pypi.org/project/memory-profiler/)
- [objgraph](https://mg.pov.lt/objgraph/)
- [Python Memory Management](https://realpython.com/python-memory-management/)

---

**Erstellt**: 2025-10-14  
**Status**: Implementation Guide  
**Nächster Schritt**: Implement tests in tests/test_memory_leaks.py
