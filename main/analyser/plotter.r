# R Script: ACGN_Plotter.R
library(tidyverse)
library(data.table)

# 1. Load Latest Data
df <- fread("D:/Dataset/25_11_26/modern_subject.csv")

# 2. Filter & Process for Plotting
plot_data <- df %>%
  filter(type == 2, is_stable == TRUE) %>%
  mutate(
    Source_Label = case_when(
      from_type == 1 ~ "Manga",
      from_type == 5 ~ "Novel",
      from_type == 4 ~ "Game",
      from_type == 0 ~ "Original",
      TRUE ~ "Other"
    )
  ) %>%
  filter(Source_Label %in% c("Manga", "Novel", "Game", "Original"))

# ==========================================
# PLOT 1: Boxplot of Quality by Source
# ==========================================
p1 <- ggplot(plot_data, aes(x = Source_Label, y = score, fill = Source_Label)) +
  geom_boxplot(alpha = 0.7, outlier.size = 0.5, outlier.alpha = 0.3) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3, fill = "white") + # Diamond = Mean
  labs(
    title = "Anime Quality Distribution by Source Material",
    subtitle = "Based on Bangumi.tv User Ratings (Stable > 1 Year)",
    x = "Source Material",
    y = "User Score",
    fill = "Source"
  ) +
  theme_minimal() +
  scale_fill_brewer(palette = "Set2")

ggsave("D:/Dataset/plot_quality_by_source.png", plot = p1, width = 10, height = 6)
print(p1)

# ==========================================
# PLOT 2: Relationship: Popularity vs Quality
# ==========================================
p2 <- ggplot(plot_data, aes(x = log1p(played_amount), y = score, color = Source_Label)) +
  geom_point(alpha = 0.3, size = 1) +
  geom_smooth(method = "lm", se = FALSE) +
  labs(
    title = "Popularity vs. Quality by Source",
    x = "Log(Played Amount)",
    y = "Score"
  ) +
  theme_minimal() +
  facet_wrap(~Source_Label)

ggsave("D:/Dataset/plot_popularity_vs_quality.png", plot = p2, width = 12, height = 8)
print(p2)
