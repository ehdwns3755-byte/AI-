# GitHub Issues - AI Trends Dashboard

GitHub에 등록할 이슈들입니다. 각 이슈를 복사해서 GitHub에서 직접 생성하세요.

---

## Issue 1️⃣: XSS 취약점: HTML 콘텐츠에 대한 이스케이프 처리 부재

**Type:** Bug 🐛  
**Priority:** 🔴 High

### 문제
`generate_html()` 메서드에서 `item['title']`과 `item['summary']` 등을 직접 HTML에 삽입하고 있습니다. 악의적인 HTML/JS 코드가 포함된 뉴스 제목이 있으면 XSS 공격이 가능합니다.

### 위치
- Line 347: `{item['title']}`
- Line 350: `{item['summary']}`

### 해결책
html 모듈의 escape() 함수를 사용하여 모든 사용자 입력을 이스케이프 처리:

```python
from html import escape
# ...
escape(item['title'])
escape(item['summary'])
```

---

## Issue 2️⃣: 에러 처리 개선: 과도하게 광범위한 Exception 처리

**Type:** Improvement 📈  
**Priority:** 🟡 Medium

### 문제
모든 fetch 메서드에서 광범위한 `except Exception as e:` 처리로 인해 구체적인 에러 원인을 파악하기 어렵습니다.

### 위치
- Line 34-35: Google News
- Line 59-60: Hacker News  
- Line 79-80: Product Hunt
- Line 100-101: Reddit

### 문제점
- 네트워크 타임아웃 vs API 에러 vs 파싱 에러 구분 불가
- 중요한 에러 정보가 손실됨
- 디버깅 어려움

### 해결책
구체적인 Exception 타입으로 분리:

```python
except requests.Timeout:
    print(f"Timeout: {url}")
except requests.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Issue 3️⃣: 로깅 부재: print()만 사용 중 - 실행 기록 남지 않음

**Type:** Improvement 📈  
**Priority:** 🟡 Medium

### 문제
프로그램이 작업 스케줄러에서 자동 실행될 때 print() 출력이 어디로 가는지 알 수 없습니다. 오류 발생 시 추적이 어렵습니다.

### 해결책
logging 모듈을 사용하여 파일에 기록:

```python
import logging

# __init__ 메서드에 추가
log_file = os.path.join(self.script_dir, 'ai_trends.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# print() 대신 사용
logging.info('AI 뉴스 수집 시작')
logging.error(f'Google News 수집 실패: {e}')
```

---

## Issue 4️⃣: Hacker News: 실제 발행일 대신 현재 날짜로 설정됨

**Type:** Bug 🐛  
**Priority:** 🟡 Medium

### 문제
Line 56에서 Hacker News의 뉴스는 항상 오늘 날짜로 저장됩니다. 실제로는 며칠 전 기사일 수 있습니다.

```python
'date': datetime.now().strftime('%Y-%m-%d'),  # ❌ 잘못됨
```

### 해결책
BeautifulSoup으로 실제 발행일을 파싱해서 사용합니다. Hacker News는 페이지에 timestamp를 포함하고 있습니다.

```python
# 실제 날짜 추출 로직 추가 필요
time_elem = story.find('span', class_='age')
if time_elem:
    # 상대 시간(예: "2 hours ago") 파싱
    pass
```

---

## Issue 5️⃣: 타임아웃 설정 불일치: Google News와 Product Hunt에 타임아웃 없음

**Type:** Bug 🐛  
**Priority:** 🟡 Medium

### 문제
- Google News (Line 22): timeout 설정 없음
- Product Hunt (Line 66): timeout 설정 없음
- Hacker News, Reddit: timeout=10

네트워크가 느릴 때 무한 대기할 수 있습니다.

### 해결책
모든 requests.get() 호출에 timeout 설정:

```python
# Google News에서 feedparser.parse() 사용 중
# feedparser는 requests를 내부적으로 사용하니, requests.get() 직접 호출로 변경

# Product Hunt
response = requests.get(url, headers=headers, timeout=10)
```

---

## Issue 6️⃣: 중복 제거 로직 개선: 제목만으로 중복 판단

**Type:** Improvement 📈  
**Priority:** 🟢 Low

### 문제
같은 뉴스가 다른 제목으로 표현되면 중복으로 감지되지 않습니다.

### 해결책
정규화된 제목으로 중복 제거:

```python
# run() 메서드에서
normalized_title = item['title'].lower().strip()
if normalized_title not in seen:
    seen.add(normalized_title)
    unique_items.append(item)
```

---

## Issue 7️⃣: robots.txt 미준수: 자동 크롤링 정책 확인 필요

**Type:** Improvement 📈  
**Priority:** 🟡 Medium (법적 이슈 가능성)

### 문제
일부 웹사이트(예: Hacker News)는 robots.txt에서 자동 크롤링을 제한할 수 있습니다.

### 해결책
- **Hacker News**: 공식 API 사용 추천
  - https://github.com/HackerNews/API
  - `https://hacker-news.firebaseio.com/v0/topstories.json`

- **Product Hunt**: RSS 피드는 공식 지원
  - 현재 방식 유지 가능

- **일반**: 적절한 User-Agent와 Delay 추가

---

## Issue 8️⃣: 뉴스 0개 수집 시 처리 로직 확인

**Type:** Improvement 📈  
**Priority:** 🟡 Medium

### 문제
모든 소스에서 뉴스를 못 가져왔을 때 빈 대시보드가 생성됩니다. 사용자가 뭐가 잘못됐는지 알 수 없습니다.

### 해결책
```python
if not self.news_items:
    logging.warning('수집된 뉴스가 없습니다. 네트워크 연결 및 API 상태 확인')
    # 옵션: 이전 데이터 사용
    self._load_previous_data()
```

---

## Issue 9️⃣: README: setup_scheduler.ps1 실행 방법이 불명확함

**Type:** Documentation 📚  
**Priority:** 🟡 Medium (사용자 경험)

### 문제
README.md에서:
1. PowerShell 실행 정책 변경 설명 부족
2. 관리자 권한 필요성 명시 안 됨
3. 오류 발생 시 대응 방법 없음

### 해결책
더 자세한 단계별 가이드 추가:

```markdown
### 3. 작업 스케줄러 설정 (관리자 권한 필요)

1. **PowerShell을 관리자로 실행**
   - Windows 검색 → "PowerShell" 검색
   - 마우스 우클릭 → "관리자 권한으로 실행"

2. **현재 실행 정책 확인** (선택사항)
   ```powershell
   Get-ExecutionPolicy
   ```

3. **실행 정책 변경** (첫 번째만 필요)
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   Y (예) 선택
   ```

4. **스크립트 실행**
   ```powershell
   cd C:\Users\Admin\Desktop\AI
   .\setup_scheduler.ps1
   ```

5. **성공 확인**
   - 콘솔에 "✅ 작업이 성공적으로 등록되었습니다!" 메시지 표시
   - 작업 스케줄러에서 "AI-Trends-Daily-Dashboard" 확인

### 문제 해결

**"PowerShell 스크립트 실행이 거부되었습니다" 오류**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"python 명령을 찾을 수 없습니다"**
- Python이 PATH에 추가되지 않음
- Python 재설치 시 "Add Python to PATH" 체크
```
```

---

## Summary

| Issue | Type | Priority | 상태 |
|-------|------|----------|------|
| XSS 취약점 | Bug | 🔴 High | TODO |
| 에러 처리 | Improvement | 🟡 Medium | TODO |
| 로깅 부재 | Improvement | 🟡 Medium | TODO |
| Hacker News 날짜 | Bug | 🟡 Medium | TODO |
| 타임아웃 설정 | Bug | 🟡 Medium | TODO |
| 중복 제거 | Improvement | 🟢 Low | TODO |
| robots.txt | Improvement | 🟡 Medium | TODO |
| 빈 결과 처리 | Improvement | 🟡 Medium | TODO |
| README 가이드 | Documentation | 🟡 Medium | TODO |

---

## 등록 방법

1. GitHub 저장소 방문: https://github.com/ehdwns3755-byte/AI-
2. "Issues" 탭 클릭
3. "New issue" 버튼 클릭
4. 위 내용을 **Title**과 **Description**에 복사-붙여넣기
5. "Submit new issue" 클릭
