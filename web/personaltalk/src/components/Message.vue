<!-- src/components/Message/Message.vue -->
<template>
  <div
    class="message-container"
    :class="['message-' + type, { 'message-show': isShow }]"
    :style="{ top: `${topOffset}px` }"
  >
    <!-- 图标 -->
    <i class="message-icon" :class="iconClass"></i>
    <!-- 提示内容 -->
    <div class="message-content">{{ content }}</div>
    <!-- 关闭按钮（可选） -->
    <i
      v-if="showClose"
      class="message-close"
      @click="handleClose"
    >×</i>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

// 接收 props：提示类型、内容、时长、是否显示关闭按钮、关闭回调
const props = defineProps({
  type: {
    type: String,
    default: 'info', // success/warning/error/info
    validator: (val) => ['success', 'warning', 'error', 'info'].includes(val)
  },
  content: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 3000, // 自动关闭时长（ms），0 表示不自动关闭
    validator: (val) => val >= 0
  },
  showClose: {
    type: Boolean,
    default: false
  },
  onClose: {
    type: Function,
    default: () => {}
  }
});

// 响应式状态：是否显示（控制动画）、顶部偏移量（避免多个提示重叠）
const isShow = ref(false);
const topOffset = ref(20); // 默认顶部偏移 20px
let closeTimer = null;

// 根据类型匹配图标（使用 Element UI 同款图标类，需引入 Element 图标库或自定义）
const iconClass = ref('');
const iconMap = {
  success: 'el-icon-success',
  warning: 'el-icon-warning',
  error: 'el-icon-error',
  info: 'el-icon-info'
};
watch(() => props.type, (newType) => {
  iconClass.value = iconMap[newType];
}, { immediate: true });

// 关闭提示框
const handleClose = () => {
  isShow.value = false;
  // 动画结束后执行回调并清理定时器
  setTimeout(() => {
    props.onClose();
    clearTimeout(closeTimer);
  }, 300); // 匹配动画时长（300ms）
};

// 组件挂载时：显示提示框 + 启动自动关闭定时器
onMounted(() => {
  // 延迟显示（触发淡入动画）
  setTimeout(() => {
    isShow.value = true;
  }, 10);

  // 自动关闭逻辑（duration > 0 时）
  if (props.duration > 0) {
    closeTimer = setTimeout(handleClose, props.duration);
  }
});

// 组件卸载时清理定时器
onUnmounted(() => {
  clearTimeout(closeTimer);
});

// 暴露方法（供外部调用关闭）
defineExpose({
  close: handleClose
});
</script>

<style scoped>
/* 基础容器样式：固定定位 + 居中 */
.message-container {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 16px;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s, transform 0.3s, top 0.3s;
  z-index: 9999; /* 确保在最上层 */
  transform: translate(-50%, -10px); /* 初始向上偏移，触发淡入效果 */
}

/* 显示状态：淡入 + 恢复位置 */
.message-show {
  opacity: 1;
  transform: translate(-50%, 0);
}

/* 不同类型的背景色和文字色 */
.message-success {
  background-color: #f0f9eb;
  color: #67c23a;
}
.message-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}
.message-error {
  background-color: #fef0f0;
  color: #f56c6c;
}
.message-info {
  background-color: #edf2fc;
  color: #409eff;
}

/* 图标样式 */
.message-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 内容样式 */
.message-content {
  flex: 1;
  font-size: 14px;
  white-space: nowrap; /* 避免换行（如需换行可删除） */
}

/* 关闭按钮样式 */
.message-close {
  margin-left: 8px;
  font-size: 16px;
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
}
.message-close:hover {
  color: #606266;
}
</style>
