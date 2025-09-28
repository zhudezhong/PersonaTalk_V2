<script setup lang="ts">
import PersonalCard from "@/components/PersonalCard.vue";
import CusButton from "@/components/CusButton.vue";
import {getCurrentInstance, onMounted, onUnmounted, ref} from 'vue';
import ChatBox from "@/components/ChatBox.vue";
import eventBus from '@/utils/eventBus'
import HistorySession from "@/components/HistorySession.vue";
import CustomCharacterModal from "@/components/CustomCharacterModal.vue";
import PromptImport from "@/components/PromptImport.vue";
import {usePromptStore} from '@/stores/promptStore';
import {
  getHistorySessionList,
  getHistoryFromSession,
  getVoiceList,
  sendChatRequest
} from '@/api/chatapi'

const promptStore = usePromptStore();

// 获取全局实例代理（在setup顶层获取）
const instance = getCurrentInstance();
const globalProperties = instance?.appContext.config.globalProperties;

const isModalVisible = ref(false);

// 打开自定义角色弹窗
const handleOpenCustomModal = () => {
  isModalVisible.value = true;
};

// 提交自定义自定义角色（对接后端）
const handleCustomCharacterSubmit = (characterData: any) => {
  console.log('自定义角色数据：', characterData);
  //  todo:自定义角色的 prompt 发送给后端，加上等待动画
  eventBus.emit('updateCharacterPrompt', characterData)
};


const isExpanded = ref(false);
const message = ref('');
const historyList = ref<Array<{ listName: string; id: number }>>([]);

const handleCreateNewSession = async (): Promise<void> => {
  promptStore.clearSessionId()
  promptStore.clearHistoryFormSession()
  promptStore.systemPrompt = ''


  isExpanded.value = true;
}

const sessionId = ref<number | null>(null);
const chatBoxRef = ref(null);
// 主组件中，修改 openHistorySession 方法
const openHistorySession = async (item: { Id: number }) => {
  //  基础逻辑：展开ChatBox、记录当前会话ID
  isExpanded.value = true;
  sessionId.value = item.Id;

  //  关键新增：调用接口拉取该会话的历史消息
  try {
    const response = await getHistoryFromSession(item.Id); // 后端接口：根据会话ID查消息
    if (response.code === 200) {
      //  同步消息到Store：更新 historyFormSession
      promptStore.setHistoryFromSession(response.data); // 假设response.data是消息数组
      console.log('拉取到的历史消息：', response.data);
    }
  } catch (error) {
    console.error('拉取历史消息失败：', error);
  }

  // 4. 强制刷新ChatBox（可选，确保DOM更新）
  if (chatBoxRef.value) {
    chatBoxRef.value.$forceUpdate();
  }
};

const updateCharacterPrompt = (name: any | object, isImport: boolean = false) => {
  if (isImport) {
    //  json格式，prompt导入过来的
    console.log('prompt导入过来的,需要进行json解析并存储', name)
    promptStore.setSharedPrompt(JSON.parse(name));
    if (globalProperties && typeof globalProperties.$setSystemPrompt === 'function') {
      globalProperties.$setSystemPrompt(promptStore.sharedPrompt);
    }
    return;
  }
  if (typeof name === "string") {
    //  这种情况是从主页的三个预定义角色过来的
    switch (name) {
      case 'Harry Potter':
        promptStore.setSharedPrompt(HarryPotter);
        break;
      case 'Socrates':
        promptStore.setSharedPrompt(Socrates);
        break;
      case 'Sherlock Holmes':
        promptStore.setSharedPrompt(SherlockHolmes);
        break;
    }
  } else if (typeof name === "object" && name !== null) {
    //  用户自定义角色过来的
    promptStore.setSharedPrompt(name);

    if (globalProperties && typeof globalProperties.$setSystemPrompt === 'function') {
      globalProperties.$setSystemPrompt(promptStore.sharedPrompt);
    }

    console.log('promptStore', promptStore.sharedPrompt)
  }
}


eventBus.on('createNewSession', handleCreateNewSession)
eventBus.on('openHistorySession', openHistorySession)
eventBus.on('updateCharacterPrompt', updateCharacterPrompt)

const voiceOptions = ref([])
const messageList = ref([])
onMounted(async () => {
  const histories = await getHistorySessionList();
  historyList.value = histories.data;
  console.log(historyList.value)

  messageList.value = promptStore.historyFormSession
  //  获取语音列表
  const voiceList = await getVoiceList();
  voiceOptions.value = voiceList.data

  console.log('voiceOptions.value', voiceOptions.value);

})

// 组件卸载时移除监听（避免内存泄漏）
onUnmounted(() => {
  eventBus.off('createNewSession', handleCreateNewSession);
  eventBus.off('openHistorySession', openHistorySession);
  eventBus.off('updateCharacterPrompt', updateCharacterPrompt);
})

const handleChatClick = () => {

  //  主页打开的会话记录，默认加载当前的角色模型以及对应的聊天记录
  if (globalProperties && typeof globalProperties.$setSystemPrompt === 'function') {
    globalProperties.$setSystemPrompt(promptStore.sharedPrompt);
  }

  isExpanded.value = true;
  sessionId.value = null;
}

const isPromptImportVisible = ref(false);

const handlePromptImport = () => {
  isPromptImportVisible.value = true;
}

const handlePromptImportSubmit = (prompt: any) => {
  console.log('导入的Prompt', prompt);
  isPromptImportVisible.value = false;
  updateCharacterPrompt(prompt, true);
}

// 处理发送消息
const handleSend = async () => {
  console.log('message', message.value)

  console.log('promptStore.systemPrompt', promptStore.systemPrompt)
  if (!promptStore.systemPrompt) {

    eventBus.emit('question-message', {
      content: message.value,
      role: 'user',
    });

    console.log('promptStore.sessionId', promptStore.sessionId)

    //  没有场景、无prompt
    const params = {
      session_id: promptStore.sessionId,
      message: message.value,
      system_prompt: promptStore.systemPrompt
    }
    message.value = ''
    const response = await sendChatRequest(params)


    if (response.code === 200) {

      eventBus.emit('answer-message', {
        content: response.data.response,
        role: 'system',
      });


      // 此处应该先把回复的消息放入缓存
      const historyFormSession = promptStore.historyFormSession;
      promptStore.setHistoryFromSession(historyFormSession);


      const sessionId = response.data.session_id;
      await promptStore.setSessionId(sessionId);
    }


  } else if (message.value.trim()) {

    if (globalProperties && typeof globalProperties.$setSystemPrompt === 'function') {
      globalProperties.$setSystemPrompt(promptStore.sharedPrompt);
    }


    eventBus.emit('question-message', {
      content: message.value,
      role: 'user',
    });


    historyList.value.unshift({
      listName: message.value,
      id: Date.now()  // 使用时间戳确保ID唯一
    });


    const params = {
      session_id: promptStore.sessionId,
      message: message.value,
      system_prompt: promptStore.systemPrompt,
      role: 'system',
    }

    message.value = '';

    const result = await sendChatRequest(params)

    if (result.code === 200) {
      eventBus.emit('answer-message', {
        content: result.data.response,
        role: 'system',
      });


      // 此处应该先把回复的消息放入缓存
      const historyFormSession = promptStore.historyFormSession;
      promptStore.setHistoryFromSession(historyFormSession);

    }


    //  todo:判断是否为新消息，新消息就需要发送请求生成新的消息列表记录

  }
};

// 处理键盘回车
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {  // 排除Shift+Enter组合键
    e.preventDefault();  // 阻止默认行为（避免换行）
    handleSend();
  }
};


interface CharacterPrompt {
  name: string;
  source: string;
  personality: string;
  languageStyle: string;
  background: string;
}

interface CharacterInfo {
  name: string;
  img: string;
  description: string;
}

const HarryPotterInfo: CharacterInfo = {
  name: "Harry Potter",
  img: 'HarryPotter.png',
  description: '在霍格沃茨魔法学校成长、凭勇气与智慧对抗伏地伏地魔、守护魔法世界的传奇巫师。',
}

const SocratesInfo: CharacterInfo = {
  name: "Socrates",
  img: 'Socrates.png',
  description: '于古希腊雅典践行哲思、凭诘问与理性探寻真理、坚守信念赴死的哲贤。',
}

const SherlockHolmesInfo: CharacterInfo = {
  name: "Sherlock Holmes",
  img: 'Holmes.png',
  description: '在伦敦贝克街立足探案、凭细节与演绎破解奇案、成侦探界传奇的神探。',
}


const HarryPotter: CharacterPrompt = {
  name:
    "Harry Potter",
  source:
    "J.K. 罗琳创作的《哈利・波特》系列小说及衍生影视，角色为霍格沃茨魔法学校格兰芬多学院学生，大难不死的男孩，伏地魔的主要对抗者",
  personality:
    "勇敢坚毅，面对危险时从不退缩，却也会有少年人的迷茫与不安；重视友情，对罗恩、赫敏等伙伴极度信任且愿意付出；内心敏感，因童年在德思礼家的经历，偶尔会在意他人眼光，但始终坚守正义与善良；不喜欢张扬，对 “大难不死的男孩” 标签感到困扰，更希望被当作普通巫师看待；偶尔会冲动行事，但关键时刻总能冷静判断，有强烈的责任感",
  languageStyle:
    "口语化且贴近少年语气，不会使用过于复杂晦涩的词汇；说话直接坦诚，很少拐弯抹角，遇到伙伴调侃时会轻松反驳（带点小幽默），面对敌人时语气坚定且带有威慑力；会偶尔提及魔法世界的特定词汇（如 “魁地奇”“魔杖”“霍格沃茨”），但不会刻意炫耀；情绪激动时会加快语速，表达关心时语气温柔，遇到困惑时会带点迟疑（比如 “呃……”“我不确定，但或许我们可以试试……”）",
  background:
    "出生于巫师家庭，父母詹姆・波特与莉莉・波特为对抗伏地魔牺牲，自幼在麻瓜姨夫德思礼家长大，受尽冷落；11 岁时得知自己的巫师身份，进入霍格沃茨格兰芬多学院，结识罗恩・韦斯莱与赫敏・格兰杰，组成核心三人组；曾多次挫败伏地魔的阴谋（如摧毁哲思冥想盆、阻止伏地魔获取魔法石、在三强争霸赛中与伏地魔正面对抗）；拥有能与蛇对话的蛇佬腔能力，是格兰芬多魁地奇球队的找球手，曾担任格兰芬多学院级长，身上带有父母留下的爱与勇气的印记"
}

const Socrates: CharacterPrompt =
  {
    name:
      "Socrates",
    source:
      "古希腊著名哲学家，西方哲学的奠基人之一，无明确文学 / 影视原著，主要形象源于柏拉图《对话录》、色诺芬《回忆苏格拉底》等著作中的记载",
    personality:
      "谦逊且善思，始终认为 “我唯一知道的就是我一无所知”；热爱真理，对一切既定观点持怀疑态度，不轻易接受未经论证的结论；耐心温和，即使面对质疑或反驳，也会以平和的语气引导对方思考；重视逻辑与理性，不依赖权威或情绪，主张通过 “诘问法”（产婆术）帮助他人挖掘自身认知；有强烈的道德坚守，即使面临死亡威胁（如雅典法庭判处死刑），也不愿违背自己的哲学信念与城邦法律",
    languageStyle:
      "以 “提问” 为核心表达方式，很少直接给出答案，而是通过层层递进的诘问引导对话者自我反思（如 “你认为这个观点的依据是什么？”“如果情况相反，你的结论还能成立吗？”）；语言简洁朴素，无华丽辞藻，多使用日常对话场景中的例子（如 “就像工匠制作工具需遵循技艺，人追求善是否也需遵循某种原则？”）；语气平和沉稳，偶尔会用轻微的反问表达对逻辑漏洞的提醒，不会显得尖锐或攻击性",
    background:
      "出生于古希腊雅典，父亲是石匠，母亲是助产士，早年曾从事雕刻工作，后投身哲学研究；一生未著述，主要通过在雅典街头、广场与他人对话传播思想，弟子包括柏拉图、色诺芬等；因主张 “认识你自己”“关注灵魂而非肉体”，且被指控 “腐蚀青年思想”“不信城邦诸神”，于公元前 399 年被雅典法庭判处死刑，饮鸩而亡；其 “诘问式” 哲学方法对西方理性思维、逻辑学及教育理念影响深远"
  }

const SherlockHolmes: CharacterPrompt = {
  name:
    "Sherlock Holmes",
  source:
    "阿瑟・柯南・道尔创作的《福尔摩斯探案集》系列小说（含《血字的研究》《四签名》《巴斯克维尔的猎犬》等），及基于原著衍生的影视、戏剧作品，是世界文学史上最经典的侦探形象之一",
  personality:
    "极度理性且观察力入微，能从常人忽略的细节（如衣物纤维、鞋底泥渍、指甲纹路）中推导关键信息；思维敏捷且逻辑性极强，擅长通过演绎推理串联线索，对 “毫无逻辑的混乱” 极度反感；性格略带孤僻，不擅长也不屑于社交礼仪，对不感兴趣的人或事会表现出明显的冷漠，甚至被误解为 “傲慢”；但在案件面前会展现出极致的专注，为追查真相可投入全部精力，甚至牺牲睡眠与饮食；重视 “有用的知识”，对化学、解剖学、犯罪心理学等与探案相关的领域精通，却对文学、哲学等 “无实用价值” 的知识刻意忽略；对挚友华生极为信任与依赖，会在华生面前流露难得的温和与坦诚",
  languageStyle:
    "说话简洁锐利，极少冗余表述，常用 “显然”“毫无疑问”“根据…… 可以推断” 等带有肯定性的词汇，体现推理的笃定；喜欢用短句与反问句引导他人关注关键线索（如 “你难道没注意到他袖口的墨迹与信纸边缘的痕迹完全吻合吗？”）；在分析案件时会不自觉陷入 “自言自语式的推理”，仿佛在与自己的思维对话；对愚蠢或主观臆断的观点会直接反驳，语气可能略显尖锐（如 “不要用你的猜测玷污推理，证据才是唯一的标尺”）；日常对话中偶尔会夹杂对化学实验、烟草种类（如他钟爱的石楠烟斗）的提及，语言带有 19 世纪英国绅士的克制感，却无过多繁文缛节",
  background:
    "出生于英国，具体家世不详（原著提及有一位担任政府官员的兄长迈克罗夫特・福尔摩斯，智力远超福尔摩斯）；居住在伦敦贝克街 221B 号公寓，与退役军医约翰・华生合租，华生既是他的助手，也是他探案经历的记录者；职业为 “咨询侦探”，接受苏格兰场警方（如雷斯垂德探长）或私人客户的委托，破解各类疑难案件，从谋杀案到珠宝失窃案均有涉猎；擅长拳击与击剑，精通化学实验（公寓内设有专属实验室），曾因研究案件需要而伪装身份，甚至短暂吸食可卡因以刺激思维（原著时代背景下的争议性设定）；一生破解无数奇案，如 “红发会”“蓝宝石案”“恐怖谷” 等，其推理方法影响了后世侦探文学与现实中的刑侦领域，成为 “逻辑与智慧” 的象征"
}
</script>

<template>
  <div class="history-session">
    <HistorySession :history-list="historyList"/>

  </div>

  <CustomCharacterModal
    :visible="isModalVisible"
    :voice-options="voiceOptions"
    @close="isModalVisible = false"
    @submit="handleCustomCharacterSubmit"
  />

  <PromptImport :visible="isPromptImportVisible"
                @close="isPromptImportVisible = false"
                @submit="handlePromptImportSubmit"/>

  <div class="container">
    <template v-if="!isExpanded">
      <div class="card-list">
        <PersonalCard :characterInfo="HarryPotterInfo"/>
        <PersonalCard :characterInfo="SocratesInfo"/>
        <PersonalCard :characterInfo="SherlockHolmesInfo"/>
      </div>
      <div class="footer-button">
        <CusButton
          buttonText="自定义角色"
          :speed="1.5"
          @click="handleOpenCustomModal"
        />
        <CusButton buttonText="prompt 导入" :speed="1.5" @click="handlePromptImport"/>
      </div>
    </template>
    <template v-else>
      <ChatBox :show="isExpanded" :message-list="messageList" ref="chatBoxRef"/>
    </template>

    <div
      class="message-talk"
      :class="{ 'expanded': isExpanded }"
      @click.stop
    >
      <div class="message-circle">
        <span v-if="!isExpanded" @click="handleChatClick"
              style="display: block;width: 100%;height: 100%">
          <i class="iconfont icon-bianjixiaoxi1"></i>
        </span>
        <span v-if="isExpanded" @click="isExpanded = false"
              style="display: block;width: 100%;height: 100%">✕</span>
      </div>

      <div class="input-container" v-if="isExpanded">
        <input
          type="text"
          v-model="message"
          placeholder="输入消息..."
          @keydown="handleKeyDown"
          ref="messageInput"
          @click.stop
        >
        <button class="send-btn" @click="handleSend">发送</button>
      </div>
    </div>

  </div>

</template>

<style scoped>

.history-session {
  position: fixed;
  left: 20px;
  top: 50px;
}

.container {
  margin: 300px auto;
  width: 650px;
  position: relative;
}

.card-list {
  width: 100%;
  display: flex;
  height: 80%;
  justify-content: space-around;
  align-items: center;
}

.footer-button {
  margin-top: 50px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.message-talk {
  width: 40px;
  cursor: pointer;
  color: #333;
  position: fixed;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  transition: all .5s ease;
  padding: 3px;
  border-radius: 30px;
  border: 2px solid #ffffff;
  box-sizing: content-box;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: transparent;
}

.message-talk.expanded {
  width: 700px;
  background-color: #f6f6f6;
  border: 2px solid #555555;
  padding: 8px 10px;
  overflow: hidden;
}

.message-circle {
  border-radius: 50%;
  width: 40px;
  height: 40px;
  text-align: center;
  line-height: 40px;
  background-color: #333333;
  transition: all .5s;
  color: white;
  flex-shrink: 0;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  opacity: 0;
  height: 40px;
  transform: translateX(-20px);
  transition: all .3s ease;
  overflow: hidden;
  padding-left: 5px;
}

.message-talk.expanded .input-container {
  opacity: 1;
  transform: translateX(0);
}

.input-container input {
  flex-grow: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
}

.input-container input:focus {
  border-color: #3B82F6;
}

.send-btn {
  padding: 8px 18px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color .3s;
}

.send-btn:hover {
  background-color: #555;
}
</style>
