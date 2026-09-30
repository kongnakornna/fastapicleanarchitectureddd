# 📚 คู่มือ Big O Notation ฉบับ Production-Ready

> **เวอร์ชัน:** 1.0 · **ระดับ:** Beginner → Advanced · **กลุ่มเป้าหมาย:** Software Engineer, Data Engineer, Backend Developer, System Architect
> **Stack:** Python 3.11+ · TypeScript · SQL · Distributed Systems
> **ใช้กับ:** Algorithm Design · Database Query · System Design · Code Review · Capacity Planning

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [บทนิยาม](#2-บทนิยาม)
3. [บทหัวข้อ (Big O)](#3-บทหัวข้อ-big-o)
4. [โครงสร้าง (Complexity Classes)](#4-โครงสร้าง-complexity-classes)
5. [หลักการวิเคราะห์ (Analysis Patterns)](#5-หลักการวิเคราะห์-analysis-patterns)
6. [แนวทางการประยุกต์ใช้](#6-แนวทางการประยุกต์ใช้)
7. [Root Cause Analysis (Performance RCA)](#7-root-cause-analysis-performance-rca)
8. [การนำไปใช้งานจริง (Production)](#8-การนำไปใช้งานจริง-production)
9. [Python Code Examples](#9-python-code-examples)
10. [AI/ML Skill (Complexity Analysis)](#10-aiml-skill-complexity-analysis)
11. [ปัญหาและแนวทางแก้ไข](#11-ปัญหาและแนวทางแก้ไข)
12. [สรุป](#12-สรุป)

---

## 1. บทนำ

### 1.1 ทำไมต้องเข้าใจ Big O?

ในโลกจริง ไม่มีใครสนใจว่าโค้ดรัน 3ms หรือ 5ms — แต่ทุกคนสนใจว่าโค้ดจะ **รันได้หรือไม่เมื่อ scale ขึ้น 100x**

| สถานการณ์ | โค้ดไม่เข้าใจ Big O | โค้ดเข้าใจ Big O |
|---|---|---|
| Users 100 คน | ✅ เร็ว | ✅ เร็ว |
| Users 10,000 คน | ⚠️ ช้า (5s) | ✅ เร็ว |
| Users 1,000,000 คน | ❌ ล่ม | ✅ ยังเร็ว |
| ข้อมูล 10GB | ❌ OOM | ✅ stream/chunk |
| DB 100M rows | ❌ timeout | ✅ index + partition |

**Big O = ภาษากลางที่บอกว่า "algorithm นี้จะแย่แค่ไหนเมื่อข้อมูลโตขึ้น"**

### 1.2 ขอบเขตของคู่มือ

คู่มือนี้ครอบคลุม:

- ✅ **ทฤษฎี** Big O, Θ, Ω, amortized, space complexity
- ✅ **การวิเคราะห์** อ่านโค้ด → อนุมาน complexity
- ✅ **Data Structures** Array, Hash, Tree, Graph, Heap
- ✅ **Algorithms** Sorting, Searching, DP, Greedy
- ✅ **Production** Database, API, Distributed System
- ✅ **เครื่องมือ** Profiling, Benchmarking, RCA
- ✅ **Patterns** Optimization playbook, Anti-patterns

**ไม่ครอบคลุม:** Formal proofs, advanced complexity theory (P vs NP, circuit complexity)

### 1.3 กลุ่มเป้าหมาย

| ระดับ | ได้อะไร |
|---|---|
| **Junior** | อ่านโค้ด → บอก complexity ได้ |
| **Mid** | เลือก data structure / algorithm ถูก |
| **Senior** | ออกแบบ system ที่ scale ได้ |
| **Architect** | Capacity planning, trade-off analysis |
| **Interview** | ผ่าน FAANG-style coding interview |

---

## 2. บทนิยาม

### 2.1 คำศัพท์พื้นฐาน

| คำ | ความหมาย | ตัวอย่าง |
|---|---|---|
| **Algorithm** | ขั้นตอนการแก้ปัญหา | Binary search |
| **Complexity** | ความซับซ้อน (เวลา/พื้นที่) | O(log n) |
| **Input Size (n)** | ขนาดข้อมูลเข้า | จำนวน elements |
| **Time Complexity** | เวลาที่ใช้เป็นฟังก์ชันของ n | O(n²) |
| **Space Complexity** | หน่วยความจำที่ใช้ | O(n) |
| **Asymptotic** | พฤติกรรมเมื่อ n → ∞ | ไม่สนใจ constant |
| **Worst Case** | กรณีแย่สุด | O(n) |
| **Average Case** | กรณีเฉลี่ย | Θ(n) |
| **Best Case** | กรณีดีสุด | Ω(1) |
| **Amortized** | เฉลี่ยระยะยาว | O(1) amortized |

### 2.2 Notation (สัญลักษณ์)

#### O (Big O) — Upper Bound

**ความหมาย:** "โตไม่เกิน..." — ขอบเขตบน

```
f(n) = O(g(n))  ⟺  ∃ c, n₀ : f(n) ≤ c·g(n) สำหรับ n ≥ n₀
```

**ใช้เมื่อ:** บอก worst case

```python
# O(n) — บอกว่า "แย่สุดคือ n"
def find_max(arr):
    return max(arr)
```

#### Ω (Big Omega) — Lower Bound

**ความหมาย:** "โตอย่างน้อย..." — ขอบเขตล่าง

```
f(n) = Ω(g(n))  ⟺  ∃ c, n₀ : f(n) ≥ c·g(n) สำหรับ n ≥ n₀
```

**ใช้เมื่อ:** บอก best case

```python
# Ω(1) — best case ของ linear search (เจอตัวแรก)
def linear_search(arr, x):
    for v in arr:
        if v == x:
            return True    # ← Ω(1) ถ้าเจอตัวแรก
    return False
```

#### Θ (Big Theta) — Tight Bound

**ความหมาย:** "โตเท่ากับ..." — ขอบเขตกระชับ (ทั้งบนและล่าง)

```
f(n) = Θ(g(n))  ⟺  f(n) = O(g(n)) และ f(n) = Ω(g(n))
```

**ใช้เมื่อ:** บอก tight bound ที่แน่นอน

```python
# Θ(n) — ทุกกรณีคือ n
def sum_all(arr):
    total = 0
    for v in arr:              # ทุก element
        total += v
    return total
```

#### o (Little o) — Strict Upper

**ความหมาย:** "โตช้ากว่า..." (strict)

```
f(n) = o(g(n))  ⟺  lim(n→∞) f(n)/g(n) = 0
```

**ตัวอย่าง:** `n = o(n²)` แต่ `2n ≠ o(n)`

### 2.3 Complexity Classes (ตารางเทียบ)

| Notation | ชื่อ | ตัวอย่าง | n=10 | n=100 | n=1,000 | n=1M |
|---|---|---|---|---|---|---|
| **O(1)** | Constant | Array access | 1 | 1 | 1 | 1 |
| **O(log n)** | Logarithmic | Binary search | 3 | 7 | 10 | 20 |
| **O(n)** | Linear | Linear scan | 10 | 100 | 1,000 | 1M |
| **O(n log n)** | Linearithmic | Merge sort | 33 | 664 | 10k | 20M |
| **O(n²)** | Quadratic | Bubble sort | 100 | 10k | 1M | 💀 |
| **O(n³)** | Cubic | Matrix mult (naive) | 1k | 1M | 1B | 💀💀 |
| **O(2ⁿ)** | Exponential | Subset sum | 1k | 💀 | 💀 | 💀 |
| **O(n!)** | Factorial | TSP brute force | 3.6M | 💀 | 💀 | 💀 |

**หมายเหตุ:** ตัวเลข = จำนวน operations โดยประมาณ

---

## 3. บทหัวข้อ (Big O)

### 3.1 Big O คืออะไร

**Big O Notation** = **ภาษาคณิตศาสตร์** ที่ใช้บอกว่า algorithm จะ **ช้าแค่ไหน** เมื่อ input โตขึ้น

คำถามที่ Big O ตอบ:
- ❓ "โค้ดนี้จะรันไหวไหมถ้า user โต 100x?"
- ❓ "Algorithm A เร็วกว่า B ที่ n เท่าไหร่?"
- ❓ "ควรใช้ hash map หรือ sorted array?"
- ❓ "ทำไม query นี้ช้าจัง?"

คำถามที่ Big O **ไม่** ตอบ:
- ❌ "โค้ดนี้รันกี่ ms?" → ต้อง benchmark
- ❌ "ใช้ memory เท่าไหร่จริงๆ?" → ต้อง profile
- ❌ "จะ work บน production ไหม?" → ต้อง load test

### 3.2 Big O ทำงานอย่างไร

#### 3.2.1 กฎการลดรูป (Simplification Rules)

**Rule 1: ตัด Constant**

```
O(2n)      → O(n)
O(5n + 3)  → O(n)
O(1000)    → O(1)
```

**Rule 2: เอา Term ที่โตสุด**

```
O(n² + n)     → O(n²)
O(n³ + n²)    → O(n³)
O(2ⁿ + n¹⁰⁰)  → O(2ⁿ)   ← exponential ชนะทุกอย่าง
```

**Rule 3: แต่ละ Statement ใช้ O(1)**

```python
x = 1              # O(1)
y = x + 1          # O(1)
print(y)           # O(1)
# รวม = O(1) + O(1) + O(1) = O(1)
```

**Rule 4: Loop = คูณด้วยจำนวนรอบ**

```python
for i in range(n):     # รัน n ครั้ง
    print(i)           # O(1) ต่อรอบ
# รวม = O(n)
```

**Rule 5: Nested Loop = คูณ**

```python
for i in range(n):         # n ครั้ง
    for j in range(n):     # n ครั้ง
        print(i, j)        # O(1)
# รวม = O(n × n) = O(n²)
```

**Rule 6: Sequential Blocks = บวก แล้วเอาตัวโต**

```python
for i in range(n):     # O(n)
    pass
for j in range(n):     # O(n)
    pass
# รวม = O(n) + O(n) = O(2n) = O(n)
```

**Rule 7: ครึ่งๆ (n/2) ก็คือ O(n)**

```python
for i in range(n // 2):   # n/2 ครั้ง
    pass
# O(n/2) = O(n)
```

**Rule 8: log n — เมื่อ input ถูกหารครึ่งทุกครั้ง**

```python
while n > 1:
    n = n // 2         # หาร 2 ทุกครั้ง
# รัน log₂(n) ครั้ง → O(log n)
```

#### 3.2.2 ตัวอย่างการวิเคราะห์

```python
# ─── ตัวอย่าง 1: O(1) ─────────────────────────
def get_first(arr):
    return arr[0]                  # O(1)


# ─── ตัวอย่าง 2: O(n) ─────────────────────────
def find_max(arr):
    best = arr[0]                  # O(1)
    for x in arr:                  # n ครั้ง
        if x > best:               # O(1)
            best = x               # O(1)
    return best                    # O(1)
# Total: O(1) + O(n) + O(1) = O(n)


# ─── ตัวอย่าง 3: O(n²) ────────────────────────
def has_duplicate_naive(arr):
    for i in range(len(arr)):          # n
        for j in range(i + 1, len(arr)):   # ~n/2
            if arr[i] == arr[j]:       # O(1)
                return True
    return False
# Total: O(n × n/2) = O(n²)


# ─── ตัวอย่าง 4: O(n) ด้วย Set ────────────────
def has_duplicate_fast(arr):
    seen = set()                       # O(1)
    for x in arr:                      # n
        if x in seen:                  # O(1) average
            return True
        seen.add(x)                    # O(1) average
    return False
# Total: O(n) ← ดีกว่า O(n²) มาก


# ─── ตัวอย่าง 5: O(log n) ─────────────────────
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1           # O(1)
    while lo <= hi:                    # log₂(n) ครั้ง
        mid = (lo + hi) // 2           # O(1)
        if arr[mid] == target:         # O(1)
            return mid
        elif arr[mid] < target:        # O(1)
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# Total: O(log n)


# ─── ตัวอย่าง 6: O(n log n) ───────────────────
def merge_sort(arr):
    if len(arr) <= 1:                  # O(1)
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])       # T(n/2)
    right = merge_sort(arr[mid:])      # T(n/2)
    return merge(left, right)          # O(n)
# T(n) = 2T(n/2) + O(n) = O(n log n)  [Master Theorem]
```

### 3.3 การใช้งาน

#### 3.3.1 ใช้ตอน Code Review

```markdown
## Code Review Checklist (Performance)

- [ ] Nested loops → เช็คว่า O(n²) หรือแย่กว่าไหม?
- [ ] `in` operator บน list vs set → O(n) vs O(1)
- [ ] String concatenation ใน loop → ควรใช้ list + join
- [ ] Recursive ไม่มี memo → exponential?
- [ ] Sort ใน loop → O(n² log n)?
- [ ] DB query ใน loop → N+1 problem
- [ ] Sorting แล้ว search → ไม่ควร O(n log n) + O(n) ถ้าใช้ set ได้ O(n)
```

#### 3.3.2 ใช้ตอนเลือก Data Structure

| งาน | Data Structure | Complexity |
|---|---|---|
| Access by index | Array | O(1) |
| Search by value | Hash Map | O(1) avg |
| Sorted iteration | Sorted Array / BST | O(n) / O(n) |
| Insert at end | Array / Deque | O(1) |
| Insert at middle | Linked List | O(1) ถ้ารู้ pointer |
| Min/Max | Heap | O(1) peek, O(log n) pop |
| Prefix search | Trie | O(k) k=ความยาว |
| Range query | Segment Tree | O(log n) |
| Nearest neighbor | KD-Tree / Ball Tree | O(log n) avg |

#### 3.3.3 ใช้ตอน Capacity Planning

**ตัวอย่าง:** ออกแบบ API ต้องรองรับ 10,000 RPS

```python
# ─── Naive: O(n) per request ─────────────────
def get_user(users, user_id):       # n = 10M users
    for u in users:
        if u.id == user_id:
            return u
# 10M × 10k RPS = 10¹¹ ops/sec → 💀

# ─── Fast: O(1) per request ──────────────────
def get_user(users_map, user_id):
    return users_map.get(user_id)   # O(1)
# 10k RPS × 1 op = 10⁴ ops/sec → ✅
```

**เครื่องมือคำนวณ:**
- ถ้า CPU = 10⁹ ops/sec
- O(n) ที่ n = 10⁶ → 1ms
- O(n²) ที่ n = 10⁶ → 10⁹ ms = 11 วัน 💀

### 3.4 ข้อดีของ Big O

| ข้อดี | รายละเอียด |
|---|---|
| ✅ **Platform-independent** | ไม่ขึ้นกับ CPU/RAM |
| ✅ **Predictive** | ทำนายก่อนรันได้ |
| ✅ **Comparable** | เทียบ algorithm ได้ |
| ✅ **Scale-aware** | บอกได้ว่าจะรอดถึง n เท่าไหร่ |
| ✅ **Interview-ready** | ทุกบริษัทใช้ |
| ✅ **Documentation** | สื่อสารในทีมได้ |
| ✅ **Design tool** | ใช้ตอนออกแบบ system |

### 3.5 ข้อเสียของ Big O

| ข้อเสีย | รายละเอียด | ตัวอย่าง |
|---|---|---|
| ❌ **Ignore constants** | O(n) ที่ n=10 อาจช้ากว่า O(n²) ที่ n=10 | Small n: insertion sort ชนะ quick sort |
| ❌ **Worst case only** | ไม่บอก average | Quick sort worst O(n²), avg O(n log n) |
| ❌ **No cache effects** | ไม่คิด cache miss | Array vs Linked list |
| ❌ **No parallelism** | ไม่คิด multi-core | GPU O(n²) อาจชนะ CPU O(n) |
| ❌ **No I/O cost** | ไม่คิด disk/network | DB query ≠ memory access |
| ❌ **Asymptotic only** | ไม่บอก n จริงในprod | n = 100 อาจไม่ต้อง optimize |
| ❌ **Ignores data distribution** | assume random | Real data ≠ uniform |
| ❌ **No language overhead** | Python ≠ C | Python loop ช้ากว่า C 100x |

### 3.6 ข้อควรระวัง / ข้อห้าม / ข้อจำกัด

#### 🚫 ข้อห้าม (Never Do)

```markdown
❌ ห้าม optimize โดยไม่วัดก่อน (premature optimization)
❌ ห้ามใช้ O(n²) กับ n > 10,000 ถ้าเลี่ยงได้
❌ ห้ามใช้ O(2ⁿ) กับ n > 30 (จะไม่มีวันเสร็จ)
❌ ห้ามเขียน recursion ไม่มี base case
❌ ห้ามใช้ `list` เป็น membership check ใน loop
❌ ห้าม string += ใน loop (Python)
❌ ห้าม sort ใน loop
❌ ห้ามเรียก DB query ใน loop (N+1 problem)
❌ ห้าม assume O(1) โดยไม่ดู implementation
❌ ห้าม assume hash เป็น O(1) เสมอ (worst case = O(n))
```

#### ⚠️ ข้อควรระวัง (Be Careful)

| หัวข้อ | ความเสี่ยง | แนวทาง |
|---|---|---|
| **Hash collision** | O(1) → O(n) | ใช้ key ที่ hash ดี |
| **Recursion depth** | Stack overflow | ใช้ iterative หรือเพิ่ม limit |
| **Amortized vs worst** | dict insert = O(1) amortized แต่บางครั้ง O(n) | รู้ความหมาย |
| **Sort stability** | เรียงไม่คงที่ | ใช้ `key=` parameter |
| **Floating point** | เปรียบเทียบผิด | ใช้ epsilon |
| **Hidden loops** | `x in dict` = O(1) แต่ `x in list` = O(n) | รู้ data structure |
| **Generator vs list** | list สร้าง memory | ใช้ generator |
| **Copy overhead** | slice = O(k) | หลีกเลี่ยง slice ใน loop |
| **Hash of mutable** | dict key ต้อง immutable | ใช้ tuple ไม่ใช่ list |
| **Integer overflow** | ในบางภาษา | Python ไม่มี แต่ภาษาอื่นมี |

#### 📏 ข้อจำกัด (Hard Limits)

| Resource | ขีดจำกัดปฏิบัติ |
|---|---|
| RAM access | ~10⁻⁹ sec |
| Disk read | ~10⁻³ sec (10⁶x ช้ากว่า RAM) |
| Network | ~10⁻² sec (10⁷x ช้ากว่า RAM) |
| Practical O(n²) limit | n ≤ 10,000 |
| Practical O(n³) limit | n ≤ 500 |
| Practical O(2ⁿ) limit | n ≤ 25 |
| Recursion depth | ~1,000 (Python default) |
| Max container size | 2⁶³ - 1 (Python int) |

### 3.7 สรุปบทหัวข้อ

- **Big O** = ภาษาบอก scale ของ algorithm
- **O/Ω/Θ** = upper/lower/tight bound
- **กฎหลัก** = ตัด constant, เอา term โตสุด
- **ใช้กับ** code review, เลือก DS, capacity planning
- **ข้อจำกัด** = ignore constant, cache, I/O
- **ข้อห้ามหลัก** = premature optimization

---

## 4. โครงสร้าง (Complexity Classes)

### 4.1 โครงสร้างคืออะไร

**Complexity Classes** = กลุ่มของ algorithm ที่มี growth rate เดียวกัน

```
                Growth Rate (n → ∞)
Fast  ←───────────────────────────────────→  Slow
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)
```

### 4.2 โครงสร้างทำงานอย่างไร

#### 4.2.1 O(1) — Constant

**特徴:** ไม่ขึ้นกับ n เลย

```python
# ✅ O(1) examples
arr[0]                    # index access
hash_map[key]             # hash lookup avg
len(arr)                  # length
stack.pop()               # pop
dict.get(key)             # get
```

**เมื่อไหร่:** ทำงานกับ element เดียว

#### 4.2.2 O(log n) — Logarithmic

**特徴:** หารครึ่งทุกครั้ง

```python
# ✅ O(log n) examples
def binary_search(arr, x):        # sorted array
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

# Height of balanced BST = log n
# Search in balanced BST = O(log n)
# heap push/pop = O(log n)
```

**เมื่อไหร่:** ข้อมูล sorted + หารครึ่งได้

#### 4.2.3 O(n) — Linear

**特徴:** ผ่านทุก element 1 ครั้ง

```python
# ✅ O(n) examples
def find_max(arr):
    best = arr[0]
    for x in arr:
        if x > best:
            best = x
    return best

sum(arr)                     # sum
"".join(list_of_strings)     # join
list(generator)              # materialize
arr.copy()                   # copy
```

**เมื่อไหร่:** ต้องดูทุก element 1 ครั้ง

#### 4.2.4 O(n log n) — Linearithmic

**特徴:** หารครึ่ง (log n) × ประมวลผลทุกตัว (n)

```python
# ✅ O(n log n) examples
sorted(arr)                  # Timsort
list.sort()                  # in-place sort
heapq.nlargest(k, arr)       # top-k

# Merge sort: T(n) = 2T(n/2) + O(n) = O(n log n)
# Quick sort avg: O(n log n)
```

**เมื่อไหร่:** Sorting, divide & conquer ที่ต้องสัมผัสทุก element

#### 4.2.5 O(n²) — Quadratic

**特徴:** Loop ซ้อน loop, pair ทุกคู่

```python
# ❌ O(n²) anti-patterns
def has_duplicate_slow(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                return True
    return False

# Bubble sort, selection sort, insertion sort (worst)
# String concatenation ใน loop (Python)
s = ""
for x in arr:
    s += str(x)              # ← O(n²)! ควรใช้ "".join()
```

**เมื่อไหร่:** เปรียบเทียบทุกคู่, ตาราง 2D

#### 4.2.6 O(n³) — Cubic

**特徴:** Loop 3 ชั้น

```python
# O(n³)
def matrix_mult_naive(A, B):
    n = len(A)
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C
# Matrix mult (naive): n³
# Floyd-Warshall: n³
```

**เมื่อไหร่:** 3 มิติ, graph algorithms

#### 4.2.7 O(2ⁿ) — Exponential

**特徴:** แบ่งเป็น 2 ทาง ทุกครั้ง

```python
# O(2ⁿ) — Fibonacci naive
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n-1) + fib_naive(n-2)

# Subset sum, Tower of Hanoi
# TSP brute force (จริงๆ คือ n!)
```

**เมื่อไหร่:** ทดสอบทุก subset (ต้องมี memoization)

#### 4.2.8 O(n!) — Factorial

**特徴:** Permutation ทั้งหมด

```python
# O(n!) — generate permutations
from itertools import permutations
list(permutations(range(n)))  # n! items

# TSP brute force: n!
# n = 10 → 3.6M
# n = 15 → 1.3T 💀
```

**เมื่อไหร่:** เฉพาะ n < 10

### 4.3 โครงสร้างการใช้งาน (เทียบ Data Structures)

#### 4.3.1 Python Collections

| Operation | list | deque | dict | set | heapq |
|---|---|---|---|---|---|
| **Access by index** | O(1) | O(n) | - | - | - |
| **Search by value** | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| **Insert at end** | O(1)* | O(1) | O(1)* | O(1)* | O(log n) |
| **Insert at front** | O(n) | O(1) | - | - | - |
| **Delete by value** | O(n) | O(n) | O(1)* | O(1)* | - |
| **Pop min** | O(n) | O(n) | - | - | O(log n) |
| **Peek min** | O(n) | O(n) | - | - | O(1) |
| **Sorted iteration** | O(n log n) | - | - | - | O(n log n) |
| **Memory** | ต่ำ | ต่ำ | สูง | สูง | ต่ำ |

`*` = amortized / average case

#### 4.3.2 Tree Structures

| Operation | BST (unbalanced) | AVL/RB | B-Tree | Trie |
|---|---|---|---|---|
| **Search** | O(n) worst | O(log n) | O(log n) | O(k) |
| **Insert** | O(n) worst | O(log n) | O(log n) | O(k) |
| **Delete** | O(n) worst | O(log n) | O(log n) | O(k) |
| **Range query** | O(n) | O(log n + k) | O(log n + k) | - |
| **Min/Max** | O(n) | O(log n) | O(log n) | - |

`k` = ความยาว key/prefix

#### 4.3.3 Graph Representations

| Operation | Adjacency List | Adjacency Matrix |
|---|---|---|
| **Space** | O(V + E) | O(V²) |
| **Add edge** | O(1) | O(1) |
| **Remove edge** | O(V) | O(1) |
| **Check edge** | O(deg(v)) | O(1) |
| **Iterate neighbors** | O(deg(v)) | O(V) |
| **BFS/DFS** | O(V + E) | O(V²) |

**ใช้เมื่อ:**
- Sparse graph (E ≈ V) → List
- Dense graph (E ≈ V²) → Matrix

### 4.4 สรุปโครงสร้าง

```
┌──────────────────────────────────────────────────────────┐
│                  COMPLEXITY LANDSCAPE                    │
│                                                          │
│  O(1)         ●─────  ยอดเยี่ยม                          │
│  O(log n)     ●─────  ดีมาก                              │
│  O(n)         ●─────  ดี                                 │
│  O(n log n)   ●─────  ยอมรับได้ (sorting)               │
│  O(n²)        ●─────  ระวัง (n > 10k)                    │
│  O(n³)        ●─────  อันตราย (n > 500)                  │
│  O(2ⁿ)        ●─────  ห้าม (n > 25)                      │
│  O(n!)        ●─────  ห้าม (n > 10)                      │
└──────────────────────────────────────────────────────────┘
```

---

## 5. หลักการวิเคราะห์ (Analysis Patterns)

### 5.1 Master Theorem

**ใช้กับ:** Recurrence T(n) = aT(n/b) + f(n)

```
T(n) = a·T(n/b) + O(n^d)

Case 1: d < log_b(a)  →  T(n) = O(n^(log_b a))
Case 2: d = log_b(a)  →  T(n) = O(n^d · log n)
Case 3: d > log_b(a)  →  T(n) = O(n^d)
```

**ตัวอย่าง:**

| Recurrence | a | b | d | log_b(a) | Result |
|---|---|---|---|---|---|
| T(n) = 2T(n/2) + O(n) | 2 | 2 | 1 | 1 | O(n log n) |
| T(n) = 2T(n/2) + O(1) | 2 | 2 | 0 | 1 | O(n) |
| T(n) = 8T(n/2) + O(n²) | 8 | 2 | 2 | 3 | O(n³) |
| T(n) = T(n/2) + O(n) | 1 | 2 | 1 | 0 | O(n) |
| T(n) = 2T(n/2) + O(n²) | 2 | 2 | 2 | 1 | O(n²) |

### 5.2 Amortized Analysis

**ความหมาย:** เฉลี่ยระยะยาว ไม่ใช่ worst case ต่อ operation

**ตัวอย่าง — Dynamic Array (Python list):**

```python
# Python list: append = O(1) amortized
arr = []
for i in range(n):
    arr.append(i)         # ← บางครั้ง resize O(n)
# Total: n appends + log n resizes
# = n × O(1) + O(1 + 2 + 4 + ... + n) = O(n)
# → per append = O(n) / n = O(1) amortized
```

**เทคนิค:**
- **Aggregate method** — total / count
- **Accounting method** — charge extra "credit"
- **Potential method** — ใช้ potential function

### 5.3 Best/Average/Worst Case

**ตัวอย่าง — Quick Sort:**

| Case | เมื่อไหร่ | Complexity |
|---|---|---|
| **Best** | Pivot = median | O(n log n) |
| **Average** | Pivot สุ่ม | O(n log n) |
| **Worst** | Pivot = min/max (sorted input!) | O(n²) |

**การรับมือ:**
- ใช้ random pivot
- ใช้ median-of-3
- Introsort (Python Timsort): fallback to merge sort

### 5.4 Space Complexity

**นับอะไร:**
- Variables
- Data structures
- Recursion stack
- Input (ถ้าไม่ count input → "auxiliary space")

**ตัวอย่าง:**

```python
# O(1) space — in-place
def reverse_inplace(arr):
    i, j = 0, len(arr) - 1
    while i < j:
        arr[i], arr[j] = arr[j], arr[i]
        i += 1
        j -= 1

# O(n) space — สร้างใหม่
def reverse_copy(arr):
    return arr[::-1]              # ← O(n) space

# O(log n) space — recursion depth
def binary_search_rec(arr, x, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == x:
        return mid
    elif arr[mid] < x:
        return binary_search_rec(arr, x, mid+1, hi)   # depth = log n
    else:
        return binary_search_rec(arr, x, lo, mid-1)
```

### 5.5 ตัวช่วยวิเคราะห์

#### 5.5.1 Table Method (นับ operations)

```python
def example(n):
    total = 0                      # 1
    for i in range(n):             # n + 1 (check)
        total += i                 # n
    for j in range(n):             # n + 1
        for k in range(n):         # n × (n + 1)
            total += j * k         # n²
    return total                   # 1
# Total: 1 + (n+1) + n + (n+1) + n(n+1) + n² + 1
#      = 2n² + 4n + 4
#      = O(n²)
```

#### 5.5.2 Recursion Tree

```
T(n) = 2T(n/2) + O(n)

Level 0:       [n]              ← O(n)
              /   \
Level 1:    [n/2] [n/2]         ← O(n)
           /  \   /  \
Level 2: [n/4][n/4][n/4][n/4]   ← O(n)
              ...
Level log n: [1][1][1][1]...    ← O(n)

Total per level: O(n)
Number of levels: log n
Total: O(n log n)
```

---

## 6. แนวทางการประยุกต์ใช้

### 6.1 Optimization Playbook

```
ปัญหา: โค้ดช้า
         │
         ▼
    ┌────────────────────┐
    │ 1. Profile ก่อน    │  ← ห้ามเดา!
    │    (cProfile)      │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 2. ระบุ hotspot    │  ← 80/20 rule
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 3. วิเคราะห์ Big O │
    └────────┬───────────┘
             │
    ┌────────┴───────────┐
    │                    │
    ▼                    ▼
Algorithm          Data Structure
เปลี่ยนวิธี       เปลี่ยน DS
    │                    │
    └────────┬───────────┘
             ▼
    ┌────────────────────┐
    │ 4. Benchmark       │
    │    (timeit)        │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 5. Verify + Monitor│
    └────────────────────┘
```

### 6.2 ตัวอย่าง Optimization จริง

#### Case 1: O(n²) → O(n)

```python
# ❌ Before: O(n²)
def find_common_slow(list1, list2):
    common = []
    for x in list1:            # n
        if x in list2:         # O(m) — list search
            common.append(x)
    return common
# Total: O(n × m)

# ✅ After: O(n + m)
def find_common_fast(list1, list2):
    set2 = set(list2)          # O(m)
    return [x for x in list1 if x in set2]   # O(n) × O(1)
# Total: O(n + m)
```

**Speedup:** n = m = 10,000 → 100M ops → 20k ops = **5,000x เร็วขึ้น!**

#### Case 2: Recursion → DP

```python
# ❌ Before: O(2ⁿ) — Fibonacci
def fib_slow(n):
    if n <= 1:
        return n
    return fib_slow(n-1) + fib_slow(n-2)

# ✅ After: O(n) — DP bottom-up
def fib_fast(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# หรือ memoization
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    return n if n <= 1 else fib_memo(n-1) + fib_memo(n-2)
```

**Speedup:** n = 40 → 2⁴⁰ ≈ 10¹² ops → 40 ops = **2.5×10¹⁰x**

#### Case 3: String Concatenation

```python
# ❌ Before: O(n²)
def build_string_slow(items):
    s = ""
    for item in items:         # n
        s += str(item)         # O(len(s)) — copy
    return s
# Total: O(n²) — แต่ละครั้ง copy string

# ✅ After: O(n)
def build_string_fast(items):
    return "".join(str(x) for x in items)
# Total: O(n)
```

**Speedup:** n = 100,000 → 10¹⁰ ops → 10⁵ ops = **100,000x**

#### Case 4: N+1 Query Problem

```python
# ❌ Before: N+1 queries
def get_users_with_orders_slow(db, user_ids):
    users = []
    for uid in user_ids:                # N users
        user = db.get_user(uid)         # 1 query each
        user.orders = db.get_orders(uid)  # 1 more query!
        users.append(user)
    return users
# Total: 1 + N + N = O(2N + 1) queries
# แต่ network I/O แพง → 2N × 50ms = 100N ms

# ✅ After: 2 queries
def get_users_with_orders_fast(db, user_ids):
    users = db.get_users_batch(user_ids)          # 1 query
    orders = db.get_orders_batch(user_ids)        # 1 query
    by_user = defaultdict(list)
    for o in orders:
        by_user[o.user_id].append(o)
    for u in users:
        u.orders = by_user[u.id]
    return users
# Total: 2 queries = 100ms
```

**Speedup:** N = 1,000 → 100,000ms → 100ms = **1,000x**

### 6.3 เลือก Algorithm ตาม Problem

| Problem | Naive | Optimal | Structure |
|---|---|---|---|
| Two Sum | O(n²) | O(n) | Hash map |
| Three Sum | O(n³) | O(n²) | Sort + two pointer |
| Longest subarray sum | O(n²) | O(n) | Sliding window |
| Search sorted | O(n) | O(log n) | Binary search |
| Sort | O(n²) | O(n log n) | Timsort/Merge |
| Top-K | O(n log n) | O(n log k) | Heap |
| LCS | O(2ⁿ) | O(nm) | DP |
| Edit distance | O(3ⁿ) | O(nm) | DP |
| Shortest path (unweighted) | O(V²) | O(V + E) | BFS |
| Shortest path (weighted) | O(V²) | O(E log V) | Dijkstra + heap |
| MST | O(E·V) | O(E log V) | Kruskal + union-find |

### 6.4 Cache และ Big O

**Cache ช่วยลด Big O ในการปฏิบัติ แต่ไม่เปลี่ยน theoretical**

```python
# Theoretical: O(2ⁿ)
# With memoization: O(n)
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive(n):
    return expensive(n-1) + expensive(n-2)
```

**Cache patterns:**

| Pattern | Use Case |
|---|---|
| **LRU** | Recent access มีประโยชน์ |
| **LFU** | Frequency สูง |
| **TTL** | Data เก่าออก |
| **Write-through** | Consistency สูง |
| **Write-back** | Performance สูง |

### 6.5 Parallelism

**Amdahl's Law:** Speedup ≤ 1 / (s + p/N)
- s = serial fraction
- p = parallel fraction
- N = processors

```python
# Sequential: O(n)
total = sum(huge_list)

# Parallel: O(n / P) โดย P = #cores
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as ex:
    chunks = [huge_list[i::4] for i in range(4)]
    results = ex.map(sum, chunks)
    total = sum(results)
```

**ข้อควรระวัง:**
- Overhead การ spawn process
- GIL ใน Python (ใช้ ProcessPoolExecutor สำหรับ CPU-bound)
- I/O bound ใช้ asyncio

---

## 7. Root Cause Analysis (Performance RCA)

### 7.1 Performance RCA Flow

```
        Production ช้า
              │
              ▼
    ┌─────────────────────┐
    │ 1. Measure          │  ← ไม่เดา!
    │    • Latency p50/p95│
    │    • Throughput     │
    │    • CPU/Mem/IO     │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ 2. Profile          │  ← cProfile, py-spy
    │    • Hot functions  │
    │    • Call graph     │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ 3. Analyze Big O    │
    │    • Per function   │
    │    • Per endpoint   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ 4. Hypothesize      │
    │    "O(n²) → O(n)"   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ 5. Fix + Verify     │
    │    Benchmark before │
    │    Benchmark after  │
    └─────────────────────┘
```

### 7.2 เครื่องมือ Profiling

#### 7.2.1 cProfile

```python
import cProfile
import pstats

def slow_function():
    return sum(i*i for i in range(1_000_000))

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    slow_function()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)   # top 10
```

**Output:**
```
ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
     1    0.045    0.045    0.045    0.045  {built-in method builtins.sum}
```

#### 7.2.2 py-spy (Sampling)

```bash
# Real-time profile (ไม่ต้องแก้โค้ด)
py-spy top --pid 12345

# Flame graph
py-spy record -o profile.svg -- python app.py

# Dump
py-spy dump --pid 12345
```

#### 7.2.3 timeit (Micro-benchmark)

```python
import timeit

# เทียบ 2 implementations
slow = """
result = []
for x in data:
    if x in check:
        result.append(x)
"""

fast = """
check_set = set(check)
result = [x for x in data if x in check_set]
"""

print("Slow:", timeit.timeit(slow, setup="data = list(range(1000)); check = list(range(500))", number=1000))
print("Fast:", timeit.timeit(fast, setup="data = list(range(1000)); check = list(range(500))", number=1000))
```

#### 7.2.4 line_profiler

```python
# ติดตั้ง: pip install line_profiler
@profile
def my_function():
    a = 1
    for i in range(1000):
        a += i
    return a

# รัน: kernprof -l -v script.py
```

### 7.3 RCA Case Studies

#### Case 1: API endpoint ช้า (2s → 200ms)

**อาการ:** `/api/users/report` p95 = 2s

**RCA:**
```
1. Measure: p95 = 2s, CPU = 80%
2. Profile: 90% time ใน `get_user_stats()`
3. Analyze: 
   for u in users:              # n = 10,000
       stats = get_orders(u)    # O(m) DB query
   → O(n × m) = O(n²) effectively
4. Hypothesize: Batch query
5. Fix: 
   - 1 query: SELECT user_id, COUNT(*) FROM orders GROUP BY user_id
   - Map result → user
6. Verify: 2s → 200ms = 10x
```

#### Case 2: Memory leak (RAM โตไม่หยุด)

**RCA:**
```
1. Measure: RAM +50MB/hour
2. Profile: tracemalloc
3. Analyze:
   cache = {}
   def process(key):
       cache[key] = expensive(key)   # ← ไม่มี eviction
   → O(n) memory ที่ n = request count
4. Fix: LRU cache with maxsize
   @lru_cache(maxsize=1000)
5. Verify: RAM stable
```

#### Case 3: Query timeout (10s)

**RCA:**
```
1. Measure: EXPLAIN ANALYZE
2. Analyze: 
   SELECT * FROM orders WHERE user_id IN (SELECT ...)
   → Nested loop without index
3. Fix:
   - Add index on orders(user_id)
   - หรือ materialized view
4. Verify: 10s → 50ms = 200x
```

### 7.4 RCA Template

```markdown
# Performance RCA Report

## 1. Symptom
- **Endpoint:** /api/users/report
- **Latency:** p95 = 2,000ms (SLA < 500ms)
- **Impact:** Users complain
- **Severity:** P1

## 2. Data Collected
- p50 = 800ms, p99 = 5,000ms
- CPU = 80%, Memory = 60%
- Query log: 10,001 queries per request

## 3. Root Cause (5 Whys)
1. Why slow? → 10,001 queries
2. Why many queries? → Loop over users
3. Why loop? → Code เขียนแบบ N+1
4. Why N+1? → ไม่รู้จัก batch query
5. ROOT: → ขาด code review pattern สำหรับ DB

## 4. Big O Analysis
- Before: O(n × m) — n users × m orders
- Target: O(n + m) — 2 queries total

## 5. Fix
```python
# Before
for user in users:
    user.orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")

# After
users = db.query("SELECT * FROM users WHERE id IN (...)")
orders = db.query("SELECT * FROM orders WHERE user_id IN (...)")
```

## 6. Verification
- Benchmark before: 2,000ms
- Benchmark after: 200ms
- Speedup: 10x

## 7. Prevention
- [ ] เพิ่ม lint rule: ห้าม DB query ใน loop
- [ ] เพิ่ม test: query count ≤ 5 ต่อ request
- [ ] Add EXPLAIN ANALYZE check ใน CI
```

---

## 8. การนำไปใช้งานจริง (Production)

### 8.1 Big O ใน Database

#### 8.1.1 Index = ลด Big O

| Operation | No Index | With Index |
|---|---|---|
| SELECT WHERE id = ? | O(n) | O(log n) |
| SELECT WHERE range | O(n) | O(log n + k) |
| JOIN | O(n × m) | O(n log m) |
| ORDER BY | O(n log n) | O(n) ถ้า index ตรง |
| GROUP BY | O(n log n) | O(n) |

**ตัวอย่าง:**
```sql
-- ❌ O(n) — full table scan
SELECT * FROM users WHERE email = 'a@b.com';

-- ✅ O(log n) — index scan
CREATE INDEX idx_users_email ON users(email);
```

#### 8.1.2 EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id)
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;

-- Output:
-- HashAggregate  (cost=...) (actual time=...)
--   -> Hash Join  (cost=...) (actual time=...)    ← O(n + m)
--        Hash Cond: (o.user_id = u.id)
--        -> Seq Scan on orders                    ← O(n)
--        -> Hash                                   ← O(m)
```

**สัญญาณเตือน:**
- `Seq Scan` บน large table → ต้อง index
- `Nested Loop` กับ large tables → O(n × m)
- `Sort` กับ huge data → memory spill

### 8.2 Big O ใน API Design

#### 8.2.1 Pagination

```python
# ❌ O(n) memory — โหลดทั้งหมด
@app.get("/users")
def list_users():
    return db.query("SELECT * FROM users").all()   # n = 1M 💀

# ✅ O(page_size) — cursor-based
@app.get("/users")
def list_users(cursor: str = None, limit: int = 50):
    query = "SELECT * FROM users WHERE id > %s ORDER BY id LIMIT %s"
    return db.query(query, [cursor or 0, limit])
```

**Complexity:**
| Pattern | Time | Space |
|---|---|---|
| Full load | O(n) | O(n) |
| Offset pagination | O(offset + limit) | O(limit) |
| Cursor pagination | O(log n + limit) | O(limit) |

#### 8.2.2 Rate Limiting

```python
# Sliding window — O(1) per request
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests: int, window: int):
        self.max = max_requests
        self.window = window
        self.requests = deque()   # timestamps

    def allow(self) -> bool:
        now = time.time()
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()   # O(1)
        if len(self.requests) < self.max:
            self.requests.append(now) # O(1)
            return True
        return False
```

### 8.3 Big O ใน Distributed System

#### 8.3.1 MapReduce

```
Input: n records
Map: O(n) — parallel across P workers → O(n/P)
Shuffle: O(n log n) — sort
Reduce: O(n) — aggregate
Total: O(n log n / P)
```

#### 8.3.2 Load Balancing

| Algorithm | Complexity | Fairness |
|---|---|---|
| Round Robin | O(1) | Fair |
| Least Connections | O(n) | Better |
| Consistent Hash | O(log n) | Sticky |
| Random | O(1) | Fair |

### 8.4 Big O ใน Caching

```python
# LRU Cache — O(1) get/put
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)   # O(1)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)   # O(1)
```

### 8.5 Capacity Planning Table

**CPU = 10⁹ ops/sec (1 GHz effective)**

| Complexity | n = 100 | n = 1K | n = 10K | n = 100K | n = 1M |
|---|---|---|---|---|---|
| O(1) | 1ns | 1ns | 1ns | 1ns | 1ns |
| O(log n) | 7ns | 10ns | 13ns | 17ns | 20ns |
| O(n) | 100ns | 1μs | 10μs | 100μs | 1ms |
| O(n log n) | 700ns | 10μs | 130μs | 1.7ms | 20ms |
| O(n²) | 10μs | 1ms | 100ms | 10s | 16min 💀 |
| O(n³) | 1ms | 1s | 100s | 11days 💀 | 💀 |
| O(2ⁿ) | 💀 | 💀 | 💀 | 💀 | 💀 |

**อ่านตาราง:**
- ถ้า SLA = 100ms
- O(n²) รอดถึง n ≈ 10,000
- O(n³) รอดถึง n ≈ 500
- O(n) รอดถึง n ≈ 100M

---

## 9. Python Code Examples

### 9.1 Two Sum — O(n²) → O(n)

```python
# ═══════════════════════════════════════════════════════════════
# two_sum.py — หาคู่ที่บวกได้ target
# ═══════════════════════════════════════════════════════════════
from typing import Optional


def two_sum_brute(nums: list[int], target: int) -> Optional[tuple[int, int]]:
    """O(n²) time, O(1) space — brute force"""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None


def two_sum_hash(nums: list[int], target: int) -> Optional[tuple[int, int]]:
    """O(n) time, O(n) space — hash map"""
    seen: dict[int, int] = {}
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:      # O(1)
            return (seen[complement], i)
        seen[x] = i
    return None


# ─── Benchmark ───
import timeit
n = 10_000
data = list(range(n))
target = n + n - 1

print("Brute:", timeit.timeit(lambda: two_sum_brute(data, target), number=1))
# ~10s

print("Hash:", timeit.timeit(lambda: two_sum_hash(data, target), number=1))
# ~1ms

# Speedup ~10,000x
```

### 9.2 Fibonacci — 5 แบบ

```python
# ═══════════════════════════════════════════════════════════════
# fibonacci.py — เปรียบเทียบ 5 implementations
# ═══════════════════════════════════════════════════════════════
from functools import lru_cache


# 1) Naive recursion — O(2ⁿ)
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# 2) Memoization (top-down) — O(n)
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


# 3) Bottom-up DP — O(n) time, O(n) space
def fib_dp(n: int) -> int:
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


# 4) Space-optimized DP — O(n) time, O(1) space
def fib_optimal(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# 5) Matrix exponentiation — O(log n)
def fib_matrix(n: int) -> int:
    def mat_mul(A, B):
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
        ]

    def mat_pow(M, p):
        result = [[1, 0], [0, 1]]
        while p > 0:
            if p & 1:
                result = mat_mul(result, M)
            M = mat_mul(M, M)
            p >>= 1
        return result

    if n <= 1:
        return n
    base = [[1, 1], [1, 0]]
    result = mat_pow(base, n)
    return result[0][1]


# ─── Benchmark n = 30 ───
import timeit
n = 30
for name, fn in [
    ("naive", fib_naive),
    ("memo", fib_memo),
    ("dp", fib_dp),
    ("optimal", fib_optimal),
    ("matrix", fib_matrix),
]:
    t = timeit.timeit(lambda: fn(n), number=10) / 10
    print(f"{name:10s}: {t*1000:.4f}ms")
# naive   : 500.0000ms  ← O(2³⁰) ≈ 10⁹ ops
# memo    : 0.0005ms    ← O(30)
# dp      : 0.0020ms    ← O(30)
# optimal : 0.0010ms    ← O(30)
# matrix  : 0.0100ms    ← O(log 30)
```

### 9.3 Sort — เปรียบเทียบ

```python
# ═══════════════════════════════════════════════════════════════
# sorting.py — เรียงลำดับด้วย algorithms ต่างๆ
# ═══════════════════════════════════════════════════════════════
import random
import timeit
from typing import Callable


def bubble_sort(arr: list[int]) -> list[int]:
    """O(n²) — แย่สุด"""
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr: list[int]) -> list[int]:
    """O(n²) worst, O(n) best — ดีกับ nearly sorted"""
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr: list[int]) -> list[int]:
    """O(n log n) — stable"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(a: list[int], b: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def quick_sort(arr: list[int]) -> list[int]:
    """O(n log n) avg, O(n²) worst"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)


def python_sort(arr: list[int]) -> list[int]:
    """O(n log n) — Timsort (optimal)"""
    return sorted(arr)


# ─── Benchmark ───
random.seed(42)
data = [random.randint(0, 10_000) for _ in range(1_000)]

for name, fn in [
    ("bubble", bubble_sort),
    ("insertion", insertion_sort),
    ("merge", merge_sort),
    ("quick", quick_sort),
    ("python", python_sort),
]:
    t = timeit.timeit(lambda: fn(data), number=1)
    print(f"{name:10s}: {t*1000:.2f}ms")
# bubble    : 80.00ms
# insertion : 35.00ms
# merge     : 3.00ms
# quick     : 2.50ms
# python    : 0.20ms  ← Timsort fastest
```

### 9.4 Data Structure Comparison

```python
# ═══════════════════════════════════════════════════════════════
# ds_benchmark.py — เทียบ data structures
# ═══════════════════════════════════════════════════════════════
import timeit
from collections import deque
from heapq import heappush, heappop


def bench(label: str, stmt: str, setup: str, n: int = 1000):
    t = timeit.timeit(stmt, setup=setup, number=n)
    print(f"{label:30s}: {t/n*1e6:.2f} μs/op")


# ─── Membership test ───
print("=== Membership (x in container) ===")
bench("list:    10k items",
      "5000 in data",
      "data = list(range(10000))")
bench("set:     10k items",
      "5000 in data",
      "data = set(range(10000))")

# ─── Queue operations ───
print("\n=== Queue ===")
bench("list.pop(0)    10k items",
      "data.pop(0)",
      "data = list(range(10000))",
      n=1000)
bench("deque.popleft() 10k items",
      "data.popleft()",
      "from collections import deque; data = deque(range(10000))")

# ─── Insert front ───
print("\n=== Insert at front ===")
bench("list.insert(0, x)",
      "data.insert(0, 0)",
      "data = list(range(10000))")
bench("deque.appendleft(x)",
      "data.appendleft(0)",
      "from collections import deque; data = deque(range(10000))")

# ─── String concatenation ───
print("\n=== String concat (1000 strings) ===")
bench("+= in loop",
      "s=''\nfor x in data: s += str(x)",
      "data = list(range(1000))",
      n=100)
bench("''.join()",
      "''.join(str(x) for x in data)",
      "data = list(range(1000))",
      n=100)

# ─── Sort then search vs set search ───
print("\n=== Search 100 times ===")
bench("sort + binary search",
      "sorted(data); [x for x in queries]",
      "data = list(range(10000)); queries = [5000]*100",
      n=100)
bench("set lookup",
      "[x for x in queries]",
      "data = set(range(10000)); queries = [5000]*100",
      n=100)
```

**ผลลัพธ์ที่คาดหวัง:**
```
=== Membership ===
list:    10k items  : 60.00 μs
set:     10k items  : 0.05 μs   ← 1200x เร็วกว่า

=== Queue ===
list.pop(0)    10k  : 25.00 μs
deque.popleft() 10k : 0.05 μs   ← 500x

=== Insert at front ===
list.insert(0, x)   : 20.00 μs
deque.appendleft(x) : 0.05 μs   ← 400x
```

### 9.5 Recursion vs Iteration

```python
# ═══════════════════════════════════════════════════════════════
# recursion.py — เปรียบเทียบ recursion vs iteration
# ═══════════════════════════════════════════════════════════════
import sys
from functools import lru_cache

# ─── Factorial ───
def factorial_rec(n: int) -> int:
    """O(n) time, O(n) space (stack)"""
    return 1 if n <= 1 else n * factorial_rec(n - 1)


def factorial_iter(n: int) -> int:
    """O(n) time, O(1) space"""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# ─── Fibonacci — binary tree recursion ───
def fib_tree(n: int) -> int:
    """O(2ⁿ) — ห้ามใช้"""
    return n if n <= 1 else fib_tree(n-1) + fib_tree(n-2)


# ─── Tree traversal ───
class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def inorder_rec(root):
    """O(n) time, O(h) space — h = tree height"""
    if root is None:
        return []
    return inorder_rec(root.left) + [root.val] + inorder_rec(root.right)


def inorder_iter(root):
    """O(n) time, O(h) space (explicit stack)"""
    result = []
    stack = []
    current = root
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result


# ─── Deep recursion limit ───
# Python default: 1000
# sys.setrecursionlimit(10000)  ← ระวัง stack overflow
```

### 9.6 Sliding Window Pattern

```python
# ═══════════════════════════════════════════════════════════════
# sliding_window.py — O(n²) → O(n)
# ═══════════════════════════════════════════════════════════════

def max_sum_subarray_brute(arr: list[int], k: int) -> int:
    """O(n × k)"""
    best = float("-inf")
    for i in range(len(arr) - k + 1):
        s = sum(arr[i:i + k])    # O(k)
        best = max(best, s)
    return best


def max_sum_subarray_sliding(arr: list[int], k: int) -> int:
    """O(n) — sliding window"""
    window = sum(arr[:k])        # O(k) ครั้งเดียว
    best = window
    for i in range(k, len(arr)):
        window += arr[i] - arr[i - k]    # O(1)
        best = max(best, window)
    return best


# ─── Benchmark ───
import random
import timeit
arr = [random.randint(-100, 100) for _ in range(10_000)]
k = 100

print("Brute:", timeit.timeit(lambda: max_sum_subarray_brute(arr, k), number=1))
# ~50ms

print("Sliding:", timeit.timeit(lambda: max_sum_subarray_sliding(arr, k), number=1))
# ~1ms

# Speedup 50x
```

### 9.7 Two Pointer Pattern

```python
# ═══════════════════════════════════════════════════════════════
# two_pointer.py — เทคนิค two pointer
# ═══════════════════════════════════════════════════════════════

def is_palindrome(s: str) -> bool:
    """O(n) time, O(1) space"""
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True


def two_sum_sorted(arr: list[int], target: int) -> tuple[int, int] | None:
    """O(n) time, O(1) space — arr ต้อง sorted"""
    i, j = 0, len(arr) - 1
    while i < j:
        s = arr[i] + arr[j]
        if s == target:
            return (i, j)
        elif s < target:
            i += 1
        else:
            j -= 1
    return None


def remove_duplicates_sorted(arr: list[int]) -> int:
    """O(n) time, O(1) space — in-place"""
    if not arr:
        return 0
    j = 0
    for i in range(1, len(arr)):
        if arr[i] != arr[j]:
            j += 1
            arr[j] = arr[i]
    return j + 1
```

---

## 10. AI/ML Skill (Complexity Analysis)

### 10.1 Skill Interface

```python
# app/skills/base.py
"""TH: Base skill interface | EN: base skill interface"""
from __future__ import annotations
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

### 10.2 Skill: Analyze Complexity

```python
# app/skills/complexity_analyzer.py
"""TH: Skill วิเคราะห์ Big O จากโค้ด | EN: Big O analyzer skill"""
from __future__ import annotations
import ast
import time
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


class ComplexityAnalyzerSkill(BaseSkill):
    """TH: วิเคราะห์ complexity ของโค้ด Python

    วิธี: parse AST → หา loop nesting → อนุมาน Big O
    """

    name = "analyze_complexity"
    description = "Analyze Big O complexity of Python code."
    parameters = {
        "code": {"type": "string", "required": True},
    }

    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        t0 = time.monotonic()
        try:
            code = kwargs["code"]
            tree = ast.parse(code)
            analyzer = _ASTAnalyzer()
            analyzer.visit(tree)
            result = {
                "time_complexity": analyzer.time_complexity,
                "space_complexity": analyzer.space_complexity,
                "loops": analyzer.loop_depth,
                "recursion": analyzer.has_recursion,
                "notes": analyzer.notes,
            }
            return SkillResult(
                success=True, output=result,
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except SyntaxError as e:
            return SkillResult(success=False, error=f"syntax: {e}")
        except Exception as e:  # noqa: BLE001
            return SkillResult(success=False, error=str(e))


class _ASTAnalyzer(ast.NodeVisitor):
    """TH: วิเคราะห์ AST เพื่อหา complexity | EN: AST complexity analyzer"""

    def __init__(self) -> None:
        self.max_depth = 0
        self.current_depth = 0
        self.has_recursion = False
        self.current_func: str | None = None
        self.func_calls: list[str] = []
        self.notes: list[str] = []
        self.loop_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prev = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = prev

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_For(self, node: ast.For) -> None:
        self.current_depth += 1
        self.loop_depth = max(self.loop_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        self.current_depth += 1
        self.loop_depth = max(self.loop_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if self.current_func and node.func.id == self.current_func:
                self.has_recursion = True
        self.generic_visit(node)

    @property
    def time_complexity(self) -> str:
        if self.has_recursion and self.loop_depth == 0:
            return "O(2ⁿ) หรือ O(n) ขึ้นอยู่กับ memoization"
        if self.loop_depth >= 3:
            return f"O(n^{self.loop_depth})"
        if self.loop_depth == 2:
            return "O(n²)"
        if self.loop_depth == 1:
            return "O(n)"
        return "O(1)"

    @property
    def space_complexity(self) -> str:
        if self.has_recursion:
            return "O(n) stack (up to recursion depth)"
        if self.loop_depth >= 1:
            return "O(1) หรือ O(n) ขึ้นอยู่กับ data structures"
        return "O(1)"
```

### 10.3 Skill: Benchmark Comparison

```python
# app/skills/benchmark.py
"""TH: Skill benchmark เปรียบเทียบ implementations"""
from __future__ import annotations
import time
from typing import Any, Callable

from app.skills.base import BaseSkill, SkillContext, SkillResult


class BenchmarkSkill(BaseSkill):
    """TH: เทียบเวลาของ implementations หลายตัว | EN: benchmark multiple functions"""

    name = "benchmark"
    description = "Benchmark multiple callables against the same input."

    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        t0 = time.monotonic()
        try:
            funcs: dict[str, Callable] = kwargs["funcs"]
            input_data = kwargs["input"]
            iterations = kwargs.get("iterations", 100)

            results: dict[str, dict[str, float]] = {}
            for name, fn in funcs.items():
                times = []
                for _ in range(iterations):
                    t_start = time.perf_counter()
                    fn(input_data)
                    t_end = time.perf_counter()
                    times.append((t_end - t_start) * 1000)  # ms

                results[name] = {
                    "mean_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "median_ms": sorted(times)[len(times) // 2],
                }

            # หาตัวเร็วสุด
            fastest = min(results.items(), key=lambda x: x[1]["mean_ms"])[0]
            for name in results:
                results[name]["relative"] = (
                    results[name]["mean_ms"] / results[fastest]["mean_ms"]
                )

            return SkillResult(
                success=True,
                output={"fastest": fastest, "results": results},
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return SkillResult(success=False, error=str(e))
```

### 10.4 Skill: Suggest Optimization

```python
# app/skills/optimizer.py
"""TH: Skill แนะนำ optimization"""
from __future__ import annotations
import ast
import time
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


class OptimizerSkill(BaseSkill):
    """TH: แนะนำการปรับปรุง performance จากโค้ด | EN: suggest optimizations"""

    name = "suggest_optimization"
    description = "Suggest Big O improvements for Python code."

    _RULES = [
        {
            "pattern": "for .+ in .+:\\s+.* in .+list",
            "hint": "ใช้ `set` แทน `list` สำหรับ membership test → O(n) → O(1)",
        },
        {
            "pattern": r's\s*\+=\s*.*in for',
            "hint": "ใช้ `''.join(list)` แทน `+=` → O(n²) → O(n)",
        },
        {
            "pattern": r"for .+:\s+for .+:",
            "hint": "พิจารณา hash map หรือ sort + two pointer → O(n²) → O(n log n)",
        },
        {
            "pattern": r"sorted\(.+\).*for",
            "hint": "หลีกเลี่ยง sort ใน loop → O(n log n) ซ้อน → ย้าย sort ออกนอก loop",
        },
        {
            "pattern": r"\.query\(|\.execute\(",
            "hint": "ตรวจสอบ N+1 query — ใช้ batch load แทน loop query",
        },
        {
            "pattern": r"arr\[i:\s*i\s*\+",
            "hint": "slice = O(k) — ถ้าอยู่ใน loop = O(n²) ใช้ index แทน",
        },
    ]

    async def execute(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        t0 = time.monotonic()
        try:
            code = kwargs["code"]
            import re
            suggestions = []
            for rule in self._RULES:
                if re.search(rule["pattern"], code, re.MULTILINE):
                    suggestions.append(rule["hint"])

            # ตรวจสอบ loop nesting
            tree = ast.parse(code)
            depth = 0
            max_depth = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    depth += 1
                    max_depth = max(max_depth, depth)

            if max_depth >= 2:
                suggestions.append(
                    f"พบ loop ซ้อน {max_depth} ชั้น — "
                    "พิจารณา hash map, sort+pointer, หรือ DP"
                )

            return SkillResult(
                success=True,
                output={"suggestions": suggestions, "loop_depth": max_depth},
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return SkillResult(success=False, error=str(e))
```

### 10.5 Skill Registry + Tests

```python
# app/skills/registry.py
from __future__ import annotations
from typing import Any

from app.skills.base import BaseSkill, SkillContext, SkillResult


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    async def execute(
        self, ctx: SkillContext, name: str, **kwargs: Any
    ) -> SkillResult:
        skill = self._skills.get(name)
        if skill is None:
            return SkillResult(success=False, error=f"unknown skill: {name}")
        return await skill.execute(ctx, **kwargs)


# ─── ทดสอบ ───
import asyncio

async def main() -> None:
    from app.skills.complexity_analyzer import ComplexityAnalyzerSkill
    from app.skills.optimizer import OptimizerSkill

    registry = SkillRegistry()
    registry.register(ComplexityAnalyzerSkill())
    registry.register(OptimizerSkill())

    ctx = SkillContext(tenant_id="t1")

    code = """
def find_dup(arr):
    result = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                result.append(arr[i])
    return result
"""

    r1 = await registry.execute(ctx, "analyze_complexity", code=code)
    print("Complexity:", r1.output)

    r2 = await registry.execute(ctx, "suggest_optimization", code=code)
    print("Optimize:", r2.output)


if __name__ == "__main__":
    asyncio.run(main())
```

**ผลลัพธ์:**
```json
{
  "time_complexity": "O(n²)",
  "space_complexity": "O(1) หรือ O(n) ขึ้นอยู่กับ data structures",
  "loops": 2,
  "recursion": false,
  "notes": []
}
{
  "suggestions": [
    "พิจารณา hash map หรือ sort + two pointer → O(n²) → O(n log n)",
    "พบ loop ซ้อน 2 ชั้น — พิจารณา hash map, sort+pointer, หรือ DP"
  ],
  "loop_depth": 2
}
```

---

## 11. ปัญหาและแนวทางแก้ไข

### 11.1 ตาราง Anti-patterns

| # | Anti-pattern | Complexity | Fix | Gain |
|---|---|---|---|---|
| 1 | `x in list` | O(n) | `x in set` | O(1) → **n×** |
| 2 | `s += x` ใน loop | O(n²) | `"".join()` | O(n) → **n×** |
| 3 | Loop ซ้อนเทียบทุกคู่ | O(n²) | Hash map / sort+pointer | O(n) → **n×** |
| 4 | Sort ใน loop | O(n² log n) | Sort นอก loop | O(n log n) → **n×** |
| 5 | Recursion ไม่มี memo | O(2ⁿ) | `@lru_cache` | O(n) → **2ⁿ/n×** |
| 6 | N+1 DB query | O(n) I/O | Batch + IN clause | 1 query → **n×** |
| 7 | List.append ใน list comp | O(n) | list comp เดียว | O(n) → **เท่าเดิม** |
| 8 | Copy ทั้ง array ใน loop | O(n²) | In-place หรือ slice นอก loop | O(n) → **n×** |
| 9 | `arr.index(x)` ใน loop | O(n²) | `enumerate` | O(n) → **n×** |
| 10 | `dict.get` pattern ผิด | O(n) | ตรวจ key ก่อน | O(1) |

### 11.2 Playbooks

#### PB-1: ระบบช้าลงเมื่อ scale

```markdown
## Diagnose
1. Benchmark ที่ n = 100, 1k, 10k, 100k
2. Plot เวลา vs n
3. ดู slopes → ระบุ complexity

## Pattern Recognition
- Slope = 0 → O(1)
- Slope ≈ 1 → O(n)
- Slope ≈ 1.1 → O(n log n)
- Slope ≈ 2 → O(n²)

## Fix (ตาม slope)
- ถ้า O(n²) → หา nested loop
- ถ้า O(n³) → หา triple nested
- ถ้า O(2ⁿ) → หา recursion
```

#### PB-2: Memory โตไม่หยุด

```markdown
## Diagnose
1. tracemalloc / memory_profiler
2. ระบุ object ที่โต
3. ตรวจ references

## Common Causes
- Cache ไม่มี eviction → LRU
- สร้าง list ใหญ่ใน loop → generator
- Recursion deep → iterative
- Event listeners ไม่ off → cleanup
```

#### PB-3: DB query ช้า

```markdown
## Diagnose
1. EXPLAIN ANALYZE
2. ดู Seq Scan, Nested Loop
3. วัด I/O

## Fix
- Seq Scan → add index
- Nested Loop → hash join
- Sort spill → increase work_mem
- N+1 → batch load
```

### 11.3 Monitoring

```python
# app/core/metrics.py
"""TH: Prometheus metrics สำหรับ performance"""
from prometheus_client import Counter, Histogram

FUNCTION_LATENCY = Histogram(
    "app_function_duration_seconds",
    "Function execution time",
    ["module", "function"],
    buckets=(0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10),
)

FUNCTION_CALLS = Counter(
    "app_function_calls_total",
    "Total function calls",
    ["module", "function", "status"],
)

DB_QUERIES = Counter(
    "app_db_queries_total",
    "DB query count",
    ["operation", "table"],
)

MEMORY_USAGE = Histogram(
    "app_memory_bytes",
    "Memory usage",
    buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600),
)


# ─── Decorator ───
import functools
import time


def track_perf(module: str):
    def decorator(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                result = await fn(*args, **kwargs)
                FUNCTION_CALLS.labels(module, fn.__name__, "success").inc()
                return result
            except Exception:
                FUNCTION_CALLS.labels(module, fn.__name__, "error").inc()
                raise
            finally:
                FUNCTION_LATENCY.labels(module, fn.__name__).observe(
                    time.perf_counter() - t0
                )

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                FUNCTION_CALLS.labels(module, fn.__name__, "success").inc()
                return result
            except Exception:
                FUNCTION_CALLS.labels(module, fn.__name__, "error").inc()
                raise
            finally:
                FUNCTION_LATENCY.labels(module, fn.__name__).observe(
                    time.perf_counter() - t0
                )

        import asyncio
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper
    return decorator
```

### 11.4 Quick Reference Card

```
╔══════════════════════════════════════════════════════════════╗
║              BIG O CHEAT SHEET                              ║
╠══════════════════════════════════════════════════════════════╣
║ COMPLEXITY    │ EXAMPLE              │ n=1M PRACTICAL      ║
║───────────────┼──────────────────────┼─────────────────────║
║ O(1)          │ dict[key]            │ ✅ OK                ║
║ O(log n)      │ binary search        │ ✅ OK                ║
║ O(n)          │ find max             │ ✅ OK (1ms)          ║
║ O(n log n)    │ sorted()             │ ✅ OK (20ms)         ║
║ O(n²)         │ nested loop          │ ⚠️ 16 min            ║
║ O(n³)         │ matrix mult          │ ❌ 11 days           ║
║ O(2ⁿ)         │ subset recursion     │ ❌ ∞                 ║
║ O(n!)         │ permutations         │ ❌ ∞                 ║
║───────────────┴──────────────────────┴─────────────────────║
║ OPERATION     │ list    │ dict/set  │ deque    │ heap       ║
║───────────────┼─────────┼───────────┼──────────┼────────────║
║ access[i]     │ O(1)    │ -         │ O(n)     │ O(1)*      ║
║ search(x)     │ O(n)    │ O(1)*     │ O(n)     │ O(n)       ║
║ insert end    │ O(1)*   │ O(1)*     │ O(1)     │ O(log n)   ║
║ insert front  │ O(n)    │ -         │ O(1)     │ -          ║
║ pop end       │ O(1)    │ -         │ O(1)     │ O(log n)   ║
║ pop front     │ O(n)    │ -         │ O(1)     │ -          ║
║ min peek      │ O(n)    │ -         │ O(n)     │ O(1)       ║
║───────────────┴─────────┴───────────┴──────────┴────────────║
║ * = amortized/average                                       ║
╠══════════════════════════════════════════════════════════════╣
║ RULES                                                        ║
║  • ตัด constant: O(2n) → O(n)                                ║
║  • เอา term โตสุด: O(n²+n) → O(n²)                           ║
║  • Nested loop = คูณ: n × n = n²                             ║
║  • หารครึ่ง = log n                                          ║
║  • 2 ทางซ้อน = 2ⁿ                                            ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 12. สรุป

### 12.1 ภาพรวม

```
┌──────────────────────────────────────────────────────────┐
│              BIG O — LEARNING PATH                       │
│                                                          │
│  Level 1: อ่าน/เขียน复杂度ได้                            │
│      ↓                                                   │
│  Level 2: เลือก DS/Algorithm ถูก                         │
│      ↓                                                   │
│  Level 3: วิเคราะห์ code review                          │
│      ↓                                                   │
│  Level 4: Optimization + Benchmark                       │
│      ↓                                                   │
│  Level 5: System Design + Capacity Planning             │
│      ↓                                                   │
│  Level 6: Performance RCA + Production Debug            │
└──────────────────────────────────────────────────────────┘
```

### 12.2 Key Takeaways

| # | บทเรียน | ทำไมสำคัญ |
|---|---|---|
| 1 | **Big O = scale language** | สื่อสารประสิทธิภาพเป็นกลาง |
| 2 | **O(n²) คือเส้นแบ่ง** | ปลอดภัย n < 10k, ระวัง n > 10k |
| 3 | **Hash map = เพื่อนแท้** | เปลี่ยน O(n) → O(1) บ่อยครั้ง |
| 4 | **Sorting = O(n log n)** | เป็น lower bound ที่พิสูจน์ได้ |
| 5 | **Divide & Conquer** | O(n log n) ผ่าน Master Theorem |
| 6 | **Memoization** | O(2ⁿ) → O(n) |
| 7 | **Optimize with data** | Profile ก่อน อย่าเดา |
| 8 | **Constant matter** | ที่ n เล็ก insertion sort ชนะ quick sort |
| 9 | **Space-time tradeoff** | บางครั้งใช้ memory แลกเวลา OK |
| 10 | **ไม่มี one-size-fits-all** | ทุก algorithm มี trade-off |

### 12.3 Checklist ใช้งานจริง

```markdown
## ✅ CODE REVIEW CHECKLIST — BIG O

### Algorithm
- [ ] ระบุ complexity ของทุก function
- [ ] ตรวจ nested loop → O(n²)?
- [ ] ตรวจ recursion → exponential?
- [ ] ตรวจ hash map/set ที่ควรใช้
- [ ] ตรวจ string concat ใน loop

### Data Structure
- [ ] list vs set vs dict → เลือกถูก?
- [ ] heap สำหรับ top-k
- [ ] deque สำหรับ queue
- [ ] generator สำหรับ lazy

### Database
- [ ] Index ตรง query?
- [ ] ไม่มี N+1
- [ ] EXPLAIN ANALYZE
- [ ] Pagination (cursor > offset)

### Memory
- [ ] Stream แทน load all
- [ ] Generator แทน list
- [ ] Cache มี eviction
- [ ] Recursion depth < limit

### Production
- [ ] Metrics (latency, memory)
- [ ] Benchmarks (before/after)
- [ ] Load test (n × 10)
- [ ] RCA ถ้า fail
```

### 12.4 Roadmap เรียนรู้ (8 สัปดาห์)

```markdown
## Week 1-2: Foundation
- Big O notation, Ω, Θ
- Common complexities
- Analyze simple code

## Week 3-4: Data Structures
- Array, Hash, Tree, Graph
- Complexity of operations
- When to use which

## Week 5-6: Algorithms
- Sorting, Searching
- Divide & Conquer
- DP, Greedy
- Graph algorithms

## Week 7-8: Production
- Profiling (cProfile, py-spy)
- Benchmarking
- RCA playbook
- Capacity planning
```

### 12.5 ทรัพยากร

#### 📚 หนังสือ
- **"Introduction to Algorithms"** (CLRS) — Cormen et al.
- **"The Algorithm Design Manual"** — Steven Skiena
- **"Grokking Algorithms"** — Aditya Bhargava (illustrated)
- **"Cracking the Coding Interview"** — Gayle McDowell

#### 🎓 คอร์ส
- **MIT 6.006** — Introduction to Algorithms
- **Princeton Algorithms I/II** — Coursera
- **Stanford CS161** — Design & Analysis of Algorithms
- **NeetCode 150** — Coding interview

#### 🛠️ เครื่องมือ
- **Big-O Cheat Sheet** — bigocheatsheet.com
- **VisuAlgo** — visualgo.net
- **Python TimeComplexity** — wiki.python.org
- **py-spy** — github.com/benfred/py-spy

#### 🧪 Libraries
- **`timeit`** — micro-benchmark
- **`cProfile`** — profiler
- **`line_profiler`** — line-level
- **`memory_profiler`** — memory
- **`py-spy`** — sampling profiler
- **`scalene`** — CPU+GPU+memory

### 12.6 คำส่งท้าย

> **"Premature optimization is the root of all evil"** — Donald Knuth
>
> **แต่ "Knowing Big O" ไม่ใช่ premature optimization — มันคือ "knowing what's possible"**

**หลักการ 5 ข้อ:**

1. **รู้ก่อน optimize** — Profile, measure, then fix
2. **คิดถึง scale** — n = 100 ต่างจาก n = 1M
3. **เลือก DS ให้ตรงงาน** — 50% ของ performance มาจากนี้
4. **เรียนรู้ trade-offs** — ไม่มีอะไรฟรี
5. **เขียนให้อ่านง่ายก่อน** — เร็วทีหลัง (ถ้าจำเป็น)

---

**📌 Version:** 1.0 · **Last Updated:** 2026-09-24 · **License:** Internal Use
**📧 Feedback:** ส่ง PR หรือ issue ผ่าน repo ภายใน
**🔗 Related:** `llm_opencode_promt.md` · `create_module_llm.py` · `RAG-Production-Guide.md`
