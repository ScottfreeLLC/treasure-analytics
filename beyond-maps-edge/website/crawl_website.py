import json
from firecrawl import FirecrawlApp

# Initialize Firecrawl with your API key
app = FirecrawlApp(api_key="fc-25025dd1ff684b849e5033fde434e74e")

# Start the crawl job for the website (replace with the actual URL)
# For example, a Bears Ears-related site like https://www.blm.gov/programs/national-conservation-lands/utah/bears-ears-national-monument
crawl_result = app.crawl_url(
	'https://treasure.quest/en/',
	params={
		'limit': 10000,  # Adjust based on the expected number of pages
		'allowBackwardLinks': True,  # Follow links to parent directories if needed
		'allowExternalLinks': False  # Avoid crawling external sites
	}
)

# Check if the crawl was successful and capture the result
if crawl_result:
	# Pretty-print the crawl result in JSON format with indentation
	pretty_output = json.dumps(crawl_result, indent=4, sort_keys=True)
	with open('crawl_output.json', 'w') as f:
		f.write(pretty_output)
else:
	print("Crawl failed or returned no results.")