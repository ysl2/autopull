import subprocess
from rich.pretty import pprint as print
import json
import pathlib
import threading

# kwargs = {'shell': True, 'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
KWARGS = {'shell': True}

# def temp():
#     with subprocess.Popen(['ls', '-la'], stdout=subprocess.PIPE) as p:
#         s = '\n'.join('{}: {}'.format(*k) for k in enumerate(dir(p)))
#         with subprocess.Popen(['less'], stdin=subprocess.PIPE) as p1:
#             r = p1.communicate(input=s.encode('utf-8'))

#   {
#     "origin": "git@git.zhlh6.cn:ysl2/LunarVim",
#     "upstream": "git@git.zhlh6.cn:LunarVim/LunarVim",
#     "branches": ["master"]
#   },
#   {
#     "origin": "git@git.zhlh6.cn:ysl2/abc",
#     "upstream": "git@git.zhlh6.cn:abc/abc",
#     "branches": ["main", "dev"]
#   },
#   {
#     "origin": "git@git.zhlh6.cn:ysl2/NvChad",
#     "upstream": "git@git.zhlh6.cn:NvChad/NvChad",
#     "branches": ["main", "dev"]
#   },
#   {
#     "origin": "git@git.zhlh6.cn:ysl2/symbols-outline.nvim",
#     "upstream": "git@git.zhlh6.cn:simrat39/symbols-outline.nvim",
#     "branches": ["master"]
#   }


def temp():
    # kwargs = {'shell': True, 'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
    kwargs = {'shell': True}

    # HACK: Songli.Yu: "Add global information."
    subprocess.Popen('git config --global user.name ysl2', **kwargs)
    subprocess.Popen('git config --global user.email www.songli.yu@gmail.com', **kwargs)

    with open('config.json', 'r') as f:
        j = json.load(f)

    # HACK: Songli.Yu: "Clone repos."
    for item in j:
        item['dir'] = pathlib.Path(item['origin'].split('/')[1])
        item['p'] = subprocess.Popen(f'git clone {item["origin"]} {item["dir"]}', **kwargs)

    print(j)

    k = []
    for item in j:
        code = item['p'].wait()
        if code == 0:
            k.append(item)
            continue
        if item['dir'].exists():
            k.append(item)
    j = k
    print(j)

    # HACK: Songli.Yu: "Add upstream url."
    for item in j:
        cmd = f'git remote add upstream {item["upstream"]}'
        subprocess.Popen(cmd, **kwargs, cwd=rf'{item["dir"]}')

    # HACK: Songli.Yu: "Merge specific branches or all branches."
    for item in j:
        if item['branches'][0] == '*':
            # TODO:
            continue
        for branch in item['branches']:
            cmd = (
                f'git checkout -b pullbot; '
                f'git fetch origin {branch}; '
                f'git reset --hard origin/{branch}; '
                f'git fetch upstream {branch}; '
                f'git merge --no-edit upstream/{branch}; '
            )
            r = subprocess.Popen(cmd, **kwargs, cwd=rf'{item["dir"]}').wait()
            if r != 0:
                subprocess.Popen('git merge --abort', **kwargs, cwd=rf'{item["dir"]}').wait()
                continue
            subprocess.Popen('git push origin pullbot', **kwargs, cwd=rf'{item["dir"]}').wait()


class MyThread(threading.Thread):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def run(self) -> None:
        # HACK: Songli.Yu: "Clone repos."
        self.item['dir'] = pathlib.Path(self.item['origin'].split('/')[1])
        r = subprocess.Popen(f'git clone {self.item["origin"]} {self.item["dir"]}', **KWARGS).wait()
        if r != 0 and not self.item['dir'].exists():
            return

        # HACK: Songli.Yu: "Add upstream url."
        cmd = f'git remote add upstream {self.item["upstream"]}'
        subprocess.Popen(cmd, **KWARGS, cwd=rf'{self.item["dir"]}').wait()

        # HACK: Songli.Yu: "Merge specific branches or all branches."
        if self.item['branches'][0] == '*':
            # TODO:
            return
        for branch in self.item['branches']:
            cmd = (
                f'git checkout -b pullbot; '
                f'git fetch origin {branch}; '
                f'git reset --hard origin/{branch}; '
                f'git fetch upstream {branch}; '
                f'git merge --no-edit upstream/{branch}; '
            )
            r = subprocess.Popen(cmd, **KWARGS, cwd=rf'{self.item["dir"]}').wait()
            if r != 0:
                subprocess.Popen('git merge --abort', **KWARGS, cwd=rf'{self.item["dir"]}').wait()
                continue
            subprocess.Popen('git push origin pullbot', **KWARGS, cwd=rf'{self.item["dir"]}').wait()


def main():

    # HACK: Songli.Yu: "Add global information."
    subprocess.Popen('git config --global user.name ysl2', **KWARGS)
    subprocess.Popen('git config --global user.email www.songli.yu@gmail.com', **KWARGS)

    with open('config.json', 'r') as f:
        j = json.load(f)

    for item in j:
        MyThread(item).start()


if __name__ == '__main__':
    main()
