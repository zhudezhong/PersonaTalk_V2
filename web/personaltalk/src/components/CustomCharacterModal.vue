<script setup lang="ts">
import {ref, defineProps, defineEmits, watch} from 'vue';
import CusButton from "@/components/CusButton.vue";
import router from '@/router';

// 定义props：接收弹窗显示状态和预填数据
const props = defineProps<{
  visible: boolean;
  prefillData?: {
    name: string;
    source: string;
    personality: string;
    languageStyle: string;
    background: string;
  };
}>();

// 定义emits：关闭弹窗、提交角色信息
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submit', data: {
    name: string;
    source: string;
    personality: string;
    languageStyle: string;
    background: string;
  }): void;
}>();

// 表单数据绑定
const form = ref({
  name: '',
  source: '',
  personality: '',
  languageStyle: '',
  background: '',
});

// 表单验证状态
const formErrors = ref({
  name: false,
  personality: false,
  background: false
});

// 监听props变化，预填数据
watch(() => props.prefillData, (newVal) => {
  if (newVal) {
    form.value = {...newVal};
  }
}, {immediate: true});

// 关闭弹窗
const handleClose = () => {
  emit('close');
  // 重置表单，避免下次打开残留数据
  form.value = {name: '', source: '', personality: '', languageStyle: '', background: ''};
  formErrors.value = {name: false, personality: false, background: false};
};

// 表单验证
const validateForm = (): boolean => {
  let isvalid = true;
  // 验证必填项
  if (!form.value.name.trim()) {
    formErrors.value.name = true;
    isvalid = false;
  } else {
    formErrors.value.name = false;
  }

  if (!form.value.personality.trim()) {
    formErrors.value.personality = true;
    isvalid = false;
  } else {
    formErrors.value.personality = false;
  }

  if (!form.value.background.trim()) {
    formErrors.value.background = true;
    isvalid = false;
  } else {
    formErrors.value.background = false;
  }

  return isvalid;
};

// 提交表单
const handleSubmit = () => {
  if (validateForm()) {
    emit('submit', {...form.value});
    handleClose(); // 提交后关闭弹窗

    router.push({path: '/SpokenDialogue'});
  }
};

// 输入时清除对应错误提示
const clearError = (field: keyof typeof formErrors.value) => {
  formErrors.value[field] = false;
};
</script>

<template>
  <transition name="overlay">
    <div class="modal-overlay" v-if="visible" @click="handleClose">
      <transition name="modal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">自定义角色</h3>
            <button class="modal-close" @click="handleClose">✕</button>
          </div>

          <div class="modal-form">
            <!-- 角色名称 -->
            <div class="form-item">
              <label class="form-label">角色名称 <span class="required">*</span></label>
              <input
                type="text"
                v-model="form.name"
                class="form-input"
                placeholder="输入角色名称（如：孙悟空）"
                @input="clearError('name')"
                :class="{ 'error': formErrors.name }"
              >
              <p class="error-text" v-if="formErrors.name">角色名称为必填项</p>
            </div>

            <!-- 角色来源 -->
            <div class="form-item">
              <label class="form-label">角色来源</label>
              <input
                type="text"
                v-model="form.source"
                class="form-input"
                placeholder="输入角色出处（如：《西游记》小说）"
              >
            </div>

            <!-- 角色性格 -->
            <div class="form-item">
              <label class="form-label">性格特点 <span class="required">*</span></label>
              <textarea
                v-model="form.personality"
                class="form-textarea"
                placeholder="描述角色的性格（如：勇敢、机智、嫉恶如仇）"
                @input="clearError('personality')"
                :class="{ 'error': formErrors.personality }"
                rows="3"
              ></textarea>
              <p class="error-text" v-if="formErrors.personality">性格特点为必填项</p>
            </div>

            <!-- 语言风格 -->
            <div class="form-item">
              <label class="form-label">语言风格</label>
              <textarea
                v-model="form.languageStyle"
                class="form-textarea"
                placeholder="描述角色的说话风格（如：口语化、文言文、幽默风趣）"
                rows="3"
              ></textarea>
            </div>

            <!-- 角色背景 -->
            <div class="form-item">
              <label class="form-label">角色背景 <span class="required">*</span></label>
              <textarea
                v-model="form.background"
                class="form-textarea"
                placeholder="描述角色的背景故事（如：来自花果山，拜菩提祖师学艺）"
                @input="clearError('background')"
                :class="{ 'error': formErrors.background }"
                rows="4"
              ></textarea>
              <p class="error-text" v-if="formErrors.background">角色背景为必填项</p>
            </div>
          </div>

          <div class="modal-footer">
            <CusButton buttonText="取消" :speed="1.2" @click="handleClose" class="cancel-btn"/>
            <CusButton buttonText="确认创建" :speed="1.2" @click="handleSubmit" class="submit-btn"/>
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>


<style scoped>
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

/* 基础样式保持不变 */
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

/* 其他原有样式保持不变 */
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

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3B82F6;
}

.form-textarea {
  resize: vertical;
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
