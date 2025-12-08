// REQ-ID: REQ-2025-003-user-login
import { AxiosInstance } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { setApiClient, useAuthStore } from '../auth'

describe('Auth Store', () => {
  beforeEach(() => {
    // 清除localStorage
    localStorage.clear()
    // 创建新的Pinia实例
    setActivePinia(createPinia())
    // 创建默认的mock axios实例（每个测试可以覆盖）
    const mockAxios = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
      request: vi.fn(),
      defaults: {} as any,
      interceptors: {} as any,
      create: vi.fn(),
    } as unknown as AxiosInstance
    setApiClient(mockAxios)
    // 注意：不在这里清除mock，让每个测试自己设置mock
  })

  describe('状态初始化', () => {
    it('应该正确初始化状态', () => {
      const store = useAuthStore()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.captcha).toBeNull()
    })

    it('应该从localStorage恢复token', () => {
      // 先设置localStorage
      localStorage.setItem('auth_token', 'test-token')
      localStorage.setItem('auth_refresh_token', 'test-refresh-token')

      // 然后创建store（会调用restoreTokens）
      const store = useAuthStore()

      // 由于restoreTokens在store定义时就被调用，需要手动触发一次
      // 或者等待nextTick
      expect(store.token).toBe('test-token')
      expect(store.refreshToken).toBe('test-refresh-token')
    })
  })

  describe('登录功能', () => {
    it('应该成功登录并更新状态', async () => {
      const mockResponse = {
        data: {
          user: {
            id: '1',
            email: 'test@example.com',
            is_email_verified: false,
          },
          token: 'access-token',
          refresh_token: 'refresh-token',
        },
      }

      // 先设置mock client
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockResolvedValueOnce(mockResponse),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      // 然后创建store
      const store = useAuthStore()

      await store.login({
        email: 'test@example.com',
        password: 'password123',
        captcha_id: 'captcha-id',
        captcha_answer: 'ABCD',
      })

      expect(store.user).toEqual(mockResponse.data.user)
      expect(store.token).toBe('access-token')
      expect(store.refreshToken).toBe('refresh-token')
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.getItem('auth_token')).toBe('access-token')
      expect(localStorage.getItem('auth_refresh_token')).toBe('refresh-token')
    })

    it('应该处理登录失败', async () => {
      const mockError = {
        response: {
          data: {
            error: '账号或密码错误',
            code: 'INVALID_CREDENTIALS',
          },
          status: 400,
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockRejectedValueOnce(mockError),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await expect(
        store.login({
          email: 'test@example.com',
          password: 'wrong-password',
          captcha_id: 'captcha-id',
          captcha_answer: 'ABCD',
        })
      ).rejects.toThrow()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('注册功能', () => {
    it('应该成功注册并更新状态', async () => {
      const mockResponse = {
        data: {
          user: {
            id: '1',
            email: 'newuser@example.com',
            is_email_verified: false,
          },
          token: 'access-token',
          refresh_token: 'refresh-token',
          message: '注册成功，请查收验证邮件',
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockResolvedValueOnce(mockResponse),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await store.register({
        email: 'newuser@example.com',
        password: 'SecurePass123',
        password_confirm: 'SecurePass123',
        captcha_id: 'captcha-id',
        captcha_answer: 'ABCD',
      })

      expect(store.user).toEqual(mockResponse.data.user)
      expect(store.token).toBe('access-token')
      expect(store.refreshToken).toBe('refresh-token')
      expect(store.isAuthenticated).toBe(true)
    })

    it('应该处理注册失败（邮箱已存在）', async () => {
      const mockError = {
        response: {
          data: {
            error: '该邮箱已被注册',
            code: 'EMAIL_EXISTS',
          },
          status: 400,
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockRejectedValueOnce(mockError),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await expect(
        store.register({
          email: 'existing@example.com',
          password: 'SecurePass123',
          password_confirm: 'SecurePass123',
          captcha_id: 'captcha-id',
          captcha_answer: 'ABCD',
        })
      ).rejects.toThrow()

      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('登出功能', () => {
    it('应该清除所有状态和localStorage', async () => {
      const store = useAuthStore()
      // 先设置一些状态
      store.user = {
        id: '1',
        email: 'test@example.com',
        is_email_verified: false,
      }
      store.token = 'access-token'
      store.refreshToken = 'refresh-token'
      localStorage.setItem('auth_token', 'access-token')
      localStorage.setItem('auth_refresh_token', 'refresh-token')

      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockResolvedValueOnce({ data: { message: '登出成功' } }),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('auth_token')).toBeFalsy()
      expect(localStorage.getItem('auth_refresh_token')).toBeFalsy()
    })

    it('应该在未登录时也能调用登出', async () => {
      const store = useAuthStore()
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockResolvedValueOnce({ data: { message: '登出成功' } }),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await store.logout()

      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('Token刷新功能', () => {
    it('应该成功刷新token', async () => {
      const mockResponse = {
        data: {
          access: 'new-access-token',
        },
      }

      // 先设置mock client
      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockResolvedValueOnce(mockResponse),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      // 然后创建store并设置refreshToken
      const store = useAuthStore()
      store.refreshToken = 'old-refresh-token'
      localStorage.setItem('auth_refresh_token', 'old-refresh-token')

      await store.refreshTokenAction()

      expect(store.token).toBe('new-access-token')
      expect(store.refreshToken).toBe('old-refresh-token') // refresh token保持不变
      expect(localStorage.getItem('auth_token')).toBe('new-access-token')
      expect(localStorage.getItem('auth_refresh_token')).toBe(
        'old-refresh-token'
      )
    })

    it('应该处理token刷新失败', async () => {
      const mockError = {
        response: {
          data: {
            error: '刷新令牌无效',
            code: 'INVALID_REFRESH_TOKEN',
          },
          status: 401,
        },
      }

      const store = useAuthStore()
      store.refreshToken = 'invalid-refresh-token'

      const mockClient = {
        get: vi.fn(),
        post: vi.fn().mockRejectedValueOnce(mockError),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await expect(store.refreshTokenAction()).rejects.toThrow()

      // 刷新失败后应该清除状态
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('验证码功能', () => {
    it('应该成功获取验证码', async () => {
      const mockResponse = {
        data: {
          captcha_id: 'captcha-id-123',
          captcha_image: 'data:image/png;base64,iVBORw0KGgo...',
          expires_in: 300,
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn().mockResolvedValueOnce(mockResponse),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await store.fetchCaptcha()

      expect(store.captcha).toEqual({
        id: 'captcha-id-123',
        image: 'data:image/png;base64,iVBORw0KGgo...',
        expiresIn: 300,
      })
    })

    it('应该成功刷新验证码', async () => {
      const mockResponse = {
        data: {
          captcha_id: 'new-captcha-id',
          captcha_image: 'data:image/png;base64,newImage...',
          expires_in: 300,
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn().mockResolvedValueOnce(mockResponse),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await store.refreshCaptcha()

      expect(store.captcha).toEqual({
        id: 'new-captcha-id',
        image: 'data:image/png;base64,newImage...',
        expiresIn: 300,
      })
    })

    it('应该处理获取验证码失败', async () => {
      const mockError = {
        response: {
          data: {
            error: '获取验证码失败',
          },
          status: 500,
        },
      }

      const store = useAuthStore()
      const mockClient = {
        get: vi.fn().mockRejectedValueOnce(mockError),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)

      await expect(store.fetchCaptcha()).rejects.toThrow()

      expect(store.captcha).toBeNull()
    })
  })

  describe('计算属性', () => {
    it('isAuthenticated应该根据token和user判断', () => {
      const store = useAuthStore()

      // 初始状态
      expect(store.isAuthenticated).toBe(false)

      // 只有token
      store.token = 'token'
      expect(store.isAuthenticated).toBe(false)

      // 有token和user
      store.user = {
        id: '1',
        email: 'test@example.com',
        is_email_verified: false,
      }
      expect(store.isAuthenticated).toBe(true)

      // 清除user
      store.user = null
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('previewLogin', () => {
    let mockClient: AxiosInstance

    beforeEach(() => {
      setActivePinia(createPinia())
      mockClient = {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)
    })

    it('应该成功调用preview API并更新preview状态', async () => {
      const mockResponse = {
        data: {
          valid: true,
          user: {
            display_name: 'Test User',
            avatar_url: 'https://example.com/avatar.jpg',
            default_avatar: false,
          },
        },
      }
      mockClient.post.mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.previewLogin({
        email: 'test@example.com',
        password: 'password123',
        captcha_id: 'test-captcha-id',
        captcha_answer: '1234',
      })

      expect(mockClient.post).toHaveBeenCalledWith('/api/auth/preview/', {
        email: 'test@example.com',
        password: 'password123',
        captcha_id: 'test-captcha-id',
        captcha_answer: '1234',
      })
      expect(store.preview).toEqual({
        valid: true,
        user: {
          display_name: 'Test User',
          avatar_url: 'https://example.com/avatar.jpg',
          default_avatar: false,
        },
      })
    })

    it('应该处理无效的账号密码', async () => {
      const mockResponse = {
        data: {
          valid: false,
          user: null,
        },
      }
      mockClient.post.mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.previewLogin({
        email: 'test@example.com',
        password: 'wrongpassword',
        captcha_id: 'test-captcha-id',
        captcha_answer: '1234',
      })

      expect(store.preview).toEqual({
        valid: false,
        user: null,
      })
    })

    it('应该处理无头像的用户', async () => {
      const mockResponse = {
        data: {
          valid: true,
          user: {
            display_name: 'Test User',
            avatar_url: null,
            avatar_letter: 'T',
          },
        },
      }
      mockClient.post.mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.previewLogin({
        email: 'test@example.com',
        password: 'password123',
        captcha_id: 'test-captcha-id',
        captcha_answer: '1234',
      })

      expect(store.preview).toEqual({
        valid: true,
        user: {
          display_name: 'Test User',
          avatar_url: null,
          avatar_letter: 'T',
        },
      })
    })

    it('应该处理API错误', async () => {
      const error = new Error('网络错误，请稍后重试')
      mockClient.post.mockRejectedValue(error)

      const store = useAuthStore()
      await expect(
        store.previewLogin({
          email: 'test@example.com',
          password: 'password123',
          captcha_id: 'test-captcha-id',
          captcha_answer: '1234',
        })
      ).rejects.toThrow('网络错误，请稍后重试')
    })
  })

  describe('sendPasswordReset', () => {
    let mockClient: AxiosInstance

    beforeEach(() => {
      mockClient = {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)
    })

    it('应该成功发送密码重置邮件', async () => {
      const mockResponse = {
        data: {
          message: '密码重置邮件已发送，请查收',
        },
      }
      mockClient.post = vi.fn().mockResolvedValue(mockResponse)

      const store = useAuthStore()
      const result = await store.sendPasswordReset({
        email: 'test@example.com',
        captcha_id: 'test-captcha-id',
        captcha_answer: '1234',
      })

      expect(mockClient.post).toHaveBeenCalledWith(
        '/api/auth/password/reset/send/',
        {
          email: 'test@example.com',
          captcha_id: 'test-captcha-id',
          captcha_answer: '1234',
        }
      )
      expect(result).toEqual(mockResponse.data)
    })

    it('应该处理验证码错误', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: '验证码错误',
            code: 'INVALID_CAPTCHA',
          },
        },
      }
      mockClient.post = vi.fn().mockRejectedValue(errorResponse)

      const store = useAuthStore()
      await expect(
        store.sendPasswordReset({
          email: 'test@example.com',
          captcha_id: 'invalid-captcha-id',
          captcha_answer: 'wrong',
        })
      ).rejects.toThrow()
    })

    it('应该处理邮箱格式错误', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: '邮箱格式不正确',
            code: 'INVALID_EMAIL',
          },
        },
      }
      mockClient.post = vi.fn().mockRejectedValue(errorResponse)

      const store = useAuthStore()
      await expect(
        store.sendPasswordReset({
          email: 'invalid-email',
          captcha_id: 'test-captcha-id',
          captcha_answer: '1234',
        })
      ).rejects.toThrow()
    })

    it('应该处理网络错误', async () => {
      const error = new Error('网络错误，请稍后重试')
      mockClient.post = vi.fn().mockRejectedValue(error)

      const store = useAuthStore()
      await expect(
        store.sendPasswordReset({
          email: 'test@example.com',
          captcha_id: 'test-captcha-id',
          captcha_answer: '1234',
        })
      ).rejects.toThrow('网络错误，请稍后重试')
    })
  })

  describe('resetPassword', () => {
    let mockClient: AxiosInstance

    beforeEach(() => {
      mockClient = {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        request: vi.fn(),
        defaults: {} as any,
        interceptors: {} as any,
        create: vi.fn(),
      } as unknown as AxiosInstance
      setApiClient(mockClient)
    })

    it('应该成功重置密码', async () => {
      const mockResponse = {
        data: {
          message: '密码重置成功',
        },
      }
      mockClient.post = vi.fn().mockResolvedValue(mockResponse)

      const store = useAuthStore()
      const result = await store.resetPassword({
        token: 'reset-token',
        password: 'NewPassword123!',
        password_confirm: 'NewPassword123!',
      })

      expect(mockClient.post).toHaveBeenCalledWith(
        '/api/auth/password/reset/',
        {
          token: 'reset-token',
          password: 'NewPassword123!',
          password_confirm: 'NewPassword123!',
        }
      )
      expect(result).toEqual(mockResponse.data)
    })

    it('应该处理密码不匹配错误', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: '两次输入的密码不一致',
            code: 'PASSWORD_MISMATCH',
          },
        },
      }
      mockClient.post = vi.fn().mockRejectedValue(errorResponse)

      const store = useAuthStore()
      await expect(
        store.resetPassword({
          token: 'reset-token',
          password: 'NewPassword123!',
          password_confirm: 'DifferentPassword123!',
        })
      ).rejects.toThrow()
    })

    it('应该处理弱密码错误', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: '密码长度至少为8位',
            code: 'WEAK_PASSWORD',
          },
        },
      }
      mockClient.post = vi.fn().mockRejectedValue(errorResponse)

      const store = useAuthStore()
      await expect(
        store.resetPassword({
          token: 'reset-token',
          password: 'weak',
          password_confirm: 'weak',
        })
      ).rejects.toThrow()
    })

    it('应该处理无效token错误', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            error: '无效的重置链接',
            code: 'INVALID_TOKEN',
          },
        },
      }
      mockClient.post = vi.fn().mockRejectedValue(errorResponse)

      const store = useAuthStore()
      await expect(
        store.resetPassword({
          token: 'invalid-token',
          password: 'NewPassword123!',
          password_confirm: 'NewPassword123!',
        })
      ).rejects.toThrow()
    })

    it('应该处理网络错误', async () => {
      const error = new Error('网络错误，请稍后重试')
      mockClient.post = vi.fn().mockRejectedValue(error)

      const store = useAuthStore()
      await expect(
        store.resetPassword({
          token: 'reset-token',
          password: 'NewPassword123!',
          password_confirm: 'NewPassword123!',
        })
      ).rejects.toThrow('网络错误，请稍后重试')
    })
  })
})
