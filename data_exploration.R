library(dplyr)
library(tidyr)

reviews_list = list()
filenames = seq(0, 10700, 100)

for (index in seq_along(filenames)) {
  filename = filenames[index]
  filename = ifelse(filename == 0, "reviews.csv", sprintf("reviews_%s.csv", filename))
  header_bool = index == 0
  df = read.csv(paste0("data/", filename), stringsAsFactors = F)
  reviews_list[[index]] <- df
}

reviews_df <- bind_rows(reviews_list) %>%
  arrange(critic_id) %>%
  filter(!(movie_id == "" & movie_title == ""))

movies_with_ids <- reviews_df %>%
  filter(movie_title != "" & movie_id != "") %>%
  distinct(movie_id, .keep_all = T) %>%
  select(movie_title, movie_id)

fix_missing_vals <- reviews_df %>%
  filter(movie_id == "") %>%
  left_join(movies_with_ids, by = c("movie_title"))

reviews_sample <- reviews_df %>%
  sample_n(1000) %>%
  arrange(critic_id)

t <- reviews_sample %>%
  select(-critic_rating, -movie_review_blurb,
         -movie_title) %>%
  spread(movie_id, critic_meter_score)


t1 <- t
