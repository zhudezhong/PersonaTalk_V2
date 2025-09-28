// src/components/Message/messagePlugin.js
import { createVNode, render, App } from 'vue';
import Message from './Message.vue';

// 存储所有提示框实例（用于计算顶部偏移，避免重叠）
let messageInstances = [];
// 基础顶部偏移（可自定义）
const BASE_TOP_OFFSET = 20;
// 提示框之间的间距
const INSTANCE_GAP = 16;

// 计算新提示框的顶部偏移（根据已存在的实例数量）
const calculateTopOffset = () => {
  return BASE_TOP_OFFSET + messageInstances.reduce((total, instance) => {
    // 获取实例的 DOM 高度（需等待 DOM 渲染完成）
    const domHeight = instance.vm.el.offsetHeight || 40; // 默认高度 40px
    return total + domHeight + INSTANCE_GAP;
  }, 0);
};

// 移除实例并重新计算其他实例的偏移
const removeInstance = (instance) => {
  const index = messageInstances.findIndex(item => item.id === instance.id);
  if (index !== -1) {
    messageInstances.splice(index, 1);
    // 重新计算剩余实例的顶部偏移
    messageInstances.forEach((item, i) => {
      item.vm.topOffset = calculateTopOffset(i);
    });
  }
};

// 核心提示方法（支持链式调用，如 $message.success().close()）
const message = (options = {}) => {
  // 处理简化调用（如 $message('内容') 或 $message.success('内容')）
  if (typeof options === 'string') {
    options = { content: options };
  }

  // 生成唯一 ID（避免实例冲突）
  const instanceId = Date.now() + Math.random().toString(36).substr(2, 9);

  // 1. 创建虚拟节点（VNode）
  const vnode = createVNode(Message, {
    ...options,
    // 关闭回调：移除实例 + 销毁 DOM
    onClose: () => {
      // 从 DOM 中移除
      render(null, container);
      // 从实例列表中移除
      removeInstance(instance);
      // 执行用户自定义的关闭回调
      options.onClose?.();
    },
    // 顶部偏移（初始计算）
    topOffset: calculateTopOffset()
  });

  // 2. 创建容器（动态插入到 body 中）
  const container = document.createElement('div');
  document.body.appendChild(container);

  // 3. 渲染虚拟节点到容器
  render(vnode, container);

  // 4. 存储实例（用于后续计算偏移和管理）
  const instance = {
    id: instanceId,
    vm: vnode,
    // 暴露关闭方法（支持链式调用）
    close: () => {
      vnode.component.exposed.close();
    }
  };
  messageInstances.push(instance);

  // 返回实例（支持链式调用，如 const msg = $message('内容'); msg.close();）
  return instance;
};

// 扩展提示类型方法（success/warning/error/info）
['success', 'warning', 'error', 'info'].forEach(type => {
  message[type] = (options) => {
    // 处理简化调用（如 $message.success('内容')）
    if (typeof options === 'string') {
      options = { content: options, type };
    } else {
      options = { ...options, type };
    }
    return message(options);
  };
});

// 关闭所有提示框（可选）
message.closeAll = () => {
  messageInstances.forEach(instance => {
    instance.close();
  });
  messageInstances = [];
};

// 插件注册函数（Vue 3 插件格式）
const messagePlugin = {
  install(app) {
    // 1. 挂载到全局属性：组件内可通过 this.$message 调用
    app.config.globalProperties.$message = message;
    // 2. 提供给 Composition API：通过 inject('$message') 调用
    app.provide('$message', message);
  }
};

// 导出插件和单独的 message 方法（支持在非组件环境调用）
export { messagePlugin, message };
