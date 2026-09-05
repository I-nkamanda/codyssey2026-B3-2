"""따옴표를 지원하는 명령 파서와 REPL."""

import shlex

from .repository import Repository


HELP = '''INIT "user name"
BRANCH <name> | SWITCH <name>
COMMIT "message" | MERGE <branch>
LOG | LOG --sort-by=date|author
PATH <hash1> <hash2> | ANCESTORS <hash>
SEARCH "keyword" | SEARCH --author="user name"
HELP | EXIT | QUIT'''


def format_commits(commits):
    """각 커밋의 필수 필드를 한 줄에 표시한다."""
    return "\n".join(
        f"{c.hash} | {c.author} | {c.timestamp.isoformat()} | {c.message}"
        for c in commits
    ) or "No commits"


def execute(repository, line):
    """출력 문자열을 반환하고 종료 명령에는 None을 반환한다."""
    try:
        parts = shlex.split(line)
    except ValueError:
        return "Invalid args"
    if not parts:
        return ""
    command, args = parts[0].upper(), parts[1:]
    try:
        if command in ("EXIT", "QUIT", "HELP") and not args:
            return HELP if command == "HELP" else None
        if command == "INIT" and len(args) == 1:
            repository.initialize(args[0])
            return f"Initialized repository.\nCurrent branch: main\nCurrent user: {repository.author}"
        if command in ("BRANCH", "SWITCH", "COMMIT", "MERGE") and len(args) == 1:
            if command == "BRANCH":
                repository.branch(args[0])
                return f"Created branch: {args[0]}"
            if command == "SWITCH":
                repository.switch(args[0])
                return f"Switched to branch: {args[0]}"
            result = repository.commit(args[0]) if command == "COMMIT" else repository.commit(
                f"Merge {args[0]} into {repository.head}", merge_branch=args[0]
            )
            return f"[{repository.head} {result.hash}] {result.message}"
        if command == "LOG":
            if not args:
                return format_commits(repository.log())
            if len(args) == 1 and args[0] in ("--sort-by=date", "--sort-by=author"):
                return format_commits(repository.log(args[0].split("=", 1)[1]))
        if command == "PATH" and len(args) == 2:
            path = repository.path(*args)
            return "Path: " + "->".join(path) if path else "No path"
        if command == "ANCESTORS" and len(args) == 1:
            return format_commits(repository.ancestors(args[0]))
        if command == "SEARCH" and len(args) == 1:
            if args[0].startswith("--author="):
                author = args[0].split("=", 1)[1]
                if not author.strip():
                    return "Invalid args"
                results = repository.search(author=author)
            elif args[0].startswith("--"):
                return "Invalid args"
            else:
                results = repository.search(keyword=args[0])
            return f"Found {len(results)} commit(s):\n" + format_commits(results)
        known = {"INIT", "BRANCH", "SWITCH", "COMMIT", "MERGE", "LOG", "PATH", "ANCESTORS", "SEARCH", "EXIT", "QUIT", "HELP"}
        return "Invalid args" if command in known else f"Unknown command: {parts[0]}"
    except ValueError as error:
        return str(error)


def repl():
    """오류 이후에도 계속 입력받으며 EOF와 Ctrl+C로도 종료한다."""
    repository = Repository()
    print("Mini Git - type HELP for commands.")
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        output = execute(repository, line)
        if output is None:
            print("Bye!")
            break
        if output:
            print(output)
