"""직접 구현한 안정 병합 정렬과 그래프 탐색."""

from collections import deque


def merge_sort(items, key=lambda item: item):
    """입력을 바꾸지 않는 안정 정렬. 시간 O(n log n), 추가 공간 O(n)."""
    items = list(items)
    if len(items) < 2:
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def topological_order(commits, children):
    """부모가 모두 출력된 노드부터 큐에 넣는 Kahn 알고리즘."""
    remaining = {h: len(c.parents) for h, c in commits.items()}
    ready = deque(h for h in commits if remaining[h] == 0)
    result = []
    while ready:
        current = ready.popleft()
        result.append(current)
        for child in children[current]:
            remaining[child] -= 1
            if remaining[child] == 0:
                ready.append(child)
    if len(result) != len(commits):
        raise ValueError("Cycle detected")
    return result


def ancestors(commits, start):
    """자기 자신을 제외한 모든 조상을 반복형 DFS로 찾는다."""
    stack = list(commits[start].parents)
    seen = set()
    result = []
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        result.append(current)
        stack.extend(commits[current].parents)
    return result


def shortest_path(commits, children, start, end):
    """무방향 BFS. 이웃을 사전순 방문해 동률 경로도 사전순 최소화한다."""
    ready = deque([start])
    previous = {start: None}
    while ready:
        current = ready.popleft()
        if current == end:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]
            return path[::-1]
        neighbors = merge_sort([*commits[current].parents, *children[current]])
        for neighbor in neighbors:
            if neighbor not in previous:
                previous[neighbor] = current
                ready.append(neighbor)
    return None
