import axios from 'axios';

// 创建 axios 实例并配置
const apiClient = axios.create({
  timeout: 30000, // 全局超时设置
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * 发送聊天请求
 * @param {Object} params - 请求参数
 * @param {string} params.message - 聊天消息内容
 * @param {string} params.system_prompt - 系统提示文本
 * @returns {Promise<Object>} - 接口响应数据
 */
export const sendChatRequest = async (params) => {
  try {

    console.log('params', params)
    // 可以在这里对参数进行二次处理，比如确保类型正确
    const requestData = {
      session_id: params.session_id || '',
      message: params.message || '',
      system_prompt: params.system_prompt || ''
    };


    const response = await apiClient.post('/api/v1/chat/text_chat', requestData);

    console.log('接口调用成功，响应数据：', response.data);
    return response.data;
  } catch (error) {
    // 统一错误处理
    if (error.response) {
      console.error('接口调用失败，状态码：', error.response.status);
      console.error('错误信息：', error.response.data);
      throw new Error(`接口错误: ${error.response.data.message || '请求失败'}`);
    } else if (error.request) {
      console.error('没有收到服务器响应：', error.request);
      throw new Error('未收到服务器响应，请检查网络或代理配置');
    } else {
      console.error('请求发送错误：', error.message);
      throw new Error(`请求错误: ${error.message}`);
    }
  }
};


export const getHistoryFromSession = async (session_id) => {

  const response = await apiClient.get(`/api/v1/sessions/${session_id}/chats`);

  return response.data;

}

export const getVoiceList = async () => {
  const response = await apiClient.get(`/api/v1/chat/voice_list`);

  return response.data;
}

export default {
  sendChatRequest, getHistoryFromSession

};
