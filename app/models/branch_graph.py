import heapq

class BranchGraph:
    def __init__(self):
        # Each edge stores destination, time weight and cost weight
        self.graph = {}

    def add_branch(self, branch_id):
        if branch_id not in self.graph:
            self.graph[branch_id] = []

    def add_connection(self, source_id, destination_id, time_weight, cost_weight=None, bidirectional=True):
        if source_id not in self.graph:
            self.add_branch(source_id)
        if destination_id not in self.graph:
            self.add_branch(destination_id)

        # If no cost is provided, we use the same value as time
        if cost_weight is None:
            cost_weight = time_weight

        for neighbor_id, _, _ in self.graph[source_id]:
            if neighbor_id == destination_id:
                return False

        self.graph[source_id].append((destination_id, time_weight, cost_weight))

        # If the user marks it as bidirectional, we also add the reverse edge
        if bidirectional:
            self.graph[destination_id].append((source_id, time_weight, cost_weight))

        return True

    def get_neighbors(self, branch_id):
        return self.graph.get(branch_id, [])

    def get_all_branches(self):
        return list(self.graph.keys())

    def get_all_connections(self):
        connections = []
        seen = set()

        for source_id, neighbors in self.graph.items():
            for destination_id, time_weight, cost_weight in neighbors:
                edge_key = tuple(sorted((source_id, destination_id)))

                if edge_key in seen:
                    continue

                seen.add(edge_key)
                connections.append((source_id, destination_id, time_weight, cost_weight))

        return connections

    def remove_branch(self, branch_id):
        if branch_id not in self.graph:
            return False

        del self.graph[branch_id]

        for source_id in self.graph:
            self.graph[source_id] = [
                (neighbor_id, time_weight, cost_weight)
                for neighbor_id, time_weight, cost_weight in self.graph[source_id]
                if neighbor_id != branch_id
            ]

        return True

    def shortest_path(self, start_id, end_id, criterion="time"):
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

            for neighbor_id, time_weight, cost_weight in self.graph[current_id]:
                # The same Dijkstra logic works, only the selected edge weight changes
                edge_weight = cost_weight if criterion == "cost" else time_weight
                new_distance = current_distance + edge_weight

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