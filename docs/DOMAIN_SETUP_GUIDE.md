# 域名配置指南

本指南将帮助您配置域名访问Bravo项目：

- **生产环境**: `layneliang.com`
- **测试环境**: `dev.layneliang.com`

---

## 📋 配置流程总览

### 🎯 您需要做的事情（用户操作）

1. 在阿里云配置DNS解析
2. 登录服务器运行SSL证书申请脚本
3. 触发自动部署

### 🤖 自动完成的事情（系统操作）

1. 自动检测SSL证书
2. 自动切换Nginx配置
3. 自动配置HTTPS
4. 自动续期证书

---

## 🚀 详细操作步骤

### 第一步：配置DNS解析（在阿里云操作）

#### 1.1 登录阿里云控制台

- 访问：https://dns.console.aliyun.com/
- 找到您的域名：`layneliang.com`

#### 1.2 添加DNS记录

添加以下两条A记录：

| 记录类型 | 主机记录 | 记录值       | TTL    |
| -------- | -------- | ------------ | ------ |
| A        | @        | 8.129.16.190 | 10分钟 |
| A        | dev      | 8.129.16.190 | 10分钟 |

**说明**：

- `@` 代表主域名 → `layneliang.com`
- `dev` 代表子域名 → `dev.layneliang.com`
- 两个域名都指向同一个服务器IP

#### 1.3 （可选）添加www跳转

如果希望 `www.layneliang.com` 也能访问，添加：

| 记录类型 | 主机记录 | 记录值         | TTL    |
| -------- | -------- | -------------- | ------ |
| CNAME    | www      | layneliang.com | 10分钟 |

#### 1.4 验证DNS解析

等待5-10分钟后，在本地电脑测试：

```bash
# Windows
nslookup layneliang.com
nslookup dev.layneliang.com

# Linux/Mac
dig layneliang.com
dig dev.layneliang.com
```

**预期结果**：都应该返回 `8.129.16.190`

---

### 第二步：申请SSL证书（在服务器操作）

#### 2.1 登录服务器

```bash
ssh root@8.129.16.190
# 或使用您的SSH密钥
ssh -i ~/.ssh/your-key.pem root@8.129.16.190
```

#### 2.2 进入项目目录

```bash
cd /root/bravo  # 或您的项目实际路径
```

#### 2.3 修改邮箱配置

在申请SSL证书前，需要设置您的真实邮箱（用于接收证书到期提醒）：

```bash
# 编辑SSL申请脚本
vim scripts/setup-ssl.sh

# 找到这一行（约第24行）：
# EMAIL="your-email@example.com"

# 修改为您的真实邮箱，例如：
# EMAIL="layneliang@example.com"
```

#### 2.4 停止前端容器（重要！）

SSL证书申请需要使用80/8080端口，必须先停止容器：

```bash
# 停止生产环境前端（如果在运行）
docker stop bravo-prod-frontend

# 停止开发环境前端（如果在运行）
docker stop bravo-dev-frontend
```

#### 2.5 申请生产环境SSL证书

```bash
# 给脚本添加执行权限
chmod +x scripts/setup-ssl.sh

# 申请生产环境证书（layneliang.com）
sudo scripts/setup-ssl.sh prod
```

**预期输出**：

```
======================================
   SSL证书配置脚本
======================================
配置生产环境SSL证书: layneliang.com
开始申请SSL证书...
...
✓ SSL证书申请成功！
证书位置: /etc/letsencrypt/live/layneliang.com/
```

#### 2.6 申请测试环境SSL证书

```bash
# 申请开发环境证书（dev.layneliang.com）
sudo scripts/setup-ssl.sh dev
```

**预期输出**：

```
✓ SSL证书申请成功！
证书位置: /etc/letsencrypt/live/dev.layneliang.com/
```

#### 2.7 验证证书文件

```bash
# 检查生产环境证书
ls -la /etc/letsencrypt/live/layneliang.com/

# 检查开发环境证书
ls -la /etc/letsencrypt/live/dev.layneliang.com/

# 应该看到以下文件：
# - fullchain.pem  (完整证书链)
# - privkey.pem    (私钥)
# - chain.pem      (中间证书)
# - cert.pem       (域名证书)
```

---

### 第三步：触发自动部署

SSL证书配置完成后，只需推送代码就会自动部署并启用域名配置。

#### 方案A：推送现有修改到dev分支

```bash
# 在本地电脑，项目目录下
git checkout dev
git pull origin dev

# 触发dev环境部署
git commit --allow-empty -m "chore: trigger deployment for domain setup"
git push origin dev
```

#### 方案B：推送到main分支

```bash
# 触发生产环境部署
git checkout main
git pull origin main
git commit --allow-empty -m "chore: trigger deployment for domain setup"
git push origin main
```

---

### 第四步：验证部署结果

#### 4.1 查看GitHub Actions

- 访问：https://github.com/Layneliang24/Bravo/actions
- 等待部署工作流完成（约2-5分钟）

#### 4.2 查看部署日志

在日志中应该看到：

```
检测到SSL证书，使用域名配置...
使用域名Nginx配置
```

#### 4.3 访问测试

**测试环境**：

- HTTP: http://dev.layneliang.com:8080 → 自动跳转HTTPS
- HTTPS: https://dev.layneliang.com:8443 ✅
- API: https://dev.layneliang.com:8443/api/
- 管理后台: https://dev.layneliang.com:8443/admin/

**生产环境**：

- HTTP: http://layneliang.com → 自动跳转HTTPS
- HTTPS: https://layneliang.com ✅
- API: https://layneliang.com/api/
- 管理后台: https://layneliang.com/admin/

#### 4.4 检查SSL证书

在浏览器中：

1. 访问 https://layneliang.com
2. 点击地址栏的锁图标
3. 查看证书信息

**预期**：

- ✅ 连接安全
- ✅ 证书由Let's Encrypt颁发
- ✅ 有效期90天

---

## 🔄 自动续期

SSL证书会**自动续期**，无需手动操作：

### 续期机制

- **检查频率**：每天凌晨3点
- **续期时机**：证书到期前30天
- **自动重启**：续期后自动重启frontend容器

### 查看续期配置

```bash
# 在服务器上查看cron任务
crontab -l | grep certbot

# 应该看到：
# 0 3 * * * certbot renew --quiet --post-hook 'docker restart $(docker ps -q -f name=frontend)'
```

### 手动测试续期

```bash
# 测试续期（不会真正续期）
sudo certbot renew --dry-run

# 强制续期（如果需要）
sudo certbot renew --force-renewal
```

---

## 🛠️ 故障排查

### 问题1：DNS解析不生效

**症状**：

```bash
nslookup layneliang.com
# 返回其他IP或无结果
```

**解决**：

1. 检查阿里云DNS记录是否正确配置
2. 等待DNS传播（最多24小时，通常5-10分钟）
3. 尝试使用其他DNS服务器测试：`nslookup layneliang.com 8.8.8.8`

---

### 问题2：SSL证书申请失败

**症状**：

```
✗ SSL证书申请失败
```

**可能原因和解决方案**：

#### 原因1：DNS未生效

```bash
# 检查DNS解析
dig layneliang.com +short
# 必须返回: 8.129.16.190
```

#### 原因2：端口被占用

```bash
# 检查80端口（生产）或8080端口（开发）
sudo lsof -i :80
sudo lsof -i :8080

# 如果有占用，停止相关容器
docker stop bravo-prod-frontend
docker stop bravo-dev-frontend
```

#### 原因3：防火墙阻止

```bash
# 检查防火墙规则
sudo firewall-cmd --list-all  # CentOS/RHEL
sudo ufw status               # Ubuntu/Debian

# 开放端口（如果需要）
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --add-port=443/tcp --permanent
sudo firewall-cmd --reload
```

#### 原因4：阿里云安全组未开放

1. 登录阿里云控制台
2. 找到ECS实例
3. 配置安全组规则
4. 添加入站规则：
   - 端口：80, 443, 8080, 8443
   - 来源：0.0.0.0/0

#### 查看详细错误日志

```bash
sudo cat /var/log/letsencrypt/letsencrypt.log
```

---

### 问题3：部署后仍然使用IP访问

**症状**：

- 部署成功，但访问域名无法访问
- 日志显示"未检测到SSL证书"

**解决**：

#### 检查证书是否存在

```bash
ls -la /etc/letsencrypt/live/layneliang.com/
ls -la /etc/letsencrypt/live/dev.layneliang.com/
```

#### 手动重新部署

```bash
cd /root/bravo
git pull origin main  # 或 origin dev

# 手动重启服务
docker-compose -f docker-compose.prod.yml restart
```

---

### 问题4：HTTPS无法访问

**症状**：

- HTTP可以访问
- HTTPS显示"无法访问此网站"

**检查1：容器端口映射**

```bash
docker ps | grep frontend

# 应该看到：
# 0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp  (生产)
# 0.0.0.0:8080->80/tcp, 0.0.0.0:8443->443/tcp  (开发)
```

**检查2：证书挂载**

```bash
# 进入容器检查
docker exec -it bravo-prod-frontend ls -la /etc/letsencrypt/live/

# 应该能看到证书文件
```

**检查3：Nginx配置**

```bash
# 检查Nginx配置语法
docker exec -it bravo-prod-frontend nginx -t

# 查看Nginx错误日志
docker exec -it bravo-prod-frontend cat /var/log/nginx/error.log
```

---

### 问题5：证书过期

**症状**：

- 浏览器提示"您的连接不是私密连接"
- 证书已过期

**解决**：

```bash
# 检查证书有效期
sudo certbot certificates

# 手动续期
sudo certbot renew --force-renewal

# 重启容器
docker restart bravo-prod-frontend
docker restart bravo-dev-frontend
```

---

## 📞 需要帮助？

如果遇到其他问题：

1. **查看部署日志**：

   ```bash
   # GitHub Actions日志
   https://github.com/Layneliang24/Bravo/actions

   # 容器日志
   docker logs bravo-prod-frontend
   docker logs bravo-dev-frontend
   ```

2. **查看服务状态**：

   ```bash
   docker ps -a
   docker-compose -f docker-compose.prod.yml ps
   ```

3. **健康检查**：

   ```bash
   # 生产环境
   curl -I https://layneliang.com/health

   # 开发环境
   curl -I https://dev.layneliang.com:8443/health
   ```

---

## 📝 操作检查清单

完成配置后，请确认以下项目：

### DNS配置

- [ ] layneliang.com → 8.129.16.190
- [ ] dev.layneliang.com → 8.129.16.190
- [ ] DNS解析已生效（nslookup验证）

### SSL证书

- [ ] 生产环境证书已申请：/etc/letsencrypt/live/layneliang.com/
- [ ] 开发环境证书已申请：/etc/letsencrypt/live/dev.layneliang.com/
- [ ] 自动续期cron任务已配置

### 部署验证

- [ ] 代码已推送并触发自动部署
- [ ] GitHub Actions工作流已成功
- [ ] 部署日志显示"使用域名配置"

### 访问测试

- [ ] https://layneliang.com 可以访问 ✅
- [ ] https://dev.layneliang.com:8443 可以访问 ✅
- [ ] HTTP自动跳转HTTPS ✅
- [ ] API接口正常 ✅
- [ ] SSL证书有效 ✅

---

## 🎉 完成！

恭喜您完成域名配置！现在您的项目可以通过以下方式访问：

### 🌐 生产环境

- **主站**: https://layneliang.com
- **API**: https://layneliang.com/api/
- **管理后台**: https://layneliang.com/admin/

### 🧪 测试环境

- **主站**: https://dev.layneliang.com:8443
- **API**: https://dev.layneliang.com:8443/api/
- **管理后台**: https://dev.layneliang.com:8443/admin/

### 🔐 安全特性

- ✅ HTTPS加密传输
- ✅ HTTP自动跳转HTTPS
- ✅ SSL证书自动续期
- ✅ 安全头配置完善

---

**文档版本**: 1.0
**最后更新**: 2025-10-16
**维护者**: Claude Sonnet 4
