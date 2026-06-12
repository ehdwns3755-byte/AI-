# Agent Team Settings

이 프로젝트의 에이전트 팀 설정입니다.

## 팀 에이전트 구성

### 1. 코드 감시 에이전트 (Code Auditor Agent)
- **목적**: 코드 품질 검토 및 이슈 발견
- **기능**: 코드 감사, 버그 탐지, 리팩토링 제안
- **권한**: 읽기, 분석, 리포트 생성
- **사용**: `iterative-document-optimization` 스킬로 자동 실행

### 2. 이슈 해결 에이전트 (Issue Resolution Agent)
- **목적**: 발견된 이슈 자동 해결
- **기능**: 코드 수정, 커밋 생성, 문서 업데이트
- **권한**: 쓰기, 커밋, 푸시
- **사용**: `issue-resolution-workflow` 스킬로 자동 실행

### 3. 데이터 분석 에이전트 (Data Analytics Agent)
- **목적**: AI 트렌드 분석 및 대시보드 생성
- **기능**: 데이터 처리, 시각화, 리포트 생성
- **권한**: 읽기, 데이터 분석, 파일 생성
- **사용**: `ai_trends_dashboard.py` 실행

## 팀 워크스페이스 설정

### 에이전트 간 통신
- 에이전트는 커밋 및 git history를 통해 협력
- 각 에이전트의 변경사항은 별도의 커밋으로 추적
- 이슈와 PR을 통한 비동기 협력 지원

### 권한 및 역할

#### Developer Role
- 코드 읽기/쓰기
- 이슈 생성/관리
- PR 생성/검토
- 에이전트 실행

#### Admin Role
- 모든 Developer 권한
- 에이전트 설정 관리
- 팀 멤버 관리
- 워크스페이스 설정

## 에이전트 실행 워크플로우

### 1. 코드 분석 사이클
```
1. Code Auditor Agent 실행
   └─> 이슈 발견 및 ISSUES.md 업데이트
   
2. Issue Resolution Agent 실행
   └─> 이슈 해결 및 커밋 생성
   
3. 반복 (수렴할 때까지)
```

### 2. 데이터 분석 사이클
```
1. Data Analytics Agent 실행
   └─> 트렌드 분석
   └─> 대시보드 생성 (ai_dashboard.html)
   └─> 결과 커밋
```

## 팀 협력 가이드

### 커밋 규칙
- 에이전트 자동 커밋: `docs:`, `fix:`, `feat:` 프리픽스 사용
- 수동 커밋: 명확한 메시지와 함께 작성
- 이슈 참조: `Fixes #123` 형식으로 이슈 링크

### 코드 리뷰
- Code Auditor가 자동으로 변경사항 검토
- 중요 변경은 팀 멤버 수동 검토 필요
- PR은 최소 1명의 승인 필수

### 문서 관리
- ISSUES.md: 자동 업데이트 (에이전트 감지)
- AGENTS.md: 이 파일 (팀 설정 문서)
- CLAUDE.md: Claude Code 설정 (있으면 우선)
- README.md: 프로젝트 개요

## 환경 변수

```bash
# GitHub 연동
GITHUB_TOKEN=your_token
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo_name

# AI 서비스 설정
ANTHROPIC_API_KEY=your_api_key
```

## 트러블슈팅

### 에이전트가 실행되지 않을 때
1. 권한 확인: `Skill(claude-api)` 허용 여부
2. API 키 확인: `ANTHROPIC_API_KEY` 설정 확인
3. 네트워크 확인: GitHub/API 연결 상태

### 커밋 실패 시
1. git config 확인: `git config --global user.name`, `user.email`
2. 권한 확인: `Bash(git commit *)` 허용 여부
3. 스테이징 상태 확인: `git status`

## 참고 자료

- [Managed Agents Overview](https://platform.claude.com/docs/en/managed-agents/overview)
- [Agent Setup Guide](https://platform.claude.com/docs/en/managed-agents/agent-setup)
- [Issue Resolution Workflow](./ISSUES.md)
