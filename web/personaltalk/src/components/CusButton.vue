<template>
  <button
    class="light-flow-button"
    :class="{ 'active': isActive }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @click="handleClick"
  >
    <span class="button-content">
      <slot>{{ buttonText }}</slot>
    </span>
    <span class="light-flow"></span>
  </button>
</template>

<script>
export default {
  name: 'CusButton',
  props: {
    buttonText: {
      type: String,
      default: 'Click Me'
    },
    color: {
      type: String,
      default: '#42b983' // 默认Vue绿色
    },
    speed: {
      type: Number,
      default: 2 // 流动速度，秒
    }
  },
  data() {
    return {
      isActive: false,
      animationTimer: null
    }
  },
  methods: {
    handleMouseEnter() {
      this.isActive = true;
      this.startAnimation();
    },
    handleMouseLeave() {
      this.isActive = false;
      this.clearAnimation();
    },
    handleClick() {
      this.$emit('click');
      // 点击时强制触发一次动画
      this.isActive = false;
      this.$nextTick(() => {
        this.isActive = true;
        this.startAnimation();
      });
    },
    startAnimation() {
      this.clearAnimation();
      // 设置周期性动画
      this.animationTimer = setInterval(() => {
        this.isActive = false;
        this.$nextTick(() => {
          this.isActive = true;
        });
      }, this.speed * 1000);
    },
    clearAnimation() {
      if (this.animationTimer) {
        clearInterval(this.animationTimer);
        this.animationTimer = null;
      }
    }
  },
  beforeDestroy() {
    this.clearAnimation();
  },
  computed: {
    lightFlowStyle() {
      return {
        backgroundColor: this.color,
        animationDuration: `${this.speed}s`
      };
    }
  }
};
</script>

<style scoped>
.light-flow-button {
  position: relative;
  overflow: hidden;
  font-size: 16px;
  padding: 10px 25px;
  font-weight: 600;
  color: white;
  background-color: #333;
  border-radius: 35px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #ffffff;
}

.light-flow-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.light-flow-button .button-content {
  position: relative;
  z-index: 2;
}

.light-flow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  transform: skewX(-25deg);
  transition: all 0.5s ease;
  opacity: 0.6;
  z-index: 1;
}

</style>
