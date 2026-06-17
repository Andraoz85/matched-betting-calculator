# Matched Betting Calculator

En Streamlit-app för matched betting, byggd för svenska användare. Appen innehåller en manuell matched betting-kalkylator och en oddsmatcher som kan hämta odds från svenska spelbolag via The Odds API och jämföra dem med Smarkets-layodds när dessa finns tillgängliga.

- Appen finns deployad på <a>https://oddsmatcher.streamlit.app/</a>
- För att få live odds från de svenska spelbolagen så måste du ha en api nyckel från <a>https://the-odds-api.com/</a>

## Vad Appen Kan Användas Till

Appen kan hjälpa dig att:

- räkna ut rekommenderad lay stake
- räkna ut exchange liability
- jämföra vinst/förlust mellan bookmaker-utfall och exchange-utfall
- beräkna rating i procent
- räkna på Free Bet SNR (Stake Not Returned)
- räkna på Free Bet SR (stake Returned)
- räkna på risk free bets
- jämföra svenska bookmakerodds mot Smarkets-layodds
- se ungefärlig API-credit-kostnad innan du hämtar liveodds
- spara senaste hämtade oddsmatcher-resultat när du växlar mellan flikarna i appen

## Så Använder Du Appen

Appen har två huvudflikar:

```text
Calculator
Oddsmatcher
```

### Calculator

Calculator-fliken används för manuella beräkningar.

Fyll i:

- back stake
- back odds
- bookmaker commission
- lay odds
- lay commission
- calculator mode
- currency symbol

Appen räknar sedan ut:

- recommended lay stake
- exchange liability
- profit if bookmaker bet wins
- profit if exchange lay wins
- difference between outcomes
- rating %

### Oddsmatcher

Oddsmatcher-fliken används för att hämta bookmakerodds och jämföra dem mot Smarkets-layodds.

Du kan välja:

- Demo data
- Live: The Odds API

Demo data kräver ingen API-nyckel och kan användas för att testa appens layout och funktioner.

Live-läget kräver en API-nyckel från The Odds API.

## Hämta API-Nyckel

För att använda liveodds behöver du en API-nyckel från The Odds API.

Gå till:

```text
https://the-odds-api.com/
```

Skapa ett konto och välj en plan. Gratisplanen brukar räcka för enklare testning, men antalet credits per månad är begränsat.

När du har skapat kontot får du en API-nyckel. Den ser ut ungefär som en lång rad bokstäver och siffror.

## Var Du Lägger In API-Nyckeln

I appen:

1. Öppna fliken `Oddsmatcher`.
2. Välj `Live: The Odds API`.
3. Klistra in din API-nyckel i fältet `The Odds API key`.
4. Välj sport.
5. Välj vilka svenska bookmakers du vill hämta odds från.
6. Tryck på `Fetch live oddsmatcher results`.

API-nyckeln ska inte delas med andra. Den används bara för att appen ska kunna hämta odds från The Odds API.

## Svenska Bookmakers

Oddsmatchern är begränsad till spelbolag/bookmaker-nycklar från The Odds API:s svenska marknad.

Listan innehåller:

- ATG
- Betinia
- BetMGM SE
- Betsson
- CampoBet
- Nya Expekt
- Hajper
- LeoVegas SE
- Mr Green
- NordicBet
- 888sport SE
- Svenska Spel
- Unibet SE

Smarkets används separat som exchange-källa.

## API Credits

The Odds API använder credits när du hämtar odds.

Appen visar en uppskattad kostnad innan du hämtar liveodds.

En förenklad modell är:

```text
credits = antal marknader x antal bookmaker-grupper
```

Appen hämtar just nu bara marknaden:

```text
h2h
```

Om alla svenska bookmakers plus Smarkets är valda blir det ungefär:

```text
13 svenska bookmakers + Smarkets = 14 keys
14 keys = 2 grupper
kostnad = cirka 2 credits per hämtning
```

Tips för att spara credits:

- hämta bara en sport åt gången
- välj bara de bookmakers du faktiskt vill jämföra
- undvik att trycka fetch om och om igen i onödan
- använd Demo data när du bara testar appen

## Varför Odds Kan Skilja Sig Från Spelbolagets Sida

Odds kan ändras snabbt. Det betyder att oddsen i appen ibland kan skilja sig från oddsen som visas direkt på spelbolagets egen webbplats.

Möjliga orsaker:

- The Odds API visar en något äldre snapshot
- bookmakeroddsen ändrades precis
- appen använder cache för att spara API-anrop
- odds kan skilja sig beroende på marknad, region eller inloggat läge

Appen visar uppdateringstid där The Odds API skickar med sådan information.

Kontrollera alltid oddsen manuellt innan du placerar ett spel.

## Calculator Modes

### Normal Matched Bet

Används för vanliga kvalspel.

Rating:

```text
rating = back odds / lay odds * 100
```

### Free Bet SNR

SNR betyder stake not returned. Det innebär att insatsen inte betalas tillbaka om free bet-spelet vinner.

Formel:

```text
lay stake = free bet stake * (back odds - 1) / (lay odds - lay commission)
```

### Free Bet SR

SR betyder stake returned. Det innebär att bonusinsatsen behandlas som återbetald om bookmaker-spelet vinner.

### Risk Free Bet

Används för risk free bet-upplägg. Appen visar hedge-resultatet innan eventuell senare återbetalning eller free bet-konvertering.

## Viktigt Att Veta

- Appen placerar inga spel automatiskt.
- Appen garanterar inte vinst.
- Odds och likviditet kan ändras snabbt.
- Kontrollera alltid bookmaker-villkor, odds, exchange-likviditet och provision innan du spelar.
- Användaren ansvarar själv för sina spelbeslut.

## Disclaimer

Matched betting och annat spelande kan innebära ekonomisk risk. Appen är endast ett kalkyl- och researchverktyg och ska inte ses som finansiell rådgivning. Kontrollera alltid aktuella odds, regler, bonusvillkor, provision och lokala lagar innan du spelar.
