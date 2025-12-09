// REQ-ID: REQ-2025-003-user-login
/**
 * 表单验证工具函数
 */

// 邮箱格式验证正则
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 错误消息，如果验证通过则返回空字符串
 */
export const validateEmail = (email: string): string => {
  if (!email) {
    return '请输入邮箱'
  }
  if (!EMAIL_REGEX.test(email)) {
    return '邮箱格式不正确'
  }
  return ''
}

/**
 * 验证密码
 * @param password 密码
 * @returns 错误消息，如果验证通过则返回空字符串
 */
export const validatePassword = (password: string): string => {
  if (!password) {
    return '请输入密码'
  }
  if (password.length < 8) {
    return '密码长度至少为8位'
  }
  return ''
}

/**
 * 验证确认密码
 * @param password 密码
 * @param passwordConfirm 确认密码
 * @returns 错误消息，如果验证通过则返回空字符串
 */
export const validatePasswordConfirm = (
  password: string,
  passwordConfirm: string
): string => {
  if (!passwordConfirm) {
    return '请确认密码'
  }
  if (password !== passwordConfirm) {
    return '两次输入的密码不一致'
  }
  return ''
}

/**
 * 验证验证码
 * @param captchaId 验证码ID
 * @param captchaAnswer 验证码答案
 * @returns 错误消息，如果验证通过则返回空字符串
 */
export const validateCaptcha = (
  captchaId: string,
  captchaAnswer: string
): string => {
  if (!captchaId || !captchaAnswer) {
    return '请输入验证码'
  }
  return ''
}
