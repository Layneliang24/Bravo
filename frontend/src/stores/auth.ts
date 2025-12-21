// REQ-ID: REQ-2025-003-user-login
import axios, { AxiosInstance } from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 判断是否在浏览器环境（Vite proxy可用）
// 如果API_BASE_URL是Docker容器名（如http://backend:8000），在浏览器中无法解析
// 应该使用相对路径，让Vite proxy处理
const useRelativePath =
  typeof window !== 'undefined' &&
  (!API_BASE_URL ||
    API_BASE_URL.includes('backend:') ||
    API_BASE_URL.includes('localhost') ||
    API_BASE_URL.includes('127.0.0.1'))

// 创建axios实例（可以在测试中被mock）
export const createApiClient = (): AxiosInstance => {
  // 在浏览器环境中，使用相对路径让Vite proxy处理
  // 在服务器端渲染（SSR）或测试环境中，使用绝对路径
  const baseURL = useRelativePath ? '' : API_BASE_URL

  return axios.create({
    baseURL,
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

export interface PreviewUser {
  display_name: string
  avatar_url?: string | null
  avatar_letter?: string
  default_avatar?: boolean
}

export interface PreviewResponse {
  valid: boolean
  user: PreviewUser | null
}

export interface PreviewCredentials {
  email: string
  password: string
  captcha_id: string
  captcha_answer: string
}

export interface SendPasswordResetCredentials {
  email: string
  captcha_id: string
  captcha_answer: string
}

export interface ResetPasswordCredentials {
  token: string
  password: string
  password_confirm: string
}

export interface SendPasswordResetResponse {
  message: string
}

export interface ResetPasswordResponse {
  message: string
}

export interface SendEmailVerificationCredentials {
  email: string
}

export interface SendEmailVerificationResponse {
  message: string
}

export interface VerifyEmailResponse {
  message: string
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
  const preview = ref<PreviewResponse | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => {
    return !!(user.value && token.value)
  })

  // 从localStorage恢复token
  const restoreTokens = () => {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const savedToken = localStorage.getItem(TOKEN_KEY)
        const savedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

        if (savedToken) {
          token.value = savedToken
        }
        if (savedRefreshToken) {
          refreshToken.value = savedRefreshToken
        }
      } catch (error) {
        // localStorage可能不可用（如某些测试环境）
        console.warn('Failed to restore tokens from localStorage:', error)
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

  // 统一的错误处理函数
  const handleApiError = (error: any, defaultMessage: string): never => {
    if (error?.response?.data?.error) {
      throw new Error(error.response.data.error)
    }
    if (error?.response) {
      throw new Error(defaultMessage)
    }
    throw new Error('网络错误，请稍后重试')
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
      handleApiError(error, '登录失败，请检查账号密码')
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
      handleApiError(error, '注册失败，请检查输入信息')
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

      if (!newToken) {
        throw new Error('Token刷新失败：响应中缺少token')
      }

      // 只更新access token，refresh token保持不变
      localStorage.setItem(TOKEN_KEY, newToken)
      token.value = newToken
    } catch (error: any) {
      // 刷新失败，清除所有状态
      user.value = null
      clearTokens()

      handleApiError(error, 'Token刷新失败，请重新登录')
    }
  }

  // 处理验证码响应的辅助函数
  const parseCaptchaResponse = (data: CaptchaResponse): Captcha => {
    return {
      id: data.captcha_id,
      image: data.captcha_image,
      expiresIn: data.expires_in,
    }
  }

  const fetchCaptcha = async (): Promise<Captcha> => {
    try {
      const response =
        await getApiClient().get<CaptchaResponse>('/api/auth/captcha/')

      const captchaData = parseCaptchaResponse(response.data)
      captcha.value = captchaData
      return captchaData
    } catch (error: any) {
      captcha.value = null
      handleApiError(error, '获取验证码失败')
    }
  }

  const refreshCaptcha = async (oldCaptchaId?: string): Promise<Captcha> => {
    try {
      // 使用POST方法，与后端API一致
      const response = await getApiClient().post<CaptchaResponse>(
        '/api/auth/captcha/refresh/',
        oldCaptchaId ? { captcha_id: oldCaptchaId } : {}
      )

      const captchaData = parseCaptchaResponse(response.data)
      captcha.value = captchaData
      return captchaData
    } catch (error: any) {
      captcha.value = null
      handleApiError(error, '刷新验证码失败')
    }
  }

  const previewLogin = async (
    credentials: PreviewCredentials
  ): Promise<PreviewResponse> => {
    try {
      const response = await getApiClient().post<PreviewResponse>(
        '/api/auth/preview/',
        credentials
      )

      // 预览API始终返回200，即使密码错误也返回{valid: false}
      preview.value = response.data
      return response.data
    } catch (error: any) {
      // 只有网络错误或验证码错误（400）或频率限制（429）才会进入catch
      preview.value = null

      // 检查是否是验证码错误
      if (
        error?.response?.status === 400 &&
        error?.response?.data?.code === 'INVALID_CAPTCHA'
      ) {
        // 验证码错误，抛出错误让调用方处理
        throw error
      }

      // 检查是否是429错误（频率限制）
      if (error?.response?.status === 429) {
        // 429错误，抛出错误让调用方处理（保留原始error对象，包含response信息）
        throw error
      }

      // 其他错误（网络错误等）
      handleApiError(error, '预验证失败，请检查输入信息')
    }
  }

  const sendPasswordReset = async (
    credentials: SendPasswordResetCredentials
  ): Promise<SendPasswordResetResponse> => {
    try {
      const response = await getApiClient().post<SendPasswordResetResponse>(
        '/api/auth/password/reset/send/',
        credentials
      )

      return response.data
    } catch (error: any) {
      handleApiError(error, '发送密码重置邮件失败，请检查输入信息')
    }
  }

  const resetPassword = async (
    credentials: ResetPasswordCredentials
  ): Promise<ResetPasswordResponse> => {
    try {
      const response = await getApiClient().post<ResetPasswordResponse>(
        '/api/auth/password/reset/',
        credentials
      )

      return response.data
    } catch (error: any) {
      handleApiError(error, '密码重置失败，请检查输入信息')
    }
  }

  const sendEmailVerification = async (
    credentials: SendEmailVerificationCredentials
  ): Promise<SendEmailVerificationResponse> => {
    try {
      const currentToken = token.value
      if (!currentToken) {
        throw new Error('未认证，请先登录')
      }

      const response = await getApiClient().post<SendEmailVerificationResponse>(
        '/api/auth/email/verify/send/',
        credentials,
        {
          headers: {
            Authorization: `Bearer ${currentToken}`,
          },
        }
      )

      return response.data
    } catch (error: any) {
      handleApiError(error, '发送验证邮件失败，请稍后重试')
    }
  }

  const verifyEmail = async (token: string): Promise<VerifyEmailResponse> => {
    try {
      const response = await getApiClient().get<VerifyEmailResponse>(
        `/api/auth/email/verify/${token}/`
      )

      return response.data
    } catch (error: any) {
      handleApiError(error, '邮箱验证失败，请稍后重试')
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
    preview,
    // 计算属性
    isAuthenticated,
    // Actions
    login,
    register,
    logout,
    refreshTokenAction,
    fetchCaptcha,
    refreshCaptcha,
    previewLogin,
    sendPasswordReset,
    resetPassword,
    sendEmailVerification,
    verifyEmail,
  }
})
