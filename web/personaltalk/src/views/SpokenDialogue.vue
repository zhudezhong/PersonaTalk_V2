<script setup lang="ts">
import {ref, onBeforeUnmount, onMounted} from 'vue';
import router from '@/router';

const isLeaving = ref(false);
let canUnmount = false;

const handleAnimationEnd = () => {
  if (isLeaving.value) {
    canUnmount = true;
    router.push({path: '/'});
  }
};

const goBack = () => {
  isLeaving.value = true; // 触发反向动画
};

onBeforeUnmount(() => {
  // 如果动画未完成，阻止立即销毁（等待 animationend 事件）
  if (!canUnmount) {
    // 这里通过阻止默认行为+等待动画完成，避免组件被强制销毁
    // 通过路由跳转销毁组件，需确保动画完成后再执行跳转
  }
});

// 6. 组件挂载后：监听动画完成事件（用于离场动画的收尾）
onMounted(() => {
  const graphEl = document.querySelector('.background-graph');
  if (graphEl) {
    graphEl.addEventListener('animationend', handleAnimationEnd);
  }
});
</script>

<template>
  <div class="container">
    <span class="go-back" @click="goBack">返回</span>
    <div
      class="background-graph"
      :class="{ 'scale-out': isLeaving }"
    >
      <div class="AI-avatar"></div>
    </div>
  </div>
</template>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
  position: relative;
}

.background-graph {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 2200px;
  height: 2200px;
  border-radius: 50%;
  background: radial-gradient(
    circle at center,
    #ffa7a1 0%,
    #ffcccc 50%,
    rgba(251, 209, 255, 0.5) 80%,
    rgba(251, 209, 255, 0) 100%
  );
  opacity: 0;

  will-change: transform, opacity;
  backface-visibility: hidden;
  perspective: 1000px;
  transform: translateZ(0);

  animation: scaleIn .5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
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
</style>
