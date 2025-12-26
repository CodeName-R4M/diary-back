web: uvicorn main:app --host 0.0.0.0 --port $PORT
release: python -m prisma generate && python -m prisma db push --skip-generate

