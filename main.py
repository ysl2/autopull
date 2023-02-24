import subprocess
import json
import pathlib
import threading
from rich.pretty import pprint as print

# KWARGS = {'shell': True, 'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
KWARGS = {'shell': True}
CONFLICTS = []


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
                f'git checkout {branch}; '
                f'git reset --hard HEAD; '
                f'git pull origin {branch}; '
                f'git fetch upstream {branch}; '
                f'git merge upstream/{branch} --allow-unrelated-histories; '
            )
            r = subprocess.Popen(cmd, **KWARGS, cwd=rf'{self.item["dir"]}').wait()
            if r != 0:
                subprocess.Popen('git merge --abort; git reset --hard HEAD', **KWARGS, cwd=rf'{self.item["dir"]}').wait()
                CONFLICTS.append((self.item['origin'], branch))
                continue
            subprocess.Popen(f'git push origin {branch}', **KWARGS, cwd=rf'{self.item["dir"]}').wait()


def main():

    # HACK: Songli.Yu: "Add global information."
    subprocess.Popen('git config --global user.name ysl2', **KWARGS)
    subprocess.Popen('git config --global user.email www.songli.yu@gmail.com', **KWARGS)

    with open('config.json', 'r') as f:
        j = json.load(f)

    threads = []

    for item in j:
        t = MyThread(item)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(CONFLICTS)


if __name__ == '__main__':
    main()
