def scraper_links(url):
    article = ""
    domain = url.split()[1]
    url = url.split()[0]
    print(url)
    
    ## TRY TO SEE IF THE LINK EXISTS. ELSE JUST RETURN NONE AND MOVE ON.
    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "lxml")
        info = json.loads(soup.find('script', type='application/ld+json').text)
    except:
        article = "Link is Dead"
        other_info = {'headline': None, 'image': None, 'description': None, 'keywords': None, '@type': None}
        return(article, other_info)

    ## IF LINK WORKS, USE JSON ELSE USE BEAUTIFUL SOUP TO GET DATA.
    try:
        article = info["articleBody"]
    except:
        try:
            if domain == "glamour":
                for posts in soup.find_all('div', {'class' : 'article__content'}):
                    article = posts.text
            elif domain == "teenvogue":
                for posts in soup.find_all('div', {'class' : 'content article-content'}):
                    article = posts.text
            elif domain == "wmagazine":
                for posts in soup.find_all('div', {'class' : 'body-text'}):
                    article = posts.text
            elif domain == "allure":
                for posts in soup.find_all('div', {'class' : 'article-body'}):
                    article = posts.text
            elif domain == "cntraveler":
                for posts in soup.find_all('div', {'class' : 'article-body'}):
                    article = posts.text
            elif domain == "architecturaldigest":
                for posts in soup.find_all('div', {'class' : 'article-content-main'}):
                    article = posts.text
            elif domain == "vogue":
                for posts in soup.find_all('div', {'class' : 'article-copy--body'}):
                    article = posts.text
        except:
            article = "Article Not Found"

            
    ## USE JSON TO EXTRACT IMAGE INFO & OTHER STUFF ELSE RETURN NONE
    
    try:        
        attributes = { 'headline', 'image', 'description', 'keywords', '@type'}
        other_info = { k:v for k,v in info.items() if k in attributes }
    except:
        other_info = { 'headline': None, 'image': None, 'description': None, 'keywords': None, '@type': None}
   

    return(article, other_info)