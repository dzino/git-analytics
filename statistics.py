# Lists and dictionaries https://habr.com/ru/post/470774/
from typing import List, TypedDict
from abc import ABC  # Abstract class
import os
import re
import numpy as np  # Moving average

# re.search('(?<=abc).*', 'abcdef').group(0)


class Date(TypedDict):
    id: str
    date: str


class DateParam(Date):
    added: int
    removed: int


class DynamicsParam(TypedDict):
    lineChanges: int
    table: List


class StatisticsParam(TypedDict):
    line: int
    commit: int
    chart: List


class Bash(ABC):
    @staticmethod
    def _request(command) -> str:
        return os.popen(command).read()

    @staticmethod
    def _search(output, regular_expression) -> List[str]:
        return re.findall(regular_expression, output)


class Dynamics(Bash):
    path: str = ""
    lineChanges: int = 0

    def __init__(self, input_path: str):
        self.path = input_path

    def __commits_date(self) -> List[Date]:
        # https://stackoverflow.com/questions/14243380/how-to-configure-git-log-to-show-commit-date/14244466
        # git log --graph --pretty=format:'%C(auto)%h%d %ci %s' | cat
        command =\
            "cd '"\
            + self.path\
            + "'; git log --graph --pretty=format:'%C(auto)%h%d %ci %s'"\
            + "| cat"
        output: str = \
            self._request(command)
        commits: List[str] = \
            self._search(output, r"(?<=^\* )\S*|(?<=\n\* )\S*")
        date: List[str] = self._search(output, r"....-..-..")
        commits_date: List[Date] = []
        for k, i in enumerate(date):
            if i != date[k - 1]:
                unit: Date = {'id': commits[k], 'date': i}
                commits_date.append(unit)
        self.lineChanges = len(commits_date)
        return commits_date

    def __changes(self) -> List[DateParam]:
        commits_date: List[Date] = self.__commits_date()
        len_commits: int = len(commits_date) - 1
        changes: List[DateParam] = []
        for k, i in enumerate(commits_date):
            if k < len_commits:
                exclude: str =\
                    "':!node_modules*' ':!*.md' ':!*.ttf' ':!*.ico' ':!*.svg'"\
                    + " ':!*.lock' ':!bootstrap.*' ':!*.jpg'"\
                    + " ':!*.snap' ':!*.png' ':!out*'"
                command: str =\
                    "cd '" + self.path\
                    + "'; git diff --shortstat %s %s -- %s | cat"\
                    % (commits_date[k + 1]["id"], i["id"], exclude)
                output: str = self._request(command)
                param: List[str] = \
                    self._search(output, r"\S*(?= insertion)|\S*(?= deletion)")
                # print(command, len(param), output) if len(param) < 4 else 0
                added: int = int(param[0]) if len(param) > 0 else 0
                removed: int = int(param[2]) if len(param) > 2 else 0
                date: DateParam = {
                    'id1': i['id'],
                    'date': i['date'],
                    "added": added,
                    "removed": removed
                }
                changes.append(date)
        return changes

    # Formatting for Google graphics
    def get(self) -> DynamicsParam:
        format_changes = [['День', 'Добавлено', 'Удалено']]
        changes: List[DateParam] = self.__changes()
        changes.reverse()
        for i in changes:
            format_changes.append([i['date'], i['added'], i['removed']])
        return {
            "lineChanges": self.lineChanges,
            "table": format_changes
        }


class MovingAverage:
    size: int = 1
    dynamics: List = []

    added: List[int] = []
    removed: List[int] = []

    newAdded: List[int] = []
    newRemoved: List[int] = []

    def __init__(self, input_dynamics: List, input_size: int):
        self.size = input_size
        self.dynamics = input_dynamics

    @staticmethod
    def __moving_average(a, n=3):
        # a = np.arange(20)
        # b = moving_average(a, n=2)
        # c = moving_average(a, n=4)

        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def get(self):
        for k, i in enumerate(self.dynamics):
            if k != 0:
                self.added.append(i[1])
                self.removed.append(i[2])
        self.newAdded = self.__moving_average(self.added, n=self.size)
        self.newRemoved = self.__moving_average(self.removed, n=self.size)

        get_dynamics = []
        for k, i in enumerate(self.dynamics):
            if k >= self.size:
                get_dynamics.append([
                    self.dynamics[k][0],
                    self.newAdded[k - self.size],
                    self.newRemoved[k - self.size]
                ])
            elif k == 0:
                get_dynamics.append(i)
        return get_dynamics


class Statistics(Bash):
    path: str = ""
    commit_len: int = 0
    line_len: int = 0
    commits_files = {}
    files_commits_lines = []

    def __init__(self, input_path: str):
        self.path = input_path

    # def __commits(self) -> List[str]:
    #     output = self._request('cd "%s"; git log --oneline' % self.path)
    #     commits: List[str] = self._search(output, r"^\S*|(?<=\n)\S*")
    #     return commits

    def __commits_files(self):
        output = self._request(
            'cd "%s";' % self.path
            + 'git log --name-only --pretty=format:'
            + '| sort | uniq -c | sort -n'
        )
        files: List[str] = \
            list(filter(lambda x: x != '', self._search(output, r"\S*(?=\n)")))
        commits: List[str] = list(filter(
            lambda x: x != '',
            self._search(output, r"[0-9]*(?=\s\S)")
        ))
        self.commit_len = \
            int(list(filter(lambda x: x != '',
                self._search(
                    output,
                    r"[0-9]{1,10}(?=\s*\n)|[0-9]{1,10}(?=\s*$)"
                )
            ))[0])
        for k, i in enumerate(files):
            self.commits_files[files[k]] = commits[k]

    def __lines_files(self):
        exclude: str = 'node_modules\|.md\|.ttf\|.ico\|.svg\|.lock'\
            + '\|bootstrap.\|.jpg\|.snap\|.png\|out/'
        output = self._request(
            'cd "%s"; git ls-files | grep -v "%s" | xargs wc -l | sort -n'
            % (self.path, exclude)
        )
        files: List[str] = list(
            filter(lambda x: x != '', self._search(output, r"\S*(?=\n)"))
        )
        lines: List[str] = list(
            filter(lambda x: x != '', self._search(output, r"[0-9]*(?=\s\S)"))
        )

        files_len = len(files)
        files_commits_lines = []
        for k, i in enumerate(files):
            file = files[k]
            if file in self.commits_files:
                file = files[k]
                commits = self.commits_files[file]
                line = lines[k]
                files_commits_lines.append([file, commits, line])

        self.files_commits_lines = files_commits_lines
        self.line_len = int(lines[files_len - 1])

    def get(self) -> StatisticsParam:
        self.__commits_files()
        self.__lines_files()
        return {
            "line": self.line_len,
            "commit": self.commit_len,
            "chart": [["Файл", "Коммиты", "Строки"]] + self.files_commits_lines
        }


if __name__ == '__main__':
    path = "/home/user/project/"
    dynamics: DynamicsParam = Dynamics(path).get()
    dynamics2: List = MovingAverage(dynamics["table"], 10).get()
    statistics = Statistics(path).get()
    my_breakpoint = True
