import './assets/main.css'

import {createApp} from 'vue'
import {createPinia} from 'pinia'

import App from './App.vue'
import router from './router'
import {usePromptStore} from "@/stores/promptStore.js";

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'


const app = createApp(App)
app.use(ElementPlus) // 注册后可全局使用

app.use(createPinia())
app.use(router)

app.mount('#app')

app.config.globalProperties.$setSystemPrompt = function (promptInfo) {

  if (!promptInfo) {
    console.log('没有选定角色，使用默认模型')
    return;
  }
  const prompt = `你现在需要完全扮演用户自定义的角色：${promptInfo.name}。
        1. 角色来源：${promptInfo.source || "无特定来源，按用户描述演绎"}；
        2. 性格特点：${promptInfo.personality || "中性性格，自然对话即可"}；
        3. 语言风格：${promptInfo.languageStyle || "正常口语，无特殊风格"}；
        4. 身份背景：${promptInfo.background || "无特定背景，专注当前对话"}；
        5. 核心要求：严格按上述设定回复，不偏离角色，不暴露AI身份，用角色的视角与用户聊天，在没有特别表明的情况下需要讲中文。`
  const promptStore = usePromptStore();

  promptStore.setSystemPrompt(prompt);

}
