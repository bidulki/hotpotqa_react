SYSTEM_MESSAGE = """Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation, and Action can be two types:
(1) Search[entity], which searches the exact entity on Wikipedia and returns the paragraph if it exists. If not, it will return some similar entities to search.
(2) Finish[answer], which returns the answer and finishes the task."""

INSIGHTS = """ 
- Final answer can exactly found at observation or question or ('yes' or 'no').   
- If a search result confirms part of the information but not the specific detail needed, use a targeted search query combining the confirmed information with the missing detail. 
- If the final answer is a person's name or group's name, ensure it matches the most complete and accurate form as found in the search results, including any middle names, additional identifiers, and correct fullname spelling.  
- If you could not search document, it is good method which instead searching in similar documents
- If you use Search[entity], It is bad to use sentence entity, please use simple entity which contains only one object
- If you use Finish[answer], answer must be exactly copied only in part of observation or question, exclude if answer is 'yes' or 'no' 
- If you think answer is plural form but the search result is singular form, you must use singular form as answer
- Please at Finish[answer], if answer is human's name, Submit his full name as the correct answer. Don't miss the middle name"""

FEWSHOTS = ["""Question: Which is the tallest skyscraper, Manhattan Life Insurance Building or 1717 Broadway?
Thought 1: I need to search Manhattan Life Insurance Building and 1717 Broadway, and find out which one is the tallest skyscraper.
Action 1: Search[Manhattan Life Insurance Building]
Observation 1: The Manhattan Life Insurance Building was a 348 ft tower at 64-66 Broadway in New York City completed in 1894 to the designs of the architects of Kimball & Thompson and slightly extended north in 1904 making its new address 64-70 Broadway.  It was the first skyscraper to pass 100 m in Manhattan.
Thought 2: The Manhattan Life Insurance Building is 348 ft tall. I need to search 1717 Broadway next.
Action 2: Search[1717 Broadway]
Observation 2: 1717 Broadway is a skyscraper located in Manhattan, New York City, United States.  At 750 feet high, it is the tallest hotel in North America.  The building contains two hotels, the Courtyard New York Manhattan/Central Park and the Residence Inn New York Manhattan/Central Park, with a total of 639 rooms.  The glass-clad building is located on the Northwest corner of 54th Street and Broadway.
Thought 3: 1717 Broadway is 750 ft tall, which is taller than the Manhattan Life Insurance Building. So the tallest skyscraper is 1717 Broadway.
Action 3: Finish[1717 Broadway]""",
"""Question: Who was the head coach of the 2016 New York Giants?
Thought 1: I need to search for the head coach of the 2016 New York Giants.
Action 1: Search[2016 New York Giants head coach]
Observation 1: Could not find [2016 New York Giants head coach]. Similar: [List of New York Giants head coaches, 2016 New York Giants season, 2017 New York Giants season, List of New York Jets head coaches, 2014 New York Giants season]
Thought 2:  Since I couldn't find the specific head coach for 2016, I should look up the 2016 New York Giants season to find out who the head coach was.
Action 2: Search[2016 New York Giants season]
Observation 2: The 2016 season was the New York Giants' 92nd season in the National Football League, their seventh playing their home games at MetLife Stadium and the first under head coach Ben McAdoo.
Thought 3: The head coach of the 2016 New York Giants was Ben McAdoo. I need to search for Ben McAdoo's full name
Action 3: Search[Ben McAdoo]
Observation 3: Benjamin Lee "Ben" McAdoo (born July 9, 1977) is an American football coach who is the head coach of the New York Giants of the National Football League (NFL).
Thought 4: The head coach of the 2016 New York Giants was Benjamin Lee "Ben" McAdoo
Action 4: Finish[Benjamin Lee "Ben" McAdoo]""",
"""Question: Which was built first, the Theodosius Cistern or the German Fountain?
Thought 1: I need to search Theodosius Cistern and the German Fountain, find out when they were built, and determine which one was built first.
Action 1: Search[Theodosius Cistern]
Observation 1: The Theodosius Cistern (Greek: Κινστέρνα Θεοδοσίου , Turkish: Şerefiye Sarnıcı ) is one of many ancient cisterns of Constantinople that lie beneath the city of Istanbul, Turkey.  The modern entrance is in Piyer Loti Caddesi, Fatih.
Thought 2: The Theodosius Cistern was built in ancient Constantinople. I should search for the German Fountain next.
Action 2: Search[German Fountain]
Observation 2: The German Fountain (Turkish: "Alman Çeşmesi" German: "Deutscher Brunnen" ) is a gazebo styled fountain in the northern end of old hippodrome (Sultanahmet Square), Istanbul, Turkey and across from the Mausoleum of Sultan Ahmed I.  It was constructed to commemorate the second anniversary of German Emperor Wilhelm II's visit to Istanbul in 1898.  It was built in Germany, then transported piece by piece and assembled in its current site in 1900.  The neo-Byzantine style fountain's octagonal dome has eight marble columns, and dome's interior is covered with golden mosaics.
Thought 3: The German Fountain was built in 1900 to commemorate the second anniversary of German Emperor Wilhelm II's visit to Istanbul in 1898. Since Theodosius Cistern was built in ancient Constantinople, Theodosius Cistern was built first
Action 3: Finish[Theodosius Cistern]""",
"""Question:  "The World Is in My Hands" is a song recorded by a German dance music act with an estimated net worth of over how much?
Thought 1: I need to search for "The World Is in My Hands" song and find the German dance music act that recorded it, then determine their estimated net worth.
Action 1: Search[The World Is in My Hands]
Observation 1: "The World Is in My Hands" is a song written by Yann Peifer, Manuel Reuter and Andres Ballinas and recorded by German dance act Cascada.  The track was confirmed as the third and final single taken from their latest compilation album “The Best of Cascada” that was released on digital retailers on March 29, 2013 via Zooland Records.
Thought 2: The song "The World Is in My Hands" was recorded by German dance act Cascada. Now I need to find the estimated net worth of Cascada.
Action 2: Search[Cascada net worth]
Observation 2: Could not find [Cascada net worth]. Similar: [Cascada, The Best of Cascada, Cascada discography, Casilda, Cașunca]
Thought 3: Instead Search for Cascada net worths, I will search for Cascada
Action 3: Search[Cascada]
Observation 3: Cascada ( ; Spanish for "Waterfall") is a German dance music act founded in 2004 by singer Natalie Horler, DJ Manian and DJ Yanou.  They are best known for their hit singles "Everytime We Touch", "What Hurts the Most" and "Evacuate the Dancefloor".  Cascada have sold over 30 million albums worldwide, an estimated 15 million digital downloads, and have an estimated net worth of over 7 million.  Cascada represented Germany at the Eurovision Song Contest 2013 in Malmö, Sweden.
Thought 4: Cascada's estimated net worth of over 7 million.
Action 4: 7 million""",
"""Question: Are The Verve and Richard Ashcroft from the same country?
Thought 1: I need to search The Verve and Richard Ashcroft, find their origins, and determine if they are from the same country.
Action 1: Search[The Verve]
Observation 1: The Verve were an English rock band formed in Wigan in 1990 by lead vocalist Richard Ashcroft, guitarist Nick McCabe, bass guitarist Simon Jones and drummer Peter Salisbury.  Guitarist and keyboard player Simon Tong later became a member.
Thought 2: The Verve formed in England, I should search for Richard Ashcroft's origin
Action 2: Search[Richard Ashcroft]
Observation 2: Richard Paul Ashcroft (born 11 September 1971) is an English singer and songwriter.  He was the lead singer and occasional rhythm guitarist of the alternative rock band The Verve from their formation in 1990 until their original split in 1999.  He became a successful solo artist in his own right, releasing three UK top three solo albums.  The Verve reformed in 2007 but again broke up by summer 2009.  Ashcroft then founded a new band, RPA & The United Nations of Sound, and released a new album on 19 July 2010.  On 22 February 2016 Ashcroft announced his fourth solo album, "These People", set for release 20 May 2016.  Chris Martin of Coldplay has described Ashcroft as "the best singer in the world".
Thought 3: Richard Ashcroft is from England. And he was the lead singer of English rock band The Verve, So they are from the same country
Action 3: Finish[yes]""",
"""Question: Are eith Nicotiana or Encyclia genus of pine trees?
Thought 1: I need to search Nicotiana and Encyclia, find out if they are genus of pine trees, and determine if either of them are.
Action 1: Search[Nicotiana]
Observation 1: Nicotiana ( ) is a genus of herbaceous plants and shrubs of the family Solanaceae, that is indigenous to the Americas, Australia, south west Africa and the South Pacific.  Various "Nicotiana" species, commonly referred to as tobacco plants, are cultivated as ornamental garden plants. " N. tabacum" is grown worldwide for production of tobacco leaf for cigarettes and other tobacco products.
Thought 2: Nicotiana is a genus of herbaceous plants, not pine trees. I need to search Encyclia next.
Action 2: Search[Encyclia]
Observation 2: Encyclia is a genus of orchids.  The genus name comes from Greek "enkykleomai" ("to encircle"), referring to the lateral lobes of the lip which encircle the column.  The abbreviation in the horticultural trade is E.
Thought 3: Encyclia is not a genus of pine trees either. Neither Nicotiana nor Encyclia are genus of pine trees.
Action 3: Finish[no]"""]