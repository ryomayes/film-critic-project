from bs4 import BeautifulSoup
import urllib2
import pandas as pd
from string import ascii_lowercase

base_url = "https://www.rottentomatoes.com"
critic_dict = {"critic_id": [], "critic_name": []}

def fetch_soup(url):
	req = urllib2.Request(url,
		headers={'User-Agent' : "Magic Browser"})

	con = urllib2.urlopen(req)
	return BeautifulSoup(con, "lxml")

for author_type in ["authors", "legacy_authors"]:
	for letter in ascii_lowercase:
		url = base_url + "/critics/" + author_type + "?letter=" + letter
		print(url)
		soup = fetch_soup(url)
		critic_wrappers = soup.find_all("p", class_ = "critic-names")
		for critic_wrapper in critic_wrappers:
			items = critic_wrapper.find_all("a")
			name_text = items[0].get_text().strip()
			name_link = base_url + items[0]["href"]
			critic_dict["critic_id"].append(name_link.replace("https://www.rottentomatoes.com/critic/", ""))
			critic_dict["critic_name"].append(name_text)

critic_df = pd.DataFrame(critic_dict).sort_values(["critic_id"])

# Format critics
# ---
# Duplicates

duplicated_critics = ["c-hooper-trask", "damon-smith", "david-wilson",
					"delia-harrington", "james-sullivan", "kevin-thomas",
					"lara-williams", "roger-smith"]

dups = critic_df.groupby("critic_name").filter(lambda x: len(x) > 1)
verified_dups = dups[dups["critic_id"].str.contains('|'.join(duplicated_critics))]

critic_df = critic_df[~critic_df["critic_id"].isin(verified_dups["critic_id"])]

verified_dups = verified_dups.join(verified_dups.groupby(["critic_name"])["critic_id"].shift(-1), rsuffix='_2')

verified_dups = verified_dups.iloc[::2]

critic_df = critic_df.append(verified_dups).sort_values(["critic_id"])

# ---
# Joint authorship

duos = critic_df[critic_df["critic_id"].str.contains("-and-")]

duos_expanded = duos["critic_id"].str.split("-and-", 1, expand = True).rename(columns = {0: "id_1", 1: "id_2"})

duos = duos.join(duos_expanded)


match_id_1 = critic_df.merge(duos,
	left_on = "critic_id", right_on = "id_1", how = "inner")[["critic_id_x", "critic_name_x", "critic_id_y"]]

match_id_2 = critic_df.merge(duos,
	left_on = "critic_id", right_on = "id_2", how = "inner")[["critic_id_x", "critic_name_x", "critic_id_y"]]

both = match_id_1.append(match_id_2).sort_values(["critic_id_x"])


multiple_collabs = both.groupby("critic_id_x").filter(lambda x: len(x) > 1)
both = both[~both["critic_id_x"].isin(multiple_collabs["critic_id_x"])]
multiple_collabs = multiple_collabs.join(multiple_collabs.groupby(["critic_id_x"])["critic_id_y"].shift(-1), rsuffix='_alt')
multiple_collabs = multiple_collabs.iloc[::2]


both = both.append(multiple_collabs).sort_values(["critic_id_x"])

critic_df = critic_df[~critic_df["critic_id"].isin(both["critic_id_y"]) & ~critic_df["critic_id"].isin(both["critic_id_x"])]

both = both.rename(columns = {"critic_id_x" : "critic_id",
	"critic_id_y" : "critic_id_2", "critic_id_y_alt" : "critic_id_3",
	"critic_name_x": "critic_name"
	})


critic_df = critic_df.append(both).sort_values(["critic_id"])
critic_df.to_csv("data/rt_critics.csv", index = False, encoding='utf-8')

