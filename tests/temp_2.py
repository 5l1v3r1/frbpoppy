import numpy as np
import bisect
import time

# Initialize an example of an array in which to search
# Array is sorted along each row
a = np.sort(np.random.rand(int(1e2), int(5e5)), axis=1)

# Set up search limits
margin = 0.05
min_v = 0.5 - margin
max_v = 0.5 + margin


# Find indices of occurances
def use_np_where():
    return np.where(((a >= min_v) & (a <= max_v)))


def use_searchsorted():
    left = np.apply_along_axis(np.searchsorted, 1, a, min_v)
    right = np.apply_along_axis(np.searchsorted, 1, a, max_v)
    unique_rows = np.where(left <= right)[0]
    bursts_per_row = right[unique_rows] - left[unique_rows]
    rows = np.repeat(unique_rows, bursts_per_row)
    cols = np.zeros(np.sum(bursts_per_row))
    cum_bursts = np.cumsum(bursts_per_row)
    cum_bursts = np.insert(cum_bursts, 0, 0)
    for i, e in enumerate(cum_bursts[1:]):
        cols[cum_bursts[i]:e] = np.arange(left[unique_rows[i]],
                                          right[unique_rows[i]])
    return rows, cols


def use_bisect():
    left = np.apply_along_axis(bisect.bisect_left, 1, a, min_v)
    right = np.apply_along_axis(bisect.bisect_right, 1, a, max_v)
    unique_rows = np.where(left <= right)[0]
    bursts_per_row = right[unique_rows] - left[unique_rows]
    rows = np.repeat(unique_rows, bursts_per_row)
    cols = np.zeros(np.sum(bursts_per_row), dtype=int)
    cum_bursts = np.cumsum(bursts_per_row)
    cum_bursts = np.insert(cum_bursts, 0, 0)
    for i, e in enumerate(cum_bursts[1:]):
        ii = unique_rows[i]
        cols[cum_bursts[i]:e] = np.arange(left[ii], right[ii])
    return rows, cols


def use_bisect_with_list():
    left = np.apply_along_axis(bisect.bisect_left, 1, a, min_v)
    right = np.apply_along_axis(bisect.bisect_right, 1, a, max_v)
    unique_rows = np.where(left <= right)[0]
    bursts_per_row = right[unique_rows] - left[unique_rows]
    rows = np.repeat(unique_rows, bursts_per_row)
    cols = []
    for i in unique_rows:
        c = np.arange(left[i], right[i])
        cols.append(c)
    cols = np.concatenate(cols)
    return rows, cols


def equal(a, b):
    e = np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    print(f'    equal: {e}')


def timeit(f):
    print(f'method: {f.__name__}')
    start = time.time()
    i = f()
    end = time.time()
    print(f'    time: {end - start}')
    return i


true_idx = timeit(use_np_where)


def test(a):
    arrays = timeit(a)
    equal(arrays, true_idx)


test(use_searchsorted)
test(use_bisect)
test(use_bisect_with_list)
