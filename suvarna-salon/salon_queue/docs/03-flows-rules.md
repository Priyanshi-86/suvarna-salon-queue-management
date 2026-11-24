## Flow: Remote Customer
- Opens home -> book appoinment -> chooses service -> selects time -> selects stylist -> confirms the booking.
- arrives at the location -> verifyies with thr receptionist -> waits into waiting are -> goes at stylist chair -> stylist updates the status from start to currently serving -> updates to done by stylist.

## Flow: Walk - in Customer
- Arrives at the locations -> ask for booking the slot to receptionist -> receptionist open the booking slot screen -> enters the details of that persong -> clicks on the book appoiment -> chooses service -> selects time -> selects stylist -> confirms the booking.
- arrives at the location -> verifyies with thr receptionist -> waits into waiting are -> goes at stylist chair -> stylist updates the status from start to currently serving -> updates to done by stylist.

## Rules:
- stylist status: start -> currently serving -> done.
- A stylist can have one client at a time.
- Waiting time ≈ total minutes of services ahead ÷ barbers working.
- Online book appoinment closes 30 min before closing; walk-ins still allowed. 
- Stylist on break -> Clients who chose them see 'Ravi is on break'.

## Test checklist:
[ ] Join with multiple serviveces: correct total time and price shown
[ ] Start/Done on Barber View updates Reception and TV
[ ] Close online queue -> Join button disabled with message
[ ] Language toggle switches all labels to Gujarati or hindi.
[ ] Waiting time goes down as customers finish.
[ ] Phone, tablet and TV windows all stay in sync