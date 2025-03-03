import instapaper

I = instapaper.Instapaper("<oauth_consumer_key>", "<oauth_consumer_secret>")
I.login("<user_name>", "<password>")

b = instapaper.Bookmark(
    I, {"url": "https://www.biblegateway.com/passage/?search=John+1&version=NIV"}
)
b.save()
