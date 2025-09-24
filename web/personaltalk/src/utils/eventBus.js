import mitt from 'mitt'

// 创建事件总线实例
const eventBus = mitt()

export default {
  on: (eventName, callback) => eventBus.on(eventName, callback),
  emit: (eventName, data) => eventBus.emit(eventName, data),
  off: (eventName, callback) => eventBus.off(eventName, callback),
  clear: () => eventBus.all.clear()
}
