<script setup lang="ts">
import {ref, onBeforeUnmount, onMounted, onUnmounted, defineProps} from 'vue';
import router from '@/router';
import SpeechAPI from "@/components/SpeechAPI.vue";
import eventBus from "@/utils/eventBus.js";

const isLeaving = ref(false);
let canUnmount = false;
let colorInterval: number | null = null; // 颜色切换定时器

interface characterPrompt {
  name: string,
  source: string,
  personality: string,
  languageStyle: string,
  background: string,
}

const props = defineProps<{
  characterPrompt: characterPrompt
}>()

const characterPrompt = props.characterPrompt;

/*
const prompt = `你现在需要完全扮演用户自定义的角色：${characterPrompt.name}。
1. 角色来源：${characterPrompt.source || "无特定来源，按用户描述演绎"}；
2. 性格特点：${characterPrompt.personality || "中性性格，自然对话即可"}；
3. 语言风格：${characterPrompt.languageStyle || "正常口语，无特殊风格"}；
4. 身份背景：${characterPrompt.background || "无特定背景，专注当前对话"}；
5. 核心要求：严格按上述设定回复，不偏离角色，不暴露AI身份，用角色的视角与用户聊天。`
*/

// 动画结束回调：控制路由跳转
const handleAnimationEnd = () => {
  if (isLeaving.value) {
    canUnmount = true;
    router.push({path: '/'});
  }
};

// 返回按钮逻辑：触发离场动画
const goBack = () => {
  isLeaving.value = true;
};

// 生成柔和随机RGB色值（契合原有浅色调，避免刺眼）
const getSoftRandomColor = () => {
  const min = 200; // 最小色值（保证颜色柔和）
  const max = 255; // 最大色值（接近白色，贴合设计风格）
  const r = Math.floor(Math.random() * (max - min + 1)) + min;
  const g = Math.floor(Math.random() * (max - min + 1)) + min;
  const b = Math.floor(Math.random() * (max - min + 1)) + min;
  return `${r}, ${g}, ${b}`;
};

// 启动背景颜色动态变化
const startColorAnimation = () => {
  const graphEl = document.querySelector('.background-graph') as HTMLElement | null;
  if (!graphEl) return;

  // 初始立即更新一次颜色
  graphEl.style.setProperty('--outer-color', getSoftRandomColor());

  // 定时更新颜色（3秒切换一次，可调整间隔）
  colorInterval = window.setInterval(() => {
    graphEl.style.setProperty('--outer-color', getSoftRandomColor());
  }, 3000);
};

// 停止颜色动画（避免内存泄漏）
const stopColorAnimation = () => {
  if (colorInterval) {
    clearInterval(colorInterval);
    colorInterval = null;
  }
};

const hangUp = () => {
  goBack();
}

// 组件挂载：监听动画结束+启动颜色动态变化
onMounted(() => {
  const graphEl = document.querySelector('.background-graph');
  if (graphEl) {
    graphEl.addEventListener('animationend', handleAnimationEnd);
  }
  startColorAnimation();

  eventBus.on('hangUp', hangUp);

  //todo:调用接口，把prompt传给后端

});

// 组件卸载前：清理事件监听+停止颜色动画
onBeforeUnmount(() => {
  const graphEl = document.querySelector('.background-graph');
  if (graphEl) {
    graphEl.removeEventListener('animationend', handleAnimationEnd);
  }
  stopColorAnimation();

  // 动画未完成时的兜底（避免强制销毁）
  if (!canUnmount) {
    // 等待动画完成后再跳转（兜底逻辑，防止路由跳转打断动画）
    setTimeout(() => {
      if (!canUnmount) {
        router.push({path: '/'});
      }
    }, 500); // 匹配scaleOut动画时长
  }
});

// 额外清理：确保定时器完全停止
onUnmounted(() => {
  stopColorAnimation();
});
</script>

<template>

  <div class="header">
    Harry Potter
  </div>
  <div class="container">
    <i class="iconfont icon-zuohua" style="position: absolute;
    z-index: 999999;
    left: 33px;
    top: 20px;
    color: black;"></i>
    <span class="go-back" @click="goBack">
      返回
    </span>
    <div
      class="background-graph"
      :class="{ 'scale-out': isLeaving }"
    >
    </div>
  </div>

  <div class="AI-avatar">
    <div class="AI-avatar-ripple"></div>
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
  animation: scaleOut .5s cubic-bezier(0.22, 0, 0.36, 0) forwards !important;
  animation-iteration-count: 1;
}

@keyframes scaleIn {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
  1% {
    transform: translate(-50%, -50%) scale(0.012);
    opacity: 0.01;
  }
  99% {
    transform: translate(-50%, -50%) scale(0.99995);
    opacity: 0.9998;
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
  1% {
    transform: translate(-50%, -50%) scale(0.99995);
    opacity: 0.9998;
  }
  2% {
    transform: translate(-50%, -50%) scale(0.9999);
    opacity: 0.9995;
  }
  98% {
    transform: translate(-50%, -50%) scale(0.024);
    opacity: 0.02;
  }
  99% {
    transform: translate(-50%, -50%) scale(0.012);
    opacity: 0.01;
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
  background-color: rgb(255, 255, 255, .5);
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
    opacity: .7;
    transform: translate(-50%, -50%) scale(0);
  }
  to {
    opacity: 0;
    transform: translate(-50%, -50%) scale(1.7);
  }
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
