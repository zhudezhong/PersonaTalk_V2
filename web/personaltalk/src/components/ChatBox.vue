<script setup>
import {defineProps, onUnmounted, ref} from 'vue'
import eventBus from "@/utils/eventBus.js";

// 定义接收的props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

const messageList = ref([{
  content: '您好，有什么可以帮助您的😊',
  isQuestion: false,
}])

const handleQuestionMessage = (args) => {
  messageList.value.push(args)
  console.log('messageList.value', messageList.value)
}

const handleAnswerMessage = (args) => {
  messageList.value.push(args)
  console.log('messageList.value', messageList.value)
}


// 组件挂载时监听事件
eventBus.on('question-message', handleQuestionMessage)

// 组件卸载时移除监听（避免内存泄漏）
onUnmounted(() => {
  eventBus.off('question-message', handleQuestionMessage)
})


// 组件挂载时监听事件
eventBus.on('answer-message', handleAnswerMessage)

// 组件卸载时移除监听（避免内存泄漏）
onUnmounted(() => {
  eventBus.off('answer-message', handleAnswerMessage)
})


</script>

<template>
  <Transition :duration="550" name="nested">
    <div v-if="show" class="chat-box">
      <div class="message-container" v-for="(msg, index) in messageList" :key="index">
        <span :class="msg.isQuestion ? 'question-class' : 'answer-class'">
          {{ msg.content }}
        </span>
      </div>
    </div>
  </Transition>
</template>

<style>
.chat-box, .inner {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin: -250px auto;
  width: 800px;
  height: 950px;
  padding: 30px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
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

