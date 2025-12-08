// REQ-ID: REQ-2025-003-user-login
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios, { AxiosInstance } from 'axios'

// API基础URL
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例（可以在测试中被mock）
export const createApiClient = (): AxiosInstance => {
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

// 默认使用创建的实例（测试时可以注入mock实例）
let apiClient = createApiClient()

// 允许在测试中注入mock的axios实例
export const setApiClient = (client: AxiosInstance) => {
  apiClient = client
}

// 获取当前apiClient（每次调用都获取最新的，支持测试中的动态注入）
const getApiClient = (): AxiosInstance => {
  return apiClient
}

// 类型定义
export interface User {
  id: string
  email: string
  is_email_verified: boolean
}

export interface Captcha {
  id: string
  image: string
  expiresIn: number
}

export interface LoginCredentials {
  email: string
  password: string
  captcha_id: string
  captcha_answer: string
}

export interface RegisterCredentials {
  email: string
  password: string
  password_confirm: string
  captcha_id: string
  captcha_answer: string
}

export interface LoginResponse {
  user: User
  token: string
  refresh_token: string
}

export interface RegisterResponse {
  user: User
  token: string
  refresh_token: string
  message?: string
}

export interface TokenRefreshResponse {
  access?: string
  token?: string
  refresh_token?: string
}

export interface CaptchaResponse {
  captcha_id: string
  captcha_image: string
  expires_in: number
}

// localStorage键名
const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'auth_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const captcha = ref<Captcha | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => {
    return !!(user.value && token.value)
  })

  // 从localStorage恢复token（延迟执行，确保在测试中可以设置localStorage）
  const restoreTokens = () => {
    // 使用nextTick确保在store创建后执行
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem(TOKEN_KEY)
      const savedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

      if (savedToken) {
        token.value = savedToken
      }
      if (savedRefreshToken) {
        refreshToken.value = savedRefreshToken
      }
    }
  }

  // 保存token到localStorage
  const saveTokens = (accessToken: string, refresh: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    token.value = accessToken
    refreshToken.value = refresh
  }

  // 清除token
  const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    token.value = null
    refreshToken.value = null
  }

  // Actions
  const login = async (
    credentials: LoginCredentials
  ): Promise<LoginResponse> => {
    try {
      const response = await getApiClient().post<LoginResponse>(
        '/api/auth/login/',
        credentials
      )

      const {
        user: userData,
        token: accessToken,
        refresh_token,
      } = response.data

      user.value = userData
      saveTokens(accessToken, refresh_token)

      return response.data
    } catch (error: any) {
      if (error.response) {
        throw new Error(
          error.response.data?.error || '登录失败，请检查账号密码'
        )
      }
      throw new Error('网络错误，请稍后重试')
    }
  }

  const register = async (
    credentials: RegisterCredentials
  ): Promise<RegisterResponse> => {
    try {
      const response = await getApiClient().post<RegisterResponse>(
        '/api/auth/register/',
        credentials
      )

      const {
        user: userData,
        token: accessToken,
        refresh_token,
      } = response.data

      user.value = userData
      saveTokens(accessToken, refresh_token)

      return response.data
    } catch (error: any) {
      if (error.response) {
        throw new Error(
          error.response.data?.error || '注册失败，请检查输入信息'
        )
      }
      throw new Error('网络错误，请稍后重试')
    }
  }

  const logout = async (): Promise<void> => {
    try {
      if (token.value) {
        await getApiClient().post('/api/auth/logout/', null, {
          headers: {
            Authorization: `Bearer ${token.value}`,
          },
        })
      }
    } catch (error) {
      // 即使登出API失败，也清除本地状态
      console.error('Logout API error:', error)
    } finally {
      user.value = null
      clearTokens()
    }
  }

  const refreshTokenAction = async (): Promise<void> => {
    if (!refreshToken.value) {
      throw new Error('没有可用的刷新令牌')
    }

    try {
      const response = await getApiClient().post<TokenRefreshResponse>(
        '/api/auth/token/refresh/',
        {
          refresh: refreshToken.value,
        }
      )

      const newToken = response.data.access || response.data.token || ''

      if (newToken) {
        // 只更新access token，refresh token保持不变
        localStorage.setItem(TOKEN_KEY, newToken)
        token.value = newToken
        // refreshToken保持不变，不需要更新
      } else {
        throw new Error('Token刷新失败：响应中缺少token')
      }
    } catch (error: any) {
      // 刷新失败，清除所有状态
      user.value = null
      clearTokens()

      if (error.response) {
        throw new Error(
          error.response.data?.error || 'Token刷新失败，请重新登录'
        )
      }
      throw new Error('网络错误，请稍后重试')
    }
  }

  const fetchCaptcha = async (): Promise<Captcha> => {
    try {
      const response =
        await getApiClient().get<CaptchaResponse>('/api/auth/captcha/')

      const captchaData: Captcha = {
        id: response.data.captcha_id,
        image: response.data.captcha_image,
        expiresIn: response.data.expires_in,
      }

      captcha.value = captchaData
      return captchaData
    } catch (error: any) {
      captcha.value = null
      if (error.response) {
        throw new Error(error.response.data?.error || '获取验证码失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  }

  const refreshCaptcha = async (): Promise<Captcha> => {
    try {
      const response = await getApiClient().get<CaptchaResponse>(
        '/api/auth/captcha/refresh/'
      )

      const captchaData: Captcha = {
        id: response.data.captcha_id,
        image: response.data.captcha_image,
        expiresIn: response.data.expires_in,
      }

      captcha.value = captchaData
      return captchaData
    } catch (error: any) {
      captcha.value = null
      if (error.response) {
        throw new Error(error.response.data?.error || '刷新验证码失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  }

  // 初始化：从localStorage恢复token
  restoreTokens()

  return {
    // 状态
    user,
    token,
    refreshToken,
    captcha,
    // 计算属性
    isAuthenticated,
    // Actions
    login,
    register,
    logout,
    refreshTokenAction,
    fetchCaptcha,
    refreshCaptcha,
  }
})
