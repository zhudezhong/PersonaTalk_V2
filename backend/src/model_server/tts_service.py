
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel, Field
from src.model_server.base import BaseModelService, ChatRequest, ChatResponse, StreamResponse


class VoiceInfo(BaseModel):
    """音色信息模型"""
    voice_name: str = Field(description="音色名称")
    voice_type: str = Field(description="音色类型ID")
    url: str = Field(description="音色示例音频URL")
    category: str = Field(description="音色分类")
    updatetime: int = Field(description="更新时间戳")


class AudioConfig(BaseModel):
    """音频配置模型"""
    voice_type: str = Field(description="音色类型ID")
    encoding: str = Field(default="mp3", description="音频编码格式")
    speed_ratio: Optional[float] = Field(1.0, description="语速比例")

class TTSRequestData(BaseModel):
    """TTS请求数据模型"""
    text: str = Field(description="要转换的文本")

class TTSRequest(BaseModel):
    """TTS请求模型"""
    audio: AudioConfig = Field(description="音频配置")
    request: TTSRequestData = Field(description="请求数据")
    
    @classmethod
    def create_simple(
        cls, 
        text: str, 
        voice_type: str, 
        encoding: str = "mp3", 
        speed_ratio: float = 1.0
    ) -> "TTSRequest":
        """
        创建简单的TTS请求
        
        Args:
            text: 要转换的文本
            voice_type: 音色类型ID
            encoding: 音频编码格式
            speed_ratio: 语速比例
            
        Returns:
            TTSRequest: TTS请求对象
        """
        return cls(
            audio=AudioConfig(
                voice_type=voice_type,
                encoding=encoding,
                speed_ratio=speed_ratio
            ),
            request=TTSRequestData(text=text)
        )


class TTSResponse(BaseModel):
    """TTS响应模型"""
    reqid: str = Field(description="请求ID")
    operation: str = Field(description="操作类型")
    sequence: int = Field(description="序列号")
    data: str = Field(description="响应数据")
    addition: Optional[Dict[str, Any]] = Field(None, description="附加信息")


class TTSModelService(BaseModelService):
    """TTS模型服务类"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "tts", **kwargs):
        """
        初始化TTS模型服务
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, base_url, model, **kwargs)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=360)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_voice_list(self) -> List[VoiceInfo]:
        """
        获取音色列表
        
        Returns:
            List[VoiceInfo]: 音色列表
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/voice/list"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"获取音色列表失败: HTTP {response.status}")
                
                data = await response.json()
                
                # 解析响应数据 - 根据示例，响应直接是数组格式
                voices = []
                if isinstance(data, list):
                    voice_list = data
                else:
                    voice_list = []
                
                for voice_data in voice_list:
                    voice = VoiceInfo(
                        voice_name=voice_data.get("voice_name", ""),
                        voice_type=voice_data.get("voice_type", ""),
                        url=voice_data.get("url", ""),
                        category=voice_data.get("category", ""),
                        updatetime=voice_data.get("updatetime", 0)
                    )
                    voices.append(voice)
                
                return voices
                
        except aiohttp.ClientError as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"获取音色列表失败: {str(e)}")
    
    async def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """
        文字转语音
        
        Args:
            request: TTS请求
            
        Returns:
            TTSResponse: TTS响应
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/voice/tts"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "audio": {
                "voice_type": request.audio.voice_type,
                "encoding": request.audio.encoding,
                "speed_ratio": request.audio.speed_ratio
            },
            "request": {
                "text": request.request.text
            }
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"TTS请求失败: HTTP {response.status}, {error_text}")
                
                # 解析JSON响应
                data = await response.json()
                return TTSResponse(
                    reqid=data.get("reqid", ""),
                    operation=data.get("operation", ""),
                    sequence=data.get("sequence", -1),
                    data=data.get("data", ""),
                    addition=data.get("addition", {})
                )
                
        except aiohttp.ClientError as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"TTS转换失败: {str(e)}")
    
    # 实现BaseModelService的抽象方法（TTS服务不需要这些方法，但为了兼容性提供默认实现）
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """TTS服务不支持聊天功能"""
        raise NotImplementedError("TTS服务不支持聊天功能")
    
    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[StreamResponse, None]:
        """TTS服务不支持流式聊天功能"""
        raise NotImplementedError("TTS服务不支持流式聊天功能")
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            # 尝试获取音色列表来检查服务健康状态
            await self.get_voice_list()
            return True
        except Exception:
            return False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

async def main():
    service = TTSModelService(
        api_key="sk-b0bb3a405dd2fed65bae69d8ce9bf643ca290bdd4210e5a7462ebd1a232b9c00",
        base_url="https://openai.qiniu.com/v1",
        model="tts"
    )
    health_flag =await service.health_check()
    if health_flag:
        print("TTS服务健康")
    else:
        print("TTS服务宕机")
    
    voice_list = await service.get_voice_list()
    print(voice_list)

    print("TTS服务获取音色列表成功")

    request = TTSRequest.create_simple(
        text="你好，我是小明",
        voice_type="qiniu_zh_female_tmjxxy"
    )
    response = await service.text_to_speech(request)
    print(response)
    print("TTS服务文字转语音成功")
    

if __name__ == "__main__":
    asyncio.run(main())