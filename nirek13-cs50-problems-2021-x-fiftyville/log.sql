-- Keep a log of any SQL queries you execute as you solve the mystery.

--theif took money out of atm on firfe street
select account_number from atm_transactions where day = 28 and month = 7 and atm_location = "Firfer Street";

--Sometime within ten minutes of the theft, I saw the thief get into a car in the courthouse parking lot and drive away. If you have security footage from the courthouse parking lot, you might want to look for cars that left the parking lot in that time frame.
--I don't know the thief's name, but it was someone I recognized. Earlier this morning, before I arrived at the courthouse, I was walking by the ATM on Fifer Street and saw the thief there withdrawing some money.
--As the thief was leaving the courthouse, they called someone who talked to them for less than a minute. In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow. The thief then asked the person on the other end of the phone to purchase the flight ticket.

account_number
28500762,28296815,76054385,49610011,16153065,86363979,25506511,81061156,26013199,

-- next steps chech phone call logs
receiver | caller
(996) 555-8899 | --(130) 555-0289
(892) 555-8872 | --(499) 555-9472
(375) 555-8161 | (367) 555-5533
(717) 555-1342 | --(499) 555-9472
(676) 555-6554 | (286) 555-6063
(725) 555-3243 | (770) 555-1861
(910) 555-3251 | --(031) 555-6622
(066) 555-9701 | (826) 555-1652
(704) 555-2131 | --(338) 555-6650

person ids of possible subjects

686048,948985,514354,458378,395717,396669,467400,449774,438727

phone numbers of suspects

"(826) 555-1652","(770) 555-1861","(286) 555-6063","(367) 555-5533"

names of possible suspects

name
Russell
Ernest

possible license plates for subjects

"5P2BI95","94KL13X","6P58WS2","4328GD8","G412CB7","L93JTIZ","322W7JE","0NTHK55"
flights leaving fiftyville
1,6,17,34,35