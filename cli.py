from race_scraper_LL import Scrape

# 1. Initiera objekt
# 2. Hämta loppnamn
# 3. Gå igenom resultatlistorna för varje lopp
race = Scrape()
race.get_races('Lidingöloppet 30', '30')
race.iterate_pages()