# 일반 규칙

## Git
```
🎉 init: 프로젝트 초기 구조
✨ feat: 새 기능
🐛 fix: 버그 수정
🔧 config: 설정
📝 docs: 문서
🔒 security: 보안
♻️ refactor: 리팩토링
🌐 discovery: AI 발견 관련
```
- .gitignore: .env, __pycache__/, node_modules/, .next/

## 테스트
- 각 Phase 끝에 동작 확인
- Swagger: http://localhost:8000/docs
- 프론트: http://localhost:3000

## 의존성
- backend: requirements.txt 버전 고정 (==)
- frontend: package.json
- 새 패키지 → 해당 파일 업데이트

## 코드
- 파일 300줄 이상 금지
- 주석은 "왜"를 설명
- TODO: `# TODO: [설명] — Phase X`
