import {defineStore} from 'pinia';

export const usePromptStore = defineStore('prompt', {
  state: () => ({
    // 核心状态：存储角色 Prompt 对象，初始值设为 null（表示“无数据”）
    sharedPrompt: null
  }), actions: {
    // 存放 Prompt：接收角色对象参数
    setSharedPrompt(prompt) {

      if (typeof prompt === 'object' && prompt !== null && prompt.name && // 确保有“角色名”
        prompt.personality && prompt.background && prompt.languageStyle) {
        this.sharedPrompt = prompt;
      } else {
        console.warn('Prompt 数据不完整！需包含 name、personality、background 属性');
      }
    },

    clearSharedPrompt() {
      this.sharedPrompt = null;
    }
  }
});
