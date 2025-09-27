<script setup lang="ts">
import {ref, defineProps, defineEmits, watch} from 'vue';
import CusButton from "@/components/CusButton.vue";

// 定义props：接收弹窗显示状态
const props = defineProps<{
  visible: boolean;
}>();

// 定义emits：关闭弹窗、提交prompt
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submit', prompt: string): void;
}>();

// prompt内容绑定
const prompt = ref('');

// 表单验证状态
const formError = ref(false);

// 关闭弹窗
const handleClose = () => {
  emit('close');
  // 重置表单，避免下次打开残留数据
  prompt.value = '';
  formError.value = false;
};

// 表单验证
const validateForm = (): boolean => {
  let isValid = true;
  // 验证prompt是否为空
  if (!prompt.value.trim()) {
    formError.value = true;
    isValid = false;
  } else {
    formError.value = false;
  }
  return isValid;
};

// 提交表单
const handleSubmit = () => {
  if (validateForm()) {
    emit('submit', prompt.value.trim());
    handleClose(); // 提交后关闭弹窗
  }
};

// 输入时清除错误提示
const clearError = () => {
  formError.value = false;
};
</script>

<template>
  <transition name="overlay">
    <div class="modal-overlay" v-if="visible" @click="handleClose">
      <transition name="modal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">导入 Prompt</h3>
            <button class="modal-close" @click="handleClose">✕</button>
          </div>

          <div class="modal-form">
            <!-- Prompt 输入 -->
            <div class="form-item">
              <label class="form-label">Prompt 内容 <span class="required">*</span></label>
              <textarea
                v-model="prompt"
                class="form-textarea"
                placeholder="请输入要导入的 Prompt 描述..."
                @input="clearError"
                :class="{ 'error': formError }"
                rows="8"
              ></textarea>
              <p class="error-text" v-if="formError">Prompt 内容为必填项</p>
            </div>
          </div>

          <div class="modal-footer">
            <CusButton buttonText="取消" :speed="1.2" @click="handleClose" class="cancel-btn"/>
            <CusButton buttonText="确认导入" :speed="1.2" @click="handleSubmit" class="submit-btn"/>
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<style scoped>
/* 复用原有过渡动画样式 */
.overlay-enter-from {
  opacity: 0;
}

.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-leave-to {
  opacity: 0;
}

.modal-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.98);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease,
  transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}

/* 复用原有弹窗基础样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 700px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 2px solid #333;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #f6f6f6;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
}

.modal-close:hover {
  color: #333;
}

.modal-form {
  padding: 24px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: border-color 0.3s;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #3B82F6;
}

.error {
  border-color: #ff4d4f !important;
}

.error-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #ff4d4f;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background-color: #f6f6f6;
  border-top: 1px solid #eee;
}

.cancel-btn {
  background-color: #fff !important;
  color: #333 !important;
  border: 1px solid #ddd !important;
}

.cancel-btn:hover {
  background-color: #f9f9f9 !important;
}

.submit-btn {
  background-color: #333 !important;
  color: #fff !important;
}

.submit-btn:hover {
  background-color: #555 !important;
}
</style>
