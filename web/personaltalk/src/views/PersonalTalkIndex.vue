<script setup lang="ts">
import PersonalCard from "@/components/PersonalCard.vue";
import CusButton from "@/components/CusButton.vue";
import {onUnmounted, ref} from 'vue';
import ChatBox from "@/components/ChatBox.vue";
import eventBus from '@/utils/eventBus'
import HistorySession from "@/components/HistorySession.vue";

const isExpanded = ref(false);
const message = ref('');

const handleCreateNewSession = () => {
  isExpanded.value = true;
}


eventBus.on('createNewSession', handleCreateNewSession)

// 组件卸载时移除监听（避免内存泄漏）
onUnmounted(() => {
  eventBus.off('createNewSession', handleCreateNewSession)
})


// 处理发送消息
const handleSend = () => {
  if (message.value.trim()) {
    console.log('发送消息:', message.value);

    eventBus.emit('question-message', {
      content: message.value,
      isQuestion: true,
    })

    // todo:此处发送请求给后端，可考虑通过socket进行通信

    if (message.value) {
      //  模拟后端回复信息，测试前端效果
      eventBus.emit('answer-message', {
        content: '思考中...',
        isQuestion: false,
      })
    }


    message.value = '';

  }
};

// 处理键盘回车
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleSend();
  }
};
</script>

<template>
  <div class="history-session">
    <HistorySession/>

  </div>
  <div class="container">
    <template v-if="!isExpanded">
      <div class="card-list">
        <PersonalCard/>
        <PersonalCard/>
        <PersonalCard/>
      </div>
      <div class="footer-button">
        <CusButton buttonText="自定义角色" :speed="1.5"/>
        <CusButton buttonText="文本聊天" :speed="1.5"/>
      </div>
    </template>
    <template v-else>
      <ChatBox :show="isExpanded"/>
    </template>

    <div
      class="message-talk"
      :class="{ 'expanded': isExpanded }"
      @click.stop
    >
      <div class="message-circle" @click="isExpanded = !isExpanded">
        <span v-if="!isExpanded">icon</span>
        <span v-if="isExpanded">✕</span>
      </div>

      <div class="input-container" v-if="isExpanded">
        <input
          type="text"
          v-model="message"
          placeholder="输入消息..."
          @keydown="handleKeyDown"
          ref="messageInput"
          @click.stop
        >
        <button class="send-btn" @click="handleSend">发送</button>
      </div>
    </div>

  </div>

</template>

<style scoped>

.history-session {
  position: fixed;
  left: 20px;
  top: 50px;
}

.container {
  margin: 300px auto;
  width: 650px;
  position: relative;
}

.card-list {
  width: 100%;
  display: flex;
  height: 80%;
  justify-content: space-around;
  align-items: center;
}

.footer-button {
  margin-top: 50px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.message-talk {
  width: 40px;
  cursor: pointer;
  color: #333;
  position: fixed;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  transition: all .5s ease;
  padding: 3px;
  border-radius: 30px;
  border: 2px solid #ffffff;
  box-sizing: content-box;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: transparent;
}

.message-talk.expanded {
  width: 700px;
  background-color: #f6f6f6;
  border: 2px solid #555555;
  padding: 8px 10px;
  overflow: hidden;
}

.message-circle {
  border-radius: 50%;
  width: 40px;
  height: 40px;
  text-align: center;
  line-height: 40px;
  background-color: #333333;
  transition: all .5s;
  color: white;
  flex-shrink: 0;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  opacity: 0;
  height: 40px;
  transform: translateX(-20px);
  transition: all .3s ease;
  overflow: hidden;
  padding-left: 5px;
}

.message-talk.expanded .input-container {
  opacity: 1;
  transform: translateX(0);
}

.input-container input {
  flex-grow: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
}

.input-container input:focus {
  border-color: #3B82F6;
}

.send-btn {
  padding: 8px 18px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color .3s;
}

.send-btn:hover {
  background-color: #555;
}
</style>
