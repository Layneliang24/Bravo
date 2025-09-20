case "lint-frontend" in
"lint-frontend")
  echo "cd frontend && npm run lint"
  ;;
"lint-backend")
  echo "cd backend && source .venv/bin/activate && python -m flake8"
  ;;
"type-check")
  echo "cd frontend && npm run type-check"
  ;;
"security-scan")
  echo "npm audit --audit-level=high --production"
  ;;
esac
