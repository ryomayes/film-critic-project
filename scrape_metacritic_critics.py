from bs4 import BeautifulSoup
import urllib2
import pandas as pd
from string import ascii_lowercase

base_url = "http://www.metacritic.com"
critic_dict = {"critic_name": [], "critic_link": [], "critic_pub": []}

def fetch_soup(url):
	req = urllib2.Request(url,
		headers={'User-Agent' : "Magic Browser"})

	con = urllib2.urlopen(req)
	return BeautifulSoup(con, "lxml")

for letter in ascii_lowercase:
	url = base_url + "/browse/movies/critic/name/" + letter
	while url is not None:
		print(url)
		soup = fetch_soup(url)
		critic_wrappers = soup.find_all("td", class_ = "title_wrapper")
		for critic_wrapper in critic_wrappers:
			items = critic_wrapper.find_all("a")
			name_text = items[0].get_text().strip().replace("\n", "")
			name_link = base_url + items[0]["href"]
			pub_text = items[1].get_text().strip().replace("\n", "")
			critic_dict["critic_name"].append(name_text)
			critic_dict["critic_link"].append(name_link)
			critic_dict["critic_pub"].append(pub_text)

		find_next = soup.find("a", {"class": "action", "rel": "next"})
		if (find_next is not None):
			url = base_url + find_next["href"]
		else:
			url = None

critic_df = pd.DataFrame(critic_dict)
critic_df.to_csv("data/metacritic_critics.csv", encoding = "utf-8")

