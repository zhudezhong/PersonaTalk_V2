<script setup lang="ts">
import {ref, defineProps, onMounted, toRefs, watch} from "vue";
import eventBus from '@/utils/eventBus'
import {usePromptStore} from "@/stores/promptStore.js";

interface HistoryItem {
  id: number
  listName: string
}

const props = defineProps<{
  historyList: HistoryItem[]
}>()

const {historyList} = toRefs(props)

// 给 isActivity 明确联合类型，避免类型模糊
const isActivity = ref<'createNew' | 'search'>('search')

// 初始化 activityList 为 null（明确类型）
const activityList = ref<number | null>(null)
const isShow = ref(true)

// 给 searchValue 初始化为空字符串，避免 undefined
const searchValue = ref<string>('')

const filteredHistoryList = ref<HistoryItem[]>([])

// 监听原始列表变化，同步更新筛选列表（添加 immediate 确保初始化时执行）
watch(historyList, (newList = []) => { // 给 newList 加默认空数组，避免 undefined
  filteredHistoryList.value = [...newList]
  // 无选中项且列表有数据时，自动选中第一项
  if (activityList.value === null && newList.length > 0) {
    activityList.value = newList[0].id
  }
}, {immediate: true})

// 监听搜索值变化，自动触发搜索（仅在搜索状态下）
watch(searchValue, (newVal = '') => { // 给 newVal 加默认空字符串
  if (isActivity.value === 'search') {
    handleSearch(newVal)
  }
})

onMounted(() => {
  // 初始化选中逻辑（加空数组判断）
  const initList = historyList.value || []
  if (initList.length > 0 && activityList.value === null) {
    activityList.value = initList[0].id
  }
})

// 搜索方法接收参数并加空值处理，避免依赖 ref 内部值可能的 undefined
const handleSearch = (keyword = '') => {
  const trimmedKeyword = keyword.trim().toLowerCase()
  const sourceList = historyList.value || [] // 加默认空数组
  if (trimmedKeyword) {
    filteredHistoryList.value = sourceList.filter(item =>
      // 加 item.listName 空值判断，避免 item 结构异常导致报错
      (item.session_name || '').toLowerCase().includes(trimmedKeyword)
    )
  } else {
    filteredHistoryList.value = [...sourceList]
  }
}
const promptStore = usePromptStore();

const handleCreateNewSession = () => {
  isActivity.value = 'createNew'
  promptStore.clearSessionId()
  console.log('promptStore', promptStore.sessionId)
  eventBus.emit('createNewSession')

  // 重置搜索值为明确空字符串
  searchValue.value = ''
  filteredHistoryList.value = [...(historyList.value || [])]
}


const handleChooseHistory = async (item: HistoryItem) => {
  console.log('item.id', item.id)

  await promptStore.setSessionId(item.id)
  if (item && item.id) {
    activityList.value = item.id
    //  修改store状态，打开这个对话

    eventBus.emit('openHistorySession', item)
  }
}

const handleSearchClick = () => {
  isActivity.value = 'search'
  // 延迟聚焦输入框（确保 DOM 已渲染），加存在性判断
  setTimeout(() => {
    const input = document.querySelector('.search-input') as HTMLInputElement
    if (input) input.focus()
  }, 100)
}
</script>

<template>
  <div
    style="display: flex;flex-direction: row;justify-content: space-around;margin-bottom: 20px;width: 300px;position: absolute;"
  >
    <div
      @click="isShow = !isShow"
      class="show-button"
      :class="[isShow ? 'button-show' : 'button-not-show']"
    >
      <!--      {{ isShow ? 'Show' : 'Hdn' }}-->
      <i v-if="isShow" class="iconfont icon-youhua"></i>
      <i v-else class="iconfont icon-zuohua"></i>
    </div>
  </div>

  <div
    class="history-session-main"
    :class="[isShow ? 'history-session-not-show' : 'history-session-show']"
  >
    <div class="controls-container">
      <!--      <div-->
      <!--        @click="handleCreateNewSession"-->
      <!--        class="control-button create-button"-->
      <!--        :class="{'expanded': isActivity === 'createNew'}"-->
      <!--      >-->
      <!--        &lt;!&ndash;        <span v-if="isActivity === 'createNew'">&ndash;&gt;-->
      <!--        &lt;!&ndash;          创建新对话&ndash;&gt;-->
      <!--        &lt;!&ndash;          <i class="iconfont icon-bianjixiaoxi"></i>&ndash;&gt;-->
      <!--        &lt;!&ndash;        </span>&ndash;&gt;-->
      <!--        <span>-->
      <!--          <i class="iconfont icon-bianjixiaoxi"></i>-->
      <!--        </span>-->
      <!--      </div>-->

      <div
        class="control-button search-button"
        :class="{'expanded': isActivity === 'search'}"
        @click="handleSearchClick"
      >
        <template v-if="isActivity === 'search'">
          <input
            type="text"
            v-model="searchValue"
            placeholder="输入关键词搜索..."
            class="search-input"
            @keyup.enter="handleSearch(searchValue)"
          >

          <i style="position: absolute;right: 11px;top: 2px;"
             class="iconfont icon-sousuo"></i>
        </template>
        <!--        <template>-->

        <!--        </template>-->
      </div>
    </div>

    <div class="history-content">
      <div
        class="history-list"
        v-for="list in (filteredHistoryList || [])"
        :key="list?.id"
        :class="[activityList === list?.id ? 'history-list-active' : '']"
        @click="handleChooseHistory(list)"
      >
        <span style="margin-right: 5px">
          <span>
            <i class="iconfont icon-bianjixiaoxi"></i>
          </span>
        </span>
        {{ list?.session_name || '' }}
      </div>

      <div
        v-if="(filteredHistoryList || []).length === 0 && (searchValue || '').trim()"
        style="text-align: center; padding: 20px; color: #999; font-size: 14px;"
      >
        未找到匹配的会话
      </div>

      <div
        v-if="(filteredHistoryList || []).length === 0 && !(searchValue || '').trim()"
        style="text-align: center; padding: 20px; color: #999; font-size: 14px;"
      >
        暂无会话记录
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-input {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 14px;
  padding: 0 15px;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.history-session-main {
  margin-top: 10px;
  width: 280px;
  height: 900px;
  background-color: #f3f4f6;
  border-radius: 10px;
  padding: 80px 20px 20px;
  transition: all .5s ease-in;
  position: relative;
  box-sizing: border-box;
}

.controls-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 20px;
  left: 10px;
  width: 250px;
}

.control-button {
  cursor: pointer;
  color: #ffffff;
  height: 40px;
  text-align: center;
  line-height: 40px;
  border-radius: 25px;
  background-color: #333333;
  overflow: hidden;
  margin-left: 10px;
  transition: width 0.3s ease-in-out;
  width: 40px;
  position: relative;
}

.control-button.expanded {
  width: 250px;
}

.history-content {
  height: 100%;
  overflow-y: scroll;
  padding-top: 10px;
}

.history-list {
  cursor: pointer;
  padding: 5px 10px;
  height: 30px;
  line-height: 20px;
  color: #373737;
  font-size: 14px;
  border: 1px solid #f3f4f6;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  background-color: rgba(0, 0, 0, 0.7);
  transition: all .5s ease-in;
}

.show-button:hover {
  background-color: rgb(0, 0, 0);
}

.button-show {
  position: fixed;
  top: 500px;
  transform: translateX(-160px);
}

.button-not-show {
  position: fixed;
  top: 500px;
  left: 280px;
  transition: all 1s;
}

.control-button::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 800px;
  background-color: rgba(255, 255, 255, 0.1);
  transform: rotate(-45deg);
  left: -30px;
  top: -320px;
  transition: all .8s;
}

.control-button:hover::after {
  left: 220px;
  top: -650px;
}

.history-session-not-show {
  transform: translateX(-290px);
}

.history-session-show {
  transform: translateX(0);
}

::-webkit-scrollbar {
  width: 4px;
  height: 3px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}
</style>
