<template>
  <div
    class="audio-avatar"
    :class="{
      'playing': isPlaying,
      'paused': !isPlaying && isReady,
      'loading': isLoading,
      'error': hasError
    }"
    @click="togglePlay"
    :title="getTitleText"
  >
    <img
      :src="avatarSrc"
      alt="语音头像"
      class="avatar-img"
    >

    <!-- 播放状态指示器（圆形波纹动画） -->
    <div v-if="isPlaying" class="playing-indicator"></div>
  </div>
</template>

<script setup>
import {ref, watch, onUnmounted, defineEmits, defineProps} from 'vue';

// -------------------------- Props 定义 --------------------------
const props = defineProps({
  // 音频来源：支持 URL/Blob/Base64
  audioSource: {
    type: [String, Blob],
    required: true
  },

  // 头像图片 URL
  avatarSrc: {
    type: String,
    default: 'https://picsum.photos/200/200?random=1'
  },

  // 父组件控制：是否强制停止播放
  forceStop: {
    type: Boolean,
    default: false
  }
});

// -------------------------- 事件定义 --------------------------
const emit = defineEmits(['play', 'pause', 'end', 'error']);

// -------------------------- 状态管理 --------------------------
const audio = ref(null);          // Audio 实例
const isPlaying = ref(false);     // 是否正在播放
const isReady = ref(false);       // 音频是否就绪
const isLoading = ref(false);     // 是否正在加载
const hasError = ref(false);      // 是否发生错误
const audioUrl = ref('');         // 音频临时 URL

// -------------------------- 计算属性 --------------------------
const getTitleText = ref('点击播放语音');

// -------------------------- 核心方法 --------------------------
// 初始化音频
const initAudio = (source) => {
  // 清除旧实例
  cleanupAudio();

  // 标记加载状态
  isLoading.value = true;
  isReady.value = false;
  hasError.value = false;
  getTitleText.value = '加载中...';

  // 根据来源类型处理
  if (source instanceof Blob) {
    // 处理 Blob 类型
    audioUrl.value = URL.createObjectURL(source);
    createAudioInstance(audioUrl.value);
  } else if (typeof source === 'string') {
    if (source.startsWith('data:audio/')) {
      // 处理 Base64 类型
      base64ToBlobAndLoad(source);
    } else {
      // 处理 URL 类型
      createAudioInstance(source);
    }
  }
};

// 创建 Audio 实例
const createAudioInstance = (url) => {
  audio.value = new Audio(url);

  // 音频就绪事件
  audio.value.addEventListener('canplay', () => {
    isLoading.value = false;
    isReady.value = true;
    getTitleText.value = '点击播放语音';
  });

  // 播放结束事件
  audio.value.addEventListener('ended', () => {
    isPlaying.value = false;
    getTitleText.value = '点击播放语音';
    emit('end');
  });

  // 错误事件
  audio.value.addEventListener('error', (err) => {
    isLoading.value = false;
    hasError.value = true;
    isPlaying.value = false;
    getTitleText.value = '播放失败，点击重试';
    emit('error', err);
  });
};

// Base64 转 Blob 并加载
const base64ToBlobAndLoad = (base64Str) => {
  try {
    const [header, data] = base64Str.split(',');
    const mimeType = header.match(/:(.*?);/)[1];
    const binaryStr = atob(data);
    const uint8Arr = new Uint8Array(binaryStr.length);

    for (let i = 0; i < binaryStr.length; i++) {
      uint8Arr[i] = binaryStr.charCodeAt(i);
    }

    const blob = new Blob([uint8Arr], {type: mimeType});
    audioUrl.value = URL.createObjectURL(blob);
    createAudioInstance(audioUrl.value);
  } catch (err) {
    isLoading.value = false;
    hasError.value = true;
    getTitleText.value = '格式错误，点击重试';
    emit('error', new Error('Base64 解析失败'));
  }
};

// 切换播放/暂停
const togglePlay = () => {
  if (!audio.value) return;

  if (isPlaying.value) {
    pauseAudio();
  } else {
    playAudio();
  }
};

// 播放音频
const playAudio = () => {
  if (!isReady.value || isPlaying.value) return;

  audio.value.play()
    .then(() => {
      isPlaying.value = true;
      hasError.value = false;
      getTitleText.value = '点击暂停语音';
      emit('play');
    })
    .catch(err => {
      hasError.value = true;
      getTitleText.value = '播放被阻止，点击重试';
      emit('error', err);
    });
};

// 暂停音频
const pauseAudio = () => {
  if (!audio.value || !isPlaying.value) return;

  audio.value.pause();
  isPlaying.value = false;
  getTitleText.value = '点击继续播放';
  emit('pause');
};

// 停止音频（重置）
const stopAudio = () => {
  if (!audio.value) return;

  audio.value.pause();
  audio.value.currentTime = 0;
  isPlaying.value = false;
  getTitleText.value = '点击播放语音';
};

// 清除音频实例
const cleanupAudio = () => {
  if (audio.value) {
    audio.value.pause();
    audio.value.removeEventListener('canplay', () => {
    });
    audio.value.removeEventListener('ended', () => {
    });
    audio.value.removeEventListener('error', () => {
    });
    audio.value = null;
  }

  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value);
    audioUrl.value = '';
  }
};

// -------------------------- 监听与生命周期 --------------------------
// 监听音频来源变化
watch(
  () => props.audioSource,
  (newSource) => {
    if (newSource) {
      initAudio(newSource);
    }
  },
  {immediate: true}
);

// 监听父组件强制停止信号
watch(
  () => props.forceStop,
  (newVal) => {
    if (newVal) {
      stopAudio();
    }
  }
);

// 组件卸载时清理资源
onUnmounted(() => {
  cleanupAudio();
});
</script>

<style scoped>
.audio-avatar {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 头像图片样式 */
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: all 0.3s ease;
}

/* 播放状态样式 */
.playing {
  transform: scale(1.05);
}

.playing .avatar-img {
  filter: brightness(1.1);
}

/* 暂停状态样式 */
.paused {
  opacity: 0.9;
}

.paused:hover {
  opacity: 1;
}

/* 加载状态样式 */
.loading .avatar-img {
  filter: grayscale(0.5);
}

/* 错误状态样式 */
.error .avatar-img {
  filter: hue-rotate(180deg) brightness(0.9);
}

/* 播放指示器动画（波纹效果） */
.playing-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  animation: pulse 2s infinite;
}

.playing-indicator::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 80%;
  height: 80%;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: pulse-inner 2s infinite;
}

/* 波纹动画 */
@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

@keyframes pulse-inner {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0;
  }
}
</style>
