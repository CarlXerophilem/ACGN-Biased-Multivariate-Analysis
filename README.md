# ACGN-Biased-Multivariate-Analysis
ACGN-Biased-Multivariate-Analysis. Includes Fourier information type relation mappings between different genres' adaptation..

## add database manually

download main dataset release on Bangumi [releases](https://github.com/bangumi/Archive/releases/tag/archive) and add path to main folder.

description:
- 条目（Subject）：
  
  | **Key**           | **含义**                                                                 |
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
  |-------------------|--------------------------------------------------------------------------|
  | `tags`            | 标签（部分）                                                              |
  | `score`           | 评分                                                                     |
  | `score_details`   | 评分细节，包含各个评分级别的分布                                            |
  | `rank`            | 类别内排名                                                                |
  |-------------------|--------------------------------------------------------------------------|
  | `meta_tags`       | 公共标签（由维基人管理）                                                   |
