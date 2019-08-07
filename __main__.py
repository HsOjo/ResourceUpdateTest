import os

from api.github import GitHub

info = {
    'user': 'HsOjo',
    'repo': 'hsojo.github.io',
}

SHA_VERSION_FILE = 'sha_version.txt'


def resource_update(user, repo, folder):
    path_sha_version = '%s/%s' % (folder, SHA_VERSION_FILE)
    if os.path.exists(path_sha_version):
        with open(path_sha_version, 'r') as io:
            sha_version = io.read()
    else:
        sha_version = None

    commits = list(reversed(GitHub.get_commits(user, repo)))
    commits_sha = [commit['sha'] for commit in commits]

    if sha_version in commits_sha:
        index = commits_sha.index(sha_version)
        commits = commits[index + 1:]

    treeses = []
    for commit in commits:
        print('Get Trees: %s' % commit['sha'])
        treeses = GitHub.get_trees(user, repo, sha=commit['sha'])

    items = {}
    for tree in treeses:
        if tree['type'] == 'tree':
            tree.pop('sha')
        items[tree.pop('path')] = tree

    items_keys = sorted(items, key=lambda k: items[k]['type'] == 'tree', reverse=True)
    for key in items_keys:
        item = items[key]
        path = '%s/%s' % (folder, key)
        if item['type'] == 'tree':
            if os.path.exists(path):
                if not os.path.isdir(path):
                    os.unlink(path)
            if not os.path.exists(path):
                print('Make Directory: %s' % key)
                os.makedirs(path)
        else:
            print('Downloading: %s' % key)
            blobs = GitHub.get_blobs(user, repo, sha=item['sha'])
            with open(path, 'wb') as io:
                io.write(blobs['content'])

    with open(path_sha_version, 'w') as io:
        io.write(commits[-1]['sha'])


resource_update(**info, folder='output')
