from my_dulwich.server import ReceivePackHandler

class my_ReceivePackHandler(ReceivePackHandler):
    """Protocol handler for downloading a pack from the client."""

    def handle(self):
        super(my_ReceivePackHandler, self).handle()

        from my_dulwich.index import build_index_from_tree

        indexfile = self.repo.index_path()
        obj_sto = self.repo.object_store
        # TODO: catch if not a reference
        tree_id = self.repo['HEAD'].tree
        # TODO: error out if unstaged or uncommited files
        build_index_from_tree(self.repo.path,indexfile,obj_sto,tree_id)



