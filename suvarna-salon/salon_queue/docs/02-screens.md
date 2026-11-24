## Screen 1: Home screen of Client (/)
- Salon Name, logo, tagline, contact number, area, 'open . Closes 8 PM' badge. 
- Previous booking history in the list: Date, Time, service type, stylist, price.
- Big Espresso fill, ivory label, subtle 0–2% shadow button to go Book Appoinment 


## Screen 2: Book Appoinment (/book_appoinment)
- All the services with the name and image are there int the card form within the button of show details.
- their details such as discription, duration, price, stylists are available on the screen with blur background with book slot button.
- the calander with timings opens and cutomer can select available date and time. A one nutton with choose stylist.
- stylist list with their current avalability status: (1) name: Priya, image in circle ,status: available (2) name: Jils, image in circle ,status: busy (3) name: Gaurang, image in circle ,status: On break,...
customer can click on the stylist.
- a confirmation button will book final appoinment.  

## Screen 3: My bookings (/my_bookings)
- clients can view their current, upcoming and previous booking. 
- all the details will be in the diffrent types of tables with all the details.

## Screen 3: Status (/status/:id)
- Token 'S-14' large, position '5th in line' - Circular countdown: 'about 5 min'; updates by itself 
- When 2nd in line: banner 'Start coming to the salon' 
- When called: full-screen gold 'It's your turn! Go to Ravi' 
- [ Cancel my spot ] with a confirmation pop-up

## Screen 4: Receptionist Dashboard (/reception) -tablet
- same as book appoinment but additionaly the receptionist will enter thier details such as name, age, gender, phone number of client.

## Screen 5: Stylist View (/stylist/:name) -phone
- Current cutomer details.
- A button to update the status to start and button changes the color to green with text 'currently serving' and after finishing the service stylist will click on that button agin and it shows 'Done' in blue color.

## Screen 6: Waiting Area TV (/display) — Large screen / TV
- Full-screen, auto-refreshing (every 5 s), no interaction required.
- Salon logo + current time in the header.
- Table of the next 7 appointments sorted by time:
  columns → Position | Token # | Client Name | Service | Stylist | Est. Time.
- Row highlights: 
    • CALLED (currently at chair) → warm gold row bg (#D4AF37).
    • NEXT UP (position 2) → soft sage green row bg (#E6EFEA).
    • Others → alternating ivory / white.
- Footer ticker: "Walk-ins welcome until 7:30 PM"

## Screen 7: Owner Dashboard (/admin) — Desktop / Tablet
- Protected by a simple PIN entry on first load (no full auth system).
- Top KPI strip (today): Total Appointments | Completed | Cancelled | Walk-ins.
- Bar chart: Hourly client flow for today (appointments per hour).
- Toggle → "This Month" switches bar chart to daily totals for the current month.
- Stylist Performance cards (one per stylist):
    • Clients served today / this month.
    • Average service time.
    • Sparkline of daily clients over last 7 days.
- Upcoming appointments table (next 3 hours): Token, Client, Service, Stylist, Time.
- Cancellations list (today): Time cancelled, Service, Stylist originally assigned.

