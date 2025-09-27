<script setup lang="ts">
import {onBeforeUnmount, onErrorCaptured, onMounted, onUnmounted, ref} from 'vue';
import router from '@/router';
import SpeechAPI from "@/components/SpeechAPI.vue";
import eventBus from "@/utils/eventBus.js";
import AudioWave from "@/components/AudioWave.vue";
import {usePromptStore} from '@/stores/promptStore';
import Loading from "@/components/Loading.vue";
import {sendChatRequest} from '@/api/chatapi'

const isLeaving = ref(false);
let canUnmount = false;
let colorInterval: number | null = null;
let timer1: number | null = null;
let timer2: number | null = null;

const beginTime = ref(0);
const connectingTime = ref(0);
const connecting = ref(false);
const receivedMessages = ref<Array<{
  type: 'user' | 'ai';
  content: string;
  time: number;
  audioUrl?: string;
}>>([]);

const characterPrompt = usePromptStore().sharedPrompt;

const getSoftRandomColor = () => {
  const min = 200;
  const max = 255;
  const r = Math.floor(Math.random() * (max - min + 1)) + min;
  const g = Math.floor(Math.random() * (max - min + 1)) + min;
  const b = Math.floor(Math.random() * (max - min + 1)) + min;
  return `${r}, ${g}, ${b}`;
};

const formatTime = (ms: number) => {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

const formatMessageTime = (timestamp: number) => {
  const date = new Date(timestamp);
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const handleAnimationEnd = () => {
  if (isLeaving.value) {
    canUnmount = true;
    router.push({path: '/'});
  }
};

const goBack = () => {
  isLeaving.value = true;
};

const startColorAnimation = () => {
  const graphEl = document.querySelector('.background-graph') as HTMLElement | null;
  if (!graphEl) return;

  graphEl.style.setProperty('--outer-color', getSoftRandomColor());
  colorInterval = window.setInterval(() => {
    graphEl.style.setProperty('--outer-color', getSoftRandomColor());
  }, 3000);
};

const stopColorAnimation = () => {
  if (colorInterval) {
    clearInterval(colorInterval);
    colorInterval = null;
  }
};

const hangUp = () => {
  goBack();
};

onMounted(async () => {
  const promptStore = usePromptStore();
  console.log('promptStore.systemPrompt', promptStore.systemPrompt)
  const params = {
    session_id: promptStore.sessionId,
    message: '',
    system_prompt: promptStore.systemPrompt,
  }
  const response = await sendChatRequest(params)

  if (response.code === 200) {
    //  响应成功，把sessionId存入pinia并发送请求创建会话记录

    const sessionId = response.data.session_id;
    promptStore.setSessionId(sessionId);
  }

  const graphEl = document.querySelector('.background-graph');
  if (graphEl) {
    graphEl.addEventListener('animationend', handleAnimationEnd);
  }
  startColorAnimation();

  eventBus.on('hangUp', hangUp);

  beginTime.value = Date.now();
  if (timer2) clearInterval(timer2);
  timer2 = setInterval(() => {
    connectingTime.value = Date.now() - beginTime.value;
  }, 1000);

});

onBeforeUnmount(() => {
  const graphEl = document.querySelector('.background-graph');
  if (graphEl) {
    graphEl.removeEventListener('animationend', handleAnimationEnd);
  }
  stopColorAnimation();

  if (timer1) clearInterval(timer1);
  if (timer2) clearInterval(timer2);

  eventBus.off('hangUp', hangUp);
  eventBus.off('speech:user_input', () => {
  });

  if (!canUnmount) {
    setTimeout(() => {
      if (!canUnmount) {
        router.push({path: '/'});
      }
    }, 500);
  }
});

onUnmounted(() => {
});

onErrorCaptured((error) => {
  console.error('[组件错误] 捕获异常:', error);
  return false;
});
</script>

<template>
  <div class="header">
    {{ characterPrompt?.name || 'HarryPotter' }}

    <div class="connect-status">
      <template v-if="connecting">
        <div>Loading</div>
        <Loading style="margin-left: 8px;"/>
      </template>

      <template v-else>
        <span style="color: #ffe9e9"> {{ formatTime(connectingTime) }}</span>
      </template>
    </div>
  </div>

  <div class="container">
    <i class="iconfont icon-zuohua back-icon"></i>
    <span class="go-back" @click="goBack">返回</span>

    <div
      class="background-graph"
      :class="{ 'scale-out': isLeaving }"
    ></div>
  </div>

  <div class="AI-avatar">
    <div class="AI-avatar-ripple"></div>
    <div v-if="!connecting" class="audio-wave-container">
      <AudioWave color="#d35e82"/>
    </div>
  </div>

  <div class="footer-button">
    <SpeechAPI/>
  </div>
</template>

<style scoped>
.header {
  position: absolute;
  top: 50px;
  left: 50%;
  color: black;
  z-index: 999;
  transform: translateX(-50%);
  font-size: 24px;
  font-family: fantasy;
}

.connect-status {
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  font-family: sans-serif;
  text-align: center;
  color: #616161;
  display: flex;
  align-items: center;
}

.container {
  width: 100%;
  height: 100vh;
}

.background-graph {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 2200px;
  height: 2200px;
  border-radius: 50%;
  --outer-color: 251, 209, 255;
  background: radial-gradient(
    circle at center,
    #ff9388 0%,
    #ffa7a7 35%,
    #ffb4ca 60%,
    rgba(var(--outer-color), 0.3) 85%,
    rgba(var(--outer-color), 0) 100%
  );
  opacity: 0;
  filter: blur(50px);
  will-change: transform, opacity, background;
  backface-visibility: hidden;
  perspective: 1000px;
  transform: translateZ(0);
  transition: background 1s ease-in-out;
  animation: scaleIn 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-iteration-count: 1;
}

.background-graph.scale-out {
  animation: scaleOut 0.5s cubic-bezier(0.22, 0, 0.36, 0) forwards !important;
  animation-iteration-count: 1;
}

@keyframes scaleIn {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
}

@keyframes scaleOut {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
}

.go-back {
  position: fixed;
  left: 50px;
  top: 20px;
  color: #181818;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  opacity: 0;
  animation: fadeIn 0.5s ease forwards 0.3s;
}

.go-back::after {
  content: "";
  position: absolute;
  left: 0;
  transform: translateX(100%);
  height: 100%;
  width: 100%;
  border-bottom: 1px solid #181818;
  transition: all 0.3s;
}

.go-back:hover::after {
  transform: translateX(0);
}

.back-icon {
  position: absolute;
  z-index: 999999;
  left: 33px;
  top: 20px;
  color: black;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.AI-avatar {
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  width: 80px;
  height: 80px;
  z-index: 99;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.AI-avatar-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #ededed;
  animation: aiAvatarRipple 3s ease 0.3s infinite;
}

@keyframes aiAvatarRipple {
  from {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(0);
  }
  to {
    opacity: 0;
    transform: translate(-50%, -50%) scale(1.7);
  }
}

.audio-wave-container {
  position: absolute;
  top: 110px;
  left: -10px;
}

.footer-button {
  display: flex;
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
}
</style>
