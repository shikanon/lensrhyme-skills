# LensRhyme Skills for Codex

把 LensRhyme 的四个创作模块作为独立 Codex skills 使用。使用你自己的 [API management Token Key](https://lensrhyme.com/api-management)，生产站点入口：[团队页](https://lensrhyme.com/team)。无需克隆 LensRhyme 应用、部署后端或配置模型供应商密钥。

## 应该用哪个 skill？

| Skill | 使用场景 | 不负责的场景 |
| --- | --- | --- |
| `lensrhyme-studio-image` | 独立文生图、参考图编辑、角色设计稿、场景俯视图 | 视频；已有 Canvas 节点或 Workbench 项目中的生成 |
| `lensrhyme-studio-video` | 独立文生视频、首帧、首尾帧、多模态参考短片 | 静态图片；项目镜头或画布工作流 |
| `lensrhyme-canvas` | Canvas 节点与连线、节点生成及 artifact、模板工作流调用、画布交付 | 独立媒体；按剧本/集/幕/场景/镜头组织的制作项目 |
| `lensrhyme-workbench` | 剧本导入、集/幕/场景/镜头、角色与场景资产、镜头版本、时间线导出 | 独立媒体；Canvas 节点图 |

**路由优先级：指定的项目/节点/镜头归属 > 工作组织方式 > 输出媒体类型。**

- “生成一张角色海报” → Studio Image。
- “把海报做成五秒视频” → Studio Video。
- “在这个画布的视频节点生成” → Canvas，即使输出是视频。
- “生成项目第三场第二个镜头” → Workbench，即使调用了视频模型。
- “把已生成的海报放进画布并继续生成” → 分阶段操作，交接真实资源 ID/URL；每阶段仅一个主 skill，不重复生成。
- “帮我做个视频”且无项目上下文 → Studio Video；不要自动扩成一套剧本项目。

## 在 Codex 安装

直接向 Codex 发送：

```text
使用 $skill-installer 从 shikanon/lensrhyme-skills 安装以下路径：
skills/lensrhyme-studio-image
skills/lensrhyme-studio-video
skills/lensrhyme-canvas
skills/lensrhyme-workbench
```

也可只安装一个路径。每个目录都有 `SKILL.md`、`agents/openai.yaml`、调用脚本和接口参考，不依赖同仓库其他 skill。安装后可在下一轮通过 `$lensrhyme-studio-image` 等名称使用。标准安装与发现机制见 [OpenAI skill 文档](https://learn.chatgpt.com/docs/build-skills)。

如果本地已有 Codex 自带 skill-installer，也可以运行它的 `scripts/install-skill-from-github.py`：

```bash
python3 /path/to/skill-installer/scripts/install-skill-from-github.py \
  --repo shikanon/lensrhyme-skills \
  --path skills/lensrhyme-studio-image skills/lensrhyme-studio-video skills/lensrhyme-canvas skills/lensrhyme-workbench
```

## 配置

要求 Python 3.10+、HTTPS 网络访问和有权限的 LensRhyme 账户。没有额外 pip/npm 依赖。

| 环境变量 | 用途 |
| --- | --- |
| `LENSRHYME_API_KEY` | 必填，用户 API management 中的 `ltr_...` Token Key，通过本地环境或 secret manager 提供，不要发到聊天中 |
| `LENSRHYME_BASE_URL` | 默认 `https://lensrhyme.com/api/v1`；不是 `/team` 页面地址 |
| `LENSRHYME_WORKSPACE_ID` | 指定 Workspace；先用 `/workspaces/` 确认成员权限 |

所有四个 skill 均使用 `Authorization: Bearer` 和可选 `X-Workspace-ID`。支持原有 IP 白名单、权限及模型访问控制。此密钥不是 OpenAI、火山引擎或其他供应商 API Key。本仓库不包含测试账号密码或任何有效凭证。

## 调用与恢复

在已安装 skill 目录执行，例如：

```bash
python3 scripts/lensrhyme_api.py request GET /models/list
python3 scripts/lensrhyme_api.py schema /api/v1/tasks/ --method POST
python3 scripts/lensrhyme_api.py request POST /tasks/ --json-file request.json --out submitted.json
python3 scripts/lensrhyme_api.py wait TASK_ID --seconds 300 --out finished.json
```

图片/视频 Studio 任务 body 示例、Canvas 关联方式、Workbench 结构与导出流程见各自 `references/api.md`。每个 skill 都有生产 OpenAPI 的模块子集，`schema` 命令无需凭证即可查阅。示例中的模型参数需与账户实时模型能力核对。

生成会消耗账户额度；仅执行用户请求的范围。生成接口返回 task ID 不代表成功。脚本不自动重试写请求，超时后通过原任务 ID 恢复；CLI 退出码 `2` 表示生成失败/取消或仍需继续轮询。`--out` 不覆盖已有记录。不要将生成结果、用户项目数据或认证文件提交到公开仓库。

## 验证与维护

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
```

客户端源码位于 `scripts/lensrhyme_api.py`，发布副本放进每个 skill 以支持独立安装。更新客户端时同步四份副本；测试会验证一致性。接口快照日期为 2026-09-21，更新契约时从部署的 `/api/v1/openapi.json` 提取模块接口及其引用 schema，避免发布用户数据或内部配置。

已验证范围和生产测试限制见 [验证记录](VALIDATION.md)。Skill 文件结构通过检查不等同于所有模型与工作流端到端通过。
