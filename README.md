<style scoped>
table {
  font-size: 12px;
}
</style>

# ACGN-Biased-Multivariate-Analysis
ACGN-Biased-Multivariate-Analysis. Includes information theory, type relation mappings between different types, and genres' adaptations..

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


- 条目之间的关联（Subject-relations）：
  | **Key**              | **含义**                                                                 |
  |----------------------|--------------------------------------------------------------------------|
  | `subject_id`         | 作品 ID                                                                  |
  | `relation_type`      | 关联类型 (1 = adaptation, 1004 = ...)                                                                |
  | `related_subject_id` | 关联作品ID                                                               |
  | `order`              | 关联排序                                                                 |




  ## Arranged dataset as csv files

  目标是分析时序变化(via: linear mixed model)和静态分布(static distribution)，利用ANOVA, ANCOVA 模型及针对name, tag的简单自然语言处理以修正参数向量(设计矩阵)。

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
  | `played_amount`        | 阅读人数，等于看过数+在看数(favorite.done $+$ favorite.doing)                                   |
  | `series`          | 是否为系列作品（单行本等）                                            |                                                                |
  | `tags`            | 标签（部分，按amount排序）                                                              |
  | `score`           | 评分                                                                     |
  | `sk`   | 评分的偏度(skewness)，采用 **score_details** 分布的standard Pearson product-moment coefficient       $ \frac{1}{\sqrt{n}}\frac{\sum_i{(\bar{x}-x_i)^3}}{\left(\sum_i{(\bar{x}-x_i)^2}\right)^{3/2}},\,\scriptsize{x_i={​score\_details}[k]}$                       |
  | `comment_amount`    | 评分人数 ($\sum_{k=1}^{count}\small{​score\_details}[k]$)                                         |

## 

  
