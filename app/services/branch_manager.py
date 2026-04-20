from app.models.branch import Branch
from app.models.branch_graph import BranchGraph


class BranchManager:
    def __init__(self):
        self.branches = []
        self.next_branch_id = 1
        self.graph = BranchGraph()

    def add_branch(self, branch: Branch):
        # Branch ids are assigned here to avoid duplicates after deletions
        if branch.id is None or branch.id <= 0:
            branch.id = self.next_branch_id
            self.next_branch_id += 1
        elif branch.id >= self.next_branch_id:
            self.next_branch_id = branch.id + 1

        self.branches.append(branch)
        self.graph.add_branch(branch.id)
        return branch

    def get_branches(self):
        return self.branches

    def find_by_id(self, branch_id):
        for branch in self.branches:
            if branch.id == branch_id:
                return branch
        return None

    def delete_branch(self, branch_id):
        branch = self.find_by_id(branch_id)
        if branch is None:
            return False

        self.branches.remove(branch)
        self.graph.remove_branch(branch_id)
        return True

    def connect_branches(self, source_id, destination_id, weight):
        source_branch = self.find_by_id(source_id)
        destination_branch = self.find_by_id(destination_id)

        if source_branch is None or destination_branch is None:
            return False

        if source_id == destination_id:
            return False

        return self.graph.add_connection(source_id, destination_id, weight)