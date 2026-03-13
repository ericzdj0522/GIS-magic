import heapq

def dijkstra(graph, start):
    # start to each node is infinite
    dist = {node: float('inf') for node in graph}
    dist[start] = 0

    min_heap = [(0, start)]

    while min_heap:
        current_dist, node = heapq.heappop(min_heap)

        if current_dist > dist[node]:
            continue

        for neighbor, weight in graph[node]:
            new_dist = current_dist + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(min_heap, (new_dist, neighbor))

    return dist

graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('A', 1), ('D', 2)],
    'C': [('A', 4), ('D', 1)],
    'D': [('B', 2), ('C', 1)]
}

result = dijkstra(graph, 'A')
print(result)