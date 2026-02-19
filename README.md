# astrbot_plugin_GPT-SoVITS

这是一个 AstrBot 的插件，用于调用本地运行的 GPT-SoVITS 文本转语音 (TTS) 服务，将 LLM 的回复转换为语音发送。

本插件专为适配 `GSVI` （`2_GPT-SoVITS-1007-cu124`版本） 的接口而设计。

## 配置说明

启用插件后，请在设置中配置以下必填项。

### 1. API 设置
*   **api_host**: 本地服务的 IP，默认为 `localhost`。
*   **api_port**: 本地服务的端口，默认为 `8000`。

### 2. 模型配置 (关键)
该插件支持 `v4`, `v2`, `v2Pro` 等多个版本的模型。请先在配置中选择正确的 **version**。

*   **Version (`version`)**: 
    *   如果模型位于 `models/v4`, `GPT_weights_v4` 等目录，请选择 `v4`。
    *   同理，如果在 `models/v2` 等目录，请选择对应版本。

*   **GPT 模型名称 (`gpt_model_name`)**:
    *   如果模型位于 `models/{version}/...` (自己在 GSVI 内下载/训练的模型)，格式为: `【GSVI】模型文件名(无后缀)`
        *   例如文件名为 `纳西妲_ZH-e10.ckpt`，则填 `【GSVI】纳西妲_ZH-e10`
    *   如果模型位于 `GPT_weights_{version}/...` (经典模式)，格式为: `【经典】模型文件名(无后缀)`

*   **SoVITS 模型名称 (`sovits_model_name`)**:
    *   如果模型位于 `models/{version}/...`，格式为: `【GSVI】模型文件名(无后缀)`
        *   例如文件名为 `纳西妲_ZH_e10_s1400_l32.pth`，则填 `【GSVI】纳西妲_ZH_e10_s1400_l32`
    *   如果模型位于 `SoVITS_weights_{version}/...`，格式为: `【经典】模型文件名(无后缀)`

### 3. 参考音频配置 (必填)
为了克隆音色，必须提供一段该角色的参考音频（3-10秒）。

*   **ref_audio_path**: 参考音频文件的**绝对路径**。
    *   注意：如果在 Windows 上，路径中的反斜杠 `\` 可能需要在 JSON 配置中转义为 `\\`，或者直接在 AstrBot 目前的 UI 中填写。
*   **prompt_text**: 参考音频对应的准确文本内容。
*   **prompt_text_lang**: 参考音频的语言 (如 `中文`, `日文`, `英文`)。

### 4. 其他设置
*   **text_lang**: 合成语音的目标语言，推荐 `中英混合`。
*   **prob**: 触发 TTS 的概率 (0-100)。
*   **send_text_with_audio**: 发送语音时是否同时发送原文文本。
*   **split_sentence**: 是否启用长句自动切分 (推荐开启)。

## 常见问题

*   **无法连接服务**: 请确保 `gsvi.bat` 窗口未关闭，且防火墙允许端口通过。
*   **模型未找到**: 请仔细检查 `gpt_model_name` 和 `sovits_model_name` 是否加了正确的前缀（`【GSVI】` 或 `【经典】`）。
*   **合成失败**: 检查 AstrBot 后台日志，确认 `ref_audio_path` 路径正确且文件存在。
