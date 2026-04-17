from app.models.branch import Branch


class BranchManager:
    def __init__(self):
        self.branches = []

    def add_branch(self, branch: Branch):
        self.branches.append(branch)

    def get_branches(self):
        return self.branches

    def find_by_id(self, branch_id):
        for branch in self.branches:
            if branch.id == branch_id:
                return branch
        return None