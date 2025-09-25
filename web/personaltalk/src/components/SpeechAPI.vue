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
        :class="[isRecognizing ? 'start-btn' : 'stop-btn' ]"
      >
        {{ isRecognizing ? '开启ing' : '静音ing' }}
      </button>
      <button
        class="hang-up"
        @click="handleHangUp"
      >
        挂断
      </button>
    </div>

  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import eventBus from "@/utils/eventBus.js";

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

// 启动识别
const startRecognition = () => {
  if (!recognition) recognition = initRecognition();
  if (!recognition || isRecognizing.value) return;

  isRecognizing.value = true;
  errorMsg.value = '';
  // statusMsg.value = '正在监听语音...';
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
      // statusMsg.value = '正在识别...';
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
      pauseTimer = setTimeout(() => {
        if (isRecognizing.value) {
          finalResult.value = currentSessionTranscript;
          // statusMsg.value = '已检测到停顿，输出最终结果（持续监听中）';
          // 重置当前会话，准备下一轮识别
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
          // statusMsg.value = '已检测到停顿，输出最终结果（持续监听中）';
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
      // statusMsg.value = `识别错误：${event.error}`;
    }
  };

  // 识别中断自动恢复
  recognition.onend = () => {
    if (isRecognizing.value && !errorMsg.value) {
      // statusMsg.value = '持续监听中...';
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
  // statusMsg.value = '已关闭语音识别';
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

const handleHangUp = () => {
  eventBus.emit('hangUp');
}
// 生命周期
onMounted(() => {
  // statusMsg.value = '正在请求麦克风权限...';
  setTimeout(() => {
    recognition = initRecognition();
    if (recognition) startRecognition();
  }, 500);
});

onUnmounted(() => {
  stopRecognition();
  recognition = null;
});
</script>

<style scoped>
.speech-container {
  width: 400px; /* 适当加宽以显示更多内容 */
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
}


.btn-group {
  display: flex;
  justify-content: center;
  gap: 10px;
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

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.realtime-box {
  padding:5px 10px;
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
