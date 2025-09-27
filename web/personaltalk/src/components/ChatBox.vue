<script setup>
import {defineProps, onMounted, onUnmounted, ref, nextTick, watch} from 'vue'
import eventBus from "@/utils/eventBus.js";
import MsgLoadingAnimation from "@/components/MsgLoadingAnimation.vue";
import Loading from "@/components/Loading.vue";
import AudioWave from "@/components/AudioWave.vue";

// 定义接收的props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  loadSession: {
    type: String,
    required: false
  }
})

const messageList = ref([])
const chatContainer = ref(null)
const showScrollButton = ref(false)
const buttonOpacity = ref(0) // 按钮透明度，用于淡入淡出效果
let scrollAnimation = null

onMounted(() => {
  if (!props.loadSession) {
    messageList.value = [{
      content: '您好，有什么可以帮助您的😊',
      isQuestion: false,
    }]
  } else {
    console.log('可以根据id从本地存储中寻找聊天数据')
  }

  // 监听滚动事件
  if (chatContainer.value) {
    chatContainer.value.addEventListener('scroll', handleScroll)
  }

  // 组件挂载时统一注册事件监听（避免分散）
  eventBus.on('question-message', handleQuestionMessage)
  eventBus.on('answer-message', handleAnswerMessage)
})

// 监听showScrollButton变化，触发淡入淡出动画
watch(showScrollButton, (newVal) => {
  if (newVal) {
    // 淡入动画
    buttonOpacity.value = 0
    const fadeIn = () => {
      buttonOpacity.value += 0.1
      if (buttonOpacity.value < 1) {
        requestAnimationFrame(fadeIn)
      } else {
        buttonOpacity.value = 1
      }
    }
    requestAnimationFrame(fadeIn)
  } else {
    // 淡出动画
    const fadeOut = () => {
      buttonOpacity.value -= 0.1
      if (buttonOpacity.value > 0) {
        requestAnimationFrame(fadeOut)
      } else {
        buttonOpacity.value = 0
      }
    }
    requestAnimationFrame(fadeOut)
  }
})

// 处理滚动事件，控制回到底部按钮的显示/隐藏
const handleScroll = () => {
  if (chatContainer.value) {
    // 当滚动距离顶部超过容器高度的一半时显示按钮
    const scrollTop = chatContainer.value.scrollTop
    const scrollHeight = chatContainer.value.scrollHeight
    const clientHeight = chatContainer.value.clientHeight

    // 避免频繁触发动画：滚动到底部200px内隐藏按钮，之外显示
    const shouldShow = scrollTop + clientHeight < scrollHeight - 200
    if (shouldShow !== showScrollButton.value) {
      showScrollButton.value = shouldShow
    }
  }
}

// 平滑滚动到聊天底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      // 取消任何正在进行的动画
      if (scrollAnimation) {
        cancelAnimationFrame(scrollAnimation)
      }

      const targetPosition = chatContainer.value.scrollHeight
      const startPosition = chatContainer.value.scrollTop
      const distance = targetPosition - startPosition
      const duration = 500 // 动画持续时间，毫秒
      const startTime = performance.now()

      // 使用requestAnimationFrame实现平滑滚动
      const animateScroll = (currentTime) => {
        const timeElapsed = currentTime - startTime
        // 使用easeOutQuad缓动函数使滚动更自然
        const progress = Math.min(timeElapsed / duration, 1)
        const easeProgress = 1 - (1 - progress) * (1 - progress)

        chatContainer.value.scrollTop = startPosition + distance * easeProgress

        if (timeElapsed < duration) {
          scrollAnimation = requestAnimationFrame(animateScroll)
        } else {
          scrollAnimation = null
        }
      }

      scrollAnimation = requestAnimationFrame(animateScroll)
    }
  })
}

const handleQuestionMessage = (args) => {
  messageList.value.push(args)
  // 新消息添加后自动滚动到底部
  scrollToBottom()
}

const handleAnswerMessage = (args) => {
  messageList.value.push(args)
  // 新消息添加后自动滚动到底部
  scrollToBottom()
}

// 组件卸载时统一清理（避免重复注册卸载逻辑）
onUnmounted(() => {
  // 移除事件总线监听
  eventBus.off('question-message', handleQuestionMessage)
  eventBus.off('answer-message', handleAnswerMessage)

  // 移除滚动事件监听
  if (chatContainer.value) {
    chatContainer.value.removeEventListener('scroll', handleScroll)
  }

  // 清除滚动动画
  if (scrollAnimation) {
    cancelAnimationFrame(scrollAnimation)
  }
})
</script>

<template>
  <Transition :duration="550" name="nested">
    <div>
      <div v-if="show" class="chat-box" ref="chatContainer">
        <div class="message-container" v-for="(msg, index) in messageList" :key="index">
          <span :class="msg.isQuestion ? 'question-class' : 'answer-class'">
            {{ msg.content }}
          </span>
        </div>
      </div>

      <!-- 回到底部按钮 - 添加了淡入淡出效果 -->
      <button
        v-if="showScrollButton || buttonOpacity > 0"
        class="scroll-to-bottom-btn"
        @click="scrollToBottom"
        :class="{ 'scrolling': scrollAnimation }"
        :style="{ opacity: buttonOpacity }"
      >
        <i class="iconfont icon-dibu"></i>
      </button>
    </div>
  </Transition>
</template>

<style>
.chat-box {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin: -250px auto;
  width: 800px;
  height: 800px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  /* 为按钮留出空间 */
  padding: 30px 30px 70px;
}

/* 回到底部按钮样式 */
.scroll-to-bottom-btn {
  position: fixed;
  bottom: 150px;
  right: 50%;
  transform: translateX(50%);
  background-color: #333333;
  color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
  border: 2px solid #aeaeae;
  /* 确保透明度变化平滑 */
  transition: opacity 0.3s ease;
}

.scroll-to-bottom-btn:hover {
  background-color: #636363;
  transform: translateX(50%) scale(1.1);
}

/* 滚动中按钮动画 */
.scroll-to-bottom-btn.scrolling {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: translateX(50%) scale(1);
  }
  50% {
    transform: translateX(50%) scale(1.1);
  }
  100% {
    transform: translateX(50%) scale(1);
  }
}

.nested-enter-active, .nested-leave-active {
  transition: all 0.3s ease-in-out;
}

/* delay leave of parent element */
.nested-leave-active {
  transition-delay: 0.25s;
}

.nested-enter-from,
.nested-leave-to {
  transform: translateY(30px);
  opacity: 0;
}

.nested-enter-active .inner,
.nested-leave-active .inner {
  transition: all 0.3s ease-in-out;
}

/* delay enter of nested element */
.nested-enter-active .inner {
  transition-delay: 0.25s;
}

.nested-enter-from .inner,
.nested-leave-to .inner {
  transform: translateX(30px);
  opacity: 0.001;
}

.message-container {
  display: flex;
  margin-bottom: 12px;
}

.question-class, .answer-class {
  padding: 8px 14px;
  border-radius: 18px;
  width: fit-content;
  max-width: 70%;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  line-height: 1.6;
}

.question-class {
  color: #ffffff;
  background-color: #3353ff;
  margin-left: auto;
  border-top-right-radius: 4px;
}

.answer-class {
  color: #333333;
  background-color: #ffffff;
  margin-right: auto;
  border-top-left-radius: 4px;
}
</style>
