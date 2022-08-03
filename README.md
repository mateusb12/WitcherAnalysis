# Witcher analysis
Witcher analysis is a project (powered by Thu Vu Data Analytics video) in which the books from The Witcher series are analysed, and the characters are listed according to their revelance among the books

**Main pipeline**
- Books are analysed using NER library, and an entity dataframe is created where each individual book sentence is attached to its own entity list
- A characters.csv file is scrapped from a the witcher fandom wiki, in order to list all available characters in each book
- Entities from the NER analysis are compared with the characters.csv file, in order to create a "character-only entities" dataframe
- This dataframe is used for network plots using PyVis library

## How to run
Scrapping the character wiki
```
webscrapping/witcher_scrapping.py
__main()
```
Plot the book network
```
wrap/wrapper.py
__main()
```
Plot characters importance over time
```
importance_over_time/character_importance.py
__main()
```