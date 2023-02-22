import subprocess
from rich.pretty import pprint as print
import json
import pathlib


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
def temp1():
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
        item['p'] = subprocess.Popen(f'git clone {item["origin"]}', **kwargs)

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
        cmd = (f'cd {item["dir"]} && git remote add upstream {item["upstream"]}',)
        subprocess.Popen(cmd, **kwargs)

    # HACK: Songli.Yu: "Merge specific branches or all branches."
    for item in j:
        if item['branches'][0] == '*':
            # TODO:
            continue
        for branch in item['branches']:
            cmd = (
                f'cd {item["dir"]} && '
                '('
                f'git checkout -b pullbot; '
                f'git fetch origin {branch}; '
                f'git reset --hard origin/{branch}; '
                f'git fetch upstream {branch}; '
                f'git merge --no-edit upstream/{branch}; '
                ')'
            )
            r = subprocess.Popen(cmd, shell=True).wait()
            if r != 0:
                subprocess.Popen(f'cd {item["dir"]} && git merge --abort', **kwargs).wait()
                continue
            subprocess.Popen(f'cd {item["dir"]} && git push origin pullbot', shell=True).wait()


if __name__ == '__main__':
    temp1()
