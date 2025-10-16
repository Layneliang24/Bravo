# 域名配置快速开始

最简洁的域名配置步骤指南，5步完成！

---

## 📋 您需要做的事情

### 1️⃣ 配置DNS（阿里云控制台）

访问：https://dns.console.aliyun.com/

添加两条A记录：

```
@ → 8.129.16.190
dev → 8.129.16.190
```

**验证**：等待5分钟后执行

```bash
nslookup layneliang.com
nslookup dev.layneliang.com
# 都应该返回 8.129.16.190
```

---

### 2️⃣ 修改邮箱配置（本地电脑）

编辑 `scripts/setup-ssl.sh` 文件，将第24行：

```bash
EMAIL="your-email@example.com"
```

改为您的真实邮箱：

```bash
EMAIL="layneliang@example.com"
```

---

### 3️⃣ 申请SSL证书（服务器操作）

```bash
# SSH登录服务器
ssh root@8.129.16.190

# 进入项目目录
cd /root/bravo  # 或您的实际路径

# 拉取最新代码（包含SSL脚本）
git pull origin main

# 停止容器（重要！）
docker stop bravo-prod-frontend bravo-dev-frontend

# 申请生产环境证书
sudo scripts/setup-ssl.sh prod

# 申请开发环境证书
sudo scripts/setup-ssl.sh dev
```

**预期输出**：

```
✓ SSL证书申请成功！
```

---

### 4️⃣ 触发自动部署（本地电脑）

```bash
# 回到本地项目目录
git commit --allow-empty -m "chore: trigger deployment for domain"
git push origin dev    # 部署开发环境
git push origin main   # 部署生产环境
```

---

### 5️⃣ 验证访问

**生产环境**：
🌐 https://layneliang.com

**开发环境**：
🧪 https://dev.layneliang.com:8443

---

## ✅ 完成检查

- [ ] DNS解析成功
- [ ] SSL证书申请成功
- [ ] GitHub Actions部署成功
- [ ] 域名可以HTTPS访问

---

## ❌ 遇到问题？

查看详细指南：[DOMAIN_SETUP_GUIDE.md](./DOMAIN_SETUP_GUIDE.md)

**常见问题**：

- DNS未生效？ → 等待10分钟
- SSL申请失败？ → 检查容器是否已停止
- 部署后无法访问？ → 检查GitHub Actions日志
- 防火墙问题？ → 在阿里云安全组开放 80, 443, 8080, 8443 端口

---

**快速开始版本**: 1.0
**详细文档**: [DOMAIN_SETUP_GUIDE.md](./DOMAIN_SETUP_GUIDE.md)
