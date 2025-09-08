# 🔒 黄金测试 - 用户核心功能测试
# 此文件受保护，仅允许人工修改
# 包含用户认证、授权和核心业务逻辑测试

import pytest

# 假设的应用导入（需要根据实际项目结构调整）
# from app.main import app
# from app.models.user import User
# from app.core.security import create_access_token
# from app.core.config import settings


class TestUserAuthentication:
    """用户认证核心测试 - 黄金测试套件"""

    @pytest.fixture
    def client(self):
        """测试客户端"""
        # return TestClient(app)
        pass

    @pytest.fixture
    def test_user_data(self):
        """测试用户数据"""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
        }

    def test_user_registration_success(self, client, test_user_data):
        """测试用户注册成功 - 核心业务逻辑"""
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201  # nosec
        data = response.json()
        assert "id" in data  # nosec
        assert data["email"] == test_user_data["email"]  # nosec
        assert data["username"] == test_user_data["username"]  # nosec
        assert "password" not in data  # 密码不应该返回  # nosec

    def test_user_registration_duplicate_email(self, client, test_user_data):
        """测试重复邮箱注册失败 - 数据完整性"""
        # 第一次注册
        client.post("/api/v1/auth/register", json=test_user_data)

        # 第二次注册相同邮箱
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 400  # nosec
        assert "already registered" in response.json()["detail"].lower()  # nosec

    def test_user_login_success(self, client, test_user_data):
        """测试用户登录成功 - 认证核心"""
        # 先注册用户
        client.post("/api/v1/auth/register", json=test_user_data)

        # 登录
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200  # nosec
        data = response.json()
        assert "access_token" in data  # nosec
        assert "token_type" in data  # nosec
        assert data["token_type"] == "bearer"  # nosec

    def test_user_login_invalid_credentials(self, client, test_user_data):
        """测试无效凭据登录失败 - 安全验证"""
        # 先注册用户
        client.post("/api/v1/auth/register", json=test_user_data)

        # 使用错误密码登录
        login_data = {"username": test_user_data["email"], "password": "WrongPassword"}
        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401  # nosec
        assert "incorrect" in response.json()["detail"].lower()  # nosec

    def test_protected_route_without_token(self, client):
        """测试未授权访问受保护路由 - 授权验证"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401  # nosec
        assert "not authenticated" in response.json()["detail"].lower()  # nosec

    def test_protected_route_with_valid_token(self, client, test_user_data):
        """测试有效令牌访问受保护路由 - 授权核心"""
        # 注册并登录获取令牌
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # 使用令牌访问受保护路由
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200  # nosec
        data = response.json()
        assert data["email"] == test_user_data["email"]  # nosec


class TestUserProfile:
    """用户资料管理核心测试"""

    @pytest.fixture
    def authenticated_client(self, client, test_user_data):
        """已认证的客户端"""
        # 注册并登录
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]

        # 设置认证头
        client.headers.update({"Authorization": f"Bearer {token}"})
        return client

    def test_update_user_profile(self, authenticated_client):
        """测试更新用户资料 - 核心功能"""
        update_data = {"full_name": "Updated Name", "bio": "Updated bio"}

        response = authenticated_client.put("/api/v1/users/me", json=update_data)

        assert response.status_code == 200  # nosec
        data = response.json()
        assert data["full_name"] == update_data["full_name"]  # nosec
        assert data["bio"] == update_data["bio"]  # nosec

    def test_change_password(self, authenticated_client):
        """测试修改密码 - 安全核心"""
        password_data = {
            "current_password": "SecurePassword123!",
            "new_password": "NewSecurePassword456!",
        }

        response = authenticated_client.post(
            "/api/v1/users/change-password", json=password_data
        )

        assert response.status_code == 200  # nosec
        assert "successfully" in response.json()["message"].lower()  # nosec

    def test_delete_user_account(self, authenticated_client):
        """测试删除用户账户 - 数据完整性"""
        response = authenticated_client.delete("/api/v1/users/me")

        assert response.status_code == 200  # nosec
        assert "deleted" in response.json()["message"].lower()  # nosec

        # 验证账户已删除
        profile_response = authenticated_client.get("/api/v1/users/me")
        assert profile_response.status_code == 401  # nosec


class TestUserPermissions:
    """用户权限管理核心测试"""

    def test_admin_access_control(self, client):
        """测试管理员访问控制 - 权限核心"""
        # 创建普通用户
        user_data = {
            "username": "normaluser",
            "email": "normal@example.com",
            "password": "Password123!",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 登录普通用户
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]

        # 尝试访问管理员路由
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/admin/users", headers=headers)

        assert response.status_code == 403  # nosec
        assert "permission" in response.json()["detail"].lower()  # nosec

    def test_user_data_isolation(self, client):
        """测试用户数据隔离 - 安全核心"""
        # 创建两个用户
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "Password123!",
        }
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "Password123!",
        }

        client.post("/api/v1/auth/register", json=user1_data)
        client.post("/api/v1/auth/register", json=user2_data)

        # 用户1登录
        login1_response = client.post(
            "/api/v1/auth/login",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        token1 = login1_response.json()["access_token"]

        # 用户1尝试访问用户2的数据（假设有用户ID路由）
        headers = {"Authorization": f"Bearer {token1}"}
        response = client.get("/api/v1/users/2", headers=headers)  # 假设用户2的ID是2

        # 应该被拒绝访问
        assert response.status_code in [403, 404]  # nosec


# 测试运行配置
if __name__ == "__main__":
    pytest.main(["-v", __file__])
