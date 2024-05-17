# Lyhyt OpenAI API-intro

Tässä repossa testailu tehdään seleniumkirjastolla ja hyödyntäen OpenAI:n Assistantteja.


## Työkalut

Repossa on tehtynä seuraavat työkalut:
- ChatGPTAssistant kirjasto - kirjasto kaikkeen keskusteluun openai:n kanssa
- openai_image.py - kuvan lataaminen chatgpt:lle (ei assistentille)



## Robot Testit

Löytyy tiedostosta tests.robot

### "Test Assistant Usage"

Perus testi jolla voi verifioida että voidaan tehdä uusi assistantti ja keskustella sen kanssa 

Ajokomento:
```robot -i prepare tests.robot```


### "Playwright python"

Perus testi jolla voi verifioida että pystytään laittamaana web sivun sisältö fileen ja lähettämään se assistantille 

Ajokomento:
```robot -d logs -i playwrightpy tests.robot```


