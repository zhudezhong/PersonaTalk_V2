<script setup lang="ts">
import {ref} from "vue";
import eventBus from '@/utils/eventBus'

const isShow = ref(false)

const handleCreateNewSession = () => {
  eventBus.emit('createNewSession')
}

</script>

<template>
  <div
    style="display: flex;flex-direction: row;justify-content: space-around;margin-bottom: 20px;width: 300px;position: absolute;">
    <div @click="isShow = !isShow" class="show-button"
         :class="[isShow?'button-show':'button-not-show']">{{ isShow ? 'Show' : 'Hdn' }}
    </div>
  </div>
  <div class="history-session-main"
       :class="[isShow?'history-session-not-show':'history-session-show']"

  >
    <div class="create-new" @click="handleCreateNewSession">创建新对话</div>

  </div>
</template>

<style scoped>
.history-session-main {
  padding: 20px;
  width: 280px;
  box-sizing: content-box;
  height: 900px;
  background-color: #fff;
  border-radius: 10px;
  transition: all .5s;
}

.show-button {
  z-index: 9;
  cursor: pointer;
  color: #ffffff;
  width: 40px;
  height: 40px;
  text-align: center;
  line-height: 40px;
  border-radius: 50%;
  background-color: #333333;
  transition: all 1s;
}

.button-show {
  position: fixed;
  top: 70px;
  transform: translateX(-100px);
}

.button-not-show {
  position: fixed;
  top: 70px;
  left: 280px;
  transition: all 1s;
}

.create-new {
  cursor: pointer;
  color: #ffffff;
  width: 230px;
  height: 40px;
  text-align: center;
  line-height: 40px;
  border-radius: 25px;
  background-color: #333333;
}

.history-session-not-show {
  transform: translateX(-330px);
}

.history-session-show {
  transform: translateX(0);
}
</style>
