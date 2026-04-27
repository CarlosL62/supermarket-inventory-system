import heapq

class BranchGraph:
    def __init__(self):
        # Adjacency list: {branch_id: [(neighbor_id, weight), ...]}
        self.graph = {}

    def add_branch(self, branch_id):
        if branch_id not in self.graph:
            self.graph[branch_id] = []

    def add_connection(self, source_id, destination_id, weight):
        if source_id not in self.graph:
            self.add_branch(source_id)
        if destination_id not in self.graph:
            self.add_branch(destination_id)

        for neighbor_id, _ in self.graph[source_id]:
            if neighbor_id == destination_id:
                return False

        self.graph[source_id].append((destination_id, weight))
        self.graph[destination_id].append((source_id, weight))  # undirected
        return True

    def get_neighbors(self, branch_id):
        return self.graph.get(branch_id, [])

    def get_all_branches(self):
        return list(self.graph.keys())

    def get_all_connections(self):

        connections = []

        seen = set()

        for source_id, neighbors in self.graph.items():

            for destination_id, weight in neighbors:

                edge_key = tuple(sorted((source_id, destination_id)))

                if edge_key in seen:
                    continue

                seen.add(edge_key)

                connections.append((source_id, destination_id, weight))

        return connections

    def remove_branch(self, branch_id):
        if branch_id not in self.graph:
            return False

        del self.graph[branch_id]

        for source_id in self.graph:
            self.graph[source_id] = [
                (neighbor_id, weight)
                for neighbor_id, weight in self.graph[source_id]
                if neighbor_id != branch_id
            ]

        return True

    def shortest_path(self, start_id, end_id):
        if start_id not in self.graph or end_id not in self.graph:
            return [], None

        distances = {branch_id: float("inf") for branch_id in self.graph}
        previous = {branch_id: None for branch_id in self.graph}
        distances[start_id] = 0

        priority_queue = [(0, start_id)]

        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)

            if current_id == end_id:
                break

            if current_distance > distances[current_id]:
                continue

            for neighbor_id, weight in self.graph[current_id]:
                new_distance = current_distance + weight

                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_id
                    heapq.heappush(priority_queue, (new_distance, neighbor_id))

        if distances[end_id] == float("inf"):
            return [], None

        path = []
        current_id = end_id

        while current_id is not None:
            path.insert(0, current_id)
            current_id = previous[current_id]

        return path, distances[end_id]