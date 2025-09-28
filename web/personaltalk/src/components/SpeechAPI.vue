<template>
  <div class="speech-container">
    <!-- 实时识别内容显示区 -->
    <div class="realtime-box" v-show="realtimeTranscript">
      <p class="realtime-text">{{ realtimeTranscript }}</p>
    </div>

    <div class="btn-group">
      <button
        @click="toggleRecognition"
        class="start-btn"
        :title="[isRecognizing ? '静音' : '开麦' ]"
        :class="[isRecognizing ? 'start-btn' : 'stop-btn' ]"
      >
        <i style="font-size: 18px" v-if="isRecognizing" class="iconfont icon-maikefeng"></i>
        <i style="font-size: 18px" v-else class="iconfont icon-mic-off"></i>
      </button>
      <button
        class="hang-up"
        title="挂断"
        @click="handleHangUp"
      >
        <i class="iconfont icon-guaduan"></i>
      </button>
      <button title="复制模型prompt"
              class="export-btn"
              @click="handleExportPrompt"
      >
        <i class="iconfont icon-daochu"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import eventBus from "@/utils/eventBus.js";
import axios from "axios";
import {usePromptStore} from "@/stores/promptStore.js";
import {getHistoryFromSession, sendChatRequest} from "@/api/chatapi.js";
import Loading from "@/components/Loading.vue";

// 响应式变量
const isRecognizing = ref(false);
const realtimeTranscript = ref(''); // 实时识别内容
const finalResult = ref(''); // 停顿后的最终结果
const errorMsg = ref('');
let recognition = null;

// 状态管理
let currentSessionTranscript = ''; // 当前会话完整内容
let lastFinalSegment = ''; // 上一段最终识别内容（用于去重）
const PAUSE_DETECTION_TIMEOUT = 1500;
let pauseTimer = null;
let wasRecognizingBeforeAudio = false; // 记录播放音频前的识别状态
const audioInstance = ref(null); // 组件级音频实例引用（关键：用于销毁时访问）

// 初始化识别实例
const initRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    errorMsg.value = '当前浏览器不支持语音识别，请使用 Chrome 或 Edge';
    return null;
  }

  const instance = new SpeechRecognition();
  instance.continuous = true;
  instance.interimResults = true; // 启用中间结果（实时显示用）
  instance.lang = 'zh-CN';
  instance.maxAlternatives = 1;
  return instance;
};

// 音频销毁工具函数（统一清理逻辑，避免内存泄漏）
const destroyAudio = () => {
  if (audioInstance.value) {
    // 1. 强制停止播放（无论当前是否在播放/缓冲）
    audioInstance.value.pause();
    // 2. 清空音频源（切断与base64资源的链接）
    audioInstance.value.src = '';
    // 3. 卸载音频数据（部分浏览器支持，进一步释放内存）
    audioInstance.value.removeAttribute('src');
    // 4. 解除所有事件监听（避免残留回调导致内存泄漏）
    audioInstance.value.onended = null;
    audioInstance.value.onerror = null;
    // 5. 清空引用（让GC回收实例）
    audioInstance.value = null;
  }
};

// 启动识别
const startRecognition = () => {
  if (!recognition) recognition = initRecognition();
  if (!recognition || isRecognizing.value) return;

  isRecognizing.value = true;
  errorMsg.value = '';
  resetTranscripts();
  clearTimeout(pauseTimer);

  // 处理识别结果（区分中间结果和最终结果）
  recognition.onresult = (event) => {
    const result = event.results[event.results.length - 1];
    const transcript = result[0]?.transcript?.trim() || '';

    // 实时显示中间结果
    if (!result.isFinal) {
      realtimeTranscript.value = currentSessionTranscript + (transcript ? ` ${transcript}` : '');
      clearTimeout(pauseTimer); // 有新输入，重置停顿计时器
      return;
    }

    // 处理最终结果（去重）
    if (result.isFinal && transcript && transcript !== lastFinalSegment) {
      lastFinalSegment = transcript;
      currentSessionTranscript = currentSessionTranscript
        ? `${currentSessionTranscript} ${transcript}`
        : transcript;
      realtimeTranscript.value = currentSessionTranscript;

      // 启动停顿检测
      clearTimeout(pauseTimer);
      pauseTimer = setTimeout(async () => {
        if (isRecognizing.value) {
          finalResult.value = currentSessionTranscript;
          // 重置当前会话，准备下一轮识别
          const promptStore = usePromptStore();
          const session_id = promptStore.sessionId

          try {
            // 准备请求数据
            const requestData = {
              session_id: session_id,
              message: finalResult.value,
              system_prompt: promptStore.systemPrompt,
            };

            console.log(promptStore.systemPrompt);
            console.log('requestData', requestData)

            eventBus.emit('question-message', {
              content: finalResult.value,
              role: 'user',
            });

            const response = await sendChatRequest(requestData)

            if (response.code === 200) {
              eventBus.emit('answer-message', {
                session_id: response.data.session_id,
                content: response.data.response,
                role: 'system',
              });

              console.log('response', response);

              // 播放音频前先记录当前识别状态并停止识别
              wasRecognizingBeforeAudio = isRecognizing.value;
              if (wasRecognizingBeforeAudio) {
                stopRecognition();
              }

              // 先销毁之前未播放完的音频（避免多音频叠加播放）
              destroyAudio();
              // 创建新音频实例并赋值给组件级引用
              audioInstance.value = new Audio();
              audioInstance.value.src = 'data:audio/aac;base64,' + response.data.audio_data;

              try {
                await audioInstance.value.play();
              } catch (error) {
                console.error('音频播放失败：', error);
                // 播放失败时恢复识别状态 + 销毁当前音频实例
                if (wasRecognizingBeforeAudio) {
                  startRecognition();
                }
                destroyAudio();
              }

              // 监听播放结束事件
              audioInstance.value.addEventListener('ended', function () {
                console.log('音频播放结束！');
                // 播放结束后恢复之前的识别状态 + 清理音频
                if (wasRecognizingBeforeAudio) {
                  startRecognition();
                }
                destroyAudio();
              });

              // 监听播放错误事件
              audioInstance.value.addEventListener('error', function () {
                console.log('音频播放错误！');
                // 错误时恢复识别状态 + 清理音频
                if (wasRecognizingBeforeAudio) {
                  startRecognition();
                }
                destroyAudio();
              });

              await promptStore.setSessionId(session_id);

              // 此处应该先把回复的消息放入缓存
              const historyFormSession = promptStore.historyFormSession;
              promptStore.setHistoryFromSession(historyFormSession);
            }
          } catch (error) {
            // 错误处理
            if (error.response) {
              console.error('接口调用失败，状态码：', error.response.status);
              console.error('错误信息：', error.response.data);
            } else if (error.request) {
              // 请求已发出，但没有收到响应
              console.error('没有收到服务器响应：', error.request);
            } else {
              // 发送请求时发生错误
              console.error('请求发送错误：', error.message);
            }
            // 发生错误时恢复识别 + 清理音频
            if (wasRecognizingBeforeAudio) {
              startRecognition();
            }
            destroyAudio();
          }

          currentSessionTranscript = '';
          lastFinalSegment = '';
        }
      }, PAUSE_DETECTION_TIMEOUT);
    }
  };

  // 语音输入结束时
  recognition.onaudioend = () => {
    if (isRecognizing.value && currentSessionTranscript) {
      clearTimeout(pauseTimer);
      pauseTimer = setTimeout(() => {
        if (isRecognizing.value) {
          finalResult.value = currentSessionTranscript;
          currentSessionTranscript = '';
          lastFinalSegment = '';
        }
      }, PAUSE_DETECTION_TIMEOUT);
    }
  };

  // 错误处理
  recognition.onerror = (event) => {
    switch (event.error) {
      case 'not-allowed':
        stopRecognition();
        errorMsg.value = '麦克风权限被拒绝，请在浏览器设置中允许';
        break;
      case 'audio-capture':
        stopRecognition();
        errorMsg.value = '未检测到麦克风，请连接设备后重试';
        break;
      default:
    }
  };

  // 识别中断自动恢复
  recognition.onend = () => {
    if (isRecognizing.value && !errorMsg.value) {
      recognition.start();
    }
  };

  // 启动识别
  try {
    recognition.start();
  } catch (err) {
    stopRecognition();
    errorMsg.value = `启动失败：${err.message}`;
  }
};

// 停止识别
const stopRecognition = () => {
  isRecognizing.value = false;
  if (recognition) {
    recognition.stop();
    recognition.abort();
  }
  clearTimeout(pauseTimer);
};

// 切换识别状态
const toggleRecognition = () => {
  if (isRecognizing.value) {
    stopRecognition();
  } else {
    finalResult.value = '';
    errorMsg.value = '';
    startRecognition();
  }
};

// 重置识别内容
const resetTranscripts = () => {
  realtimeTranscript.value = '';
  currentSessionTranscript = '';
  lastFinalSegment = '';
};

const promptStore = usePromptStore();

const handleHangUp = () => {
  eventBus.emit('hangUp');
}

const handleExportPrompt = async () => {
  const contentToCopy = JSON.stringify(promptStore.sharedPrompt);

  try {
    await navigator.clipboard.writeText(contentToCopy);
    console.log('内容已成功复制到剪切板');
  } catch (error) {
    console.error('复制内容时出现错误:', error);
  }
}

const beginRecognize = () => {
  isRecognizing.value = true;
  startRecognition();
}

eventBus.on('beginRecognize', beginRecognize);

// 生命周期
onMounted(() => {
  setTimeout(() => {
    recognition = initRecognition();
    if (recognition) startRecognition();
  }, 500);
});

onUnmounted(() => {
  // 1. 先停止语音识别
  stopRecognition();
  recognition = null;
  // 2. 强制销毁未播放完的音频（核心修改点）
  destroyAudio();
});
</script>

<style scoped>
.speech-container {
  width: 400px;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
}

.btn-group {
  display: flex;
  gap: 10px;
  margin-left: 25px;
  align-items: center;
  justify-content: space-between;
}

button {
  width: 60px;
  height: 60px;
  padding: 16px;
  border: none;
  cursor: pointer;
  border-radius: 50%;
  font-size: 12px;
}

.start-btn {
  background: rgba(0, 0, 0, 0.3);
  color: #ffffff;
  margin-right: 30px;
  transition: 0.1s;
}

.start-btn:hover {
  background: rgba(51, 51, 51, 0.5);
}

.stop-btn {
  background: rgba(0, 0, 0, 0.3);
  color: #000000;
  opacity: 0.7;
}

.hang-up {
  color: white;
  background-color: #ff5d5d;
}

.hang-up:hover {
  color: white;
  background-color: #ff4c4c;
}

.export-btn {
  background: rgba(0, 0, 0, 0.3);
  color: #ffffff;
  margin-right: 30px;
  transition: 0.1s;
  margin-left: 30px;
}

.export-btn:hover {
  background: rgba(51, 51, 51, 0.5);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.realtime-box {
  padding: 5px 10px;
  background: #f5f5f5;
  border-radius: 5px;
  text-align: left;
  margin-bottom: 20px;
}

.realtime-text {
  margin: 5px;
  color: #333;
  min-height: 24px;
}
</style>
