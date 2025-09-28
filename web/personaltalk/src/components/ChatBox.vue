<script setup>
import {defineProps, onMounted, onUnmounted, ref, nextTick, watch} from 'vue'
import eventBus from "@/utils/eventBus.js";
import MsgLoadingAnimation from "@/components/MsgLoadingAnimation.vue";
import Loading from "@/components/Loading.vue";
import AudioWave from "@/components/AudioWave.vue";
import {usePromptStore} from "@/stores/promptStore.js";

// 定义接收的props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  loadSession: {
    type: String,
    required: false
  },
  messageList: {
    type: Array,
    default: () => [] // 确保默认值为数组
  }
})

// 核心修改：定义内部响应式数组，用于追踪消息列表变化
let innerMessageList = ref([])
if (props.messageList?.length > 0) {
  innerMessageList = ref([...props.messageList])
} else {
  innerMessageList = ref([])
}

const chatContainer = ref(null)
const showScrollButton = ref(false)
const buttonOpacity = ref(0) // 按钮透明度，用于淡入淡出效果
let scrollAnimation = null

const promptStore = usePromptStore()

// 监听props中的messageList变化，同步到内部数组
watch(
  () => props.messageList,
  (newVal) => {
    console.log(typeof newVal)
    if (Array.isArray(newVal)) {
      innerMessageList.value = [...newVal] // 深拷贝确保响应式更新
    }
  },
  {immediate: true, deep: true} // 立即执行+深度监听（处理嵌套对象）
)

onMounted(() => {
  if (!props.loadSession) {
    // 初始化数据时修改内部数组（而非直接修改props）
    innerMessageList.value = promptStore.historyFormSession?.length
      ? promptStore.historyFormSession
      : []
    console.log('初始化消息列表:', innerMessageList.value)
  } else {
    console.log('可以根据id从本地存储中寻找聊天数据')
  }

  // 监听滚动事件
  if (chatContainer.value) {
    chatContainer.value.addEventListener('scroll', handleScroll)
  }

  // 注册事件监听
  eventBus.on('question-message', handleQuestionMessage)
  eventBus.on('answer-message', handleAnswerMessage)

  // 初始滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
})

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
        const progress = Math.min(timeElapsed / duration, 1)
        const easeProgress = 1 - (1 - progress) * (1 - progress) // 缓动函数

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
watch(
  () => promptStore.historyFormSession,
  (newMessageList) => {
    if (newMessageList && newMessageList.length) {
      innerMessageList.value = [...newMessageList]; // 同步到内部数组
      scrollToBottom(); // 滚动到底部，显示最新消息
    }
  },
  {immediate: true, deep: true} // immediate：初始化时执行；deep：监听数组内部变化
);

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
    const scrollTop = chatContainer.value.scrollTop
    const scrollHeight = chatContainer.value.scrollHeight
    const clientHeight = chatContainer.value.clientHeight

    // 滚动到底部200px内隐藏按钮，之外显示
    const shouldShow = scrollTop + clientHeight < scrollHeight - 200
    if (shouldShow !== showScrollButton.value) {
      showScrollButton.value = shouldShow
    }
  }
}


// 处理新问题消息（修改内部数组）
const handleQuestionMessage = (args) => {
  console.log('收到问题消息:', args)
  innerMessageList.value.push(args)
  scrollToBottom()
}

// 处理新回答消息（修改内部数组）
const handleAnswerMessage = (args) => {
  console.log('收到回答消息:', args)
  innerMessageList.value.push(args)
  scrollToBottom()
}

// 组件卸载时清理
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
        <div
          class="message-container"
          v-for="(msg, index) in innerMessageList"
          :key="index"
        >
        <span
          v-show="msg.content.trim()"
          :class="msg.role !== 'system' ? 'question-class' : 'answer-class'"
        >
            {{ msg.content }}
          </span>
        </div>
      </div>

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
  transition: opacity 0.3s ease;
}

.scroll-to-bottom-btn:hover {
  background-color: #636363;
  transform: translateX(50%) scale(1.1);
}

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
  overflow: hidden;
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
