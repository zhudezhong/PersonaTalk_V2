<template>
  <div style="position: relative;width: 100%;height: 100%;overflow: hidden">
    <router-view/>
  </div>
</template>

<script>
export default {
  data() {
    return {
      timer: null,
      hue: 120, // 初始色相
      hueIncrement: 2.0 // 更小的色相增量，变化更平缓
    };
  },
  methods: {
    // 更新颜色（调淡处理）
    updateColors() {
      this.hue = (this.hue + this.hueIncrement) % 360;


      const primary = '#fcf0ff';

      const secondary = 'hsl(294,100%,92%)';
      const edge = '#f8ccfb';

      document.body.style.setProperty('--color1', primary);
      document.body.style.setProperty('--color2', secondary);
      document.body.style.setProperty('--color3', edge);
    }
  },
  mounted() {
    document.body.style.cssText = `
      margin: 0;
      padding: 0;
      min-height: 100vh;
      /* 径向渐变 - 从中心扩散 */
      background: radial-gradient(
        circle at center,
        var(--color1),
        var(--color2) 40%,
        var(--color3) 80%
      );
      background-size: 120% 120%;
      transition: background 1.5s cubic-bezier(0.4, 0, 0.2, 1); /* 更长的过渡时间 */
    `;

    this.updateColors();

    const keyframes = [
      {backgroundPosition: '30% 30%', backgroundSize: '100% 100%'},
      {backgroundPosition: '45% 45%', backgroundSize: '120% 120%'},
      {backgroundPosition: '55% 55%', backgroundSize: '140% 140%'},
      {backgroundPosition: '50% 50%', backgroundSize: '100% 100%'}
    ];

    const options = {
      duration: 2000,
      iterations: Infinity,
      easing: 'ease-in-out'
    };

    document.body.animate(keyframes, options);

    this.timer = setInterval(() => this.updateColors(), 2000);
  },
  beforeUnmount() {
    clearInterval(this.timer);
  }
};
</script>

<style scoped>

</style>
