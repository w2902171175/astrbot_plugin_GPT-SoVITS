<div align="center">

# 🎙️ astrbot_plugin_GPT-SoVITS

![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue?style=flat-square)
![License](https://img.shields.io/badge/License-AGPL--3.0-green?style=flat-square)
![GPT-SoVITS](https://img.shields.io/badge/GPT--SoVITS-V2~V4-orange?style=flat-square)

**一个 AstrBot 插件，调用本地运行的 GPT-SoVITS TTS 服务，将 LLM 的每条回复自动转换为语音发送。**

专为 **GSVI** (`GPT-SoVITS-1007-cu124`) 的 `/infer_classic` 接口设计，同时兼容经典部署模式。

</div>

---

## 📋 配置说明

### 一、服务连接

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `api_host` | GPT-SoVITS 服务 IP | `localhost` |
| `api_port` | GPT-SoVITS 服务端口 | `8000` |

> 💡 本机运行保持默认即可；部署在其他机器时填对应 IP。

---

### 二、角色标识（可选）

| 字段 | 说明 |
|------|------|
| `character_name` | 角色备注名，仅显示在启动日志中，方便多实例时区分，不影响推理 |

---

### 三、模型配置（必填）

#### 3.1 模型版本

选择与所用模型文件对应的版本，**选错将导致推理失败**。

| 版本 | 对应目录（GSVI）| 对应目录（经典）|
|:----:|----------------|----------------|
| `v4` | `models/v4/` | `GPT_weights_v4/` / `SoVITS_weights_v4/` |
| `v3` | `models/v3/` | `GPT_weights_v3/` / `SoVITS_weights_v3/` |
| `v2Pro` | `models/v2Pro/` | `GPT_weights_v2Pro/` / `SoVITS_weights_v2Pro/` |
| `v2` | `models/v2/` | `GPT_weights_v2/` / `SoVITS_weights_v2/` |

#### 3.2 模型前缀

插件会自动将前缀拼接到模型名之前，无需手动输入括号。

| 选项 | 实际前缀 | 适用场景 |
|:----:|:--------:|----------|
| `GSVI` | `【GSVI】` | 模型位于 GSVI 的 `models/` 目录（推荐） |
| `经典` | `【经典】` | 模型位于 `GPT_weights_*/` 等经典目录 |
| `无前缀` | 无 | 直接使用填写的原始模型名 |

#### 3.3 模型名称

填写模型文件名，**不含后缀、不含前缀括号**，插件会自动加上。

| 字段 | 对应文件类型 | 示例 |
|------|:-----------:|------|
| `gpt_model_name` | `.ckpt` 文件 | `纳西妲_ZH-e10` |
| `sovits_model_name` | `.pth` 文件 | `纳西妲_ZH_e10_s1400_l32` |

> ⚠️ 请使用绝对路径，路径两端**不要**加双引号。

---

### 四、参考音频配置（必填）

| 字段 | 说明 |
|------|------|
| `ref_audio_path` | 参考音频的绝对路径，建议 3~10 秒清晰单人语音 |
| `prompt_text` | 参考音频中说的文字内容，需与音频语言一致 |
| `prompt_text_lang` | 参考音频的语言（下拉选择） |
| `text_lang` | 合成目标语言，推荐 `中英混合` |

---

### 五、触发与行为

| 字段 | 说明 | 默认值 |
|------|------|:------:|
| `prob` | 触发 TTS 的概率（0-100），100 表示每次都触发 | `100` |
| `cooldown` | 群聊冷却时间（秒），同一会话的最短触发间隔 | `0` |
| `text_limit` | 最长文本字符数，超出将截断，0 表示不限制 | `0` |
| `send_text_with_audio` | 是否在语音后附带 `[STT]` 原文 | `false` |
| `split_sentence` | 是否按标点切分长句再推理，改善长文本自然度 | `true` |

---

### 六、推理参数（高级）

| 字段 | 说明 | 推荐值 |
|------|------|:------:|
| `top_k` | Top-K 采样，越小越稳定 | `5~20` |
| `top_p` | Top-P 累计概率截断 | `1.0` |
| `temperature` | 温度系数，越低越稳定 | `0.8~1.2` |
| `speed_facter` | 语速系数，1.0 为正常速度 | `0.8~1.2` |

---

### 七、磁盘清理（可选）

| 字段 | 说明 |
|------|------|
| `outputs_path` | GPT-SoVITS 的 `outputs` 文件夹绝对路径，填写后将在语音发送成功 **5 秒后**自动删除服务端生成的 wav 文件，留空则不删除 |


---

## ❓ 常见问题

<details>
<summary><b>🔴 无法连接服务</b></summary>

确保 `gsvi.bat` 窗口未关闭，防火墙允许对应端口通过，`api_host` 和 `api_port` 与实际一致。

</details>

<details>
<summary><b>🔴 模型未找到 / 推理失败</b></summary>

- 检查 `version` 是否与模型文件所在目录对应
- 检查 `model_prefix` 选择是否正确（GSVI 目录用 `GSVI`，经典目录用 `经典`）
- 检查模型名是否填写了文件名（不含后缀、不含括号前缀）

</details>

<details>
<summary><b>🟡 音色克隆效果差</b></summary>

- 参考音频建议使用 3~10 秒、无背景噪声的单人语音
- `prompt_text` 必须与参考音频实际内容完全一致
- `prompt_text_lang` 需与音频语言匹配

</details>

---

## 🙏 致谢

- 感谢 **@花儿不哭、@红血球AE3803、@白菜工厂1145号员工、@AI-Hobbyist** 大佬们提供的 [GPT-SoVITS V4 推理特化一键包](https://www.modelscope.cn/models/aihobbyist/GPT-SoVITS-Inference/files)
- 感谢 **@Amnemon** 大佬的 [genie_tts_local](https://github.com/Amnemon/genie_tts_local) 插件提供的思路

---

## 📄 许可证

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 许可证，详情请查看 [LICENSE](LICENSE) 文件。

---

## ☕ 赞助一杯奶茶

如果这个插件对你有帮助，欢迎请我喝杯奶茶 🧋，感谢支持！

<div align="center">
  <img src="assets/wechat_pay.jpg" alt="微信赞赏码" width="240"/>
  <br/>
  <sub>微信扫码赞赏</sub>
</div>

