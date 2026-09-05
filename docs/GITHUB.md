# GitHub에 처음 올리는 방법

이 폴더에는 프로그램, 테스트, 설명서, 불필요한 파일 제외 설정, 자동 검사 설정이 준비되어 있습니다. 외부 패키지가 없어 `requirements.txt`는 필요하지 않습니다. 아직 원격 저장소를 만들거나 파일을 업로드한 상태는 아닙니다.

## 업로드 전

1. `python main.py`로 프로그램을 실행합니다.
2. `python -m unittest discover -s tests -v`로 검사를 실행합니다.
3. 공개하려는 자료인지 확인합니다. 과제 원문 `b3-2-mission.md`의 재배포 권한이 불명확하다면 우선 비공개 저장소를 사용하세요.

## Git을 이용한 업로드

GitHub에서 빈 저장소를 만듭니다. 이름은 예를 들어 `mini-git`로 정할 수 있습니다. 아래 흐름에서는 GitHub 쪽 README와 .gitignore 자동 생성을 선택하지 않습니다. 이 폴더에 이미 있습니다.

이 폴더에서 터미널을 열고 다음을 실행합니다. 이 문서의 실제 Git 명령은 프로그램 안의 `mini-git>` 프롬프트에서 실행하는 명령이 아닙니다.

```sh
git init
git add .
git commit -m "Implement Mini Git and learning guide"
git branch -M main
```

Git이 사용자 정보를 요구하면 본인의 이름과 이메일을 해당 저장소에 설정한 뒤 commit을 다시 실행합니다.

```sh
git config user.name "본인 이름"
git config user.email "본인 이메일"
```

그다음 GitHub가 새 저장소 화면에서 제공하는 주소를 아래 예시 주소 대신 입력합니다.

```sh
git remote add origin https://github.com/YOUR_NAME/YOUR_REPOSITORY.git
git push -u origin main
```

`YOUR_NAME`과 `YOUR_REPOSITORY`는 반드시 실제 값으로 바꿉니다. 인증 요청은 GitHub의 로그인 안내에 따릅니다. 토큰이나 비밀번호를 코드 파일에 적지 않습니다.

업로드 후 README가 표시되고, Actions에서 `Python tests` 결과를 확인할 수 있습니다. 초록색 성공 표시라면 설정된 Python 버전의 검사를 통과한 것입니다.

## 이후 수정분 올리기

```sh
git add .
git commit -m "Update Mini Git"
git push
```

`.gitignore`는 Python 임시 파일과 가상 환경 등을 제외합니다. `.gitattributes`는 운영체제 간 줄바꿈 차이를 줄입니다. 공개 라이선스는 저작권자의 선택이므로 자동으로 부여하지 않았습니다. 배포 허용 범위를 정한 후 필요한 LICENSE를 추가하세요.
