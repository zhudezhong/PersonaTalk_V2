<script setup lang="ts">
// 定义颜色props，设置默认值
const props = defineProps<{
  color?: string
}>()

// 处理默认颜色
const defaultColor = props.color || '#74abef'
</script>

<template>
  <div class="audio-wave">
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
    <div class="wave-bar" :style="{ backgroundColor: defaultColor }"></div>
  </div>
</template>

<style scoped>
.audio-wave {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  width: 100px;
  height: 40px;
  padding: 10px;
}

.wave-bar {
  width: 3px;
  border-radius: 3px;
  animation: wave 1s ease-in-out infinite;
}

/* 为每个音波条设置不同的动画延迟和高度，创造错落有致的效果 */
.wave-bar:nth-child(1) {
  height: 15px;
  animation-delay: -0.9s;
}

.wave-bar:nth-child(2) {
  height: 30px;
  animation-delay: -0.8s;
}

.wave-bar:nth-child(3) {
  height: 20px;
  animation-delay: -0.7s;
}

.wave-bar:nth-child(4) {
  height: 25px;
  animation-delay: -0.6s;
}

.wave-bar:nth-child(5) {
  height: 10px;
  animation-delay: -0.5s;
}

.wave-bar:nth-child(6) {
  height: 35px;
  animation-delay: -0.4s;
}

.wave-bar:nth-child(7) {
  height: 20px;
  animation-delay: -0.3s;
}

.wave-bar:nth-child(8) {
  height: 15px;
  animation-delay: -0.2s;
}

.wave-bar:nth-child(9) {
  height: 25px;
  animation-delay: -0.1s;
}

.wave-bar:nth-child(10) {
  height: 10px;
  animation-delay: 0s;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

</style>
