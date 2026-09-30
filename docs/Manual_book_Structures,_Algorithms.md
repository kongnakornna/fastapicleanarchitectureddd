# 📚 คู่มือ Data Structures, Algorithms, Functional Programming และ OOP ฉบับ Production-Ready

> **เวอร์ชัน:** 1.0 · **ระดับ:** Beginner → Advanced · **กลุ่มเป้าหมาย:** Software Engineer, Backend Developer, System Architect
> **Stack:** Python 3.11+ · TypeScript · SQL · Distributed Systems
> **ใช้กับ:** System Design · Code Review · Refactoring · Interview · Architecture Decision

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [บทนิยาม](#2-บทนิยาม)
3. [บทหัวข้อ — 4 เสาหลัก](#3-บทหัวข้อ--4-เสาหลัก)
   - 3.1 [Data Structures](#31-data-structures-คืออะไร)
   - 3.2 [Algorithms](#32-algorithms-คืออะไร)
   - 3.3 [Functional Programming](#33-functional-programming-คืออะไร)
   - 3.4 [OOP](#34-object-oriented-programming-คืออะไร)
4. [โครงสร้าง (Structural Comparison)](#4-โครงสร้าง-structural-comparison)
5. [DDD + Clean Architecture + Modular Design](#5-ddd--clean-architecture--modular-design)
6. [แนวทางการประยุกต์ใช้](#6-แนวทางการประยุกต์ใช้)
7. [Root Cause Analysis (Design RCA)](#7-root-cause-analysis-design-rca)
8. [การนำไปใช้งานจริง (Production)](#8-การนำไปใช้งานจริง-production)
9. [Python Code Examples](#9-python-code-examples)
10. [AI/ML Skill (Code Assistant)](#10-aiml-skill-code-assistant)
11. [ปัญหาและแนวทางแก้ไข](#11-ปัญหาและแนวทางแก้ไข)
12. [สรุป](#12-สรุป)

---

## 1. บทนำ

### 1.1 ทำไมต้องเข้าใจทั้ง 4?

Software Engineer ที่เก่ง **ไม่ใช่** คนที่รู้ syntax ลึก แต่เป็นคนที่:

| คำถาม | ต้องรู้ |
|---|---|
| "เก็บข้อมูล 1M records ยังไง?" | **Data Structures** |
| "ค้นหาเร็วสุดยังไง?" | **Algorithms** |
| "ลด bugs ยังไง?" | **Functional Programming** |
| "ออกแบบโค้ดที่ maintain ได้?" | **OOP** |

**ทั้ง 4 นี้ไม่ใช่ "ทางเลือก" แต่เป็น "เครื่องมือ"** ที่ต้องเลือกใช้ให้ถูกสถานการณ์

```
┌─────────────────────────────────────────────────────┐
│              SOFTWARE ENGINEERING                   │
│                                                     │
│   Data Structures ─── Algorithms                    │
│   (จัดเก็บ)          (ประมวลผล)                    │
│         │              │                            │
│         └──────┬───────┘                            │
│                │                                    │
│          Functional ──── OOP                        │
│          (composition)   (encapsulation)            │
│                │              │                     │
│                └──────┬───────┘                     │
│                       │                             │
│                   Architecture                      │
│                       │                             │
│                   Production                        │
└─────────────────────────────────────────────────────┘
```

### 1.2 ขอบเขตของคู่มือ

คู่มือนี้ครอบคลุม:

- ✅ **Data Structures** — Array, List, Stack, Queue, Hash, Tree, Graph, Heap
- ✅ **Algorithms** — Sorting, Searching, DP, Greedy, Graph, String
- ✅ **Functional Programming** — Pure functions, immutability, composition, monads
- ✅ **OOP** — Encapsulation, inheritance, polymorphism, SOLID
- ✅ **การประยุกต์ใช้** — เลือก paradigm ให้ตรงงาน
- ✅ **Production** — Code review, refactoring, testing, performance
- ✅ **Python Code** — ตัวอย่างครบทุกหัวข้อ

**ไม่ครอบคลุม:** Formal verification, type theory, category theory (ขั้นสูง)

### 1.3 กลุ่มเป้าหมาย

| ระดับ | ได้อะไร |
|---|---|
| **Junior** | พื้นฐาน DS/A + เลือก paradigm ถูก |
| **Mid** | Refactor code ได้ + design patterns |
| **Senior** | Architecture decisions + trade-offs |
| **Architect** | Governance + enterprise patterns |
| **Interview** | ผ่าน FAANG-style + system design |

---

## 2. บทนิยาม

### 2.1 คำศัพท์ Data Structures

| คำ | ความหมาย | ตัวอย่าง |
|---|---|---|
| **Array** | ข้อมูลเรียงติดกัน | `[1, 2, 3]` |
| **Linked List** | โหนดเชื่อมด้วย pointer | ใช้ใน queue implementation |
| **Stack** | LIFO (Last In First Out) | Undo history |
| **Queue** | FIFO (First In First Out) | Task queue |
| **Hash Table** | Key-value mapping | `dict`, `set` |
| **Tree** | โครงสร้าง hierarchical | File system |
| **Graph** | โหนด + เส้นเชื่อม | Social network |
| **Heap** | Tree ที่มี priority | Priority queue |
| **Trie** | Tree สำหรับ string | Autocomplete |

### 2.2 คำศัพท์ Algorithms

| คำ | ความหมาย |
|---|---|
| **Time Complexity** | เวลาที่ใช้เป็นฟังก์ชันของ input |
| **Space Complexity** | Memory ที่ใช้ |
| **Stable Sort** | เรียงแล้วค่าเท่ากันยังคง order เดิม |
| **In-place** | ไม่ใช้ memory เพิ่ม |
| **Divide & Conquer** | แบ่งปัญหาเป็น sub-problems |
| **Dynamic Programming** | เก็บผลลัพธ์ย่อยเพื่อ reuse |
| **Greedy** | เลือก best ที่แต่ละขั้น |
| **Backtracking** | ลองผิดลองถูก + ย้อนกลับ |

### 2.3 คำศัพท์ Functional Programming

| คำ | ความหมาย |
|---|---|
| **Pure Function** | ไม่มี side effects + deterministic |
| **Immutability** | ไม่แก้ state เดิม |
| **First-class Function** | function เป็น value ได้ |
| **Higher-order Function** | รับ/คืน function |
| **Composition** | รวม function เล็กเป็นใหญ่ |
| **Currying** | แตก function หลาย argument |
| **Monad** | Wrapper สำหรับ computation |
| **Functor** | Structure ที่ map ได้ |
| **Referential Transparency** | แทน expression ด้วย value ได้ |

### 2.4 คำศัพท์ OOP

| คำ | ความหมาย |
|---|---|
| **Class** | blueprint สำหรับ object |
| **Object** | instance ของ class |
| **Encapsulation** | ซ่อน state, expose behavior |
| **Inheritance** | สืบทอดจาก class แม่ |
| **Polymorphism** | interface เดียว behavior ต่าง |
| **Abstraction** | ซ่อนรายละเอียด |
| **Composition** | รวม object (has-a) |
| **Aggregation** | weak has-a |
| **Association** | รู้จักกัน |
| **SOLID** | 5 principles |
| **Interface** | contract |

---

## 3. บทหัวข้อ — 4 เสาหลัก

### 3.1 Data Structures คืออะไร

**Data Structure** = วิธี **จัดเก็บและจัดเรียงข้อมูล** ในหน่วยความจำ เพื่อให้ **เข้าถึง/แก้ไขได้อย่างมีประสิทธิภาพ**

#### 3.1.1 ประเภทของ Data Structures

```
┌─────────────────────────────────────────────────────┐
│           DATA STRUCTURES TAXONOMY                  │
│                                                     │
│  Linear                       Non-Linear            │
│  ├── Array                    ├── Tree              │
│  ├── Linked List              │   ├── BST           │
│  ├── Stack                    │   ├── AVL           │
│  ├── Queue                    │   ├── Red-Black     │
│  └── Deque                    │   └── Trie          │
│                               ├── Graph             │
│  Hash                         │   ├── Directed      │
│  └── Hash Table               │   └── Undirected    │
│                               └── Heap              │
│                                   ├── Min-Heap      │
│                                   └── Max-Heap      │
└─────────────────────────────────────────────────────┘
```

#### 3.1.2 Complexity Cheat Sheet

| DS | Access | Search | Insert | Delete | Space |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| Stack | O(n) | O(n) | O(1) | O(1) | O(n) |
| Queue | O(n) | O(n) | O(1) | O(1) | O(n) |
| Hash Table | - | O(1)* | O(1)* | O(1)* | O(n) |
| BST (balanced) | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(1)** | O(n) | O(log n) | O(log n) | O(n) |
| Trie | - | O(k) | O(k) | O(k) | O(n×k) |
| Graph (adj list) | - | O(V+E) | O(1) | O(1) | O(V+E) |

`*` = average, `**` = peek min/max, `k` = key length

#### 3.1.3 ตัวอย่าง Python

```python
# ═══════════════════════════════════════════════════════════════
# data_structures.py — Data Structures พื้นฐาน
# ═══════════════════════════════════════════════════════════════
from collections import deque, Counter, defaultdict
from heapq import heappush, heappop, heapify
from typing import Any, Optional


# ─── 1) Stack (LIFO) ─────────────────────────
class Stack:
    """TH: Stack แบบ LIFO | EN: LIFO stack"""
    def __init__(self):
        self._items: list[Any] = []

    def push(self, item: Any) -> None:
        self._items.append(item)         # O(1)

    def pop(self) -> Any:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()         # O(1)

    def peek(self) -> Any:
        return self._items[-1]           # O(1)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)


# ─── 2) Queue (FIFO) ─────────────────────────
class Queue:
    """TH: Queue แบบ FIFO | EN: FIFO queue"""
    def __init__(self):
        self._items: deque = deque()

    def enqueue(self, item: Any) -> None:
        self._items.append(item)         # O(1)

    def dequeue(self) -> Any:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()     # O(1)

    def peek(self) -> Any:
        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0


# ─── 3) Singly Linked List ───────────────────
class Node:
    __slots__ = ("value", "next")

    def __init__(self, value: Any, next: Optional["Node"] = None):
        self.value = value
        self.next = next


class LinkedList:
    """TH: Singly Linked List | EN: singly linked list"""
    def __init__(self):
        self.head: Optional[Node] = None
        self.size = 0

    def append(self, value: Any) -> None:
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:              # O(n)
                cur = cur.next
            cur.next = node
        self.size += 1

    def prepend(self, value: Any) -> None:
        self.head = Node(value, self.head)  # O(1)
        self.size += 1

    def find(self, value: Any) -> Optional[Node]:
        cur = self.head
        while cur:                       # O(n)
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def to_list(self) -> list[Any]:
        out, cur = [], self.head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out


# ─── 4) Binary Search Tree ───────────────────
class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key: Any, value: Any = None):
        self.key = key
        self.value = value if value is not None else key
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None


class BST:
    """TH: Binary Search Tree | EN: binary search tree"""
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, key: Any, value: Any = None) -> None:
        self.root = self._insert(self.root, key, value)

    def _insert(self, node: Optional[BSTNode], key: Any, value: Any) -> BSTNode:
        if node is None:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value  # update
        return node

    def search(self, key: Any) -> Optional[Any]:
        cur = self.root
        while cur:
            if key == cur.key:
                return cur.value
            cur = cur.left if key < cur.key else cur.right
        return None

    def inorder(self) -> list[Any]:
        result: list[Any] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[BSTNode], out: list[Any]) -> None:
        if node:
            self._inorder(node.left, out)
            out.append(node.key)
            self._inorder(node.right, out)


# ─── 5) Min Heap (Priority Queue) ────────────
class MinHeap:
    """TH: Min Heap | EN: min-heap"""
    def __init__(self):
        self._items: list[Any] = []

    def push(self, item: Any) -> None:
        heappush(self._items, item)      # O(log n)

    def pop(self) -> Any:
        if not self._items:
            raise IndexError("pop from empty heap")
        return heappop(self._items)      # O(log n)

    def peek(self) -> Any:
        return self._items[0]            # O(1)


# ─── 6) Graph (Adjacency List) ───────────────
class Graph:
    """TH: Graph ด้วย adjacency list | EN: graph with adjacency list"""
    def __init__(self, directed: bool = False):
        self.adj: dict[Any, list[Any]] = defaultdict(list)
        self.directed = directed

    def add_edge(self, u: Any, v: Any) -> None:
        self.adj[u].append(v)
        if not self.directed:
            self.adj[v].append(u)

    def bfs(self, start: Any) -> list[Any]:
        """TH: BFS | EN: breadth-first search"""
        visited = {start}
        queue = deque([start])
        order: list[Any] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for nb in self.adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        return order

    def dfs(self, start: Any) -> list[Any]:
        """TH: DFS (iterative) | EN: depth-first search"""
        visited: set = set()
        stack = [start]
        order: list[Any] = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            order.append(node)
            for nb in reversed(self.adj[node]):
                if nb not in visited:
                    stack.append(nb)
        return order


# ─── 7) Trie ─────────────────────────────────
class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_end = False


class Trie:
    """TH: Trie สำหรับ autocomplete | EN: trie for autocomplete"""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        node = self._find(prefix)
        if node is None:
            return []
        results: list[str] = []
        self._collect(node, prefix, results, limit)
        return results

    def _collect(
        self, node: TrieNode, prefix: str,
        out: list[str], limit: int,
    ) -> None:
        if len(out) >= limit:
            return
        if node.is_end:
            out.append(prefix)
        for ch, child in node.children.items():
            self._collect(child, prefix + ch, out, limit)
```

#### 3.1.4 การใช้งาน — เลือก DS ให้ตรงงาน

| งาน | DS | ทำไม |
|---|---|---|
| LRU cache | Hash + Doubly Linked List | O(1) get/put |
| Task queue | Queue | FIFO |
| Undo | Stack | LIFO |
| Search autocomplete | Trie | O(k) prefix |
| Top-K | Heap | O(n log k) |
| Friend recommendations | Graph | BFS/DFS |
| Leaderboard | Sorted set | O(log n) rank |
| Rate limiter | Sliding window + Counter | O(1) check |
| Session store | Hash table | O(1) lookup |

---

### 3.2 Algorithms คืออะไร

**Algorithm** = **ขั้นตอนการแก้ปัญหา** ที่ชัดเจน, deterministic, มีขอบเขต, และมีประสิทธิภาพ

#### 3.2.1 ประเภท Algorithms

```
┌─────────────────────────────────────────────────────┐
│              ALGORITHM FAMILIES                     │
│                                                     │
│  Sorting          Searching       Graph             │
│  ├── Bubble       ├── Linear      ├── BFS           │
│  ├── Insertion    ├── Binary      ├── DFS           │
│  ├── Merge        ├── Hash        ├── Dijkstra      │
│  ├── Quick        └── Interp.     ├── Bellman-Ford  │
│  └── Heap                         ├── Floyd-Warshall│
│                                   ├── Topological   │
│  Dynamic Prog.    Greedy          └── MST (Kruskal) │
│  ├── Knapsack     ├── Activity                     │
│  ├── LCS          ├── Huffman                       │
│  ├── Edit Dist.   ├── Coin Change                   │
│  └── LIS          └── Interval Sched.               │
│                                                     │
│  String           Backtracking    Divide & Conquer  │
│  ├── KMP          ├── N-Queens    ├── Merge Sort    │
│  ├── Rabin-Karp   ├── Sudoku      ├── Quick Sort    │
│  ├── Z-algo       └── Subset Sum  ├── Binary Search │
│  └── Trie Match                   └── Fast Pow      │
└─────────────────────────────────────────────────────┘
```

#### 3.2.2 Algorithms Complexity

| Algorithm | Time | Space | Use Case |
|---|---|---|---|
| Linear Search | O(n) | O(1) | Unsorted |
| Binary Search | O(log n) | O(1) | Sorted |
| Merge Sort | O(n log n) | O(n) | Stable sort |
| Quick Sort | O(n log n)* | O(log n) | In-place |
| Heap Sort | O(n log n) | O(1) | In-place, no recursion |
| Counting Sort | O(n + k) | O(k) | Small range |
| Radix Sort | O(d × n) | O(n + k) | Fixed-length |
| BFS | O(V + E) | O(V) | Shortest path (unweighted) |
| DFS | O(V + E) | O(V) | Topological, cycle detect |
| Dijkstra | O((V+E) log V) | O(V) | Weighted shortest |
| Bellman-Ford | O(V × E) | O(V) | Negative edges |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs |
| Kruskal MST | O(E log E) | O(V) | Min spanning tree |

`*` = average; worst case O(n²)

#### 3.2.3 ตัวอย่าง Python

```python
# ═══════════════════════════════════════════════════════════════
# algorithms.py — Algorithms พื้นฐาน
# ═══════════════════════════════════════════════════════════════
from typing import Any, Callable, Optional
from functools import lru_cache


# ─── 1) Sorting ─────────────────────────────
def merge_sort(arr: list) -> list:
    """O(n log n) — stable"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(a: list, b: list) -> list:
    result: list = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def quick_sort(arr: list) -> list:
    """O(n log n) avg, O(n²) worst"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)


# ─── 2) Searching ───────────────────────────
def binary_search(arr: list, target: Any) -> int:
    """O(log n) — arr must be sorted"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ─── 3) Dynamic Programming ─────────────────
def longest_common_subsequence(a: str, b: str) -> int:
    """O(n×m) time, O(n×m) space"""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def edit_distance(a: str, b: str) -> int:
    """O(n×m) — Levenshtein"""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # delete
                dp[i][j - 1] + 1,        # insert
                dp[i - 1][j - 1] + cost, # replace
            )
    return dp[n][m]


def knapsack_01(weights: list[int], values: list[int], cap: int) -> int:
    """O(n × cap) — 0/1 knapsack"""
    n = len(weights)
    dp = [0] * (cap + 1)
    for i in range(n):
        for w in range(cap, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[cap]


@lru_cache(maxsize=None)
def coin_change(coins: tuple[int, ...], amount: int) -> int:
    """O(amount × len(coins)) — min coins"""
    if amount == 0:
        return 0
    if amount < 0:
        return float("inf")
    return min(
        (coin_change(coins, amount - c) + 1 for c in coins),
        default=float("inf"),
    )


# ─── 4) Greedy ──────────────────────────────
def activity_selection(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """O(n log n) — max non-overlapping intervals"""
    intervals.sort(key=lambda x: x[1])
    result: list[tuple[int, int]] = []
    last_end = -1
    for start, end in intervals:
        if start >= last_end:
            result.append((start, end))
            last_end = end
    return result


# ─── 5) Graph Algorithms ────────────────────
import heapq


def dijkstra(
    graph: dict[Any, list[tuple[Any, int]]], start: Any,
) -> dict[Any, int]:
    """O((V+E) log V) — shortest path"""
    dist: dict[Any, int] = {start: 0}
    heap: list[tuple[int, Any]] = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph.get(node, []):
            nd = d + weight
            if nd < dist.get(neighbor, float("inf")):
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))
    return dist


def topological_sort(graph: dict[Any, list[Any]]) -> list[Any]:
    """O(V + E) — Kahn's algorithm"""
    in_degree: dict[Any, int] = {n: 0 for n in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    queue = [n for n in in_degree if in_degree[n] == 0]
    result: list[Any] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return result


# ─── 6) String Algorithms ───────────────────
def kmp_search(text: str, pattern: str) -> list[int]:
    """O(n + m) — Knuth-Morris-Pratt"""
    def build_lps(p: str) -> list[int]:
        lps = [0] * len(p)
        length = 0
        i = 1
        while i < len(p):
            if p[i] == p[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length > 0:
                length = lps[length - 1]
            else:
                i += 1
        return lps

    if not pattern:
        return []
    lps = build_lps(pattern)
    matches: list[int] = []
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                matches.append(i - j)
                j = lps[j - 1]
        elif j > 0:
            j = lps[j - 1]
        else:
            i += 1
    return matches


# ─── 7) Backtracking ────────────────────────
def solve_n_queens(n: int) -> list[list[str]]:
    """O(n!) — N-Queens"""
    solutions: list[list[str]] = []
    board = [["."] * n for _ in range(n)]
    cols: set = set()
    diag1: set = set()  # row - col
    diag2: set = set()  # row + col

    def backtrack(row: int) -> None:
        if row == n:
            solutions.append(["".join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            board[row][col] = "Q"
            backtrack(row + 1)
            board[row][col] = "."
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)

    backtrack(0)
    return solutions
```

#### 3.2.4 เลือก Algorithm ให้ตรงงาน

| งาน | Algorithm | Complexity |
|---|---|---|
| Sort 10M records | Timsort | O(n log n) |
| Top-10 from stream | Min-heap size 10 | O(n log 10) |
| Shortest path map | Dijkstra / A* | O((V+E) log V) |
| Detect cycle | DFS | O(V+E) |
| Autocomplete | Trie | O(k) |
| Diff text | Myers diff / LCS | O(n×d) |
| Rate limit | Token bucket | O(1) |
| Group by | Hash map | O(n) |
| Search substring | KMP / Boyer-Moore | O(n+m) |
| Similar images | Locality Sensitive Hashing | O(1) |

---

### 3.3 Functional Programming คืออะไร

**Functional Programming (FP)** = paradigm ที่:
- ใช้ **pure functions** เป็นหลัก
- **ห้าม** แก้ state
- **compose** function เล็กเป็นใหญ่
- หลีกเลี่ยง side effects

#### 3.3.1 หลักการ FP

```
┌─────────────────────────────────────────────────────┐
│              FP CORE PRINCIPLES                     │
│                                                     │
│  1. Pure Functions                                  │
│     • input → output เท่านั้น                       │
│     • ไม่มี side effects                            │
│     • deterministic                                 │
│                                                     │
│  2. Immutability                                    │
│     • สร้างใหม่ ไม่แก้ของเก่า                       │
│     • thread-safe by default                        │
│                                                     │
│  3. Function Composition                           │
│     • f ∘ g (x) = f(g(x))                          │
│     • เล็ก → ใหญ่                                   │
│                                                     │
│  4. First-class Functions                          │
│     • function = value                              │
│     • ส่ง/คืนได้                                    │
│                                                     │
│  5. Higher-order Functions                         │
│     • รับ/คืน function                             │
│     • map, filter, reduce                          │
│                                                     │
│  6. Declarative Style                              │
│     • บอก "อะไร" ไม่ใช่ "ยังไง"                     │
│                                                     │
│  7. Referential Transparency                       │
│     • แทน expression ด้วย value ได้                 │
└─────────────────────────────────────────────────────┘
```

#### 3.3.2 Pure vs Impure

```python
# ❌ Impure — มี side effect + mutable
counter = 0

def add_impure(x):
    global counter
    counter += 1
    return x + counter


# ✅ Pure — deterministic, no side effect
def add_pure(x, y):
    return x + y


# ❌ Impure — mutate input
def append_impure(lst, x):
    lst.append(x)      # ← mutate!
    return lst


# ✅ Pure — สร้างใหม่
def append_pure(lst, x):
    return [*lst, x]
```

#### 3.3.3 FP Building Blocks

```python
# ═══════════════════════════════════════════════════════════════
# functional.py — FP patterns ใน Python
# ═══════════════════════════════════════════════════════════════
from functools import reduce, partial
from operator import add, mul
from itertools import accumulate, chain, groupby, islice
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# ─── 1) Higher-order functions ────────────────
def compose(*funcs: Callable) -> Callable:
    """TH: f ∘ g ∘ h — compose จากขวาไปซ้าย | EN: compose right-to-left"""
    def composed(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed


def pipe(*funcs: Callable) -> Callable:
    """TH: pipe จากซ้ายไปขวา | EN: pipe left-to-right"""
    def piped(x: Any) -> Any:
        for f in funcs:
            x = f(x)
        return x
    return piped


# ─── 2) Currying ─────────────────────────────
def curry2(f: Callable[[Any, Any], Any]) -> Callable[[Any], Callable[[Any], Any]]:
    """TH: แตก f(a,b) → f(a)(b) | EN: curry 2-arg function"""
    return lambda a: lambda b: f(a, b)


add_curried = curry2(add)
add5 = add_curried(5)          # partial application
assert add5(3) == 8


# ─── 3) Map / Filter / Reduce ────────────────
def pipeline_example(numbers: list[int]) -> int:
    """TH: ผลรวมของกำลังสองของเลขคู่ | EN: sum of squares of evens"""
    return reduce(
        add,
        map(lambda x: x * x, filter(lambda x: x % 2 == 0, numbers)),
        0,
    )


# ─── 4) Immutable data ──────────────────────
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class User:
    """TH: User immutable | EN: immutable User"""
    id: int
    name: str
    email: str
    role: str = "user"

    def with_role(self, role: str) -> "User":
        """TH: คืน User ใหม่ | EN: return new User"""
        return replace(self, role=role)


# ─── 5) Function composition in pipeline ────
def process_users(users: Iterable[User]) -> list[User]:
    """TH: pipeline ที่ pure | EN: pure pipeline"""
    return list(
        map(
            lambda u: u.with_role("admin"),
            filter(lambda u: u.id > 100, users),
        )
    )


# ─── 6) Lazy evaluation ─────────────────────
def fibonacci_gen():
    """TH: generator สำหรับ infinite sequence"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(n: int, iterable: Iterable[T]) -> list[T]:
    return list(islice(iterable, n))


# first 10 Fibonacci
fib10 = take(10, fibonacci_gen())
assert fib10 == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# ─── 7) Maybe / Option pattern ──────────────
from typing import Optional, Generic


class Maybe(Generic[T]):
    """TH: Maybe monad — handle None ได้ปลอดภัย | EN: Maybe monad"""

    __slots__ = ("_value",)

    def __init__(self, value: Optional[T]):
        self._value = value

    @classmethod
    def just(cls, value: T) -> "Maybe[T]":
        return cls(value)

    @classmethod
    def nothing(cls) -> "Maybe[T]":
        return cls(None)

    def is_present(self) -> bool:
        return self._value is not None

    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        if self._value is None:
            return Maybe.nothing()
        return Maybe.just(f(self._value))

    def flat_map(self, f: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        if self._value is None:
            return Maybe.nothing()
        return f(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value if self._value is not None else default


# ─── 8) Result / Either pattern ─────────────
@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err:
    error: str


Result = Ok[T] | Err


def parse_int(s: str) -> Result[int]:
    try:
        return Ok(int(s))
    except ValueError as e:
        return Err(str(e))


def divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Err("division by zero")
    return Ok(a / b)


# ─── 9) Function memoization (pure) ────────
from functools import lru_cache


@lru_cache(maxsize=128)
def fib_pure(n: int) -> int:
    """TH: pure + memoized | EN: pure + memoized"""
    return n if n < 2 else fib_pure(n - 1) + fib_pure(n - 2)


# ─── 10) Immutable updates with copy ────────
def update_nested(data: dict, path: list[str], value: Any) -> dict:
    """TH: อัปเดต nested dict โดยไม่แก้ของเดิม | EN: nested update (pure)"""
    if not path:
        return value
    key = path[0]
    child = data.get(key, {}) if isinstance(data, dict) else {}
    return {**data, key: update_nested(child, path[1:], value)}


original = {"a": {"b": {"c": 1}}}
updated = update_nested(original, ["a", "b", "c"], 42)
assert original == {"a": {"b": {"c": 1}}}    # unchanged
assert updated == {"a": {"b": {"c": 42}}}
```

#### 3.3.4 FP ในโลกจริง

| Use Case | FP Pattern |
|---|---|
| Data transformation | `map` / `filter` / `reduce` |
| API pipelines | Function composition |
| Event sourcing | Immutable events |
| Concurrency | Immutability → no locks |
| Testing | Pure functions → easy test |
| React/Redux | Reducer (pure), immutable state |
| Stream processing | `itertools`, generators |
| Error handling | `Result` / `Maybe` |

---

### 3.4 Object-Oriented Programming คืออะไร

**OOP** = paradigm ที่จัดโครงสร้างโค้ดเป็น **objects** ที่มี:
- **state** (attributes)
- **behavior** (methods)

#### 3.4.1 4 เสาหลัก OOP

```
┌─────────────────────────────────────────────────────┐
│              OOP PILLARS                            │
│                                                     │
│  1. Encapsulation                                   │
│     • ซ่อน internal state                          │
│     • expose เฉพาะ public API                      │
│     • ใช้ _protected, __private                    │
│                                                     │
│  2. Abstraction                                     │
│     • แสดงเฉพาะ "อะไร"                              │
│     • ซ่อน "ยังไง"                                  │
│     • ใช้ ABC / Protocol                           │
│                                                     │
│  3. Inheritance                                     │
│     • สืบทอด attributes/methods                     │
│     • is-a relationship                            │
│     • ระวัง: ลึกเกินไป (fragile base class)        │
│                                                     │
│  4. Polymorphism                                    │
│     • interface เดียว, behavior ต่าง               │
│     • duck typing / protocol                       │
│     • method overriding                            │
└─────────────────────────────────────────────────────┘
```

#### 3.4.2 SOLID Principles

| หลัก | ความหมาย | ตัวอย่าง |
|---|---|---|
| **S** — Single Responsibility | class ควรมีเหตุผลเดียวในการเปลี่ยน | `UserRepository` แค่ CRUD |
| **O** — Open/Closed | เปิดให้ extend, ปิดให้ modify | ใช้ strategy pattern |
| **L** — Liskov Substitution | subclass แทน superclass ได้ | `Square` ไม่ควรสืบ `Rectangle` |
| **I** — Interface Segregation | interface เล็กๆ ดีกว่าใหญ่ | `Reader` + `Writer` แยก |
| **D** — Dependency Inversion | depend on abstraction | inject repository |

#### 3.4.3 ตัวอย่าง Python

```python
# ═══════════════════════════════════════════════════════════════
# oop.py — OOP patterns
# ═══════════════════════════════════════════════════════════════
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol, runtime_checkable
from datetime import UTC, datetime


# ─── 1) Encapsulation ────────────────────────
class BankAccount:
    """TH: บัญชีธนาคาร — encapsulate balance | EN: bank account"""

    def __init__(self, owner: str, balance: Decimal = Decimal("0")):
        self._owner = owner
        self._balance = balance
        self._transactions: list[Decimal] = []

    @property
    def balance(self) -> Decimal:
        """TH: อ่านได้ แต่แก้ไม่ได้ | EN: read-only"""
        return self._balance

    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount
        self._transactions.append(amount)

    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        self._transactions.append(-amount)


# ─── 2) Abstraction (ABC) ───────────────────
class Storage(ABC):
    """TH: interface สำหรับ storage | EN: storage interface"""

    @abstractmethod
    async def save(self, key: str, value: bytes) -> None: ...

    @abstractmethod
    async def load(self, key: str) -> bytes | None: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...


class S3Storage(Storage):
    async def save(self, key: str, value: bytes) -> None:
        # S3 implementation
        ...

    async def load(self, key: str) -> bytes | None:
        ...

    async def delete(self, key: str) -> bool:
        ...


# ─── 3) Protocol (structural typing) ────────
@runtime_checkable
class Greeter(Protocol):
    """TH: protocol (duck typing) | EN: greeter protocol"""

    def greet(self, name: str) -> str: ...


class EnglishGreeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}"


class ThaiGreeter:
    def greet(self, name: str) -> str:
        return f"สวัสดี {name}"


def say_hello(g: Greeter, name: str) -> str:
    """TH: รับอะไรก็ได้ที่มี greet() | EN: accepts any Greeter"""
    return g.greet(name)


# ─── 4) Inheritance + Polymorphism ──────────
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        return f"{self.__class__.__name__}: area={self.area():.2f}"


class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h

    def perimeter(self) -> float:
        return 2 * (self.w + self.h)


class Circle(Shape):
    def __init__(self, r: float):
        self.r = r

    def area(self) -> float:
        import math
        return math.pi * self.r ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.r


# ─── 5) Composition over inheritance ────────
@dataclass
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")


@dataclass
class MetricsCollector:
    def increment(self, name: str) -> None:
        print(f"[METRIC] {name}++")


class OrderService:
    """TH: composition — has-a | EN: composition"""

    def __init__(self, logger: Logger, metrics: MetricsCollector):
        self._logger = logger
        self._metrics = metrics

    def place_order(self, order_id: str) -> None:
        self._logger.log(f"Order {order_id} placed")
        self._metrics.increment("orders.placed")


# ─── 6) Strategy Pattern ─────────────────────
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, amount: Decimal) -> Decimal: ...


class NoDiscount(DiscountStrategy):
    def apply(self, amount: Decimal) -> Decimal:
        return amount


class PercentDiscount(DiscountStrategy):
    def __init__(self, percent: Decimal):
        self.percent = percent

    def apply(self, amount: Decimal) -> Decimal:
        return amount * (1 - self.percent / 100)


class Order:
    def __init__(self, amount: Decimal, strategy: DiscountStrategy):
        self.amount = amount
        self.strategy = strategy

    def total(self) -> Decimal:
        return self.strategy.apply(self.amount)


# ─── 7) Factory Pattern ─────────────────────
class NotificationSender(ABC):
    @abstractmethod
    def send(self, to: str, msg: str) -> None: ...


class EmailSender(NotificationSender):
    def send(self, to: str, msg: str) -> None:
        print(f"Email to {to}: {msg}")


class SMSSender(NotificationSender):
    def send(self, to: str, msg: str) -> None:
        print(f"SMS to {to}: {msg}")


class NotificationFactory:
    _senders = {
        "email": EmailSender,
        "sms": SMSSender,
    }

    @classmethod
    def create(cls, channel: str) -> NotificationSender:
        sender_cls = cls._senders.get(channel)
        if sender_cls is None:
            raise ValueError(f"unknown channel: {channel}")
        return sender_cls()


# ─── 8) Repository Pattern ──────────────────
@dataclass
class UserEntity:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: int) -> UserEntity | None: ...

    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity: ...


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[int, UserEntity] = {}

    async def find_by_id(self, user_id: int) -> UserEntity | None:
        return self._store.get(user_id)

    async def save(self, user: UserEntity) -> UserEntity:
        self._store[user.id] = user
        return user


# ─── 9) Dunder methods (Pythonic OOP) ───────
class Vector:
    """TH: vector 2D ที่รองรับ + - * len str | EN: 2D vector"""

    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __len__(self) -> int:
        return 2

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"


# ─── 10) Dataclass + frozen ────────────────
@dataclass(frozen=True, slots=True)
class Money:
    """TH: Money immutable | EN: immutable Money"""
    amount: Decimal
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

#### 3.4.4 OOP Anti-patterns

| Anti-pattern | ปัญหา | Fix |
|---|---|---|
| **God Class** | class ใหญ่ 1000+ บรรทัด | แยกตาม responsibility |
| **Anemic Model** | class มีแค่ getter/setter | ย้าย logic เข้า class |
| **Deep Inheritance** | 5+ ชั้น | ใช้ composition |
| **Singleton abuse** | global state | dependency injection |
| **Feature Envy** | method ใช้ data class อื่น | ย้าย method |
| **Shotgun Surgery** | เปลี่ยน 1 feature → แก้ 10 files | รวม related code |
| **Yo-Yo Problem** | inheritance hierarchy อ่านยาก | flatten + composition |
| **Base class explosion** | มี class แม่เยอะ | trait / mixin / protocol |

---

## 4. โครงสร้าง (Structural Comparison)

### 4.1 เปรียบเทียบ 4 Paradigms

| มิติ | Data Structures | Algorithms | FP | OOP |
|---|---|---|---|---|
| **Focus** | จัดเก็บข้อมูล | ประมวลผล | Composition | Encapsulation |
| **Unit** | โครงสร้าง | ขั้นตอน | Function | Object |
| **State** | Mutable | Mutable | Immutable | Mutable |
| **Concurrency** | ต้อง lock | ต้อง lock | Thread-safe | ต้อง lock |
| **Testing** | Medium | Easy | Easy | Medium |
| **Reuse** | Low | Medium | High | High |
| **Learning curve** | Low | Medium | High | Medium |
| **Domain modeling** | - | - | Poor | Excellent |
| **Data transformation** | - | Medium | Excellent | Good |
| **Performance** | High | High | Medium | Medium |

### 4.2 เมื่อไหร่ใช้อะไร

```
┌─────────────────────────────────────────────────────┐
│              DECISION MATRIX                        │
│                                                     │
│  Use Case                    → Best Choice         │
│  ─────────────────────────────────────────────     │
│  Domain modeling             → OOP                 │
│  Data transformation         → FP                  │
│  Performance-critical        → DS + Algo           │
│  Concurrent/parallel         → FP + DS             │
│  Config/DI                   → OOP                 │
│  Stream processing           → FP                  │
│  State machine               → OOP                 │
│  Math/stats                  → FP + NumPy          │
│  API/controller              → OOP + FP            │
│  Business rules              → OOP + FP            │
│  Search/sort                 → DS + Algo           │
│  Graph problems              → Algo + DS           │
│  Cache                       → DS                  │
│  Serialization               → OOP                 │
│  Testing                     → FP (pure)           │
└─────────────────────────────────────────────────────┘
```

### 4.3 ผสมผสาน (Pragmatic Approach)

**โลกจริงไม่ใช่ pure paradigm** — ใช้ให้เหมาะ:

```python
# ═══════════════════════════════════════════════════════════════
# pragmatic.py — ผสม OOP + FP + DS + Algo
# ═══════════════════════════════════════════════════════════════
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Callable, Iterable
from decimal import Decimal


# ─── OOP: Domain model ───────────────────────
@dataclass(frozen=True)
class Order:
    id: str
    customer_id: str
    items: tuple[tuple[str, Decimal], ...]  # (sku, price)
    discount_pct: Decimal = Decimal("0")

    @property
    def subtotal(self) -> Decimal:
        return sum(p for _, p in self.items)

    def with_discount(self, pct: Decimal) -> "Order":
        return replace(self, discount_pct=pct)


# ─── FP: Pure functions ─────────────────────
def apply_discount(order: Order) -> Decimal:
    """TH: pure | EN: pure"""
    return order.subtotal * (1 - order.discount_pct / 100)


def is_high_value(order: Order) -> bool:
    """TH: pure predicate | EN: pure predicate"""
    return apply_discount(order) > Decimal("1000")


# ─── FP: Composition ────────────────────────
def pipeline(*funcs: Callable) -> Callable:
    def pipe(x):
        for f in funcs:
            x = f(x)
        return x
    return pipe


process_orders = pipeline(
    lambda orders: (o for o in orders if is_high_value(o)),
    lambda orders: sorted(orders, key=apply_discount, reverse=True),
    lambda orders: list(orders),
)


# ─── DS: Priority queue for top-K ───────────
import heapq


def top_k_orders(orders: Iterable[Order], k: int) -> list[Order]:
    """TH: top-K ด้วย heap | EN: top-K via heap"""
    heap: list = []
    for order in orders:
        total = apply_discount(order)
        if len(heap) < k:
            heapq.heappush(heap, (total, order))
        elif total > heap[0][0]:
            heapq.heapreplace(heap, (total, order))
    return [o for _, o in sorted(heap, key=lambda x: x[0], reverse=True)]


# ─── OOP: Service layer (uses FP + DS) ────
class OrderService:
    def __init__(self, repo):
        self._repo = repo

    def get_top_orders(self, customer_id: str, k: int = 10) -> list[Order]:
        orders = self._repo.find_by_customer(customer_id)
        high_value = process_orders(orders)
        return top_k_orders(high_value, k)
```

---

## 5. DDD + Clean Architecture + Modular Design

### 5.1 โครงสร้าง 4 Layer

```
┌─────────────────────────────────────────────────────┐
│  PRESENTATION (HTTP/CLI/UI)                         │
│  • FastAPI Routers · Pydantic Schemas               │
├─────────────────────────────────────────────────────┤
│  APPLICATION (Use Cases)                            │
│  • Orchestration · Ports (interfaces)               │
│  • Pure business logic (FP-style)                   │
├─────────────────────────────────────────────────────┤
│  DOMAIN (Entities/VOs/Events)                       │
│  • Pure data · No framework · No I/O                │
│  • OOP + FP mix for business rules                  │
├─────────────────────────────────────────────────────┤
│  INFRASTRUCTURE (Adapters)                          │
│  • Repositories · Vector DB · LLM clients           │
│  • DS + Algorithms heavy                            │
└─────────────────────────────────────────────────────┘
```

### 5.2 ตัวอย่างจริง

```python
# ═══════════════════════════════════════════════════════════════
# domain/entities/order.py — DOMAIN (pure)
# ═══════════════════════════════════════════════════════════════
from dataclasses import dataclass, replace
from decimal import Decimal


@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.qty


@dataclass(frozen=True)
class Order:
    id: str
    customer_id: str
    lines: tuple[OrderLine, ...]

    @property
    def subtotal(self) -> Decimal:
        return sum(line.total for line in self.lines)

    def with_discount(self, pct: Decimal) -> "Order":
        return replace(self, discount_pct=pct)


# ═══════════════════════════════════════════════════════════════
# application/use_case.py — APPLICATION (pure orchestration)
# ═══════════════════════════════════════════════════════════════
from typing import Protocol
from decimal import Decimal


class OrderRepo(Protocol):
    async def find_by_id(self, order_id: str) -> Order | None: ...
    async def save(self, order: Order) -> None: ...


class ApplyDiscountUseCase:
    """TH: Use case ที่ pure + testable | EN: pure + testable"""

    def __init__(self, repo: OrderRepo):
        self._repo = repo

    async def execute(self, order_id: str, pct: Decimal) -> Order:
        if not Decimal("0") <= pct <= Decimal("100"):
            raise ValueError("discount must be 0-100")

        order = await self._repo.find_by_id(order_id)
        if order is None:
            raise LookupError(f"order {order_id} not found")

        discounted = order.with_discount(pct)
        await self._repo.save(discounted)
        return discounted


# ═══════════════════════════════════════════════════════════════
# infrastructure/repo.py — INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════
class SqlOrderRepo:
    def __init__(self, session):
        self._session = session

    async def find_by_id(self, order_id: str) -> Order | None:
        row = await self._session.get(OrderRow, order_id)
        return self._to_entity(row) if row else None

    async def save(self, order: Order) -> None:
        ...

    def _to_entity(self, row) -> Order:
        ...
```

---

## 6. แนวทางการประยุกต์ใช้

### 6.1 เลือก Paradigm ตามงาน

| งาน | Paradigm | ตัวอย่าง |
|---|---|---|
| Domain model | OOP | `Order`, `Customer` |
| Business rules | FP | `validate`, `apply_discount` |
| Data pipeline | FP | `map/filter/reduce` |
| Search algorithm | Algo | Binary search |
| Cache | DS | LRU, TTL |
| Concurrency | FP + DS | Actor, queue |
| API layer | OOP | Controller, DI |
| Config | OOP | `Settings` |
| Serialization | OOP + FP | Pydantic + validators |
| Testing | FP | Pure functions |
| State machine | OOP + FP | Transitions |
| Event sourcing | FP | Immutable events |

### 6.2 Patterns ที่ใช้บ่อย

```python
# ═══════════════════════════════════════════════════════════════
# patterns.py — Patterns ที่ใช้ทุกวัน
# ═══════════════════════════════════════════════════════════════
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


# ─── 1) Factory ─────────────────────────────
class Parser(ABC):
    @abstractmethod
    def parse(self, raw: bytes) -> dict: ...


class JsonParser(Parser):
    def parse(self, raw: bytes) -> dict:
        import json
        return json.loads(raw)


class CsvParser(Parser):
    def parse(self, raw: bytes) -> dict:
        import csv, io
        reader = csv.DictReader(io.StringIO(raw.decode()))
        return {"rows": list(reader)}


class ParserFactory:
    _registry: dict[str, type[Parser]] = {}

    @classmethod
    def register(cls, name: str, parser_cls: type[Parser]) -> None:
        cls._registry[name] = parser_cls

    @classmethod
    def create(cls, name: str) -> Parser:
        if name not in cls._registry:
            raise ValueError(f"unknown parser: {name}")
        return cls._registry[name]()


ParserFactory.register("json", JsonParser)
ParserFactory.register("csv", CsvParser)


# ─── 2) Strategy ─────────────────────────────
class Sorter(ABC):
    @abstractmethod
    def sort(self, arr: list) -> list: ...


class QuickSorter(Sorter):
    def sort(self, arr: list) -> list:
        return sorted(arr)  # simplified


class MergeSorter(Sorter):
    def sort(self, arr: list) -> list:
        return sorted(arr)  # simplified


@dataclass
class DataProcessor:
    sorter: Sorter

    def process(self, arr: list) -> list:
        return self.sorter.sort(arr)


# ─── 3) Observer ─────────────────────────────
class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subscribers.setdefault(event, []).append(handler)

    def publish(self, event: str, payload: Any) -> None:
        for handler in self._subscribers.get(event, []):
            handler(payload)


# ─── 4) Repository ──────────────────────────
class UserRepo(Protocol):
    async def find_by_id(self, id: int) -> dict | None: ...
    async def save(self, user: dict) -> dict: ...


# ─── 5) Builder ─────────────────────────────
class QueryBuilder:
    """TH: SQL query builder | EN: SQL query builder"""

    def __init__(self, table: str):
        self._table = table
        self._where: list[str] = []
        self._limit: int | None = None
        self._order: str | None = None

    def where(self, cond: str) -> "QueryBuilder":
        self._where.append(cond)
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def order_by(self, col: str) -> "QueryBuilder":
        self._order = col
        return self

    def build(self) -> str:
        q = f"SELECT * FROM {self._table}"
        if self._where:
            q += " WHERE " + " AND ".join(self._where)
        if self._order:
            q += f" ORDER BY {self._order}"
        if self._limit is not None:
            q += f" LIMIT {self._limit}"
        return q


# ─── 6) Decorator (Python) ─────────────────
def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)):
    """TH: retry decorator | EN: retry decorator"""
    import functools
    import time

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator


# ─── 7) Pipeline (FP) ─────────────────────
def pipeline_pure(*funcs: Callable) -> Callable:
    def run(x):
        for f in funcs:
            x = f(x)
        return x
    return run


# ─── 8) Chain of Responsibility ─────────────
class Handler(ABC):
    _next: "Handler | None" = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler

    def handle(self, request: Any) -> Any:
        if self._next:
            return self._next.handle(request)
        return None


class AuthHandler(Handler):
    def handle(self, request: Any) -> Any:
        if not request.get("token"):
            raise PermissionError("no token")
        return super().handle(request)


class RateLimitHandler(Handler):
    def handle(self, request: Any) -> Any:
        if request.get("rps", 0) > 100:
            raise RuntimeError("rate limited")
        return super().handle(request)
```

---

## 7. Root Cause Analysis (Design RCA)

### 7.1 RCA Flow

```
          Bug / Incident
                │
                ▼
    ┌───────────────────────┐
    │ 1. Reproduce          │
    │ 2. Isolate            │
    │ 3. Hypothesize        │
    │ 4. Fix                │
    │ 5. Verify             │
    │ 6. Prevent            │
    └───────────────────────┘
```

### 7.2 RCA Matrix

| อาการ | Root Cause (paradigm) | Fix |
|---|---|---|
| Bugs ลดยาก | Mutating state | FP: immutable |
| Code ทดสอบไม่ได้ | Hard-coded deps | OOP: DI + Protocol |
| Performance แย่ | Wrong DS | เลือก DS ใหม่ |
| ช้าเมื่อ n โต | O(n²) | Algorithm ใหม่ |
| Concurrency bugs | Shared mutable | FP + immutable |
| God Class | Violated SRP | แยก class |
| Duplicated logic | No composition | FP: higher-order |
| Fragile inheritance | Deep hierarchy | Composition |
| Cannot mock | Concrete deps | OOP: interface |
| Serialization bugs | No schema | Pydantic + VO |

### 7.3 ตัวอย่าง RCA

```markdown
# RCA: Bug ในระบบ order

## Symptom
- Order บางรายการถูก charge 2 ครั้ง
- เกิด 0.1% ของ orders

## Timeline
- T0: Deploy v1.2.0
- T0+2h: Alert เริ่มมา
- T0+4h: Fix applied

## Investigation

### 1. Reproduce
- ต้องการ concurrent requests
- ไม่ reproduce ได้ใน single-thread

### 2. Isolate
- Code path: OrderService.place_order()
- Concurrency test → reproduce

### 3. Root Cause (5 Whys)
1. Why duplicate? → charge ถูกเรียก 2 ครั้ง
2. Why 2 ครั้ง? → idempotency key ไม่ทำงาน
3. Why ไม่ทำงาน? → `dict.get` return None ระหว่าง in-flight
4. Why? → ไม่มี lock ระหว่าง check + set
5. ROOT: → **Shared mutable state + race condition**

### 4. Fix
```python
# ❌ Before (race condition)
def process(self, key):
    if self._seen.get(key):
        return cached
    self._seen[key] = "processing"    # ← race!
    return do_work()

# ✅ After (atomic with lock)
from threading import Lock

def process(self, key):
    with self._lock:
        if self._seen.get(key):
            return cached
        self._seen[key] = "processing"
    return do_work()
```

### 5. Prevent
- [ ] Add concurrency test
- [ ] Use Redis SETNX (atomic)
- [ ] FP: immutable state
```

---

## 8. การนำไปใช้งานจริง (Production)

### 8.1 Production Readiness Checklist

```markdown
## ✅ PRODUCTION CHECKLIST — Code Quality

### Data Structures
- [ ] เลือก DS ตรงกับ access pattern
- [ ] ระบุ Big O ใน comment
- [ ] ใช้ built-in (list/dict/set) ก่อน custom
- [ ] Bounded structures (max size)

### Algorithms
- [ ] Complexity documented
- [ ] Benchmark ก่อน optimize
- [ ] Handle edge cases (empty, n=1, n=large)
- [ ] Deterministic (หรือ seed random)

### Functional Programming
- [ ] Pure functions ที่ layer in
- [ ] Immutable data structures
- [ ] ไม่มี side effects ใน domain
- [ ] Compose functions

### OOP
- [ ] SOLID principles
- [ ] Composition > Inheritance
- [ ] Interface เล็ก (ISP)
- [ ] Dependency injection
- [ ] ไม่มี god class
- [ ] Immutable where possible
```

### 8.2 Code Review Checklist

```markdown
## 🔍 CODE REVIEW — 4 PARADIGMS

### Data Structures
- [ ] `list` vs `set` เลือกถูก?
- [ ] Membership check ที่ไม่ควร O(n)?
- [ ] `dict` ใช้เป็น lookup map?
- [ ] Heap สำหรับ priority?
- [ ] Deque สำหรับ queue?

### Algorithms
- [ ] Nested loops → O(n²)?
- [ ] Sort ใน loop?
- [ ] Recursion ที่อาจ stack overflow?
- [ ] Memoization ที่ขาด?

### Functional Programming
- [ ] Function pure?
- [ ] No mutation?
- [ ] Side effects isolated?
- [ ] Composition ไม่ใช่ god function?

### OOP
- [ ] Class มี responsibility เดียว?
- [ ] สืบทอดลึกเกินไป?
- [ ] Interface segregate?
- [ ] Depends on abstraction?
```

### 8.3 Performance Monitoring

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram

FUNCTION_LATENCY = Histogram(
    "app_function_duration_seconds",
    "Function execution time",
    ["module", "function"],
    buckets=(0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10),
)

DATA_STRUCTURE_SIZE = Histogram(
    "app_ds_size",
    "Data structure size",
    ["name", "type"],
    buckets=(10, 100, 1000, 10000, 100000, 1000000),
)

PARADIGM_USAGE = Counter(
    "app_paradigm_usage_total",
    "Usage by paradigm",
    ["paradigm"],   # "oop", "fp", "algo", "ds"
)
```

### 8.4 Testing Strategy

```python
# ═══════════════════════════════════════════════════════════════
# tests/test_strategy.py — Test strategy ตาม paradigm
# ═══════════════════════════════════════════════════════════════
import pytest
from decimal import Decimal


# ─── 1) FP: Unit test แบบ pure ────────────────
def test_apply_discount_pure():
    """FP: trivial to test, no mocks"""
    order = Order(id="1", customer_id="c1", lines=(
        OrderLine("sku", 2, Decimal("10")),
    ))
    assert order.subtotal == Decimal("20")


# ─── 2) OOP: Test with DI ────────────────────
class FakeRepo:
    def __init__(self):
        self._data = {}

    async def find_by_id(self, order_id):
        return self._data.get(order_id)

    async def save(self, order):
        self._data[order.id] = order


@pytest.mark.asyncio
async def test_use_case_with_fake_repo():
    repo = FakeRepo()
    order = Order(id="1", customer_id="c1", lines=(
        OrderLine("sku", 1, Decimal("100")),
    ))
    await repo.save(order)
    uc = ApplyDiscountUseCase(repo)
    result = await uc.execute("1", Decimal("10"))
    assert result.subtotal == Decimal("100")


# ─── 3) DS/Algo: Property-based test ─────────
from hypothesis import given, strategies as st


@given(st.lists(st.integers(), min_size=0, max_size=100))
def test_merge_sort_returns_sorted(arr):
    result = merge_sort(arr)
    assert result == sorted(arr)


@given(st.lists(st.integers(), min_size=0, max_size=100))
def test_binary_search_finds(arr):
    arr = sorted(arr)
    if arr:
        target = arr[len(arr) // 2]
        assert binary_search(arr, target) >= 0


# ─── 4) Integration test ─────────────────────
@pytest.mark.integration
async def test_full_pipeline(db_session):
    # real DB
    ...
```

---

## 9. Python Code Examples

### 9.1 LRU Cache (DS + Algo + OOP)

```python
# ═══════════════════════════════════════════════════════════════
# lru_cache.py — LRU cache implementation
# ═══════════════════════════════════════════════════════════════
from collections import OrderedDict
from typing import Any, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """TH: LRU cache ด้วย OrderedDict | EN: LRU cache with OrderedDict"""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._cap = capacity
        self._cache: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)     # O(1)
        return self._cache[key]

    def put(self, key: K, value: V) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._cap:
            self._cache.popitem(last=False)   # O(1)


# ─── Functional version ─────────────────────
from functools import lru_cache


@lru_cache(maxsize=128)
def expensive_compute(n: int) -> int:
    """TH: memoization ด้วย lru_cache | EN: memoization"""
    return sum(i * i for i in range(n))
```

### 9.2 Event Sourcing (FP + OOP)

```python
# ═══════════════════════════════════════════════════════════════
# event_sourcing.py — Event sourcing
# ═══════════════════════════════════════════════════════════════
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import Union


# ─── Events (immutable) ─────────────────────
@dataclass(frozen=True)
class AccountOpened:
    account_id: str
    owner: str
    at: datetime = datetime.now(UTC) if False else None  # placeholder


@dataclass(frozen=True)
class MoneyDeposited:
    account_id: str
    amount: Decimal
    at: datetime = None  # type: ignore


@dataclass(frozen=True)
class MoneyWithdrawn:
    account_id: str
    amount: Decimal
    at: datetime = None  # type: ignore


Event = Union[AccountOpened, MoneyDeposited, MoneyWithdrawn]


# ─── State (immutable) ──────────────────────
@dataclass(frozen=True)
class AccountState:
    id: str
    owner: str
    balance: Decimal


# ─── Reducer (pure) ─────────────────────────
def apply_event(state: AccountState | None, event: Event) -> AccountState:
    """TH: pure reducer | EN: pure reducer"""
    if isinstance(event, AccountOpened):
        return AccountState(id=event.account_id, owner=event.owner, balance=Decimal("0"))
    if state is None:
        raise ValueError("state must exist")
    if isinstance(event, MoneyDeposited):
        return replace(state, balance=state.balance + event.amount)
    if isinstance(event, MoneyWithdrawn):
        if event.amount > state.balance:
            raise ValueError("insufficient funds")
        return replace(state, balance=state.balance - event.amount)
    return state


def rebuild(events: list[Event]) -> AccountState:
    """TH: rebuild state จาก events | EN: rebuild state"""
    from functools import reduce
    state: AccountState | None = None
    for event in events:
        state = apply_event(state, event)
    if state is None:
        raise ValueError("no events")
    return state
```

### 9.3 Pipeline Processing (FP)

```python
# ═══════════════════════════════════════════════════════════════
# pipeline.py — FP pipeline
# ═══════════════════════════════════════════════════════════════
from functools import reduce
from operator import add
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def pipeline(*funcs: Callable) -> Callable:
    """TH: compose ซ้ายไปขวา | EN: left-to-right compose"""
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


# ─── Example: ETL ────────────────────────────
def extract(raw: str) -> list[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def parse(lines: list[str]) -> list[tuple[str, int]]:
    out = []
    for line in lines:
        parts = line.split(",")
        if len(parts) == 2:
            try:
                out.append((parts[0], int(parts[1])))
            except ValueError:
                continue
    return out


def filter_positive(data: list[tuple[str, int]]) -> list[tuple[str, int]]:
    return [(k, v) for k, v in data if v > 0]


def aggregate(data: list[tuple[str, int]]) -> dict[str, int]:
    from collections import defaultdict
    result = defaultdict(int)
    for k, v in data:
        result[k] += v
    return dict(result)


# ─── Compose ────────────────────────────────
etl = pipeline(extract, parse, filter_positive, aggregate)

raw = """
apple,10
banana,-5
apple,20
cherry,15
"""
result = etl(raw)
# {'apple': 30, 'cherry': 15}
```

### 9.4 Priority Queue with Custom Ordering (Algo + OOP)

```python
# ═══════════════════════════════════════════════════════════════
# priority_queue.py
# ═══════════════════════════════════════════════════════════════
import heapq
from dataclasses import dataclass, field
from itertools import count
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    """TH: item ที่เรียงตาม priority | EN: priority item"""
    priority: int
    counter: int = field(compare=False)
    data: Any = field(compare=False)


class PriorityQueue:
    """TH: priority queue (stable) | EN: stable priority queue"""

    _counter = count()

    def __init__(self):
        self._heap: list[PrioritizedItem] = []

    def push(self, item: Any, priority: int) -> None:
        heapq.heappush(
            self._heap,
            PrioritizedItem(priority, next(self._counter), item),
        )

    def pop(self) -> Any:
        if not self._heap:
            raise IndexError("pop from empty queue")
        return heapq.heappop(self._heap).data

    def __len__(self) -> int:
        return len(self._heap)
```

---

## 10. AI/ML Skill (Code Assistant)

### 10.1 Skill Interface

```python
# app/skills/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SkillContext:
    tenant_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SkillResult:
    success: bool
    output: Any = None
    error: str | None = None
    latency_ms: int = 0


class BaseSkill(ABC):
    name: str = "base"
    description: str = ""

    @abstractmethod
    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult: ...
```

### 10.2 Skill: Suggest Data Structure

```python
# app/skills/suggest_ds.py
"""TH: แนะนำ DS จาก use case | EN: suggest DS from use case"""
import ast
import re
import time
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


RULES = [
    {
        "keywords": ["lru", "cache", "evict"],
        "suggest": "OrderedDict / Hash + Doubly Linked List",
        "complexity": "O(1) get/put",
    },
    {
        "keywords": ["priority", "top-k", "min", "max"],
        "suggest": "heapq (Min Heap)",
        "complexity": "O(log n) push/pop",
    },
    {
        "keywords": ["fifo", "queue", "task"],
        "suggest": "collections.deque",
        "complexity": "O(1) enqueue/dequeue",
    },
    {
        "keywords": ["lifo", "undo", "stack"],
        "suggest": "list (append/pop)",
        "complexity": "O(1) push/pop",
    },
    {
        "keywords": ["lookup", "map", "index"],
        "suggest": "dict / set",
        "complexity": "O(1) average",
    },
    {
        "keywords": ["sorted", "range", "rank"],
        "suggest": "sortedcontainers.SortedList",
        "complexity": "O(log n) insert, O(log n) range",
    },
    {
        "keywords": ["prefix", "autocomplete"],
        "suggest": "Trie",
        "complexity": "O(k) k=key length",
    },
    {
        "keywords": ["graph", "network", "path"],
        "suggest": "Adjacency List (defaultdict)",
        "complexity": "O(V+E)",
    },
]


class SuggestDataStructureSkill(BaseSkill):
    name = "suggest_ds"
    description = "Suggest data structure from requirements."
    parameters = {
        "text": {"type": "string", "required": True},
    }

    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        t0 = time.monotonic()
        try:
            text = kwargs["text"].lower()
            matches = []
            for rule in RULES:
                if any(kw in text for kw in rule["keywords"]):
                    matches.append({
                        "suggestion": rule["suggest"],
                        "complexity": rule["complexity"],
                    })
            return SkillResult(
                success=True,
                output={"matches": matches, "count": len(matches)},
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return SkillResult(success=False, error=str(e))
```

### 10.3 Skill: Refactor Suggester

```python
# app/skills/refactor.py
"""TH: แนะนำ refactor | EN: suggest refactoring"""
import ast
import re
import time
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


class RefactorSuggesterSkill(BaseSkill):
    name = "suggest_refactor"
    description = "Suggest refactoring based on code smells."

    PATTERNS = [
        (r"for\s+\w+\s+in\s+\w+:\s*\n\s+.*in\s+\w+\s*:", 
         "Use set for membership → O(1)"),
        (r"\w+\s*\+=\s*.*\n.*for\s+", 
         "Use ''.join() → O(n) instead of O(n²)"),
        (r"for\s+.*:\s*\n.*for\s+.*:", 
         "Nested loop → try hash map or sort+pointer"),
        (r"sorted\(.*\)\s*\n.*for\s+", 
         "Sort inside loop → move outside"),
        (r"def\s+\w+\([^)]*\):\s*\n(?:.*\n){50,}", 
         "Function > 50 lines → extract smaller functions"),
        (r"class\s+\w+[^\n]*:\s*\n(?:.*\n){200,}", 
         "Class > 200 lines → split by responsibility"),
        (r"def\s+\w+\(self[^)]*\):\s*\n(?:.*\n){30,}", 
         "Method > 30 lines → extract"),
        (r"if\s+.*:\s*\n(?:.*\n){20,}", 
         "Long if block → consider polymorphism"),
    ]

    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        t0 = time.monotonic()
        try:
            code = kwargs["code"]
            suggestions = []
            for pattern, hint in self.PATTERNS:
                if re.search(pattern, code, re.MULTILINE):
                    suggestions.append(hint)

            # detect functional opportunities
            if "for" in code and ".append" in code:
                suggestions.append(
                    "Loop + append → consider list comprehension or map/filter"
                )

            # detect mutable default
            if re.search(r"def \w+\([^)]*=\s*(\[\]|\{\})", code):
                suggestions.append(
                    "Mutable default arg → use None + init inside"
                )

            return SkillResult(
                success=True,
                output={"suggestions": suggestions, "count": len(suggestions)},
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return SkillResult(success=False, error=str(e))
```

### 10.4 Skill Registry + Integration

```python
# app/skills/registry.py
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    def all_specs(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": {
                        "type": "object",
                        "properties": getattr(s, "parameters", {}),
                        "required": [
                            k for k, v in getattr(s, "parameters", {}).items()
                            if isinstance(v, dict) and v.get("required")
                        ],
                    },
                },
            }
            for s in self._skills.values()
        ]

    async def execute(
        self, ctx: SkillContext, name: str, **kwargs: Any
    ) -> SkillResult:
        skill = self._skills.get(name)
        if skill is None:
            return SkillResult(success=False, error=f"unknown skill: {name}")
        return await skill.execute(ctx, **kwargs)


# ─── Demo ───
import asyncio


async def main() -> None:
    from app.skills.suggest_ds import SuggestDataStructureSkill
    from app.skills.refactor import RefactorSuggesterSkill

    registry = SkillRegistry()
    registry.register(SuggestDataStructureSkill())
    registry.register(RefactorSuggesterSkill())

    ctx = SkillContext(tenant_id="demo")

    r1 = await registry.execute(
        ctx, "suggest_ds",
        text="Need LRU cache with O(1) evict for top-10 users",
    )
    print(r1.output)

    r2 = await registry.execute(
        ctx, "suggest_refactor",
        code="""
def process(items, check):
    for x in items:
        if x in check:
            print(x)
    s = ""
    for x in items:
        s += str(x)
    return s
""",
    )
    print(r2.output)


if __name__ == "__main__":
    asyncio.run(main())
```

**ผลลัพธ์:**
```json
{
  "matches": [
    {"suggestion": "OrderedDict / Hash + Doubly Linked List", "complexity": "O(1) get/put"},
    {"suggestion": "heapq (Min Heap)", "complexity": "O(log n) push/pop"}
  ],
  "count": 2
}
{
  "suggestions": [
    "Use set for membership → O(1)",
    "Use ''.join() → O(n) instead of O(n²)",
    "Loop + append → consider list comprehension or map/filter"
  ],
  "count": 3
}
```

---

## 11. ปัญหาและแนวทางแก้ไข

### 11.1 ตาราง Anti-patterns รวม

| # | Anti-pattern | Paradigm | ปัญหา | Fix |
|---|---|---|---|---|
| 1 | `x in list` | DS | O(n) | `x in set` |
| 2 | String `+=` loop | DS | O(n²) | `"".join()` |
| 3 | Nested loop | Algo | O(n²) | Hash map / sort+pointer |
| 4 | Recursion ไม่มี memo | Algo | O(2ⁿ) | `@lru_cache` |
| 5 | Mutable default arg | FP | Shared state bug | `None` + init |
| 6 | Mutate shared state | FP | Race condition | Immutable + copy |
| 7 | God Class | OOP | Test/maintain ยาก | แยก SRP |
| 8 | Deep inheritance | OOP | Fragile | Composition |
| 9 | Concrete dep | OOP | Mock ยาก | Protocol / DI |
| 10 | Anemic model | OOP | Logic กระจาย | ย้ายเข้า class |
| 11 | Copy ใหญ่ไม่จำเป็น | FP | Memory | `replace()` / shared |
| 12 | Sort ใน loop | Algo | O(n² log n) | Sort นอก loop |
| 13 | String concat ใน loop | DS | O(n²) | list + join |
| 14 | Lambda ซับซ้อน | FP | อ่านยาก | Named function |
| 15 | Recursion depth สูง | Algo | Stack overflow | Iterative |
| 16 | No type hints | OOP+FP | บั๊กตอน runtime | `mypy` |
| 17 | Catch-all except | All | ซ่อนบั๊ก | Specific exception |
| 18 | Global state | OOP+FP | Test ยาก | DI |

### 11.2 Decision Tree — เลือก Paradigm

```
ปัญหา
  │
  ├── มี state ไหม?
  │     │
  │     ├── Yes → จัดการ state ที่ OOP boundary
  │     └── No  → ใช้ FP
  │
  ├── คำนวณหนักไหม?
  │     │
  │     ├── Yes → Algo + DS
  │     └── No  → Composable FP
  │
  ├── Concurrency?
  │     │
  │     ├── Yes → Immutable + FP
  │     └── No  → Mutate OK
  │
  └── Domain modeling?
        │
        ├── Yes → OOP + DDD
        └── No  → FP
```

### 11.3 Quick Wins

```python
# ─── 1) list → set (10-1000x) ────────────────
# ❌
for x in items:
    if x in existing_list:    # O(n)
        ...
# ✅
existing_set = set(existing_list)
for x in items:
    if x in existing_set:     # O(1)
        ...

# ─── 2) string += → join (10-1000x) ────────
# ❌
s = ""
for x in items:
    s += str(x)
# ✅
s = "".join(str(x) for x in items)

# ─── 3) recursion → memo ────────────────────
# ❌
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
# ✅
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

# ─── 4) nested loop → hash ──────────────────
# ❌
def find_common(a, b):
    return [x for x in a if x in b]  # O(n×m)
# ✅
def find_common(a, b):
    set_b = set(b)
    return [x for x in a if x in set_b]  # O(n+m)

# ─── 5) mutate → copy ───────────────────────
# ❌
def add_role(user, role):
    user.roles.append(role)  # mutate!
    return user
# ✅ (frozen dataclass)
def add_role(user, role):
    from dataclasses import replace
    return replace(user, roles=(*user.roles, role))
```

### 11.4 RCA Playbooks

#### PB-1: Bug หายากใน production

```markdown
## Diagnose
1. มี mutating state? → FP fix
2. มี concurrent access? → Lock / actor
3. Test coverage ต่ำ? → Add integration test

## Common Causes
- Shared mutable dict/set
- Global variable
- Class attribute ที่ควร instance
- Mutable default argument
```

#### PB-2: Code ใหญ่เกินไป

```markdown
## Diagnose
1. Class > 500 บรรทัด? → SRP violated
2. Function > 50 บรรทัด? → Extract
3. Cyclomatic > 15? → Split

## Fix
- Extract Method
- Extract Class
- Introduce Parameter Object
- Replace Conditional with Polymorphism
```

#### PB-3: Performance ไม่ผ่าน

```markdown
## Diagnose
1. Profile ก่อน
2. Identify hotspot
3. วิเคราะห์ Big O
4. Benchmark alternative

## Fix Order
1. Algorithm (O(n²) → O(n log n))
2. Data structure (list → set)
3. Caching (memo)
4. Micro-opt (loop unroll)
```

---

## 12. สรุป

### 12.1 ภาพรวม

```
┌─────────────────────────────────────────────────────┐
│          LEARNING PATH                              │
│                                                     │
│  Junior: DS/A basics + เขียน OOP ได้                │
│      ↓                                              │
│  Mid: อ่าน code review + FP composition            │
│      ↓                                              │
│  Senior: เลือก paradigm + ออกแบบ DS/Algo           │
│      ↓                                              │
│  Lead: Architecture + trade-off                     │
│      ↓                                              │
│  Architect: Governance + enterprise patterns        │
└─────────────────────────────────────────────────────┘
```

### 12.2 Key Takeaways

| # | บทเรียน | ทำไมสำคัญ |
|---|---|---|
| 1 | **DS = พื้นฐานทุกอย่าง** | 50% performance มาจาก DS |
| 2 | **Algorithm = ลด complexity** | O(n²) → O(n log n) |
| 3 | **FP = ลด bugs** | Pure + immutable |
| 4 | **OOP = model domain** | Encapsulation + polymorphism |
| 5 | **ผสมกัน ไม่ใช่เลือก** | Pragmatic > dogmatic |
| 6 | **Composition > Inheritance** | ยืดหยุ่นกว่า |
| 7 | **Immutability default** | Thread-safe + testable |
| 8 | **Measure ก่อน optimize** | อย่าเดา |
| 9 | **Pattern > reinvention** | Factory, Strategy, Repository |
| 10 | **Test ทุก paradigm** | Unit + property + integration |

### 12.3 Checklist ใช้งานจริง

```markdown
## ✅ DAILY CHECKLIST

### Data Structures
- [ ] `set` สำหรับ membership
- [ ] `dict` สำหรับ lookup
- [ ] `deque` สำหรับ queue
- [ ] `heapq` สำหรับ priority
- [ ] `defaultdict` สำหรับ group

### Algorithms
- [ ] ระบุ Big O
- [ ] ไม่มี nested loop ถ้าเลี่ยงได้
- [ ] Sort นอก loop
- [ ] Memoize recursion
- [ ] Test edge cases

### Functional
- [ ] Pure ที่ layer in
- [ ] Immutable data
- [ ] Compose functions
- [ ] No side effects
- [ ] Lazy เมื่อได้

### OOP
- [ ] SRP ทุก class
- [ ] DI ไม่ใช่ hard-code
- [ ] Interface เล็ก
- [ ] Composition > Inheritance
- [ ] Frozen dataclass ที่ทำได้

### Production
- [ ] Type hints ครบ
- [ ] Metrics + logs
- [ ] Test coverage ≥ 80%
- [ ] Benchmarked
- [ ] Documented
```

### 12.4 Roadmap 12 สัปดาห์

```markdown
## Week 1-2: Data Structures
- Array, List, Stack, Queue
- Hash table, Set
- Tree, Heap
- Graph, Trie
- Practice: LeetCode Easy

## Week 3-4: Algorithms
- Sorting (merge, quick, heap)
- Searching (binary, BFS, DFS)
- DP (knapsack, LCS, edit)
- Greedy, Backtracking
- Practice: LeetCode Medium

## Week 5-6: Functional Programming
- Pure functions
- Immutability
- map/filter/reduce
- Composition, currying
- Monad (Maybe, Result)
- Practice: Refactor code ด้วย FP

## Week 7-8: OOP
- SOLID
- Design patterns (GoF)
- Composition > Inheritance
- Protocol / ABC
- DI + Repository
- Practice: Implement patterns

## Week 9-10: Integration
- DDD + Clean Architecture
- Layered design
- Testing strategy
- Refactoring legacy
- Practice: Real project

## Week 11-12: Production
- Performance tuning
- Profiling
- RCA
- Monitoring
- Practice: Optimize real system
```

### 12.5 ทรัพยากร

#### 📚 หนังสือ
- **"Introduction to Algorithms"** (CLRS)
- **"Grokking Algorithms"** — Aditya Bhargava
- **"Functional Programming in Python"** — David Mertz
- **"Design Patterns"** — Gang of Four
- **"Clean Code"** — Robert C. Martin
- **"Refactoring"** — Martin Fowler
- **"Domain-Driven Design"** — Eric Evans

#### 🎓 คอร์ส
- **MIT 6.006** — Algorithms
- **Princeton Algorithms** — Coursera
- **SICP** — Structure and Interpretation
- **Functional Programming in Scala** — Coursera

#### 🛠️ Libraries
- **`dataclasses`** — immutable VOs
- **`functools`** — `lru_cache`, `partial`, `reduce`
- **`itertools`** — lazy iterators
- **`collections`** — `deque`, `Counter`, `defaultdict`
- **`heapq`** — priority queue
- **`sortedcontainers`** — sorted list/dict
- **`pydantic`** — validation + immutability
- **`hypothesis`** — property-based testing

#### 🧪 Practice
- **LeetCode** — problems
- **NeetCode 150** — curated
- **Exercism** — languages
- **Advent of Code** — fun

### 12.6 คำส่งท้าย

> **"ไม่มีการ paradigm ที่ดีที่สุด — มีแต่ paradigm ที่เหมาะกับงาน"**
>
> **Data Structures** = วิธีเก็บ → เลือกให้ตรง access
> **Algorithms** = วิธีคิด → เลือกให้ตรง complexity
> **FP** = วิธีประกอบ → เลือกให้ตรง data flow
> **OOP** = วิธี model → เลือกให้ตรง domain
>
> **Pro tip:** เขียน FP ที่ core, ใช้ OOP ที่ boundary, DS/Algo ที่ hotspot

---

**📌 Version:** 1.0 · **Last Updated:** 2026-09-24 · **License:** Internal Use
**📧 Feedback:** ส่ง PR หรือ issue ผ่าน repo ภายใน
**🔗 Related:** `llm_opencode_promt.md` · `Big-O-Guide.md` · `RAG-Production-Guide.md`
