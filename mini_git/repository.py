"""커밋, 브랜치 및 검색 인덱스를 메모리에 저장한다."""

from dataclasses import dataclass
from datetime import datetime, timezone

from .algorithms import ancestors, merge_sort, shortest_path, topological_order


@dataclass(frozen=True)
class Commit:
    """생성 후 변경하지 않는 커밋 메타데이터."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]


class Repository:
    """브랜치는 마지막 커밋의 이름표이고 HEAD는 현재 브랜치 이름이다."""

    def __init__(self):
        self.author = None
        self.head = None
        self.commits = {}
        self.branches = {}
        self.children = {}
        self.keyword_index = {}
        self.author_index = {}
        self.counter = 0

    def require_init(self):
        if self.head is None:
            raise ValueError("Repository not initialized")

    def initialize(self, author):
        """중복 INIT은 기존 기록을 지우지 않고 거절한다."""
        if self.head is not None:
            raise ValueError("Already initialized")
        if not author.strip():
            raise ValueError("Invalid args")
        self.author = author
        self.head = "main"
        self.branches["main"] = None

    def require_branch(self, name):
        if name not in self.branches:
            raise ValueError(f"Unknown branch: {name}")

    def require_commit(self, commit_hash):
        if commit_hash not in self.commits:
            raise ValueError(f"Unknown commit: {commit_hash}")

    def branch(self, name):
        self.require_init()
        if not name.strip():
            raise ValueError("Invalid args")
        if name in self.branches:
            raise ValueError(f"Branch already exists: {name}")
        self.branches[name] = self.branches[self.head]

    def switch(self, name):
        self.require_init()
        self.require_branch(name)
        self.head = name

    def commit(self, message, merge_branch=None):
        """기존 노드만 부모로 연결하여 사이클 생성을 방지한다."""
        self.require_init()
        if not message.strip():
            raise ValueError("Invalid args")
        current = self.branches[self.head]
        parents = () if current is None else (current,)
        if merge_branch is not None:
            self.require_branch(merge_branch)
            other = self.branches[merge_branch]
            if current is None or other is None or current == other:
                raise ValueError("Merge requires two distinct non-empty heads")
            parents += (other,)
        # 증가 정수의 16진수 표현: 암호학적 해시는 아니며 절대 재사용하지 않는다.
        self.counter += 1
        commit_hash = format(self.counter, "016x")
        result = Commit(commit_hash, message, self.author, datetime.now(timezone.utc), parents)
        self.commits[commit_hash] = result
        self.children[commit_hash] = []
        for parent in parents:
            self.children[parent].append(commit_hash)
        self.branches[self.head] = commit_hash
        for token in set(message.lower().split()):
            self.keyword_index.setdefault(token, []).append(commit_hash)
        self.author_index.setdefault(self.author, []).append(commit_hash)
        return result

    def log(self, sort_by=None):
        """모든 브랜치의 커밋을 출력한다. 옵션 정렬은 위상 순서를 보장하지 않는다."""
        self.require_init()
        if sort_by is None:
            return [self.commits[h] for h in topological_order(self.commits, self.children)]
        if sort_by not in ("date", "author"):
            raise ValueError("Invalid args")
        key = (lambda c: c.timestamp) if sort_by == "date" else (lambda c: c.author)
        return merge_sort(self.commits.values(), key)

    def search(self, keyword=None, author=None):
        """단어 교집합 검색. 커밋 전체가 아닌 인덱스 목록만 조회한다."""
        self.require_init()
        if author is not None:
            hashes = self.author_index.get(author, [])
        else:
            tokens = set((keyword or "").lower().split())
            if not tokens:
                raise ValueError("Invalid args")
            postings = merge_sort([self.keyword_index.get(t, []) for t in tokens], len)
            matches = set(postings[0])
            for posting in postings[1:]:
                if not matches:
                    break
                matches.intersection_update(posting)
            hashes = [h for h in postings[0] if h in matches]
        return [self.commits[h] for h in hashes]

    def path(self, start, end):
        self.require_init()
        self.require_commit(start)
        self.require_commit(end)
        return shortest_path(self.commits, self.children, start, end)

    def ancestors(self, commit_hash):
        self.require_init()
        self.require_commit(commit_hash)
        return [self.commits[h] for h in ancestors(self.commits, commit_hash)]
