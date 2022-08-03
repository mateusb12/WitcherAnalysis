# Witcher analysis
Witcher analysis is a project (powered by Thu Vu Data Analytics video) in which the books from The Witcher series are analysed, and the characters are listed according to their revelance among the books

**Main pipeline**
- Books are analysed using NER library, and an entity dataframe is created where each individual book sentence is
attached to its own entity list

![sample image](https://i.imgur.com/iKg2nyM.png)

- A characters.csv file is scrapped from a the witcher fandom wiki, in order to list all available characters in each book
![sample image](https://i.imgur.com/yM99aVF.png)
- Entities from the NER analysis are compared with the characters.csv file, in order to create a "character-only
entities" filtered dataframe

![sample image](https://i.imgur.com/UC3ekE0.png)
- The last dataframe is used for network plots using PyVis library
![sample image](https://i.imgur.com/d1l1ToA.png)
- You can also try importance plots
![sample image](https://i.imgur.com/XLigFm2.png)
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