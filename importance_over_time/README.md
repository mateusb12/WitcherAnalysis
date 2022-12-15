
# Character importance over time
Character importance is a measure of how much a given character is involved in the interactions and events of a book. In NLP context, this can be determined by analyzing the text of a book and using various techniques to identify the characters and their interactions. Once these interactions have been identified, they can be used to create a social graph, which is a visual representation of the relationships between the characters.

![Network graph](https://i.imgur.com/1UINepX.png)

*Character interactions on book 2 "New Moon"*


The degree centrality metric is one way to measure character importance in a social graph. This metric assigns a value to each character based on how many interactions they have with other characters. In this context, the higher the degree centrality, the more important the character is considered to be.

![Character importance table](https://i.imgur.com/nOpI2Tr.png)

*Character importance aggregated throughout 3 books*

From the table above we can create a beautiful chart that indicates how much each character has evolved throughout a series of books

![enter image description here](https://i.imgur.com/R61L9FB.png)

*Importance over time chart*
    
## How to run  
You can run it by executing the plot_series_importance function on importance_over_time folder
![enter image description here](https://i.imgur.com/ztl6QJc.png)
```  
importance_over_time/character_importance_calculator.py  
__main()  
```  

