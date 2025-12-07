# ACGN-Biased-Multivariate-Analysis
ACGN-Biased-Multivariate-Analysis. Includes Fourier information type relation mappings between different genres' adaptation..

## Add database manually

download main dataset release on Bangumi [releases](https://github.com/bangumi/Archive/releases/tag/archive) and add path to main folder.

源数据描述 (description of original data). 主要使用subject.jsonlite文件
- 条目（Subject）：
  
  | **Key**           | **含义 (Definition)**                                                                 |
  |-------------------|--------------------------------------------------------------------------|
  | `id`              | 条目 ID                                                                  |
  | `type`            | 作品类型，1表示漫画，2表示动画，3表示音乐，4表示游戏，6表示三次元             |
  | `name`            | 条目名                                                                   |
  | `name_cn`         | 条目简体中文名                                                            |
  | `infobox`         | 条目原始 **wiki** 字符串                                                   |
  | `platform`        | 条目平台，即剧场版/TV/Anime等等                                            |
  | `summary`         | 条目简介                                                                  |
  | `nsfw`            | 是否为NSFW（Not Safe For Work，是否含有成人内容）                           |
  | `date`            | 发行日期                                                                  |
  | `favorite`        | 收藏状态（想看、看过、在看、搁置、抛弃）                                     |
  | `series`          | 是否为系列作品（单行本等）                                                  |                                                                |
  | `tags`            | 标签（部分）                                                              |
  | `score`           | 评分                                                                     |
  | `score_details`   | 评分细节，包含各个评分级别的分布                                            |
  | `rank`            | 类别内排名                                                                |
  | `meta_tags`       | 公共标签（由维基人管理）                                                   |

- 人物（Person）：
  | **Key**           | **含义**                                                                 |
  |-------------------|--------------------------------------------------------------------------|
  | `id`              | 人物 ID                                                                  |
  | `name`            | 人物名                                                                   |
  | `type`            | 类型，1表示个人，2表示公司，3表示组合                                      |
  | `career`          | 人物职业                                                                  |
  | `infobox`         | 原始 **wiki** 字符串                                                      |
  | `summary`         | 人物简介                                                                  |
  | `comments`        | 评论/吐槽数                                                               |
  | `collects`        | 收藏数                                                                   |

- 角色（Character）：
  | **Key**           | **含义**                                                                 |
  |-------------------|--------------------------------------------------------------------------|
  | `id`              | 角色 ID                                                                  |
  | `role`            | 角色类型，1表示角色，2表示机体，3表示组织，4...                             |
  | `name`            | 角色名                                                                   |
  | `infobox`         | 原始 **wiki** 字符串                                                      |
  | `summary`         | 角色简介                                                                  |
  | `comments`        | 评论/吐槽数                                                               |
  | `collects`        | 收藏数                                                                    |

- 章节（Episode）:
  | **Key**           | **含义**                                                                   |
  |-------------------|-----------------------------------------------------------------------------|
  | `id`            | 章节 ID                                                                      |
  | `name`          | 章节名称                                                                      |
  | `name_cn`       | 章节简体中文名                                                                 |
  | `description`   | 章节介绍                                                                      |
  | `airdate`       | 播出时间                                                                      |
  | `disc`          | 该章节存在于第几张光盘                                                         |
  | `duration`      | 播放时长                                                                      |
  | `subject_id`    | 作品 ID                                                                      |
  | `sort`          | 序话，该章节是第几集                                                            |
  | `type`          | 类型，0表示正篇，1表示特别篇，2表示OP，3表示ED，4表示Trailer，5表示MAD，6表示其他    |

- 条目之间的关联（Subject-relations）：
  | **Key**              | **含义**                                                                 |
  |----------------------|--------------------------------------------------------------------------|
  | `subject_id`         | 作品 ID                                                                  |
  | `relation_type`      | 关联类型                                                                 |
  | `related_subject_id` | 关联作品ID                                                               |
  | `order`              | 关联排序                                                                 |

- 条目与角色的关联（Subject-characters）：
  | **Key**              | **含义**                                                                 |
  |----------------------|--------------------------------------------------------------------------|
  | `character_id`      | 角色 ID                                                                   |
  | `subject_id`        | 作品 ID                                                                   |
  | `type`              | 角色类型：1 主角，2 配角，3 客串                                            |
  | `order`             | 作品角色列表排序：按 (`type`, `order`) 排序，不保证 `order` 连续            |

- 条目与人物的关联（Subject-persons）：
  | **Key**              | **含义**                                                                 |
  |----------------------|--------------------------------------------------------------------------|
  | `person_id`          | 人物 ID                                                                  |
  | `subject_id`         | 作品 ID                                                                  |
  | `position`           | 担任职位                                                                 |

- 人物与角色的关联（Person-characters）：
  | **Key**              | **含义**                                                                 |
  |----------------------|--------------------------------------------------------------------------|
  | `person_id`          | 人物 ID                                                                  |
  | `subject_id`         | 条目 ID                                                                  |
  | `character_id`       | 对应条目中的角色 ID                                                       |
  | `summary`            | 概要                                                                     |


  ## Arranged dataset as csv files

  目标是分析时序变化和静态分布，利用三参数ANCOVA 模型及针对name, tag的简单自然语言处理以修正参数向量。

  | **Key**           | **含义 (Definition)**                                                                 |
  |-------------------|--------------------------------------------------------------------------|
  |  `rank`           | 类别内排名                                                                  |
  | `type`            | 作品类型，1表示漫画，2表示动画，3表示音乐，4表示游戏，5表示小说            |
  | `name`            | 条目名                                                                   |
  | `name_cn`         | 条目简体中文名                                                            |
  | `episode_number`  | 条目集数或话数，来自原 **infobox:{}**                                                 |
  | `platform`        | 条目平台细分？，即 OST(0)/?(2)/剧场版(3)/3D-Netflix(5)/TV Anime(1)/ Novel(1002)/Game(4001) /Manga,Comics (1001) /公式书(1006)                               |
  | `nsfw`            | 是否为NSFW（Not Safe For Work，是否含有成人内容）                           |
  | `date`            | 发行日期 (一般情况)                                                                 |
  | `played_amount`        | 阅读人数，等于看过数+在看数                                     |
  | `series`          | 是否为系列作品（单行本等）                                                 |                                                                |
  | `tags`            | 标签（部分，按amount排序）                                                              |
  | `score`           | 评分                                                                     |
  | `sk`   | 评分的偏度(skewness)，采用 **score_details** 分布的standard Pearson product-moment coefficient                              |
  | `comment_amount`    | 评分人数                                              |

## 

  
