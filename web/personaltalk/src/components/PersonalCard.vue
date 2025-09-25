<script setup lang="ts">
import router from '@/router';


const beginSpokenDialogue = () => {
  router.push({path: '/SpokenDialogue'});
}
</script>

<template>
  <div class="info-main" @click="beginSpokenDialogue">
    <div class="character-image">

    </div>
    <span class="character-name">
      Harry Potter
    </span>
    <span class="character-desc">
        在霍格沃茨魔法学校成长、凭勇气与智慧对抗伏地伏地魔、守护魔法世界的传奇巫师。
    </span>

    <div class="begin-talk">开始对话</div>
  </div>
</template>

<style scoped>
.info-main {
  cursor: pointer;
  width: 200px;
  height: 250px;
  border: 1px solid #d5d5d5;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

/* 径向渐变遮罩层 - 作为单独的遮罩元素 */
.info-main::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  /* 径向渐变：中心透明向边缘过渡到深色 */
  background: radial-gradient(
    circle at center,
    rgba(0, 0, 0, 0.1) 20%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.7) 100%
  );
}

.character-image {
  width: 100%;
  height: 100%;
  background-color: #e8e8e8;
  background-image: url('https://picsum.photos/300/400');
  background-size: cover;
  background-position: center;
  transition: all .3s;
  transform: scale(1.05);
}

.info-main:hover .character-image {
  transform: scale(1.00);
}

.character-name {
  position: absolute;
  top: 50px;
  left: 0;
  width: 100%;
  text-align: center;
  color: #fff;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  z-index: 2;
  padding: 0 8px;
  box-sizing: border-box;
  transition: all .5s;
}

.character-desc {
  z-index: 99;
  display: flex;
  margin: 10px;
  position: absolute;
  top: 80px;
  left: 0;
  color: #fff;
  padding: 5px;
  opacity: 0;
  font-size: 12px;
  transition: all 1s;
}

.info-main:hover .character-desc {
  opacity: 1;
}

.info-main::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 40%;
  z-index: 1;
}

.begin-talk {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 99;
  font-size: 14px;
  text-align: center;
  line-height: 30px;
  transition: all .5s;
  width: 100px;
  height: 30px;
  border-radius: 15px;
  border: 1px solid #ffffff;
  color: #fff;
  overflow: hidden;
  opacity: 0;
}

.begin-talk::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 500px;
  background-color: #bababa;
  transform: rotate(-45deg);
  left: 20px;
  top: -180px;
  transition: all .5s;
}

.begin-talk:hover::after {
  top: -350px;
  left: 10px;
}

.info-main:hover .begin-talk {
  opacity: 1;
}
</style>
