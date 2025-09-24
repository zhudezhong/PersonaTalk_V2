<script setup lang="ts">
import {ref, defineProps, onMounted, toRefs} from "vue";
import eventBus from '@/utils/eventBus'

interface HistoryItem {
  Id: number
  listName: string
}

const props = defineProps<{
  historyList: HistoryItem[]
}>()

const {historyList} = toRefs(props)

const activityList = ref(null)
const isShow = ref(false)

onMounted(() => {
  activityList.value = historyList[0]?.Id
  console.log(historyList)
})

const handleCreateNewSession = () => {
  eventBus.emit('createNewSession')
}

const handleChooseHistory = (item: HistoryItem) => {
  activityList.value = item.Id
  console.log(item)

  eventBus.emit('openHistorySession', item)

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

    <div class="history-list" v-for="list in historyList" :key="list.Id"
         :class="[activityList === list.Id?'history-list-active':'history-list']"
         @click="handleChooseHistory(list)">
      <span style="margin-right: 5px">@</span>
      {{ list.listName }}
    </div>
  </div>
</template>

<style scoped>
.history-session-main {
  width: 250px;
  box-sizing: content-box;
  height: 850px;
  background-color: #f3f4f6;
  border-radius: 10px;
  padding: 80px 20px 20px;
  transition: all .5s;
}

.history-list {
  z-index: 999;
  cursor: pointer;
  padding: 5px 10px;
  height: 20px;
  line-height: 20px;
  color: #373737;
  font-size: 14px;
  box-sizing: content-box;
  border: 1px solid #f3f4f6;
}

.history-list:hover {
  background-color: #e9eaec;
  border-radius: 10px;
}


.history-list-active {
  background-color: #ffffff;
  border: 1px solid #d1d1d1;
  box-shadow: inset 0 0 1px #d1d1d1;
  border-radius: 10px;
}

.history-list-active:hover {
  background-color: #ffffff !important;

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
  transform: translateX(-130px);
}

.button-not-show {
  position: fixed;
  top: 70px;
  left: 250px;
  transition: all 1s;
}

.create-new {
  cursor: pointer;
  color: #ffffff;
  width: 200px;
  height: 40px;
  text-align: center;
  line-height: 40px;
  border-radius: 25px;
  background-color: #333333;
  overflow: hidden;
  position: absolute;
  top: 20px;
}

.create-new::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 800px;
  background-color: #a8a8a8;
  transform: rotate(-45deg);
  left: 20px;
  top: -320px;
  transition: all .3s;
}

.create-new:hover::after {
  top: -650px;
  left: 10px;
}

.history-session-not-show {
  transform: translateX(-300px);
}

.history-session-show {
  transform: translateX(0);
}
</style>
