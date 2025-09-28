import {defineStore} from 'pinia';
import {getHistoryFromSession} from "@/api/chatapi.js";

// 定义本地存储的键名
const STORAGE_KEYS = {
  sharedPrompt: 'app_shared_prompt',
  systemPrompt: 'app_system_prompt',
  sessionId: 'app_session_id',
  historyFormSession: 'app_history_form_session',
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
    historyFormSession: loadFromStorage(STORAGE_KEYS.historyFormSession),
  }), actions: {
    setSharedPrompt(prompt) {
      if (typeof prompt === 'object' && prompt !== null && prompt.name && prompt.personality && prompt.background && prompt.languageStyle) {
        this.sharedPrompt = prompt;
        saveToStorage(STORAGE_KEYS.sharedPrompt, prompt);
      } else {
        console.warn('Prompt 数据不完整！需包含 name、personality、background、languageStyle 属性');
      }
    },

    clearSharedPrompt() {
      this.sharedPrompt = null;
      localStorage.removeItem(STORAGE_KEYS.sharedPrompt);
    },

    setSystemPrompt(prompt) {
      this.systemPrompt = prompt;
      saveToStorage(STORAGE_KEYS.systemPrompt, prompt);
    },

    clearSystemPrompt() {
      this.systemPrompt = null;
      localStorage.removeItem(STORAGE_KEYS.systemPrompt);
    },

    async setSessionId(sessionId) {
      console.log('sessionId', sessionId);
      this.sessionId = sessionId; // 先更新 sessionId 状态
      try {
        // 调用接口获取对应会话记录
        const history = await getHistoryFromSession(sessionId);

        console.log(history);
        this.setHistoryFromSession(history.data?.chat_records);
      } catch (error) {
        console.error('获取会话记录失败：', error);
        // 失败时清除旧记录，避免数据不一致
        this.clearHistoryFormSession();
      }
      // 无论接口是否成功，都保存 sessionId 到本地存储
      saveToStorage(STORAGE_KEYS.sessionId, sessionId);
    },

    clearSessionId() {
      this.sessionId = null;
      localStorage.removeItem(STORAGE_KEYS.sessionId);
      this.clearHistoryFormSession()
    },

    // 避免与 state 中的 historyFormSession 冲突
    setHistoryFromSession(historyFormSession) {
      this.historyFormSession = historyFormSession;
      saveToStorage(STORAGE_KEYS.historyFormSession, historyFormSession);
      console.log('更新了当前的会话记录', historyFormSession);
    },

    clearHistoryFormSession() {
      this.historyFormSession = null;
      localStorage.removeItem(STORAGE_KEYS.historyFormSession);
    },
  }
});
