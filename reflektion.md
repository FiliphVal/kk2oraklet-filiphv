
Säkerhetsaspekter
Hantering av API-nycklar
Applikationen använder dotenv för att läsa känsliga variabler från en lokal .env-fil, vilken är blockerad i .gitignore så att den aldrig hamnar på GitHub. Om filen checkas in blir hemligheterna publika. Det finns bottar som skannar ständigt efter nycklar som råkat läckats i repon och detta  kan leda till datastöld eller enorma kostnader. Om en läcka sker måste nyckeln tas bort med det samma och git historiken rensas. Man har själv märkt när man gjort egna repon och kollat statistik att det alltid finns typ 50 unique people som har clonaet ner repot och detta är för att de letar efter läckta nycklar.

Risker med filuppladdningar 
När man låter folk ladda upp vilka filer som helst till en server så bjuder man nästan in till problem. Någon med dåliga avsikter skulle kunna skicka in skadlig kod som körs på servern så att de kan hacka den, eller så laddar de bara upp helt sjukt stora filer för att fylla upp minnet och få hela applikationen att krascha. Jag löste detta genom att lägga in två enkla spärrar i min kod för att göra den säker. Den första spärren kollar filformatet så att appen bara godkänner filer som slutar på .csv. Den andra spärren kollar storleken på filen innan den ens hinner läsas in, så om filen är större än 10 MB så stoppas den direkt för att skydda serverns minne.

Prompt Injection 
Det här är när en användare försöker lura AI modellen genom att skriva dolda instruktioner i själva frågan, som till exempel att skriva att modellen ska strunta i alla tidigare regler och berätta ett skämt istället. För att stoppa det här i min kod så har jag byggt min promptbuilder så att användarens fråga automatiskt stängs in mellan två tydliga taggar, START och END. Ovanför dessa taggar har jag gett modellen en instruktion som säger att den bara får kolla på statistiken från Pandas och att den absolut måste ignorera allt som användaren försöker lura i den inuti frågetaggarna.

Dataskydd (GDPR)
Problem med nuvarande utformning : Om någon laddar upp ett dataset som innehåller riktiga personuppgifter så krockar appen ganska hårt med GDPR direkt. Det beror på att filen just nu sparas helt öppet och oskyddat i serverns tillfälliga minne. Sen skickas den datan vidare rakt in i AI modellen. Även om modellen bara får se den sammanfattade statistiken, så kan det finnas unika textrader eller väldigt konstiga extremvärden i siffrorna som gör att man ändå kan lista ut exakt vilken person det handlar om.

Krav för produktionssättning
 Om den här tjänsten skulle rullas ut på riktigt så hade det krävts en hel del ändringar. För det första måste man informera användarna om hur deras data används och få deras godkännande. Man hade också behövt bygga en funktion som automatiskt rensar bort känsliga kolumner som namn, personnummer eller mejladresser innan datan ens hinner analyseras eller skickas till AI modellen. Det som är väldigt positivt med min nuvarande lösning är dock att jag kör modellen helt lokalt. Eftersom ingen data skickas iväg till några extrna molntjänster eller företag på nätet så lämnar informationen aldrig vår egen miljö, vilket är ett stort plus för GDPR.

AI risker och ansvar
Begränsningar hos små modeller Små modeller, som till exempel SmolLLM2 på 135M parametrar, har väldigt svårt att hålla reda på mycket information och långa texter på samma gång. När jag testade den märkte jag att den blev helt förvirrad när den fick en hel hög med beskrivande statistik i prompten från Pandas. Den började hitta på saker, klippte av ord mitt i meningar och fastnade i oändliga textloopar där den bara upprepade sig. Den lyckades inte ens fatta vad datasetet handlade om eller att det var golfstatistik den kollade på, ett exempel var när jag frågade vad datasetet handlade om och den svarar att sporten heter “SG/Putts” vilket är en kolumn i datasetet. Det var därför jag valde att uppgradera till Qwen/Qwen2.5-0.5B-Instruct istället. Den modellen är fortfarande så pass liten att den laddas ner snabbt och körs utan problem lokalt på en vanlig laptop CPU, men den har tillräckligt med kapacitet för att faktiskt förstå sammanhanget och svara rätt på frågorna.

Konkret exempel på bias 
Modeller svarar nästan alltid bäst på sådant som de har sett mest av i sin träning innan. Om man ställer en öppen fråga till AI modellen som till exempel "Vem är bäst i det här datasetet?", så finns det en stor risk att den bara går på vad den redan tror baserat på sin träningsdata. Den kanske svarar Tiger Woods bara för att han är den mest kända golfspelaren i världen, istället för att faktiskt läsa av siffrorna och göra en ärlig analys av statistiken som den skulle analysera.

Testning av tillförlitlighet
 För att vara helt säker på att applikationen är stabil och inte kraschar när folk använder den har jag skrivit automatiska tester med pytest och fastAPIs testclient. Dessa tester kollar att appen stoppar felaktiga beteenden, till exempel att den skickar tillbaka rätt felkoder om man försöker ställa frågor eller hämta statistik innan man ens har laddat upp en fil, eller om man försöker ladda upp en fil med fel format.

Designval
Fördelar med Runnable mönstret 
Att dela upp appen med runnable mönstret där man länkar ihop stegen med operatorn (prompt_builder | llm_runner | response_parser) gör koden ren och städad. Varje liten klass har sitt eget unika ansvar. Promptbuilder fixar bara texten, LLMRunner sköter snacket med AI modellen och responseparser paketerar slutsvaret. Det blir extremt mycket lättare att underhålla än om man hade tryckt in precis all logik i en enda stor funktion. Om jag vill ändra på något i min prompt så behöver jag bara ändra i den klassen, utan att riskera att förstöra för AI exekveringen eller JSON parseringen längre ner i kedjan.

Största tekniska hindret och dess lösning
 Mitt absolut största problem under arbetet var nätverksanropen i början. Jag försökte först köra modeller online via Hugging Faces API, men jag fick bara krascher och felmeddelanden om rate limits hela tiden. Efter att ha felsökt detta en hel dag utan att hitta någon lösning bestämde jag mig för att strunta i api lösningen helt och hållet och köra modellen lokalt på min egen dator istället via transformers pipeline. Tack vare att jag hade byggt hela flödet som en flexbel runnable kedja blev det här bytet väldigt smidigt, eftersom jag bara behövde uppdatera koden i mitt exekveringssteg. När SmolLLM2 sen inte gav vettiga svar lokalt kunde jag tack vare samma flexibla kod enkelt byta ut den mot den smartare Qwen modellen och knappt behöva ändra om någoti koden.


