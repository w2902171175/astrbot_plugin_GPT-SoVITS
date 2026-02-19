import os
import time
import random
import uuid
import wave
import asyncio
from typing import Dict, Any
from pathlib import Path

from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp

from astrbot.core.star.register import register_on_decorating_result as on_decorating_result
from astrbot.core.star.register import register_command as command


@register(
    "gpt_sovits_tts_local",
    "Amnemon",
    "支持本地 GPT-SoVITS 的文字转语音插件",
    "1.0.0"
)
class GPTSoVITSTTSLocal(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        
        self.gpt_model_name = config.get('gpt_model_name', '')
        self.sovits_model_name = config.get('sovits_model_name', '')
        self.version = config.get('version', 'v4') # 新增版本配置
        self.ref_audio_path = config.get('ref_audio_path', '')
        self.prompt_text = config.get('prompt_text', '')
        self.prompt_text_lang = config.get('prompt_text_lang', '中文')
        self.text_lang = config.get('text_lang', '中英混合')
        
        self.prob = float(config.get('prob', 100.0)) / 100.0
        self.text_limit = int(config.get('text_limit', 0))
        self.cooldown = int(config.get('cooldown', 0))
        self.send_text_with_audio = bool(config.get('send_text_with_audio', False))
        
        self.top_k = int(config.get('top_k', 5))
        self.top_p = float(config.get('top_p', 1.0))
        self.temperature = float(config.get('temperature', 1.0))
        self.speed_facter = float(config.get('speed_facter', 1.0))
        self.split_sentence = bool(config.get('split_sentence', True))

        self.api_host = config.get('api_host', 'localhost')
        self.api_port = int(config.get('api_port', 8000))

        self.base_url = f"http://{self.api_host}:{self.api_port}"
        self.temp_dir = Path(__file__).parent / "temp_audio"
        self.temp_dir.mkdir(exist_ok=True)

        self._session_state: Dict[str, Any] = {}
        
        logger.info(f"[GPTSoVITSTTSLocal] 插件已加载，TTS 服务地址: {self.base_url}")
        logger.info(f"[GPTSoVITSTTSLocal] GPT模型: {self.gpt_model_name}, SoVITS模型: {self.sovits_model_name}")

    async def _post(self, endpoint: str, data: dict, return_json=True):
        import httpx
        try:
            logger.debug(f"[GPTSoVITSTTSLocal] 正在请求 {self.base_url}{endpoint}，参数: {data}")
            async with httpx.AsyncClient(timeout=60) as client: # TTS 生成可能较慢，增加超时
                resp = await client.post(f"{self.base_url}{endpoint}", json=data)
                
                if not return_json:
                    # 如果返回的是音频文件流，直接返回 content
                    # 注意：GPT-SoVITS API 有时返回 JSON 有时返回文件流，取决于实现
                    # 这里假设如果响应头是 audio/wav 或者内容是二进制流
                    return resp.content
                
                # 尝试解析 JSON
                try:
                    json_data = resp.json()
                    logger.debug(f"[GPTSoVITSTTSLocal] 收到 JSON 响应: {json_data}")
                    return json_data
                except:
                   # 解析 JSON 失败，可能直接返回了二进制流（虽然不应该在 return_json=True 时发生）
                   return resp.content

        except Exception as e:
            logger.error(f"[GPTSoVITSTTSLocal] 请求失败 {endpoint}: {e}")
            raise

    async def _download_audio(self, url: str) -> bytes:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.content
        except Exception as e:
            logger.error(f"[GPTSoVITSTTSLocal] 下载音频失败 {url}: {e}")
            return None

    @on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """
        LLM 回复后触发，进行 TTS 转换
        """
        result = event.get_result()
        if not result or not result.chain:
            return

        # 提取纯文本部分并记录索引
        full_text = ""
        plain_indices = []
        for i, comp in enumerate(result.chain):
            if isinstance(comp, Comp.Plain):
                full_text += comp.text
                plain_indices.append(i)
        
        full_text = full_text.strip()
        if not full_text:
            return

        # 概率触发
        if random.random() > self.prob:
            return

        # 检查冷却
        session_id = event.session_id
        now = time.time()
        last_time = self._session_state.get(session_id, {}).get("last_trigger", 0)
        if self.cooldown > 0 and now - last_time < self.cooldown:
            return
        
        # 记录触发时间
        if session_id not in self._session_state:
            self._session_state[session_id] = {}
        self._session_state[session_id]["last_trigger"] = now

        # 文本截断
        tts_text = full_text
        if self.text_limit > 0 and len(tts_text) > self.text_limit:
            logger.warning(f"[GPTSoVITSTTSLocal] 文本过长，截断前 {self.text_limit} 个字符")
            tts_text = tts_text[:self.text_limit]

        logger.info(f"[GPTSoVITSTTSLocal] 开始转换语音: {tts_text[:20]}...")

        # 构造请求参数
        payload = {
            "gpt_model_name": self.gpt_model_name,
            "sovits_model_name": self.sovits_model_name,
            "ref_audio_path": self.ref_audio_path,
            "prompt_text": self.prompt_text,
            "prompt_text_lang": self.prompt_text_lang,
            "text": tts_text,
            "text_lang": self.text_lang,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "speed_facter": self.speed_facter,
            "text_split_method": "按标点符号切" if self.split_sentence else "不切", 
            "batch_size": 1,
            "batch_threshold": 0.75,
            "split_bucket": True,
            "fragment_interval": 0.3,
            "media_type": "wav",
            "parallel_infer": True,
            "repetition_penalty": 1.35,
            "seed": -1,
            "sample_steps": 16,
            "if_sr": False,
            "version": self.version # 将 version 加入参数
        }

        try:
            # 调用 infer_classic 接口
            # 注意：该接口返回的是 JSON，包含 audio_url
            resp = await self._post("/infer_classic", payload)
            
            audio_url = resp.get("audio_url")
            if not audio_url:
                logger.error(f"[GPTSoVITSTTSLocal] TTS 接口未返回 audio_url: {resp}")
                return

            # 如果返回的是本地 localhost url，需要下载内容或者让 AstrBot 处理
            # 如果配置的是 0.0.0.0，返回的 url 可能是 0.0.0.0:port，这在部分系统上可能无法直接连接
            # 尝试替换为配置的 host
            audio_url = audio_url.replace("0.0.0.0", self.api_host)
            
            audio_data = await self._download_audio(audio_url)
            if not audio_data:
                 logger.error(f"[GPTSoVITSTTSLocal] 无法获取音频数据")
                 return

            # 保存为临时文件
            file_name = f"{uuid.uuid4()}.wav"
            file_path = self.temp_dir / file_name
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            logger.info(f"[GPTSoVITSTTSLocal] 音频已保存: {file_path}")

            # 修改消息链
            # 移除原来的纯文本组件（如果只有文本，就全移除了）
            if plain_indices:
                # 从后往前删，避免索引偏移
                for i in sorted(plain_indices, reverse=True):
                    del result.chain[i]
                
                # 插入音频组件到原来的第一个文本的位置
                insert_pos = plain_indices[0]
                result.chain.insert(insert_pos, Comp.Record(file=str(file_path)))
                
                # 如果开启了同时也发送文字
                if self.send_text_with_audio:
                     result.chain.insert(insert_pos + 1, Comp.Plain(f"\n[原文]\n{full_text}"))
            else:
                 # 理论上不会进这里，因为前面判断了 full_text
                 result.chain.append(Comp.Record(file=str(file_path)))
            
            # 清理临时文件
            asyncio.create_task(self._cleanup_later(file_path))

        except Exception as e:
            logger.error(f"[GPTSoVITSTTSLocal] TTS 转换异常: {e}")

    async def _cleanup_later(self, path: Path, delay=60):
        await asyncio.sleep(delay)
        try:
            if path.exists():
                path.unlink()
                logger.debug(f"[GPTSoVITSTTSLocal] 清理临时文件: {path}")
        except Exception as e:
            logger.warning(f"[GPTSoVITSTTSLocal] 清理文件失败: {e}")

