# Mini Git — 커밋 기록과 그래프를 배우는 CLI

과제 원문은 [b3-2-mission.md](b3-2-mission.md)입니다. Python 3.10 이상에서 실행하며 외부 패키지 설치는 필요 없습니다.

실제 파일의 내용을 저장하는 Git이 아니라 **누가, 언제, 어떤 메시지로 기록을 남겼고 어떤 기록에서 이어졌는지**를 관리하는 학습용 프로그램입니다. 종료하면 데이터는 사라집니다.

## 실행

이 폴더에서 터미널을 열고 실행하세요. Windows에서 `python`이 없고 Python Launcher가 있다면 `py main.py`를 사용할 수 있습니다.

```sh
python main.py
```

`mini-git>` 뒤에 명령을 입력합니다. 안내는 `HELP`, 종료는 `EXIT` 또는 `QUIT`입니다. 명령 이름은 대소문자를 구분하지 않습니다. 공백이 있는 인자는 큰따옴표로 감쌉니다.

```text
INIT "Alice Kim"
COMMIT "Initial commit"
BRANCH feature
SWITCH feature
COMMIT "Add login feature"
SWITCH main
COMMIT "Add payment feature"
LOG
PATH 0000000000000002 0000000000000003
SEARCH "login"
SEARCH --author="Alice Kim"
MERGE feature
ANCESTORS 0000000000000004
QUIT
```

위 경로 결과는 `Path: 0000000000000002->0000000000000001->0000000000000003`입니다. 새 실행에서는 첫 커밋부터 `0000000000000001`, `0000000000000002` 순서로 ID가 부여됩니다. 16진수라 9 다음은 a입니다. 날짜는 실행 시점의 UTC로 표시됩니다.

전체 예제는 [examples/demo.txt](examples/demo.txt)에 있습니다. PowerShell에서 한 번에 실행하려면 다음을 사용합니다.

```powershell
Get-Content examples/demo.txt | python main.py
```

## 고등학생 대상 시연

[시연 매뉴얼](../docs/DEMO_MANUAL.md)은 발표자가 따라 할 수 있는 12~15분 진행 대본입니다. 단계별 입력 명령, 예상 결과, 쉬운 설명 멘트와 학생에게 던질 질문을 담았습니다. 5분 축약 순서, 예상 질문과 답변, 오류 대응 방법도 제공합니다.

시연 전에 프로그램을 새로 실행하고 매뉴얼 순서대로 진행하면 기록 번호가 예시와 일치합니다. 발표 중에는 시연 매뉴얼을, 수업 준비에는 [학습 자료](../docs/LEARNING.md)를 활용하세요.

현재 로컬 폴더에서는 실행 파일과 `docs`가 이 README의 상위 폴더에 있습니다. 실행은 `main.py`가 있는 폴더에서 하세요. GitHub 업로드 시 프로그램과 `docs`를 저장소 안에 함께 포함하고, 위 두 링크를 각각 `docs/DEMO_MANUAL.md`, `docs/LEARNING.md`로 바꾸면 됩니다.

## 명령 및 해석 규칙

- `INIT "사용자 이름"`: main 브랜치와 사용자를 만듭니다. 다시 INIT하면 `Already initialized`로 거절하여 기존 기록을 보호합니다.
- `BRANCH 이름`: 현재 커밋을 가리키는 브랜치를 만듭니다. 자동 전환하지 않습니다. 중복 이름은 거절합니다.
- `SWITCH 이름`: 현재 브랜치를 바꿉니다. 사용자 이름은 바뀌지 않습니다.
- `COMMIT "메시지"`: 현재 브랜치의 마지막 커밋을 부모로 기록합니다. 첫 커밋에는 부모가 없습니다.
- `LOG`: **모든 브랜치의 전체 기록**을 부모부터 출력합니다. 같은 단계에서는 저장 및 큐 등록 순서를 따릅니다.
- `LOG --sort-by=date`: UTC 시각 오름차순입니다.
- `LOG --sort-by=author`: 작성자 문자열 오름차순입니다. 정렬 옵션의 동률은 생성 순서를 유지하며, 옵션 사용 시 부모 우선 순서는 보장하지 않습니다.
- `PATH ID1 ID2`: 부모 연결을 양방향으로 이동할 수 있다고 보고 최소 간선 경로를 찾습니다. 동률이면 `hash1->hash2->...` 문자열의 사전순 최소 경로를 선택합니다. 연결이 없으면 `No path`, 같은 ID라면 그 ID 하나입니다.
- `ANCESTORS ID`: 자신을 제외한 모든 조상을 중복 없이 DFS 방문 순서로 표시합니다.
- `SEARCH "단어"`: 소문자로 변환한 공백 단위 **정확한 토큰** 검색입니다. `login`은 `login,`이나 `logins`와 다릅니다. 여러 단어는 순서와 무관하게 모두 포함해야 합니다. 부분 문자열/연속 문장 검색은 아닙니다.
- `SEARCH --author="이름"`: 대소문자를 구분하는 작성자 전체 이름 검색입니다. 검색 결과는 생성 순서입니다.
- `MERGE 브랜치`: 선택 과제 구현입니다. 현재 HEAD와 대상 HEAD를 부모로 하는 새 커밋을 만듭니다. 두 HEAD는 비어 있지 않고 서로 달라야 합니다. 파일 충돌 처리나 실제 Git의 fast-forward는 구현하지 않습니다.

브랜치 이름과 옵션 값은 대소문자를 구분합니다. 없는 이름은 `Unknown branch: ...`, 없는 ID는 `Unknown commit: ...`, 잘못된 인자나 닫히지 않은 따옴표는 `Invalid args`를 출력하고 계속 실행합니다. ID는 전체를 입력해야 합니다.

## 파일 구성과 검증

- `main.py`: 실행 진입점.
- `mini_git/cli.py`: 명령 해석과 반복 입력.
- `mini_git/repository.py`: 커밋·브랜치·두 역색인.
- `mini_git/algorithms.py`: 직접 구현한 병합 정렬, 위상 정렬, BFS, DFS.
- `tests/test_mini_git.py`: 분기/병합, 동률 경로, 연결 끊김, 인덱스 검색, 오류, 정렬 안정성 등 검사.
- `.github/workflows/tests.yml`: GitHub push/PR 시 Python 버전별 자동 검사.
- [학습 자료](docs/LEARNING.md): 쉬운 개념 설명, 실습, 알고리즘 비용, 발표 문장.
- [시연 매뉴얼](../docs/DEMO_MANUAL.md): 고등학생 대상 대본, 명령과 예상 결과, 질의응답 및 오류 대응.
- [요구사항 점검](docs/REQUIREMENTS.md): 구현 위치와 검증 근거.
- [GitHub 업로드 안내](docs/GITHUB.md): 처음 업로드하는 방법.

```sh
python -m unittest discover -s tests -v
```

표준 정렬 API와 그래프 전용 라이브러리는 사용하지 않습니다. 해시 필드는 증가 카운터를 16진수 문자열로 바꾼 **식별자**이며 실제 Git의 내용 기반 해시는 아닙니다. 정수는 계속 증가하므로 같은 실행 안에서 중복되지 않습니다.

선택 과제 중 MERGE를 구현했습니다. Diff와 두 정렬 알고리즘의 성능 비교는 구현 범위에 포함하지 않았습니다. GitHub에 실제 업로드하거나 공개 라이선스를 지정하는 작업은 수행하지 않았습니다.
