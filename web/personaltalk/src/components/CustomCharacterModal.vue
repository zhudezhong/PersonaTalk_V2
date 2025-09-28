<script setup lang="ts">
import {ref, defineProps, defineEmits, watch} from 'vue';
import CusButton from "@/components/CusButton.vue";
import router from '@/router';

// 定义props：接收弹窗显示状态、预填数据和音色选项（包含音频地址）
const props = defineProps<{
  visible: boolean;
  prefillData?: {
    name: string;
    source: string;
    personality: string;
    languageStyle: string;
    background: string;
    voiceType: string; // 预填音色字段
  };
  voiceOptions: {
    voice_name: string;
    voice_type: string;
    audio_url: string; // 新增：音频播放地址
  }[];
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
    voiceType: string; // 提交音色字段
  }): void;
}>();

// 表单数据绑定
const form = ref({
  name: '',
  source: '',
  personality: '',
  languageStyle: '',
  background: '',
  voiceType: '', // 音色字段
});

// 播放状态管理（记录当前正在播放的音频索引）
const playingIndex = ref<number | null>(null);
const audioRefs = ref<HTMLAudioElement[]>([]); // 音频元素引用

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
  // 停止所有音频播放
  stopAllAudio();
  // 重置表单
  form.value = {
    name: '',
    source: '',
    personality: '',
    languageStyle: '',
    background: '',
    voiceType: ''
  };
  formErrors.value = {name: false, personality: false, background: false};
  playingIndex.value = null;
};

// 音频播放控制
const playAudio = (index: number, url: string) => {
  // 停止当前正在播放的音频
  if (playingIndex.value !== null && playingIndex.value !== index) {
    stopAudio(playingIndex.value);
  }

  // 创建或获取音频元素
  if (!audioRefs.value[index]) {
    audioRefs.value[index] = new Audio(url);
    // 音频结束时更新状态
    audioRefs.value[index].onended = () => {
      if (playingIndex.value === index) {
        playingIndex.value = null;
      }
    };
  }

  const audio = audioRefs.value[index];
  if (playingIndex.value === index) {
    // 暂停当前播放
    audio.pause();
    playingIndex.value = null;
  } else {
    // 播放新音频
    audio.src = url;
    console.log(audio.src)
    audio.play().catch(error => {
      console.error('音频播放失败:', error);
      playingIndex.value = null;
    });
    playingIndex.value = index;
  }
};

// 停止指定索引的音频
const stopAudio = (index: number) => {
  if (audioRefs.value[index]) {
    audioRefs.value[index].pause();
  }
};

// 停止所有音频
const stopAllAudio = () => {
  audioRefs.value.forEach(audio => {
    if (audio) audio.pause();
  });
  playingIndex.value = null;
};

// 表单验证
const validateForm = (): boolean => {
  let isValid = true;
  // 验证必填项
  if (!form.value.name.trim()) {
    formErrors.value.name = true;
    isValid = false;
  } else {
    formErrors.value.name = false;
  }

  if (!form.value.personality.trim()) {
    formErrors.value.personality = true;
    isValid = false;
  } else {
    formErrors.value.personality = false;
  }

  if (!form.value.background.trim()) {
    formErrors.value.background = true;
    isValid = false;
  } else {
    formErrors.value.background = false;
  }

  return isValid;
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

// 组件卸载时清理音频
const cleanupAudio = () => {
  stopAllAudio();
  audioRefs.value = [];
};

// 监听组件卸载
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    cleanupAudio();
  }
});
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
            <!-- 角色名称和音色下拉框 -->
            <div class="form-item name-voice-wrapper">
              <div class="name-column">
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
              <div class="voice-column">
                <label class="form-label">选择音色</label>
                <div class="voice-selector">
                  <select
                    v-model="form.voiceType"
                    class="form-select"
                  >
                    <option value="">请选择音色</option>
                    <option
                      v-for="(item, index) in props.voiceOptions"
                      :key="item.voice_type"
                      :value="item.voice_type"
                    >
                      {{ item.voice_name }}
                    </option>
                  </select>

<!--                  &lt;!&ndash; 音色试听列表 &ndash;&gt;-->
<!--                  <div class="voice-preview-list">-->
<!--                    <div-->
<!--                      v-for="(item, index) in props.voiceOptions"-->
<!--                      :key="item.voice_type"-->
<!--                      class="voice-preview-item"-->
<!--                    >-->
<!--                      <span class="voice-name">{{ item.voice_name }}</span>-->
<!--                      <button-->
<!--                        class="play-btn"-->
<!--                        @click="playAudio(index, item.url)"-->
<!--                        :class="{ 'playing': playingIndex === index }"-->
<!--                        aria-label="播放音频"-->
<!--                      >-->
<!--                        <i class="icon">-->
<!--                          {{ playingIndex === index ? '⏸' : '▶' }}-->
<!--                        </i>-->
<!--                      </button>-->
<!--                    </div>-->
<!--                  </div>-->
                </div>
              </div>
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
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
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

/* 角色名称和音色布局 */
.name-voice-wrapper {
  display: flex;
  gap: 20px;
}

.name-column,
.voice-column {
  flex: 1;
}

/* 下拉框样式 */
.form-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23666' d='M6 8L0 0h12L6 8z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 12px 8px;
  padding-right: 32px;
  margin-bottom: 12px;
}

.form-select option {
  padding: 10px;
  background-color: #fff;
}

/* 音频播放列表样式 */
.voice-selector {
  display: flex;
  flex-direction: column;
}

.voice-preview-list {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 8px;
  max-height: 150px;
  overflow-y: auto;
  background-color: #fafafa;
}

.voice-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  margin-bottom: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.voice-preview-item:hover {
  background-color: #f0f7ff;
}

.voice-name {
  font-size: 13px;
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.play-btn {
  background-color: transparent;
  border: 1px solid #3B82F6;
  color: #3B82F6;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
  transition: all 0.2s;
}

.play-btn.playing {
  background-color: #3B82F6;
  color: white;
}

.play-btn:hover {
  background-color: #f0f7ff;
}

.play-btn.playing:hover {
  background-color: #2563eb;
}
</style>
