# Agent Harness Architecture
## AI Trends Dashboard Project

프로젝트에 Claude 공식 문서 기반 에이전트 하네스 구조 적용

---

## 1. 전체 구조도

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Harness Layer                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Coordinator Agent (Main Orchestrator)        │   │
│  │  - Role: 트렌드 수집 작업 분배 및 결과 통합         │   │
│  │  - Model: claude-opus-4-8 (coordinator)              │   │
│  │  - Tools: agent_toolset_20260401 (multiagent)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│        ┌─────────────────┼─────────────────┐                 │
│        ↓                 ↓                 ↓                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │  Trend   │      │  Code    │      │  Data    │           │
│  │Collection│      │ Auditor  │      │Analytics │           │
│  │ Agent    │      │ Agent    │      │ Agent    │           │
│  │(웹검색) │      │(품질검사)│      │(시각화) │           │
│  └──────────┘      └──────────┘      └──────────┘           │
│        │                 │                 │                 │
│        └─────────────────┴─────────────────┘                 │
│                          │                                    │
│                   ┌──────↓──────┐                            │
│                   │   Results   │                            │
│                   │  Aggregator │                            │
│                   └──────┬──────┘                            │
│                          │                                    │
└──────────────────────────┼────────────────────────────────────┘
                           │
                    ┌──────↓──────┐
                    │  Dashboard  │
                    │   Output    │
                    └─────────────┘
```

---

## 2. 핵심 세 가지 구현 방식

### A. Tool Runner SDK (즉시 적용)

**목적**: 대시보드 데이터 수집/분석의 자동 루프 구성

**구현 파일**: `agent_harness_runner.py`

```python
from anthropic import Anthropic
from typing import Any

client = Anthropic()

# 1️⃣ @beta_tool 데코레이터로 도구 정의
@beta_tool  # Python SDK의 beta tool
def fetch_ai_trends(source: str, days: int = 7) -> str:
    """
    최근 AI 트렌드 수집
    
    Args:
        source: 뉴스 소스 ('hacker-news', 'arxiv', 'reddit')
        days: 수집 기간 (일)
    
    Returns:
        JSON 형식의 트렌드 데이터
    """
    # 기존 ai_trends_dashboard.py의 fetch_trends 로직 활용
    # feedparser, beautifulsoup4 사용
    pass

@beta_tool
def analyze_trends(trends_data: str) -> str:
    """트렌드 분석 및 인사이트 생성"""
    pass

@beta_tool
def generate_dashboard(analysis: str) -> str:
    """HTML 대시보드 생성"""
    pass

# 2️⃣ Tool Runner 초기화 및 루프 실행
def run_dashboard_agent():
    """Tool Runner 기반 자동 에이전트 루프"""
    
    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=4096,
        effort="high",
        tools=[
            fetch_ai_trends,
            analyze_trends,
            generate_dashboard
        ],
        messages=[
            {
                "role": "user",
                "content": "최근 7일간의 AI 트렌드를 수집하고 분석해서 대시보드를 생성해줘"
            }
        ],
        system="""당신은 AI 트렌드 분석 에이전트입니다.
        
다음 절차를 따르세요:
1. fetch_ai_trends를 호출해 최근 트렌드 데이터 수집
2. 수집된 데이터를 analyze_trends로 분석
3. 분석 결과를 generate_dashboard로 시각화
4. 완성된 대시보드 URL 반환

각 단계마다 진행 상황을 명확히 보고해주세요.""",
        max_iterations=10,  # 무한 루프 방지
    )
    
    # 3️⃣ Tool Runner가 자동으로 루프 실행
    # - Claude가 tool을 요청 → 자동 실행 → 결과 반환
    # - tool use 없는 응답이 나올 때까지 반복
    
    final_response = runner.until_done()  # 최종 결과만 획득
    return final_response

if __name__ == "__main__":
    result = run_dashboard_agent()
    print(result)
```

**매커니즘**:
- Runner가 매 iteration마다 Claude 호출
- Claude가 tool 사용 → 자동 실행 → 결과 피드백
- tool use 없을 때까지 반복
- `until_done()`: 최종 메시지만 반환 (context 절약)

**설정값**:
- `effort="high"`: 복잡 분석에 적합
- `max_iterations=10`: 폭주 방지
- `max_tokens=4096`: 출력 제한

---

### B. Multiagent Coordinator Pattern (확장성)

**목적**: 여러 전문 에이전트가 병렬로 협력하는 구조

**구현 파일**: `agent_harness_coordinator.py`

```python
import anthropic
from typing import Generator

client = anthropic.Anthropic()

# 1️⃣ 전문 에이전트 정의 (Managed Agents API 사용)
# 사전에 생성되어야 함 (ID 저장)

COORDINATOR_AGENT_ID = "agent_coordinator_xyz"
TREND_COLLECTOR_AGENT_ID = "agent_trend_xyz"
CODE_AUDITOR_AGENT_ID = "agent_auditor_xyz"
DATA_ANALYST_AGENT_ID = "agent_analyst_xyz"

# 2️⃣ Coordinator 설정 (multiagent 라우팅)
coordinator_config = {
    "model": "claude-opus-4-8",
    "prompt": """당신은 AI 트렌드 대시보드 코디네이터입니다.

다음 전문 에이전트들을 활용하세요:
- TrendCollector: 트렌드 데이터 수집 (병렬 처리 가능)
- CodeAuditor: 프로젝트 코드 품질 검사
- DataAnalyst: 수집 데이터 분석 및 시각화

각 에이전트에 작업을 분배하고 결과를 통합하세요.""",
    "multiagent": {
        "type": "coordinator",
        "agents": [
            {"type": "agent", "id": TREND_COLLECTOR_AGENT_ID},
            {"type": "agent", "id": CODE_AUDITOR_AGENT_ID},
            {"type": "agent", "id": DATA_ANALYST_AGENT_ID}
        ]
    },
    "tools": [
        {
            "type": "agent_toolset_20260401"  # 에이전트 위임 도구
        }
    ]
}

# 3️⃣ 세션 실행 (multiagent session)
def run_multiagent_session() -> Generator[dict, None, None]:
    """Multiagent 세션으로 작업 병렬 분배"""
    
    # 세션 생성
    session = client.beta.sessions.create(
        agent_id=COORDINATOR_AGENT_ID,
        environment_id="cloud_sandbox",  # Anthropic 클라우드
    )
    
    session_id = session.id
    
    # 사용자 요청 전송
    user_event = {
        "type": "user_message",
        "content": """다음을 병렬로 처리해줘:
        1. 최근 7일 AI 트렌드 수집 (TrendCollector)
        2. 현재 코드 품질 검사 (CodeAuditor)
        3. 수집 데이터 분석 (DataAnalyst)
        
        모든 결과를 통합해서 최종 대시보드 생성"""
    }
    
    # SSE 스트림으로 이벤트 수신
    with client.beta.sessions.stream(
        session_id=session_id,
        event=user_event
    ) as stream:
        for event in stream:
            yield event
            
            # 이벤트 타입별 처리
            if event.type == "thread_created":
                print(f"✓ Agent thread 생성: {event.thread_id}")
            
            elif event.type == "agent.thread_message_received":
                print(f"✓ Agent 작업 완료: {event.agent_id}")
            
            elif event.type == "session.status_idle":
                print(f"✅ 모든 에이전트 완료")
            
            elif event.type == "session.requires_action":
                # 사용자 승인 필요 시
                print(f"⚠️ 승인 필요: {event.action}")

# 4️⃣ 에이전트 thread 구조 (자동 관리)
# Primary thread: 전체 활동의 압축 뷰
#   ├─ Session thread (TrendCollector): 병렬 실행
#   ├─ Session thread (CodeAuditor): 병렬 실행  
#   └─ Session thread (DataAnalyst): 병렬 실행
```

**핵심 매커니즘**:
- **Coordinator**: 최상위 에이전트가 다른 에이전트에 task 위임
- **Threads**: 각 에이전트는 자체 thread에서 격리된 context로 실행
- **Parallel execution**: 독립 task는 동시 처리
- **SSE stream**: 실시간 이벤트 수신

**세션 상태**:
- `running`: 에이전트 작업 중
- `idle`: 대기 상태
- `requires_action`: 승인 필요
- `terminated`: 완료

---

### C. Agent SDK Loop Pattern (세밀한 제어)

**목적**: HITL 승인, 커스텀 로깅, 조건부 실행이 필요할 때

**구현 파일**: `agent_harness_sdk.py`

```python
from anthropic import Anthropic
from anthropic.types.messages import MessageStartEvent

client = Anthropic()

def run_agent_with_human_approval():
    """Agent SDK 기반 수동 루프 - HITL 패턴"""
    
    system_prompt = """당신은 AI 트렌드 분석 에이전트입니다.
    
다음 도구들을 사용해 작업을 완료하세요:
- fetch_trends: AI 트렌드 데이터 수집
- analyze_data: 데이터 분석
- generate_report: 리포트 생성"""
    
    messages = [
        {
            "role": "user",
            "content": "최근 AI 트렌드를 분석해서 리포트 생성해줘"
        }
    ]
    
    tools = [
        # tool 정의 (스키마)
    ]
    
    # 1️⃣ 수동 루프 (세밀한 제어)
    turn_count = 0
    max_turns = 10
    
    while turn_count < max_turns:
        turn_count += 1
        
        print(f"\n=== Turn {turn_count} ===")
        
        # 2️⃣ Claude 호출
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            system=system_prompt,
            tools=tools,
            messages=messages
        )
        
        # 3️⃣ 응답 처리
        
        # Tool use가 없으면 완료
        if response.stop_reason == "end_turn":
            print(f"✅ 에이전트 작업 완료")
            print(f"Final response: {response.content[0].text}")
            break
        
        # Tool use 요청 처리
        if response.stop_reason == "tool_use":
            
            # 🔄 메시지 이력에 assistant 응답 추가
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # 4️⃣ Tool 실행 결과 수집
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id
                    
                    print(f"Tool 호출: {tool_name}")
                    print(f"Input: {tool_input}")
                    
                    # 5️⃣ HITL 승인 (선택)
                    # 중요한 작업은 승인 대기
                    if tool_name == "generate_report":
                        approval = input("리포트 생성을 승인하시겠습니까? (y/n): ")
                        if approval != "y":
                            print("❌ 작업 취소됨")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": "사용자가 작업을 거부했습니다.",
                                "is_error": True
                            })
                            continue
                    
                    # 6️⃣ Tool 실행 (실제 함수 호출)
                    try:
                        if tool_name == "fetch_trends":
                            result = fetch_trends(tool_input.get("days", 7))
                        elif tool_name == "analyze_data":
                            result = analyze_data(tool_input.get("data"))
                        elif tool_name == "generate_report":
                            result = generate_report(tool_input.get("analysis"))
                        else:
                            result = f"Unknown tool: {tool_name}"
                            is_error = True
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result,
                            "is_error": False
                        })
                        
                        # 커스텀 로깅
                        print(f"✓ Tool 실행 완료: {len(result)} chars")
                    
                    except Exception as e:
                        print(f"❌ Tool 에러: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })
            
            # 7️⃣ Tool 결과를 메시지에 추가
            messages.append({
                "role": "user",
                "content": tool_results
            })
    
    return response

# Tool 함수 구현
def fetch_trends(days: int) -> str:
    # ai_trends_dashboard.py의 fetch 로직 활용
    pass

def analyze_data(data: str) -> str:
    # 분석 로직
    pass

def generate_report(analysis: str) -> str:
    # 리포트 생성 로직
    pass

if __name__ == "__main__":
    result = run_agent_with_human_approval()
```

**특징**:
- **수동 루프**: 매 iteration 제어 가능
- **HITL 승인**: 중요 작업 전 사용자 확인
- **에러 처리**: tool 실패 시 `is_error: true`로 처리
- **커스텀 로깅**: 각 단계 상세 기록
- **조건부 실행**: tool 실행 전 커스텀 로직

---

## 3. 프로젝트 파일 구성

```
C:\Users\Admin\Desktop\AI\
├── agent_harness/
│   ├── __init__.py
│   ├── runner.py                    # Tool Runner 구현
│   ├── coordinator.py               # Multiagent Coordinator
│   ├── sdk_loop.py                  # Agent SDK 수동 루프
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── trend_collector.py      # @beta_tool 도구들
│   │   ├── code_auditor.py
│   │   └── data_analyst.py
│   └── config.py                    # 공통 설정
│
├── AGENT_HARNESS.md                 # 이 파일
├── AGENTS.md                        # 팀 에이전트 설정
├── ai_trends_dashboard.py           # 기존 구현
├── app.py
└── requirements.txt
```

---

## 4. 구현 우선순위

### Phase 1: Tool Runner (1주)
- ✅ 간단, 인프라 불필요
- ✅ 기존 코드 재사용 용이
- 시작점: `agent_harness/runner.py`

### Phase 2: Agent SDK Loop (2주)
- HITL 승인 필요한 경우
- 커스텀 로깅 추가
- 시작점: `agent_harness/sdk_loop.py`

### Phase 3: Multiagent Coordinator (1개월)
- 병렬 처리 필요할 때
- Managed Agents 베타 접근 요청
- 시작점: `agent_harness/coordinator.py`

---

## 5. 클라우드 환경 선택

| 구현 방식 | 로컬 | 클라우드 | 베타 | 추천 |
|----------|------|--------|------|------|
| **Tool Runner** | ✅ | ❌ | ❌ | Phase 1 |
| **Agent SDK** | ✅ | ❌ | ❌ | Phase 2 |
| **Managed Agents** | ❌ | ✅ | ✅ | Phase 3 |

---

## 6. 환경 변수 설정

```bash
# .env 파일
ANTHROPIC_API_KEY=sk-ant-...

# Tool Runner용
TRENDS_SOURCES=hacker-news,arxiv,reddit
ANALYSIS_DEPTH=high

# Managed Agents용 (Phase 3)
MANAGED_AGENT_ID=agent_coordinator_...
ENVIRONMENT_ID=cloud_sandbox
```

---

## 7. 공식 문서 참고

- **Tool Runner SDK**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner
- **Agent SDK Loop**: https://code.claude.com/docs/en/agent-sdk/agent-loop
- **Managed Agents**: https://platform.claude.com/docs/en/managed-agents/overview
- **Multiagent Pattern**: https://platform.claude.com/docs/en/managed-agents/multi-agent

---

## 8. Next Steps

1. **requirements.txt에 추가**:
   ```
   anthropic>=0.28.0  # beta_tool 지원
   ```

2. **agent_harness/tools/trend_collector.py 작성**:
   - @beta_tool 데코레이터
   - fetch_ai_trends() 함수
   - feedparser, beautifulsoup4 활용

3. **agent_harness/runner.py 구현**:
   - Tool Runner 초기화
   - 자동 루프 테스트

4. **테스트**:
   ```bash
   python -m agent_harness.runner
   ```

