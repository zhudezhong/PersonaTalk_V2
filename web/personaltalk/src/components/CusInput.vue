<template>
  <div class="input-container">
    <input
      type="text"
      class="circle-input"
      placeholder="请输入内容..."
      @blur="handleBlur"
      ref="animatedInput"
    >
    <i class="fa fa-search input-icon"></i>
  </div>
</template>

<script>
export default {
  name: 'AnimatedCircleInput',
  props: {
    color: {
      type: String,
      default: '#3B82F6'
    },
    inputWidth: {
      type: String,
      default: '16rem'
    },
    circleSize: {
      type: String,
      default: '3rem'
    },
    placeholder: {
      type: String,
      default: '请输入内容...'
    }
  },
  methods: {
    handleBlur() {
      if (this.$refs.animatedInput.value.trim() === '') {
      }
    }
  },
  mounted() {
    const style = document.createElement('style')
    style.textContent = `
      .circle-input:focus {
        border-color: ${this.color};
      }
    `
    document.head.appendChild(style)
  }
}
</script>

<style scoped>
.input-container {
  position: relative;
}

.circle-input {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  background-color: transparent;
  padding: 0;
  color: transparent;
  outline: none;
  transition: all 0.5s ease-in-out;
}

.circle-input:focus {
  width: 16rem;
  padding: 0 1rem;
  color: #1f2937;
  border-radius: 0.5rem;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.circle-input:focus + .input-icon {
  opacity: 0;
}
</style>
