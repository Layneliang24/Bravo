#!/bin/bash
# 删除未验证用户的便捷脚本

EMAIL="${1:-}"

if [ -z "$EMAIL" ]; then
    echo "用法: ./scripts/delete-unverified-user.sh <email>"
    echo "示例: ./scripts/delete-unverified-user.sh 2227208441@qq.com"
    exit 1
fi

echo "正在删除未验证用户: $EMAIL"

docker-compose exec backend python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.filter(email='$EMAIL', is_email_verified=False).first()
if user:
    username = user.username
    user.delete()
    print(f"✅ 已删除未验证用户: {username} ($EMAIL)")
else:
    print(f"❌ 未找到未验证用户: $EMAIL")
    print("提示: 用户可能不存在或邮箱已验证")
EOF
