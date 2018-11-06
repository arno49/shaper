from path import Path


def find_git_root(folder):
    folder = Path(folder).abspath()
    while True:
        git_config = folder / '.git' / 'config'
        if git_config.exists():
            return folder
        folder = folder.parent
        if folder == '/':
            raise RuntimeError('Cannot find git repo')
