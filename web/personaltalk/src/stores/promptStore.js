import {defineStore} from 'pinia';

// 定义本地存储的键名
const STORAGE_KEYS = {
  sharedPrompt: 'app_shared_prompt', systemPrompt: 'app_system_prompt', sessionId: 'app_session_id'
};

// 从本地存储加载数据的工具函数
const loadFromStorage = (key) => {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error('Failed to load from storage:', error);
    return null;
  }
};

// 保存数据到本地存储的工具函数
const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Failed to save to storage:', error);
  }
};

export const usePromptStore = defineStore('prompt', {
  state: () => ({
    // 从本地存储初始化状态
    sharedPrompt: loadFromStorage(STORAGE_KEYS.sharedPrompt),
    systemPrompt: loadFromStorage(STORAGE_KEYS.systemPrompt),
    sessionId: loadFromStorage(STORAGE_KEYS.sessionId),

  }), actions: {
    setSharedPrompt(prompt) {
      if (typeof prompt === 'object' && prompt !== null && prompt.name && prompt.personality && prompt.background && prompt.languageStyle) {
        this.sharedPrompt = prompt;
        // 同步保存到本地存储
        saveToStorage(STORAGE_KEYS.sharedPrompt, prompt);
      } else {
        console.warn('Prompt 数据不完整！需包含 name、personality、background、languageStyle 属性');
      }
    },

    clearSharedPrompt() {
      this.sharedPrompt = null;
      // 同时清除本地存储
      localStorage.removeItem(STORAGE_KEYS.sharedPrompt);
    },

    setSystemPrompt(prompt) {
      this.systemPrompt = prompt;
      // 同步保存到本地存储
      saveToStorage(STORAGE_KEYS.systemPrompt, prompt);
    },

    clearSystemPrompt() {
      this.systemPrompt = null;
      // 同时清除本地存储
      localStorage.removeItem(STORAGE_KEYS.systemPrompt);
    },

    setSessionId(sessionId) {
      this.sessionId = sessionId;
      // 修复：将 prompt 改为 sessionId
      saveToStorage(STORAGE_KEYS.sessionId, sessionId);
    },

    clearSessionId() {
      this.sessionId = null;
      // 同时清除本地存储
      localStorage.removeItem(STORAGE_KEYS.sessionId);
    },
  }
});
