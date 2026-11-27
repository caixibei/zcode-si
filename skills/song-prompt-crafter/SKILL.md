---
name: "song-prompt-crafter"
description: "把用户的情绪、主题、曲风需求转化为 Suno/Udio 等平台的三层歌曲生成提示词(风格字段+排除字段+歌词内联标签),内置情绪→声学特征翻译、收/倒判别轴、抗AI歌词规则与抽卡迭代策略"
---

# 歌曲生成提示词撰写(song-prompt-crafter)

将用户的情绪、主题、曲风需求,转化为音乐生成平台(Suno / Udio 等)能高效消化的提示词。最终交付物是一套可直接粘贴使用的**三层提示词**:风格字段 + 排除字段 + 歌词字段(含内联演唱标签)。

## 核心认知(决定一切写法)

1. **模型做特征采样,不做指令执行。** 它从提示词中提取风格特征去匹配训练分布,不会按顺序执行你的要求。所以:正向特征用逗号分隔的特征短语,不用长句指令;条件逻辑("若偏甜则……")绝对不要写进提示词,那是给用户的迭代策略。
2. **否定词写进正向字段会反噬。** "不要电子舞曲"这类 token 会提高被采样概率(粉红大象效应)。所有否定内容只进排除字段(平台自带的 Exclude Styles / 排除风格框)。提示词正文、内联标签中一律用对应的正向特征替换(不喊唱→"restrained quiet chorus";不亮→"dark timbre")。本技能产出的任何字段里都不应出现 no/not/不要 开头的短语,排除字段除外。
3. **服从度随长度衰减。** 前 200~400 字权重最大,之后基本是噪声。加字不如换词:每轮迭代改一两个关键词,而不是追加描述。
4. **裸情绪形容词是弱特征,声学与演唱特征是强特征。** "sad" "melancholic" 各平台都用滥了,区分度低;把情绪翻译成气息、干湿比、乐句收束方式、编曲留白等可执行特征,才是提示词的全部技术含量。见翻译表。

## 工作流程

### 第一步:需求采集

用户没说清就先问,已明确则跳过。需要确认的维度:

- **主题与情绪内核**:不只是"悲伤",要问清是"向外倒"(嚎哭、倾诉、宣泄)还是"向内收"(压抑、释怀、算了)——这决定全部演唱与混响特征,见判别轴。
- **人声**:性别、声部(男低/男中/女中…)、质感偏好(干净/气声/沙哑)。
- **曲风、速度、调性明暗**、是否升调。
- **语言与结构**:语言、大致段落(Intro/Verse/Chorus/Bridge/Outro)、每段情绪走向。
- **歌词来源**:用户自备(→校验+加标签)或代写(→走歌词规则)。
- **目标平台**(未说明则默认 Suno,按平台适配节输出)。

### 第二步:情绪 → 声学特征翻译

这是核心工序。拿到情绪内核后,先判断收/倒,再从两张表选特征。表是起点不是终点,组合时保持"每个特征都服务于情绪内核",砍掉与内核无关的堆砌。

**判别轴:向内收 vs 向外倒(用户没说清时,用这条轴帮他定位)**

| 维度 | 向内收(压抑/释怀/苍凉型) | 向外倒(宣泄/倾诉/爆发型) |
|---|---|---|
| 气息 | 气多于声,字尾散掉 | 声带全闭合,字字送满 |
| 音量动态 | 压低,弱混,轻推 | 推响,副歌爆发 |
| 乐句收尾 | 收得快而轻,像咽回去 | 拖长、加重、甩出去 |
| 混响 | 干声为主,短混响,留换气声 | 长尾混响,铺满空间感 |
| 编曲 | 稀疏留白,余音暴露 | 密度和力度随情绪爬升 |
| 典型措辞 | breathy, intimate, dry mix, restrained | soaring, powerful, anthemic, wide reverb |

**翻译表(情绪 → 强特征,中英对照,英文进字段)**

| 情绪内核 | 声学/演唱特征(写入风格字段) |
|---|---|
| 苍凉、克制、释怀(收) | low clean baritone/tenor, breathy, half-spoken verses, phrase endings falling softly, intimate close-mic vocal, dry mix, short plate reverb, audible breaths, sparse arrangement, spacious, cinematic |
| 孤独、疏离 | monotonous low vocal, minimal arrangement, wide stereo with dry center vocal, lo-fi texture |
| 温暖、怀旧(注意防甜) | warm acoustic guitar, soft brushed drums, mid-low register, restrained dynamics, tape saturation(防甜:压高频、减亮色,而非加沙哑) |
| 愤怒、压抑的爆发(倒) | tense low verses, limited-range melodic shout, distorted bass, garage mix, dry and close |
| 悲怆、宣泄(倒) | soaring powerful vocals, belted chorus, wide lush reverb, crescendo arrangement |
| 深情、私密 | whisper-adjacent soft vocal, close-mic, minimal guitar, almost no drums |
| 神圣、庄严 | choir pad, organ, slow tempo, wide but dark reverb, low register lead |
| 恍惚、迷离 | half-whispered vocal, drowsy phrasing, heavy tape wobble, muted drums |

通用编码规律(超出表格时自行翻译用):

- 音区=情绪海拔:压抑贴说话音高,宣泄抬四度以上;全曲不升 Key 时,正向字段写 "static key",排除字段写 "key change"。
- 气声比=脆弱度:气多声少→脆弱、空茫;全闭合→坚定、爆发。
- 混响长度=空间孤独感:越干越近越私密,越湿越远越苍茫;但重混响会同时糊掉气声细节,收型慎用。
- 留白=电影感:写"哪些乐器不碰什么"(guitar stays in low positions, erhu mid-low register only, sparse percussion at emotional nodes only)比罗列要什么更能控制画面。
- 副歌写法:模型的默认是推响副歌,若要弱副歌必须显式写正向措辞 "restrained quiet chorus, soft dynamics, minimal lift",并在排除字段加 belting——而不是写 "no loud chorus"。

### 第三步:分层组装

只按用户需求组装,不堆砌与内核无关的特征。

**第 1 层·风格字段**(Suno 风格框等)

- 200~400 字符为宜,重要的放前面。
- 中英混排策略:英文技术词(BPM、声部、混响、配器)编码更稳,中文留给语义与意境(平台对中文语义有响应)。也可全英文求稳。
- 结构模板(按需取舍):

```
[语言] [曲风] , [BPM] BPM, [调性] . [人声:声部+质感+演唱方式]. [段落动态]. [配器:每件的音区与奏法约束]. [混响/制作:干湿、空间]. [情绪统摄词, 1-3个]
```

- 示例(内向收型):

```
Chinese folk-rock ballad, 62 BPM, dark minor key. Low clean baritone, breathy, intimate close-mic vocal, dry mix, short plate reverb, audible breaths. Half-spoken verses, phrase endings falling softly; restrained quiet chorus, soft dynamics. Sparse fingerpicked acoustic guitar in low positions, erhu short strokes in mid-low register, occasional side stick. Spacious, cinematic, melancholic but quietly resolved, ends in whisper.
```

**第 2 层·排除字段**(Suno Exclude Styles 等)

- 全部否定内容集中于此;正向字段做一次自查,混进的否定词移过来。
- 从用户负面约束逐条翻译成英文特征词,常用词库:raspy, hoarse, vocal fry, belting, high male vocal, female vocal, EDM, dense drums, busy drums, march feel, fast strumming, upbeat, bright major key, long hall reverb, key change, autotune, melodramatic, aggressive drums。
- 示例:`raspy, hoarse, vocal fry, belting, high male vocal, female vocal, EDM, dense drums, march feel, bright major key, long hall reverb, key change, upbeat`

**第 3 层·歌词字段**(含内联演唱标签)

- 结构标签:`[Intro] [Verse] [Chorus] [Bridge] [Outro]`,按用户要求排布。
- 在结构标签内追加演唱指令,格式 `[Verse 1: breathy half-spoken, low]`,这是绕过风格字段长度限制、把演唱指令下沉的有效手段,对段落级差异(如弱副歌、戏腔式念白)尤其有效。标签内同样用正向措辞。
- 标签用英文;歌词本身用目标语言。
- 用户自带歌词时:校验段落完整性,只在标签层动刀,不改词。
- 结尾想收得住,就在最后一段标签写 `[Outro: whispered, fading]`,并保证末段歌词只有一两行。

### 歌词创作规则(用户要求代写时)

核心理念:让**动作和物象**自己说话,情绪词全部隐去。直接套用以下规则:

1. 严禁任何具体人名。
2. 不套现成词库,从核心意象的**物理触感**出发,自创陌生、具体、可感的物象组合(雨落在什么上面、风吹动什么、手边有什么、听见什么、摸到什么)。
3. 少名词堆叠,多用"一个动作 + 一个物象"的短句。
4. 每段至少一个**未完成的动作**,制造"一半"感:手抬到一半、话说到一半、门推到一半、茶续到一半停住。
5. 对立情绪不直说,用**两件物象对照**:一件还留着,一件已收起;一件朝向 A,一件朝向 B。
6. 结尾以景结情:落在某个动作停住、或某个物象安静下来的画面,不把话说尽。
7. 回避清单:直白大字眼(一生、永远、永别、再也无法)、现代口语口水话、网络古风套话(渡口、三生石、惊鸿一类一眼 AI 的词)、说理句。
8. Bridge 段宜短、念白感(可半文半白);Outro 段宜少,留气声收尾空间。
9. 语气:叙事、电影感、留白;不煽情,不甜腻。

### 平台适配

- **Suno**(默认):v4.5+ 支持较长风格字段与 Exclude Styles 框;歌词框贴歌词+内联标签;Custom Mode 必开。风格字段超长会稀释权重,砍无关特征优于压缩语句。
- **Udio**:字段近似,风格描述同样特征化;段内手动延伸(manual extend)能力强,适合把弱副歌、念白段拆开逐段生成后拼接。提示词可稍长,但也遵循前重后轻。
- **海绵音乐/天工等中文平台**:纯中文风格字段可用,翻译表中英文词可意译回中文(如"气声、干声为主、短混响、句尾轻收");排除字段若无非负框,把最关键的 2~3 条否定以正向反义写进风格字段末尾(如"全程低音区男声"替代"不要高音")——这是唯一允许否定语义进正向字段的例外场景。
- 其他平台:套用三层结构,按其字段上限裁剪,优先保第 1、2 层。

### 抽卡迭代策略(输出提示词时随附给用户)

- 精细人声目标的现实命中率约十几次抽卡挑一次,提前告知用户。
- 每轮只改 1~2 个关键词:结果偏甜/偏暖→降人声音量、增气声比、减高频(写 breathier, darker, less bright),绝不加沙哑类词;副歌被推响→确认正向字段有 "restrained quiet chorus" 且排除字段有 belting;戏腔/特殊唱法不达标→要么移到段落标签强化,要么换更接近训练分布的措辞。
- 出现完全不想要的元素→优先移入排除字段,而不是在正向字段写"不要 X"。
- 保留每次的生成结果与所用提示词的对应关系,收敛更快。

## 输出格式

按用户平台交付四件套,代码块包裹、可直接复制:

1. **风格字段**(第 1 层)
2. **排除字段**(第 2 层)
3. **歌词字段**(第 3 层,含结构标签+内联演唱标签;用户自备歌词则标注改动仅限标签)
4. **迭代建议**:3~5 条针对性的"偏了就改哪个词"指引(按迭代策略节写)

交付后附一句期望管理:一次出片是运气,十次收敛是常态。

## 完整示例(供校准,勿照抄)

用户需求:中文男声,苍凉释怀,民谣摇滚,慢速,含一段压着唱的戏腔念白,结尾轻声释怀,主题"山海之间,一半理解一半算了"。

- 风格字段与排除字段:见第三步示例。
- 歌词字段(示意,展示标签用法):

```
[Intro]
[Verse 1: breathy half-spoken, low, phrases falling softly]
(雨落在具体物上的两三句,含一个未完成的动作)
[Chorus: restrained quiet lift, soft dynamics]
(两件物象对照,情绪不直说)
[Verse 2: breathy, low]
[Chorus: restrained quiet lift, soft dynamics]
[Bridge: low recitative, half-spoken with a hint of Chinese opera cadence, pressed, dark timbre]
(短,念白感)
[Outro: whispered, fading]
(一两行,以景结情)
```

自检要点:正向字段无否定词;情绪词已全部翻译为特征;特征均可回溯到用户需求;无与内核无关的堆砌;歌词无回避清单内容。
