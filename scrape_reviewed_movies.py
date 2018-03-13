from bs4 import BeautifulSoup
import urllib2
import httplib
import pandas as pd
import time
import ssl

critics_df = pd.DataFrame.from_csv("data/rt_critics.csv", index_col=None)

base_url = "https://www.rottentomatoes.com/critic/{}/movies"

def fetch_soup(url, try_num = 1):
	print(url + " try: " + str(try_num))
	req = urllib2.Request(url,
		headers={'User-Agent' : "Magic Browser"})

	
	try:
		con = urllib2.urlopen(req, timeout = 2)
		result = BeautifulSoup(con, "lxml")
	except (urllib2.URLError, httplib.IncompleteRead) as e:
		print("URLError or IncompleteRead: " + url + " " + str(e))
		time.sleep(10)
		if (try_num >= 100):
			raise ValueError("Too many URL errors. Stopping.")
		else:
			try_num += 1
			return fetch_soup(url, try_num)
	except ssl.SSLError:
		print("Timeout Error: " + url)
		time.sleep(3)
		try_num += 1
		return fetch_soup(url, try_num)
	else:
		return result

def scrape_table_data(soup, reviews_dict):
	table = soup.find("table", class_ = "table-striped").find_all("tr")
	table = table[1:]
	for row in table:
		cells = row.find_all("td")
		col_1 = cells[0].find("span")
		if col_1 is not None:
			critic_meter_score = col_1.get("class")[2]
			critic_rating = col_1.get("title").strip()
		else:
			critic_meter_score = None
			critic_rating = None
		# -- skip 2nd column in html (movie aggregate rating)
		col_2 = cells[2]
		movie_id = col_2.find("a").get("href").replace("/m/", "")
		movie_title = col_2.get_text().strip()
		col_3 = cells[3]
		movie_review_blurb = col_3.find("a").previousSibling.string.strip()
		if ind == 0:
			most_recent_pub = col_3.find("a").get_text().replace("&dash;", "").strip()
		reviews_dict["critic_id"].append(critic_id)
		reviews_dict["critic_rating"].append(critic_rating)
		reviews_dict["critic_meter_score"].append(critic_meter_score)
		reviews_dict["movie_id"].append(movie_id)
		reviews_dict["movie_title"].append(movie_title)
		reviews_dict["movie_review_blurb"].append(movie_review_blurb)

	return(reviews_dict)


reviews_dict = {"critic_id" : [], "critic_meter_score" : [],
				"critic_rating" : [], "movie_id" : [], "movie_title" : [],
				"movie_review_blurb": []}

# critic_id = "dave-white"
ind = 0

# print(scrape_table_data(fetch_soup("https://www.rottentomatoes.com/critic/dave-white/movies?page=38"), reviews_dict))


for i in range(len(critics_df["critic_id"])):
	critic_id = critics_df.iloc[i]["critic_id"]
	ids = [critic_id, critics_df.iloc[i]["critic_id_2"],
		   critics_df.iloc[i]["critic_id_3"]]
	ids = [item for item in ids if not pd.isnull(item)]
	for c_id in ids:
		url = base_url.format(c_id)
		soup = fetch_soup(url)
		reviews_dict = scrape_table_data(soup, reviews_dict)
		next_page = soup.find("ul", class_ = "pagination").find_all("a")[3].get("href")
		while(next_page != "#"):
			next_url = url + next_page
			soup = fetch_soup(next_url)
			reviews_dict = scrape_table_data(soup, reviews_dict)
			next_page = soup.find("ul", class_ = "pagination").find_all("a")[3].get("href")
	ind += 1
	if (ind % 100 == 0):
		reviews_df = pd.DataFrame(reviews_dict).sort_values(["critic_id"])
		reviews_df.to_csv("data/reviews_{}.csv".format(ind),  index = False, encoding = "utf-8")
		reviews_dict = {"critic_id" : [], "critic_meter_score" : [],
				"critic_rating" : [], "movie_id" : [], "movie_title" : [],
				"movie_review_blurb": []}

reviews_df = pd.DataFrame(reviews_dict).sort_values(["critic_id"])
reviews_df.to_csv("data/reviews.csv", index = False, encoding = "utf-8")

