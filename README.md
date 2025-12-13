# Desktop Kitty

Windows 데스크톱 환경에서 돌아다니는 귀여운 고양이 펫 애플리케이션입니다.

## 🌟 주요 기능

- **다양한 행동 패턴**: 걷기, 앉기, 잠자기, 마우스 따라다니기 등 다양한 상태를 가집니다.
- **상호작용**:
  - **드래그**: 마우스로 펫을 집어서 원하는 위치로 옮길 수 있습니다.
  - **더블 클릭**: 펫을 쓰다듬어 친밀도를 높일 수 있습니다.
  - **우클릭 메뉴**: 중력 모드, 따라오기 모드, 잠재우기, 설정 등 다양한 기능을 제어할 수 있습니다.
- **상태 시스템**: 배고픔, 친밀도, 졸림 등의 상태가 존재하며, 시간에 따라 변화합니다.
- **데이터 저장**: 펫의 상태와 설정이 자동으로 저장되어 재시작 시에도 유지됩니다.
- **커스텀 스프라이트**: `assets` 폴더를 통해 나만의 스프라이트를 적용할 수 있습니다.
- **멀티 모니터 지원**: 다중 모니터 환경에서도 자유롭게 이동할 수 있습니다.

## 🛠️ 설치 및 실행

### 요구 사항

- Windows 10 또는 11
- Python 3.8 이상

### 설치

1. 의존성 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

### 실행

터미널에서 다음 명령어를 실행하세요:

```bash
python main.py
```

## 📂 프로젝트 구조

```text
Desktop Kitty/
├── main.py                 # 프로그램 진입점
├── pet_data.json           # 펫 상태 데이터 (자동 생성)
├── settings.json           # 사용자 설정 데이터 (자동 생성)
├── Kitty.ico               # 애플리케이션 아이콘
├── src/
│   ├── pet_entity.py       # 펫의 메인 로직 및 윈도우 처리
│   ├── pet_status.py       # 펫의 상태(배고픔, 친밀도 등) 관리
│   ├── status_window.py    # 상태 표시창 UI
│   ├── sprite_manager.py   # 스프라이트 이미지 로드 및 관리
│   ├── state_machine.py    # 펫의 행동(FSM) 제어
│   ├── cursor_utils.py     # 마우스 커서 관련 유틸리티
│   ├── resource_utils.py   # 리소스 경로 처리 유틸리티
│   ├── config.py           # 설정 관리
│   └── constants.py        # 상수 정의
├── assets/                 # 이미지 리소스 폴더
└── DesktopKitty.spec       # PyInstaller 빌드 설정 파일
```

## ⌨️ 개발 정보

- **Framework**: PyQt6
- **Architecture**:
  - **Entity**: `PetEntity` 클래스가 투명 윈도우로 펫을 렌더링합니다.
  - **Component**: 상태(`PetStatus`), 스크립트(`SpriteManager`), 행동(`StateMachine`)이 모듈화되어 있습니다.
- **Packaging**: PyInstaller를 사용하여 단일 실행 파일(.exe)로 빌드할 수 있습니다.

## 📝 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 용도로 제작되었습니다.
