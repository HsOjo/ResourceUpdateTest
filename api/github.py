import base64
import time

from utils.web_interactive import WebInteractive as wi


class GitHub:
    @staticmethod
    @wi.response('json')
    @wi.request('GET', 'https://api.github.com/repos/%s/%s/commits')
    def _commits(user, repo, sha=None, path=None, author=None, since=None, until=None):
        params = locals()
        for k in ['user', 'repo']:
            params.pop(k)
        req_data = {
            'url_args': (user, repo),
            'params': params,
        }
        return req_data

    @staticmethod
    @wi.response('json')
    @wi.request('GET', 'https://api.github.com/repos/%s/%s/git/trees/%s')
    def _git_trees(user, repo, sha, recursive=None):
        params = locals()
        for k in ['user', 'repo', 'sha']:
            params.pop(k)
        req_data = {
            'url_args': (user, repo, sha),
            'params': params,
        }
        return req_data

    @staticmethod
    @wi.response('json')
    @wi.request('GET', 'https://api.github.com/repos/%s/%s/git/blobs/%s')
    def _git_blobs(user, repo, sha):
        req_data = {
            'url_args': (user, repo, sha),
        }
        return req_data

    @staticmethod
    def get_commits(user, repo, sha=None):
        raw_commits = GitHub._commits(user, repo, sha)

        commits = []
        for rc in raw_commits:
            info = rc['commit']  # type: dict
            date = time.strptime(info['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
            item = {
                'sha': rc['sha'],
                'sha_tree': info['tree']['sha'],
                'date': time.strftime('%Y-%m-%d %H:%M:%S', date),
                'message': info['message'],
            }
            commits.append(item)

        rc_last = raw_commits[-1]
        if len(rc_last['parents']) != 0:
            parent = rc_last['parents'][0]
            next_commits = GitHub.get_commits(user, repo, parent['sha'])
            for nc in next_commits:
                commits.append(nc)

        return commits

    @staticmethod
    def get_trees(user, repo, sha, recursive=1):
        raw_trees = GitHub._git_trees(user, repo, sha, recursive)  # type: dict

        if 'tree' in raw_trees:
            trees = []
            for rt in raw_trees['tree']:
                item = {
                    'path': rt['path'],
                    'type': rt['type'],
                    'sha': rt['sha'],
                }
                if item['type'] == 'blob':
                    item['size'] = rt['size']

                trees.append(item)

            if raw_trees['truncated']:
                next_trees = GitHub.get_trees(user, repo, sha, recursive + 1)
                for nt in next_trees:
                    trees.append(nt)

            return trees

    @staticmethod
    def get_blobs(user, repo, sha):
        raw_blobs = GitHub._git_blobs(user, repo, sha)

        print(raw_blobs)
        size = raw_blobs['size']
        content = base64.b64decode(raw_blobs['content'])

        blobs = {
            'size': size,
            'content': content,
            'validate': len(content) == size,
        }

        return blobs
