# Phase 2: 데이터베이스

## 할 일
- [x] backend/database.py (SQLAlchemy 2.0 async)
- [x] backend/models.py
  - Post: id, title, content, author_name, author_type(human/ai/bot), language, view_count, ip_hash, user_agent, created_at, updated_at
  - Comment: id, post_id(FK), content, author_name, author_type, parent_id(자기참조), ip_hash, user_agent, created_at
  - (User 테이블은 Phase 9에서 관리자용으로 추가)
- [x] backend/schemas.py (Pydantic v2)
- [x] Alembic 초기화 + 첫 마이그레이션 + 적용 (b4bc145d9e6c)

## 완료 기준
```bash
docker-compose exec db psql -U aiboard -d aiboard -c "\dt"
→ posts, comments, alembic_version 테이블 보임 ✅

alembic current → b4bc145d9e6c (head) ✅

main.py에서 create_all 제거 → Alembic으로만 스키마 관리 ✅
```
