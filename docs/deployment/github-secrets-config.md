# GitHub Secrets 配置说明

本文档说明部署工作流中使用的 GitHub Secrets 配置。

## Secrets 列表

### 1. `TXYUN_HOST`

**用途**：SSH 连接的目标服务器地址

**填写内容**：

- 服务器的公网 IP 地址（如：`1.12.181.3`）
- 或服务器的域名（如：`dev.layneliang.com`）

**示例**：

```
1.12.181.3
```

**注意事项**：

- 必须是可公网访问的 IP 或域名
- 确保该地址可以从 GitHub Actions Runner 访问

---

### 2. `TXYUN_USER`

**用途**：SSH 登录的用户名

**填写内容**：

- 服务器上具有 SSH 访问权限的用户名
- 通常是 `ubuntu`、`root` 或自定义用户名

**示例**：

```
ubuntu
```

**注意事项**：

- 确保该用户有执行部署脚本的权限
- 确保该用户的 `~/.ssh/authorized_keys` 中包含对应的公钥

---

### 3. `TXYUN_SSH_KEY`

**用途**：SSH 私钥，用于身份验证

**填写内容**：

- 完整的 SSH 私钥内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）
- 或 `-----BEGIN RSA PRIVATE KEY-----` 格式的私钥

**示例**：

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...
（完整的私钥内容）
...
-----END OPENSSH PRIVATE KEY-----
```

**注意事项**：

- **必须包含完整的私钥头尾标记**
- 私钥对应的公钥必须已经添加到服务器的 `~/.ssh/authorized_keys` 中
- 确保私钥有正确的权限（本地文件应该是 `600`）
- 不要在私钥前后添加额外的空格或换行

**如何生成 SSH 密钥对**：

```bash
# 生成新的 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# 查看公钥（需要添加到服务器的 authorized_keys）
cat ~/.ssh/github_actions_deploy.pub

# 查看私钥（需要添加到 GitHub Secrets）
cat ~/.ssh/github_actions_deploy
```

**如何将公钥添加到服务器**：

```bash
# 在服务器上执行
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

### 4. `TXYUN_REGISTRY_USERNAME`

**用途**：阿里云容器镜像服务的用户名

**填写内容**：

- 阿里云容器镜像服务的登录用户名
- 通常是阿里云账号的用户名或邮箱

**示例**：

```
your-aliyun-username
```

**注意事项**：

- 确保该账号有拉取镜像的权限
- 镜像仓库地址：`crpi-noqbdktswju6cuew.cn-shenzhen.personal.cr.aliyuncs.com`

---

### 5. `TXYUN_REGISTRY_PASSWORD`

**用途**：阿里云容器镜像服务的登录密码

**填写内容**：

- 阿里云容器镜像服务的登录密码
- 或访问令牌（Access Token）

**示例**：

```
your-aliyun-password
```

**注意事项**：

- 建议使用访问令牌而不是账号密码（更安全）
- 确保密码/令牌有拉取镜像的权限

**如何获取访问令牌**：

1. 登录阿里云控制台
2. 进入容器镜像服务
3. 访问凭证 → 设置固定密码或创建访问令牌

---

## 配置检查清单

在配置完成后，请确认：

- [ ] `TXYUN_HOST` 填写了正确的服务器 IP 或域名
- [ ] `TXYUN_USER` 填写了正确的 SSH 用户名
- [ ] `TXYUN_SSH_KEY` 填写了完整的私钥（包含头尾标记）
- [ ] 私钥对应的公钥已添加到服务器的 `~/.ssh/authorized_keys`
- [ ] 可以在本地使用该私钥成功 SSH 连接到服务器
- [ ] `TXYUN_REGISTRY_USERNAME` 填写了正确的镜像仓库用户名
- [ ] `TXYUN_REGISTRY_PASSWORD` 填写了正确的密码或访问令牌
- [ ] 可以在服务器上使用该凭据成功登录镜像仓库

---

## 测试连接

### 测试 SSH 连接

```bash
# 使用私钥测试 SSH 连接
ssh -i ~/.ssh/github_actions_deploy ubuntu@1.12.181.3 "echo 'SSH连接成功'"
```

### 测试镜像仓库登录

```bash
# 在服务器上测试镜像仓库登录
echo "your-password" | docker login crpi-noqbdktswju6cuew.cn-shenzhen.personal.cr.aliyuncs.com --username "your-username" --password-stdin
```

---

## 常见问题

### Q: SSH 连接超时

**A**: 检查：

1. `TXYUN_HOST` 是否正确
2. 服务器防火墙是否允许 22 端口
3. 服务器是否可公网访问
4. GitHub Actions Runner IP 是否被阻止

### Q: SSH 认证失败

**A**: 检查：

1. `TXYUN_SSH_KEY` 是否完整（包含头尾标记）
2. 私钥对应的公钥是否已添加到服务器的 `authorized_keys`
3. 服务器上的 `authorized_keys` 文件权限是否正确（`600`）

### Q: 镜像拉取失败

**A**: 检查：

1. `TXYUN_REGISTRY_USERNAME` 和 `TXYUN_REGISTRY_PASSWORD` 是否正确
2. 账号是否有拉取镜像的权限
3. 镜像仓库地址是否正确

---

## 安全建议

1. **使用访问令牌**：建议使用访问令牌而不是账号密码
2. **定期轮换密钥**：定期更换 SSH 密钥和访问令牌
3. **最小权限原则**：只授予必要的权限
4. **监控访问日志**：定期检查服务器的 SSH 访问日志
