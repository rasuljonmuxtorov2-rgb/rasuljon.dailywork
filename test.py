import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
#                        TOKEN
# ============================================================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ============================================================
#                     SUPER ADMIN ID
# ============================================================
SUPER_ADMIN_ID = 1638174769

# ============================================================
#                      MA'LUMOTLAR
# ============================================================
admins = {SUPER_ADMIN_ID}
allowed_users = {}   # {uid: {"ism": .., "familya": .., "guruh": ..}}
kutayotganlar = {}   # {uid: {"ism": .., "familya": .., "guruh": ..}}

FANLAR = {
    "avto":       "🛣 Avto yo\'llar texnologiyasi",
    "matematika": "📐 Matematika",
    "fizika":     "⚡ Fizika",
    "biologiya":  "🌿 Biologiya",
}

TESTLAR = {
    "avto": [
        {"savol": "Barxan qumlarini zichlash … yordamida olib boriladi?", "variantlar": ["tebratuvchi katoklar", "zichlovchi katoklar", "mushtli", "plitali"], "togri": "tebratuvchi katoklar"},
        {"savol": "Tuproqning hisobiiy ko’rsatkichlariga nimalar kiradi?", "variantlar": ["elastiklik moduli, Puasson koeffitsiyenti, ichki ishqalanish burchagi, tishlashish koeffitsiyenti", "suriluvchanligi, ichki ishqalanish burchagi", "qattiqliq, eziluvchanligi elastiklik moduli", "elastiklik moduli, tishlashish koeffitsiyenti"], "togri": "elastiklik moduli, Puasson koeffitsiyenti, ichki ishqalanish burchagi, tishlashish koeffitsiyenti"},
        {"savol": "Ib toifali yo‘llarning qatnov qismi kengligi", "variantlar": ["3.75", "3.0", "4.0", "3.6"], "togri": "3.75"},
        {"savol": "V toifali yolning qatnov qismi kengligi", "variantlar": ["6", "7", "7.5", "16.5"], "togri": "6"},
        {"savol": "Avtomobil yollarini qurishning nechta xususiyatlari mavjud?", "variantlar": ["4", "5", "7", "3"], "togri": "4"},
        {"savol": "Brigadaga ajratilgan uchastka deb nimaga aytiladi?", "variantlar": ["ish qamroviga", "ish fronti", "frontga", "hammasi"], "togri": "ish qamroviga"},
        {"savol": "Qurilishda ishlab chiqarish nechta omilga bogliq va uning tasirida boladi?", "variantlar": ["4", "5", "3", "7"], "togri": "4"},
        {"savol": "BMT elon qilgan Dunyo hamjamiyatining turgun rivojlanish tamoyillarida nechta shart qoyilgan?", "variantlar": ["3", "4", "2", "6"], "togri": "3"},
        {"savol": "Texnologik loyihalash nechta turga bolinadi?", "variantlar": ["2", "3", "7", "5"], "togri": "2"},
        {"savol": "Texnik meyorlash-tarifni toping?", "variantlar": ["bu ishlab chiqarishni zaxiralari sarfini izlanishdagi ilmiy tizim", "bajarish shartlarini izlanishi", "samaradorligini izlanishi", "bu ijrochilar, mehnat qurollarini izlani"], "togri": "bu ishlab chiqarishni zaxiralari sarfini izlanishdagi ilmiy tizim"},
        {"savol": "Rekultivatsiya nima?", "variantlar": ["yerni tabiatga tiklab qaytarish", "qarovsiz yerni qaytarish", "aholiga tiklab qaytarish", "aholiga berish"], "togri": "yerni tabiatga tiklab qaytarish"},
        {"savol": "Kotarmaning baladligi necha metr bolganda yol poyi noqulay sharoitda deb hisoblanadi?", "variantlar": ["baladligi 12 metrdan katta bolmagan kotarmalar", "balandligi 11 metrdan kata kotarmalarda", "balandligi 13 metrdan kata kotarmalarda", "balandligi 15 metrdan kata kotarmalarda"], "togri": "baladligi 12 metrdan katta bolmagan kotarmalar"},
        {"savol": "Oymaning chuqurligi necha metr bolganda yol poyi noqulay sharoitda deb hisoblanadi?", "variantlar": ["chuqurligi 12 metrdan katta oymalarda", "chuqurligi 11 metrdan katta oymalarda", "chuqurligi 13 metrdan katta oymalarda", "chuqurligi 15 metrdan katta oymalarda"], "togri": "chuqurligi 12 metrdan katta oymalarda"},
        {"savol": "Mustahkamligi koproq gruntlarni yol poyining qaysi qismiga joylashtirish kerak?", "variantlar": ["yuqori qismiga ishlatiladi", "pastki qismiga", "orta qismiga", "togri kelgan qismiga"], "togri": "yuqori qismiga ishlatiladi"},
        {"savol": "Kotarma qurish uchun ishlatiladigan gruntlar nechchi guruhga bolinadi?", "variantlar": ["4", "5", "3", "7"], "togri": "4"},
        {"savol": "Kotarmaning yuqori qismiga (1,0-1,5 m) qaysi turdagi gruntlarni ishlatish kerak?", "variantlar": ["yaxshi va mustahkamroq", "tabiiy", "maydalash", "qumli"], "togri": "yaxshi va mustahkamroq"},
        {"savol": "Agar kotarma har xil turdagi gruntlardan qurilsa, ular qandan joylashtirilishi kerak?", "variantlar": ["har bir turdagi grunt alohida gorizontal qatlam shaklida yotqizilish kerak", "grunt alohida vertikal qatlam shaklida yotqizilish kerak", "grunt gorizontal, vertikal shaklida yotqizilish kerak", "aralash qatlam shaklida yotqizilish kerak"], "togri": "har bir turdagi grunt alohida gorizontal qatlam shaklida yotqizilish kerak"},
        {"savol": "Yol poyi yuzasini tekislash, kotarma va oymaning yon qiyaliklarini hamda ariqlarni mustahkamlash, osimlik qatlamini tiklash qaysi ish turiga kiradi?", "variantlar": ["pardozlash ishlari", "yengil ishlari", "asosiy ishlar", "yakuniy ishlar"], "togri": "pardozlash ishlari"},
        {"savol": "Yol poyini qurishda ish tarkibi togri korsatilgan qatorni aniqlang?", "variantlar": ["tayyorgarlik ishlari, kotarmani qurish va oymani oyishdagi asosiy ishlar, pardozlash ishlari", "kotarmani qurish va oymani oyishdagi asosiy ishlar", "pardozlash ishlari kotarmani qurish va oymani oyish", "pardozlash ishlari va oymani oyishdagi asosiy ishlar"], "togri": "tayyorgarlik ishlari, kotarmani qurish va oymani oyishdagi asosiy ishlar, pardozlash ishlari"},
        {"savol": "Gruntlarni 100 m masofaga surishni qaysi mexanizm yordamida bajarish maqsadga muvofiq?", "variantlar": ["buldozerda", "skreper", "avtogreyder", "ekskavator"], "togri": "buldozerda"},
        {"savol": "Gruntlarni tashish masofasi 100 metrdan 3 kilometrgacha bolganda yer ishlarini qaysi mexanizm yordamida bajarish maqsadga muvofiq?", "variantlar": ["skreperda", "buldozer", "avtogreyder", "ekskavator"], "togri": "skreperda"},
        {"savol": "Qaysi turdagi gruntlarni ishlatishda muzlash amalda ahamiyatga ega emas?", "variantlar": ["tog jinsli gruntlarni", "gilli", "tabiiy", "qumli"], "togri": "tog jinsli gruntlarni"},
        {"savol": "Zichlash koeffitsientining qiymati qaysi meyoriy hujjatda keltirilgan?", "variantlar": ["SHNQ 2.05.02 - 07", "SHNQ 3.05.02 - 08", "SHNQ 4.02.02 - 04", "SHNQ 2.05.02 96"], "togri": "SHNQ 2.05.02 - 07"},
        {"savol": "Yer yuzasiga chiqqan va qoplama, oqim, gumbaz ko‘rinishida qotib qolgan, magmalardan hosil bo‘lgan turli xil tog‘ jinslari qanday nomlanadi?", "variantlar": ["quyma (effuziv) tog‘ jinslari", "kremniy", "metamorfik", "parchalangan"], "togri": "quyma (effuziv) tog‘ jinslari"},
        {"savol": "Massasi 4-5 t titratuvchi katok bilan zichlaganda grunt qatlami necha sm bolishi mumkin?", "variantlar": ["40-50", "60-80", "80-100", "100-150"], "togri": "40-50"},
        {"savol": "Katta massali titratuvchi katok bilan zichlaganda grunt qatlami necha sm bolishi mumkin?", "variantlar": ["60-80", "70-90", "80-100", "100-150"], "togri": "60-80"},
        {"savol": "Katta massali titratuvchi katok bilan zichlaganda tog jinslarini qatlami necha sm bolishi mumkin?", "variantlar": ["100-150", "120-160", "150-180", "170-180"], "togri": "100-150"},
        {"savol": "Quvur va koprik qoziqlari oldida gruntlarni zichlashning nechta xususiyatlari mavjud ?", "variantlar": ["12", "11", "9", "13"], "togri": "12"},
        {"savol": "Tosh maydalovchi mashina maydalash sistemasiga ko‘ra nechta turlarga bo‘linadi?", "variantlar": ["5 turga", "6 turga", "4 turga", "8 turga"], "togri": "5 turga"},
        {"savol": "Yo‘lning geometrik o‘qining joylardagi holatini belgilovchi chiziq - bu?", "variantlar": ["trassa", "egri", "aylanma", "to‘g‘ri"], "togri": "trassa"},
        {"savol": "Qurilish ishlari boshlanguncha joylardagi yol holatini qaytadan aniqlashtirish va mustahkamlash jarayoni nima deyiladi?", "variantlar": ["trassani tiklash", "trassa loyihasi", "trassasi", "mustahkamlash"], "togri": "trassani tiklash"},
        {"savol": "Yol mitaqasida uchrovchi mayda toshlar (hajmi 1 m3) qaysi mexanizm bilan uning tashqarisiga chiqariladi?", "variantlar": ["bulldozer bilan", "skreper", "ekskavator", "avtogreyder"], "togri": "bulldozer bilan"},
        {"savol": "Butakeskichning unumdorligini oshirish uchun nima qilish kerak?", "variantlar": ["pichogini otkirlab borish", "ikki smenada ishlatish", "uch smenada ishlatish", "koeffitsientini oshirish"], "togri": "pichogini otkirlab borish"},
        {"savol": "Burilish burchagini uchidagi ustunchaga yoziladigan malumotlar togri korsatilgan qatorni aniqlang?", "variantlar": ["burilish burchagi, egri radiusi, tangensi va bissektrisasi", "egrining burchagi, tangensi va bissektrisasi", "burilish burchagi, bissektrisasi va domeri", "egrining burchagi, bissektrisasi va domeri"], "togri": "burilish burchagi, egri radiusi, tangensi va bissektrisasi"},
        {"savol": "Grunt osimlik qatlamini kesish va surish boyicha buldozer ish unumdorligini aniqlashda kotarilish yoki qiyalikni hisobga olinadigan koeffitsiyent togri korsatilgan qatorni aniqlang?", "variantlar": ["0,5 2,25", "0,6 2,54", "0,7 2,66", "0,8 2,76"], "togri": "0,5 2,25"},
        {"savol": "Grunt osimlik qatlamini kesish va surish boyicha bulldozer ish unumdorligini aniqlashda kotarilishni hisobga olinadigan koeffitsiyent togri korsatilgan qatorni aniqlang?", "variantlar": ["0,5", "0,6", "0,4", "0,8"], "togri": "0,5"},
        {"savol": "Yoldan suv qochiruvchi inshootlar nechta guruhga bolinadi?", "variantlar": ["2", "3", "7", "5"], "togri": "2"},
        {"savol": "Yon ariqlarni chuqurligi necha metr bolishi kerak?", "variantlar": ["0,5 metrdan oshmasligi kerak", "0,6 metdlan oshmasligi kerak", "0,4 metrdan oshmasligi kerak", "0,8 metrdan oshmasligi kerak"], "togri": "0,5 metrdan oshmasligi kerak"},
        {"savol": "Ariqlarni yoni va tubini mustahkamlashda qollaniladigan plita olchami togri korsatilgan qatorni aniqlang.", "variantlar": ["40x40x12", "50x50x13", "30x30x11", "70x70x15"], "togri": "40x40x12"},
        {"savol": "Drenaj tizimida korish quduqlari oraliq masofalari necha metr boladi", "variantlar": ["60-80 metr", "90-95 metr", "100-175 metr", "160-185 metr"], "togri": "60-80 metr"},
        {"savol": "Drenaj tizimida korish quduqlari materiallari nimalar hisoblanadi?", "variantlar": ["diametri 1 m bolgan temir beton halqalar", "diametri 1,2 m bolgan temir beton halqalar", "diametri 2 m bolgan temir beton halqalar", "diametri 2,2 m bolgan temir beton halqalar"], "togri": "diametri 1 m bolgan temir beton halqalar"},
        {"savol": "Grunt qatlami birining ustiga boshqasini ketma-ketlikda kotarmaning kerakli balandligiga yetkaziladigan qurilish usuli togri korsatilgan qatorni aniqlang?", "variantlar": ["qatlamlab yotqizish usuli", "yarus usuli", "zig-zak usuli", "sakkiz usuli"], "togri": "qatlamlab yotqizish usuli"},
        {"savol": "Yon rezervlar bor bolgan yol yer maydonini necha marta kop egallaydi?", "variantlar": ["2", "2.5", "3", "3.5"], "togri": "2"},
        {"savol": "Kotarma balandligi 0,6-0,8 m, ayrim hollarda 1 m bolganda gruntlar olinadigan joy togri korsatilgan qatorni aniqlang.", "variantlar": ["yon rezerv", "karyer", "oyma", "maxsusjoy"], "togri": "yon rezerv"},
        {"savol": "Osimlik qatlami yaratish bilan yon qiyalik nechta usul bilan mustahkamlanadi?", "variantlar": ["2", "3", "1", "5"], "togri": "2"},
        {"savol": "Osimlik qatlami yaratish bilan yon qiyalik birinchi usul bilan mustahkamlanganda necha sm qalinlikda osimlik qatlami yotqiziladi?", "variantlar": ["11-15 sm", "4 sm", "4-6 sm", "6-8 sm"], "togri": "11-15 sm"},
        {"savol": "Yol poyini qoya toshli gruntlarda qurish usuli togri korsatilgan qatorni aniqlang.?", "variantlar": ["portlatish yoli bilan", "bulldozer bilan", "skreper bilan", "ekskavator bilan"], "togri": "portlatish yoli bilan"},
        {"savol": "Yol poyini qoya toshli gruntlarda qurish portlatish yoli bilan amalga oshirilganda portlatish ishlarining bahosi necha foizni tashkil etadi?", "variantlar": ["55-60", "50-55", "45-55", "40-45"], "togri": "55-60"},
        {"savol": "Burgulash burchagi vertikalga nisbatan ntcha gradus bolishi mumkin?", "variantlar": ["0-90", "45", "180", "150"], "togri": "0-90"},
        {"savol": "BES-219 rusumli snaryad unumdorligi sharoshkanikiga nisbata oshishi qaysi qatorda togri korsatilgan?", "variantlar": ["2-3", "1-2", "1.5-2", "1.5-1.8"], "togri": "2-3"},
        {"savol": "Burgulashning ish unumdorligi qattiq tog jinsida smenada necha metrga teng?", "variantlar": ["15-20", "12-15", "10-12", "8-10"], "togri": "15-20"},
        {"savol": "Portlatish moddalarining zaryadlarining portlatish bilan bajariladigan ishlar deb aytiladi?", "variantlar": ["Portlatish ishlari", "bajariladiganr", "moddalar", "portlatish"], "togri": "Portlatish ishlari"},
        {"savol": "Ekskavator va transport vositalarining ish unumdorligini oshirish uchun burgulash ishlari necha smenada olib borilishi lozim?", "variantlar": ["2-3", "1-2", "3-4", "1-6"], "togri": "2-3"},
        {"savol": "Chuqurligi necha metrdan katta oyma va yarim oymalar qazish balandligi boyicha bir necha yarusda burgulash portlatish ishlari bilan birgalikda olib boriladi.", "variantlar": ["6-8", "5-7", "3-5", "1-3"], "togri": "6-8"},
        {"savol": "Qoya gruntlarida yarim oymani qazish loyihaviy kesimning qaysi pogonasidan boshlanadi?", "variantlar": ["250", "280", "300", "260"], "togri": "250"},
        {"savol": "Qoya gruntlarida yarim oymani qazish loyihaviy kesimning qaysi pogonasidan boshlanadi? (Takroriy)", "variantlar": ["yuqori", "quyi", "orta", "oqi"], "togri": "yuqori"},
        {"savol": "Shorlangan gruntlar nechta turga bolinadi?", "variantlar": ["3", "4", "2", "6"], "togri": "3"},
        {"savol": "Zichlash va surishda gruntni yopishib qolmasligi uchun suvga chidamsiz shorxokli va taqirli gruntlarni namligi qancha bolganda namlikka keltiriladi.", "variantlar": ["(0,9) qulay", "(0,88) qulay", "(0,96) qulay", "(0,94) qulay"], "togri": "(0,9) qulay"},
        {"savol": "Yol toshamasining turlari, qaplamaning asosiy korinishlari va ularni qollash doirasi qaysi meyoriy hujjatda berilgan?", "variantlar": ["SHNQ 2.05.02-07", "SHNQ 3.03.03-08", "SHNQ 4.04.02-06", "SHNQ 2.05.04-04"], "togri": "SHNQ 2.05.02-07"},
        {"savol": "Yol toshamasi turlari togri korsatilgan qatorni aniqlang?", "variantlar": ["mukammal, yengillashtirilgan, otuvchi, oddiy", "yengillashtirilgan, otuvchi, oddiy", "kapital yengillashtirilgan, otuvchi,", "mukammal, yengillashtirilgan,"], "togri": "mukammal, yengillashtirilgan, otuvchi, oddiy"},
        {"savol": "SHNQ 2.05.02-07 ga asosan mayda donali asfaltbeton qoplamaning eng kam qalinligi necha santimetr qabul qilinishi kerak ?", "variantlar": ["3-5", "4-6", "6-8", "8-10"], "togri": "3-5"},
        {"savol": "Asfaltbeton va sementbetonlar qanday materiallar qatoriga kiradi?", "variantlar": ["bikir plastik", "nobikir", "noplastik", "plastik"], "togri": "bikir plastik"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida Ia toifali yolning kondalang kesim uzunligi qancha?", "variantlar": ["28,5", "27,5", "15", "9"], "togri": "28,5"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida Ib toifali yolning kondalang kesim uzunligi qancha.", "variantlar": ["27,5", "8", "12", "10"], "togri": "27,5"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida II toifali yolning kondalang kesim uzunligi qancha.", "variantlar": ["15", "12", "10", "8"], "togri": "15"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida III toifali yolning kondalang kesim uzunligi qancha.", "variantlar": ["12", "13", "11", "15"], "togri": "12"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida IV toifali yolning kondalang kesim uzunligi qancha", "variantlar": ["10", "9", "11", "17"], "togri": "10"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida V toifali yolning kondalang kesim uzunligi qancha?", "variantlar": ["8", "7", "9", "11"], "togri": "8"},
        {"savol": "SHNQ 2.05.02-07 ning 5-jadvalida Ia toifali yolning harakat jadalligi qancha?", "variantlar": ["14000 dan yuqori", "2000-6000", "4000-6000", "200 gacha"], "togri": "14000 dan yuqori"},
        {"savol": "Mustahkamlangan gruntlarni xususiyatlarini oshirish maqsadida .. qollaniladi", "variantlar": ["sirt-faol", "sifatli", "sement", "kop"], "togri": "sirt-faol"},
        {"savol": "Suvga toyingan mustahkamlangan grunt namunalarining siqilishdagi mustahkamlik chegarasi 200 haroratda, birinchi sinf mustahkamlik boyicha necha MPa teng?", "variantlar": ["4,0-2,5", "2,5-2,0", "2,0-1,2", "1,5-1,0"], "togri": "4,0-2,5"},
        {"savol": "Ortacha zichlikni olchov birligi", "variantlar": ["kg/m3", "kg/m2", "g/sm2", "MPa"], "togri": "kg/m3"},
        {"savol": "Tokma zichlik qaysi qurilish materialalari uchun aniqlanadi", "variantlar": ["sochiluvchan qurilish materiallari uchun", "zich qurilish materiallari uchun", "tolali qurilish materiallari uchun", "govak materiallar uchun"], "togri": "sochiluvchan qurilish materiallari uchun"},
        {"savol": "Elastiklik nima", "variantlar": ["materialning kuch ostida shakl ozgarishi va kuch olinganidan keyin boshlangich shakl va olchamlariga kelish xossasi", "materialning kuch ostida shakli ozgarishi", "materialning uzilmasdan chozilishi", "materialning egiluvchanligi"], "togri": "materialning kuch ostida shakl ozgarishi va kuch olinganidan keyin boshlangich shakl va olchamlariga kelish xossasi"},
        {"savol": "Bitumlarni chaqnash harorati", "variantlar": ["180", "170", "160", "150"], "togri": "180"},
        {"savol": "Kalendar grafikni tuzishda eng asosiy belgilanadigan korsatkichlar -", "variantlar": ["barcha ishlarning hajmlari va vaqt boyicha navbati", "asosiy ishlarning hajmlari boyicha navbati", "ikkinchi darajali ishlar boyicha navbati", "barcha ishlarning faqat bajarish navbati"], "togri": "barcha ishlarning hajmlari va vaqt boyicha navbati"},
        {"savol": "Eng oddiy, texnologik bir jinsli va tashkiliy ajralmas qurilish jarayoni bu ?", "variantlar": ["ish operatsiyasi", "ish jarayoni", "texnologik", "ishchi karta"], "togri": "ish operatsiyasi"},
        {"savol": "Soatlik grafiklar tartibini korsatadi", "variantlar": ["zaxvatkalarda mashinalardan turli vaqtda foydalanish", "potoklarda turli vaqtda foydalanish", "asosiy mashinalardan foydalanish", "potoklarda vaqtdan foydalanish"], "togri": "zaxvatkalarda mashinalardan turli vaqtda foydalanish"},
        {"savol": "Soatlik grafiklardagi chiziqlarda nimalar korsatiladi?", "variantlar": ["mashina rusumi, uning potokdagi raqami va foydalanish koeffitsiynti", "uning davlat va potokdagi raqami", "uning davlat va potokdagi raqami va foydalanishi", "uning yuk kotarish qobiliyati va foydalanish"], "togri": "mashina rusumi, uning potokdagi raqami va foydalanish koeffitsiynti"},
        {"savol": "Osimlik qatlamini kochirishdan maqsad?", "variantlar": ["yo‘l pоyi yon bаg‘r qiyaliklаrini o‘simlik qаtlаmli grunt bilаn mustаhkаmlаsh vа аtrоf muhitni himоya qilish", "yo‘l pоyini zаmin bilаn mustаhkаm birikishini tа’minlаsh.", "yo’l pоyi оstidаn suv yo‘li hоsil bo‘lmаslikni tа’minlаsh", "yo‘l pоyi buzilishidаn sаqlаsh"], "togri": "yo‘l pоyi yon bаg‘r qiyaliklаrini o‘simlik qаtlаmli grunt bilаn mustаhkаmlаsh vа аtrоf muhitni himоya qilish"},
        {"savol": "Yo‘l mintаqаsini tаyyorlаsh ishlаrini kеtmа-kеtligi tаrkibini ko‘rsаting?", "variantlar": ["trаssаni tiklаsh vа mustаhkаmlаsh, mintаqаni tоzаlаsh, yеr to‘shаmаsini rеjаlаsh, o‘simlik qаtlаmini ko‘chirish vа uni sаqlаsh", "mintаqаni tоzаlаsh, o‘simlik qаtlаmini ko‘chirish, yo‘l pоyini rеjаlаsh.", "yo‘l pоyini rеjаlаsh, o‘qimlik qаtlаmini ko‘chirish.", "yer оsti suvlаrini qоchirish, mintаqаni tоzаlаsh."], "togri": "trаssаni tiklаsh vа mustаhkаmlаsh, mintаqаni tоzаlаsh, yеr to‘shаmаsini rеjаlаsh, o‘simlik qаtlаmini ko‘chirish vа uni sаqlаsh"},
        {"savol": "Pаrdоzlаsh ishlаrigа nimаlаr kirаdi?", "variantlar": ["yo‘l pоyini yuzаsigа tеkislаsh, o‘ymа vа ko‘tаrmаlаrni yon qiyaligini suv yuvib kеtishidаn sаqlаsh, o‘simlik qаvаtini qаytа yotqizish.", "yo‘l pоyini suv yuvishidаn sаqlаsh ishlаrini bаjаrish.", "o‘simlik qаvаtini qаytа yotqizish vа uni mustаhkаmlаsh.", "Yo‘lgа аjrаtilgаn mintаqаni yuzаsigа pаrdоz bеrish."], "togri": "yo‘l pоyini yuzаsigа tеkislаsh, o‘ymа vа ko‘tаrmаlаrni yon qiyaligini suv yuvib kеtishidаn sаqlаsh, o‘simlik qаvаtini qаytа yotqizish."},
        {"savol": "Аsоsiy ishlаrgа nimаlаr kirаdi?", "variantlar": ["o‘ymаlаrni o‘yish vа ko‘tаrmаlаrni qurish.", "o‘ymаlаrni o‘yish.", "ko‘tаrmаni ko‘tаrish.", "o‘simlik qаvаtini оlish."], "togri": "o‘ymаlаrni o‘yish vа ko‘tаrmаlаrni qurish."},
        {"savol": "Tехnоlоgiya jаrаyon tаrkibidаgi ishchi оpеrаtsiya nimа?", "variantlar": ["oddiy bir turdаgi elеmеntаr ish", "tехnоlоgik оqim", "kоmplеks mехаnizаtsiya.", "tехnоlоgik jаrаyon"], "togri": "oddiy bir turdаgi elеmеntаr ish"},
        {"savol": "Tuprоq ishlаrini bаjаrish muddаti qаysi оmillаrgа bоg‘liq?", "variantlar": ["iqlim shаrоitigа.", "mаshinаlаriga", "rеlеfgа.", "gruntgа."], "togri": "iqlim shаrоitigа."},
        {"savol": "Suvga to‘yingan mustahkamlangan grunt namunalarining siqilishdagi mustahkamlik chegarasi 200 haroratda, ikkinchi sinf mustahkamlik boyicha necha MPa teng?", "variantlar": ["2,5-2,0", "4,0-2,5", "2,0-1,5", "1,5-1,3"], "togri": "2,5-2,0"},
        {"savol": "Suvga toyingan mustahkamlangan grunt namunalarining siqilishdagi mustahkamlik chegarasi 500 haroratda, birinchi sinf mustahkamlik boyicha necha MPa teng?", "variantlar": ["2,0 kam emas", "1,5 kam emas", "1,3 kam emas", "0,5 kam emas"], "togri": "2,0 kam emas"},
        {"savol": "Suvga toyingan mustahkamlangan grunt namunalarining siqilishdagi mustahkamlik chegarasi 500 haroratda, ikkinchi sinf mustahkamlik boyicha necha MPa teng?", "variantlar": ["1,2 kam emas", "1,5 kam emas", "1,9 kam emas", "2,5 kam emas"], "togri": "1,2 kam emas"},
        {"savol": "Qattiq qoplamalar va asoslarning konstruksiyalari nechta belgi boyicha klafikatsiya qilish qabul qilingan?", "variantlar": ["8", "7", "9", "5"], "togri": "8"},
        {"savol": "Boylama yonalishdagi choklar qoplamaning eni necha metrdan keng bolganda ornatiladi?", "variantlar": ["4.5", "5.0", "5.2", "6.0"], "togri": "4.5"},
        {"savol": "Tехnоlоgik kаrtаdа nimаlаr аniqlаnаdi?", "variantlar": ["qurilish ishlаrini tехnоlоgiyasi vа ishni tаshkil qilish.", "kеrаkli mехаnizmlаr miqdоri.", "bаjаrilаdigаn ish hаjmi.", "mехаnizmlаrni ish unumdоrligi."], "togri": "qurilish ishlаrini tехnоlоgiyasi vа ishni tаshkil qilish."},
        {"savol": "Nimа uchun grunt yumshаtilаdi?", "variantlar": ["yer qаzuvchi mаshinаlаrni ish unumdоrligini оshirish.", "gruntlаrni tаbiiy nаmligini uzоqrоq sаqlаsh.", "gruntlаrni bir хil strukturаgа kеltirish", "gruntlаrni yuzа qismini nаmli."], "togri": "yer qаzuvchi mаshinаlаrni ish unumdоrligini оshirish."},
        {"savol": "V toifali yo‘lda sementbeton qoplamada bo‘ylama chokni eni nemchi metr bo‘ladi ?", "variantlar": ["bo‘lmaydi", "5,0", "4,5", "6.0"], "togri": "bo‘lmaydi"},
        {"savol": "Nеchа хil usul bilаn ko‘tаrmа qurish mumkin?", "variantlar": ["3", "10", "6", "8"], "togri": "3"},
        {"savol": "Nеchа хil usul bilаn o‘ymа qurish mumkin?", "variantlar": ["2", "5", "7", "9"], "togri": "2"},
        {"savol": "Bоg‘lоvchilаr bilаn ishlоv bеrilmаgаn mаtеriаllаrdаn yo‘l аsоslаrini qаndаy hаvо hаrоrаtidа bаjаrishgа ruхsаt etilаdi?", "variantlar": ["0 C dаn kаm bo‘lmаgаndа", "+ 13 C dаn kаm bo‘lmаgаndа", "+5 C dаn kаm bo‘lmаgаndа", "15 C dаn kаm bo‘lmаgаndа"], "togri": "0 C dаn kаm bo‘lmаgаndа"},
        {"savol": "Qаysi eng pаst hаrоrаtdа issiq аsfаltоbеtоn qоrishmаsini qоplаmаgа zichlаnishi mumkin?", "variantlar": ["120 C", "90 C", "100 C", "110 C"], "togri": "120 C"},
        {"savol": "Sеmеntоbеtоn qоplаmаlаrini qurish tехnоlоgiyasi bo‘yichа tаsnifi?", "variantlar": ["mоnоlit, yig‘mа, yig‘mа-mоnоlit.", "ikki qаtlаmi.", "аrmаturаli.", "yеngil bеtоnli"], "togri": "mоnоlit, yig‘mа, yig‘mа-mоnоlit."},
        {"savol": "Qаysi hаrоrаtdа аsfаltоbеtоn qоrishmаsini yo‘lgа yotqizish mumkin?", "variantlar": ["120-150", "50-90", "25-50", "90-110"], "togri": "120-150"},
        {"savol": "Yo‘l pоyini qаtlаmlаb qurishdаn mаqsаd nimа?", "variantlar": ["tаlаb etilgаn mustаhkаmlikkа erishish.", "tеz qurish.", "mехаnizmlаr sоni.", "mехаnizm."], "togri": "tаlаb etilgаn mustаhkаmlikkа erishish."},
        {"savol": "Buldоzеr yordаmidа bаrхаn qumli gruntlаrni оptimаl surish mаsоfаsini ko‘rsаting?", "variantlar": ["150 m.gаchа", "210 mgаchа", "170m.gаchа", "180m.gаchа"], "togri": "150 m.gаchа"},
        {"savol": "Skrеpеr bilаn guruntlаrni оptimаl tаshish mаsоfаsini ko‘rsаting?", "variantlar": ["5 km.gаchа", "10 km.gаchа", "4 km.gаchа", "8 km.gаchа"], "togri": "5 km.gаchа"},
        {"savol": "Qurish ishlаrini bаjаrish muddаti qаysi оmilgа bоg‘liq?", "variantlar": ["iqlim shаrоitigа.", "mаshinаlаriga.", "jоygа.", "gruntgа"], "togri": "iqlim shаrоitigа."},
        {"savol": "Gruntni оptimаl nаmlik qiymаti qаchоn e’tibоrgа оlinаdi?", "variantlar": ["gruntlаrni zichlаshdа", "gruntlаrni qаzishdа.", "gruntlаrni surishdа.", "gruntlаrni yoyishdа"], "togri": "gruntlаrni zichlаshdа"},
        {"savol": "Gruntni оptimаl nаmlik vа mаksimаl zichlik qiymаti qаysi аsbоb yordаmidа аniqlаnаdi?", "variantlar": ["sоyuzdоrnii.", "giprоdоrnii", "tоlchkоmеr ХАDI.", "prоgibоmеr MАDI"], "togri": "sоyuzdоrnii."},
        {"savol": "Gruntni оptimаl nаmlik qiymаti qаysi tехnоlоgik jаrаyondа muhim аhаmiyatgа egа?", "variantlar": ["gruntni zichlаshdа.", "gruntlаrni qаzishdа", "gruntlаrni surishdа", "gruntlаrni yoyishdа"], "togri": "gruntni zichlаshdа."},
        {"savol": "Qаndаy gruntlаrdаn yo‘l pоyini qurish mаqsаdgа muvоfiq?", "variantlar": ["supеs bilan", "glinа", "qum", "suglinоk"], "togri": "supеs bilan"},
        {"savol": "Chiziqli kаlаndаr grаfigini tuzishdаn mаqsаd nimаlаrdаn ibоrаt?", "variantlar": ["qurilish muddаtini аniqlаsh, ishlаr kеtmа-kеtligi vа bаjаrilаdigаn muddаti, kеrаkli mаshinа mехаnizmlаr vа ishlаr sоnini аniqlаsh, kеrаkli qurilish mаtеriаllаrini аniqlаb ishni to‘g‘ri tаshkil qilish.", "ishlаnmаydigаn kunlаrni аniqlаsh, qаchоn, qаеrgа, qаnchа yo‘l qurilish mаtеriаllаrini kеrаkligi оldindаn bilish.", "ishlаrni to‘g‘ri tаshkil etishdа kеrаkli bo‘lgаn mаshinа mехаnizmldаrni sоnini оldindаn bilish.", "bаjаrilаdigаn ishlаrni хаrаktеrini"], "togri": "qurilish muddаtini аniqlаsh, ishlаr kеtmа-kеtligi vа bаjаrilаdigаn muddаti, kеrаkli mаshinа mехаnizmlаr vа ishlаr sоnini аniqlаsh, kеrаkli qurilish mаtеriаllаrini аniqlаb ishni to‘g‘ri tаshkil qilish."},
        {"savol": "Pоrtlоvchi mоddаni jоylаshtirish uchun tоg‘ jinslаridа qаzilаdigаn silindrsimоn sun’iy chuqurlikni nomlanishi.", "variantlar": ["shpurlar bilan", "shtаbеl", "tushirish", "qоrishmаlаr"], "togri": "shpurlar bilan"},
        {"savol": "Asfalt yotkizgich avtomatik sistemasini aniqlang?", "variantlar": ["avtoplan 1", "ish- konbi", "profil 10", "profil 20"], "togri": "avtoplan 1"},
        {"savol": "Minorali ABZni texnologik jihozlarining balandligi qanchagacha boladi?", "variantlar": ["20 m", "25 m gacha", "15 m", "35m gacha"], "togri": "20 m"},
        {"savol": "Ekskavatorni ish unumdorligi ish jihozni burilish burchagi ortishi bilan qanday ozgaradi?", "variantlar": ["ortadib boradi", "ozgarmaydi", "kamayadi", "ortacha"], "togri": "ortadib boradi"},
        {"savol": "Temperaturaga kora qanday turdagi asfalt qorishmalari boladi?", "variantlar": ["issiq, sovuq.", "sovuq, issiq, motadil.", "issiq, iliq, ortach", "iliq, sovuq, ortach"], "togri": "issiq, sovuq."},
        {"savol": "Katok qaysi guruh mashinasiga kiradi?", "variantlar": ["tayyorgarlik ishlari mashinalari", "yer qazish mashinalari", "zichlash mashinalari", "yuk kotarish mashinalari"], "togri": "zichlash mashinalari"},
        {"savol": "Oymani ketma-ket qismlarga bolib qazilsa, bunday usul nima deb nomlanadi.", "variantlar": ["yarus usuli", "zig-zak", "sakkiz", "qatlamlab yotqizish"], "togri": "yarus usuli"},
        {"savol": "Avtomobil yollari sinflari togri korsatilgan qatorni aniqlang", "variantlar": ["avtomagistrallar, tezkor yollar, odatdagi yol turlari", "xalqaro, davlat, mahalliy", "Ia, Ib, II, III, IV, V", "xalqaro, davlat, mahalliy yol turlari"], "togri": "avtomagistrallar, tezkor yollar, odatdagi yol turlari"},
        {"savol": "V toifadagi yolda yol yoqasi kengligi necha metr bolishi kerak?", "variantlar": ["1,75", "2.0", "4.0", "2.4"], "togri": "1,75"}
    ],
    "matematika": [
        {"savol": "2 + 2 = ?",  "variantlar": ["3", "4", "5", "6"],    "togri": "4"},
        {"savol": "5 × 6 = ?",  "variantlar": ["25", "30", "35", "36"],"togri": "30"},
        {"savol": "√81 = ?",    "variantlar": ["7", "8", "9", "10"],   "togri": "9"},
    ],
    "fizika": [
        {"savol": "Yorug'lik tezligi?",       "variantlar": ["200,000 km/s","300,000 km/s","400,000 km/s","500,000 km/s"], "togri": "300,000 km/s"},
        {"savol": "Og'irlik kuchi formulasi?","variantlar": ["F = ma","G = mg","E = mc²","P = mv"],                        "togri": "G = mg"},
        {"savol": "1 Nyuton = ?",             "variantlar": ["kg·m/s","kg·m/s²","kg/m²","m/s²"],                          "togri": "kg·m/s²"},
    ],
    "biologiya": [
        {"savol": "Fotosintez qayerda?",   "variantlar": ["Yadro","Mitoxondriya","Xloroplast","Ribosoma"],                                       "togri": "Xloroplast"},
        {"savol": "DNK nima?",             "variantlar": ["Dezoksiribonuklein kislota","Ribonuklein kislota","Adenozin trifosfat","Aminokislota"],"togri": "Dezoksiribonuklein kislota"},
        {"savol": "Inson xromosoma soni?", "variantlar": ["44","46","48","42"],                                                                   "togri": "46"},
    ],
}

natijalar = {}

# ============================================================
#                        STATES
# ============================================================
class Royxat(StatesGroup):
    ism      = State()
    familya  = State()
    guruh    = State()

class AdminState(StatesGroup):
    admin_id     = State()
    ruxsat_ol_id = State()
    test_fan     = State()
    test_savol   = State()
    test_var_a   = State()
    test_var_b   = State()
    test_var_c   = State()
    test_var_d   = State()
    test_togri   = State()
    ochir_index  = State()
    ochir_fan    = State()

class UserState(StatesGroup):
    test_jarayoni = State()

# ============================================================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ============================================================
#                      KLAVIATURALAR
# ============================================================
def admin_klaviatura():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Kutayotganlar",              callback_data="a_kutayotganlar")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar ro'yxati",  callback_data="a_foydalanuvchilar")],
        [InlineKeyboardButton(text="🚫 Ruxsatni olib qo'yish",     callback_data="a_ruxsat_ol")],
        [InlineKeyboardButton(text="👑 Admin qo'shish",             callback_data="a_admin_qosh")],
        [InlineKeyboardButton(text="📋 Adminlar ro'yxati",          callback_data="a_adminlar")],
        [InlineKeyboardButton(text="📊 Natijalar",                  callback_data="a_natijalar")],
        [InlineKeyboardButton(text="➕ Test qo'shish",              callback_data="a_test_qosh")],
        [InlineKeyboardButton(text="🗑 Test o'chirish",             callback_data="a_test_ochir")],
        [InlineKeyboardButton(text="👀 Testlarni ko'rish",          callback_data="a_testlar")],
    ])

def fan_klaviatura():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛣 Avto yo\'llar texnologiyasi", callback_data="fan_avto")],
        [InlineKeyboardButton(text="📐 Matematika",   callback_data="fan_matematika")],
        [InlineKeyboardButton(text="⚡ Fizika",       callback_data="fan_fizika")],
        [InlineKeyboardButton(text="🌿 Biologiya",    callback_data="fan_biologiya")],
        [InlineKeyboardButton(text="🏠 Asosiy bo'lim", callback_data="a_bosh")],
    ])

def bosh_tugma():
    """Faqat 'Asosiy bo'lim' tugmasidan iborat klaviatura"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy bo'lim", callback_data="a_bosh")],
    ])

def variant_klaviatura(variantlar, fan, test_index, ara_v=None):
    harflar = ["🔵 A", "🔵 B", "🔵 C", "🔵 D"]
    if ara_v is None:
        ara_v = list(range(len(variantlar)))
    tugmalar = [
        [InlineKeyboardButton(
            text=f"{harflar[i]}) {variantlar[ara_v[i]]}",
            callback_data=f"j_{fan}_{test_index}_{ara_v[i]}"
        )] for i in range(len(ara_v))
    ]
    tugmalar.append([InlineKeyboardButton(text="🏠 Asosiy bo'lim", callback_data="a_bosh")])
    return InlineKeyboardMarkup(inline_keyboard=tugmalar)

def natija_klaviatura(togri_i, variantlar, ara=None):
    harflar = ["A", "B", "C", "D"]
    if ara is None:
        ara = list(range(len(variantlar)))
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'✅' if ara[i] == togri_i else '❌'} {harflar[i]}) {variantlar[ara[i]]}",
            callback_data="noop"
        )] for i in range(len(ara))
    ])

def tasdiq_klaviatura(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"tasdiq_{uid}")],
        [InlineKeyboardButton(text="⏳ Kutish",     callback_data=f"kutish_{uid}")],
        [InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"rad_{uid}")],
    ])

# ============================================================
#                        /start
# ============================================================
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    if uid in admins:
        await message.answer(
            f"👑 *Xush kelibsiz, Admin!*\nID: `{uid}`",
            parse_mode="Markdown",
            reply_markup=admin_klaviatura()
        )
    elif uid in allowed_users:
        info = allowed_users[uid]
        await message.answer(
            f"✅ Xush kelibsiz, *{info['ism']} {info['familya']}*!\n"
            f"🏫 Guruh: {info['guruh']}\n\n"
            f"📚 Qaysi fandan test topshirmoqchisiz?",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=fan_klaviatura()
        )
    elif uid in kutayotganlar:
        await message.answer("⏳ So'rovingiz admin tomonidan ko'rib chiqilmoqda. Kuting...")
    else:
        await state.set_state(Royxat.ism)
        await message.answer(
            "👋 Xush kelibsiz!\n\n"
            "Botdan foydalanish uchun ro'yxatdan o'ting.\n\n"
            "✏️ *Ismingizni* kiriting:",
            parse_mode="Markdown"
        )

# ============================================================
#                     RO'YXATDAN O'TISH
# ============================================================
@dp.message(Royxat.ism)
async def royxat_ism(message: Message, state: FSMContext):
    await state.update_data(ism=message.text.strip())
    await state.set_state(Royxat.familya)
    await message.answer("✏️ *Familyangizni* kiriting:", parse_mode="Markdown")

@dp.message(Royxat.familya)
async def royxat_familya(message: Message, state: FSMContext):
    await state.update_data(familya=message.text.strip())
    await state.set_state(Royxat.guruh)
    await message.answer("🏫 *Guruhingizni* kiriting (masalan: 10-A):", parse_mode="Markdown")

@dp.message(Royxat.guruh)
async def royxat_guruh(message: Message, state: FSMContext):
    data = await state.get_data()
    uid = message.from_user.id
    guruh = message.text.strip()

    kutayotganlar[uid] = {
        "ism": data["ism"],
        "familya": data["familya"],
        "guruh": guruh
    }

    await message.answer(
        f"✅ So'rovingiz yuborildi!\n\n"
        f"👤 Ism: *{data['ism']} {data['familya']}*\n"
        f"🏫 Guruh: *{guruh}*\n\n"
        f"⏳ Admin tasdiqlashini kuting...",
        parse_mode="Markdown"
    )
    await state.clear()

    # Barcha adminlarga xabar yuborish
    for admin_id in admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=f"📬 *Yangi ro'yxatdan o'tish so'rovi!*\n\n"
                     f"👤 Ism: *{data['ism']} {data['familya']}*\n"
                     f"🏫 Guruh: *{guruh}*\n"
                     f"🆔 ID: `{uid}`\n\n"
                     f"Tasdiqlaysizmi?",
                parse_mode="Markdown",
                reply_markup=tasdiq_klaviatura(uid)
            )
        except:
            pass

# ============================================================
#               ADMIN — TASDIQLASH / RAD ETISH
# ============================================================
@dp.callback_query(F.data.startswith("tasdiq_"))
async def tasdiq(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    uid = int(callback.data.split("_")[1])
    if uid not in kutayotganlar:
        await callback.message.edit_text("⚠️ Bu foydalanuvchi allaqachon ko'rib chiqilgan.")
        await callback.answer(); return

    info = kutayotganlar.pop(uid)
    allowed_users[uid] = info

    await callback.message.edit_text(
        f"✅ *Tasdiqlandi!*\n\n"
        f"👤 {info['ism']} {info['familya']}\n"
        f"🏫 Guruh: {info['guruh']}\n"
        f"🆔 ID: `{uid}`",
        parse_mode="Markdown"
    )

    try:
        await bot.send_message(
            chat_id=uid,
            text=f"🎉 *Tabriklaymiz, {info['ism']}!*\n\n"
                 f"Sizning so'rovingiz tasdiqlandi.\n"
                 f"Endi testlardan foydalana olasiz!\n\n"
                 f"📚 Qaysi fandan boshlaysiz?",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=fan_klaviatura()
        )
    except:
        pass

    await callback.answer("✅ Tasdiqlandi!")

@dp.callback_query(F.data.startswith("kutish_"))
async def kutish(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    uid = int(callback.data.split("_")[1])
    if uid not in kutayotganlar:
        await callback.message.edit_text("⚠️ Bu foydalanuvchi allaqachon ko'rib chiqilgan.")
        await callback.answer(); return

    info = kutayotganlar[uid]

    await callback.message.edit_text(
        f"⏳ *Kutishga qo'yildi*\n\n"
        f"👤 {info['ism']} {info['familya']}\n"
        f"🏫 Guruh: {info['guruh']}\n"
        f"🆔 ID: `{uid}`\n\n"
        f"Keyinroq qaror qilishingiz mumkin.",
        parse_mode="Markdown",
        reply_markup=tasdiq_klaviatura(uid)
    )

    try:
        await bot.send_message(
            chat_id=uid,
            text="⏳ So'rovingiz hali ko'rib chiqilmoqda. Biroz sabr qiling..."
        )
    except: pass

    await callback.answer("⏳ Kutishga qo'yildi!")

@dp.callback_query(F.data.startswith("rad_"))
async def rad(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    uid = int(callback.data.split("_")[1])
    if uid not in kutayotganlar:
        await callback.message.edit_text("⚠️ Bu foydalanuvchi allaqachon ko'rib chiqilgan.")
        await callback.answer(); return

    info = kutayotganlar.pop(uid)

    await callback.message.edit_text(
        f"❌ *Rad etildi*\n\n"
        f"👤 {info['ism']} {info['familya']}\n"
        f"🏫 Guruh: {info['guruh']}\n"
        f"🆔 ID: `{uid}`",
        parse_mode="Markdown"
    )

    try:
        await bot.send_message(
            chat_id=uid,
            text="❌ Afsuski, so'rovingiz rad etildi.\n"
                 "Qo'shimcha ma'lumot uchun admin bilan bog'laning."
        )
    except:
        pass

    await callback.answer("❌ Rad etildi!")

# ============================================================
#               ADMIN — KUTAYOTGANLAR RO'YXATI
# ============================================================
@dp.callback_query(F.data == "a_kutayotganlar")
async def a_kutayotganlar(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    if not kutayotganlar:
        await callback.message.answer("📋 Hozircha kutayotgan foydalanuvchi yo'q.", reply_markup=bosh_tugma())
        await callback.answer(); return

    for uid, info in kutayotganlar.items():
        await callback.message.answer(
            f"📬 *So'rov*\n\n"
            f"👤 {info['ism']} {info['familya']}\n"
            f"🏫 Guruh: {info['guruh']}\n"
            f"🆔 ID: `{uid}`",
            parse_mode="Markdown",
            reply_markup=tasdiq_klaviatura(uid)
        )
    await callback.message.answer("⬆️ Yuqoridagi so'rovlarni ko'rib chiqing.", reply_markup=bosh_tugma())
    await callback.answer()

# ============================================================
#             ADMIN — FOYDALANUVCHILAR RO'YXATI
# ============================================================
@dp.callback_query(F.data == "a_foydalanuvchilar")
async def a_foydalanuvchilar(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    if not allowed_users:
        await callback.message.answer("👥 Hozircha ruxsatli foydalanuvchi yo'q.", reply_markup=bosh_tugma())
    else:
        text = "👥 *Ruxsatli foydalanuvchilar:*\n\n"
        for uid, info in allowed_users.items():
            text += (f"👤 *{info['ism']} {info['familya']}*\n"
                     f"   🏫 Guruh: {info['guruh']}\n"
                     f"   🆔 ID: `{uid}`\n\n")
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=bosh_tugma())
    await callback.answer()

# ============================================================
#             ADMIN — RUXSATNI OLIB QO'YISH
# ============================================================
@dp.callback_query(F.data == "a_ruxsat_ol")
async def a_ruxsat_ol(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return
    if not allowed_users:
        await callback.message.answer("👥 Hozircha ruxsatli foydalanuvchi yo'q.")
        await callback.answer(); return
    buttons = []
    for uid, info in allowed_users.items():
        buttons.append([InlineKeyboardButton(
            text=f"👤 {info['ism']} {info['familya']} | {info['guruh']}",
            callback_data=f"rol_{uid}"
        )])
    await callback.message.answer(
        "🚫 Ruxsatini olib qo'ymoqchi bo'lgan foydalanuvchini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("rol_"))
async def rol_tanlandi(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return
    uid = int(callback.data.split("_")[1])
    if uid in allowed_users:
        info = allowed_users.pop(uid)
        await callback.message.edit_text(
            f"🚫 *{info['ism']} {info['familya']}* ruxsati olib qo'yildi!",
            parse_mode="Markdown"
        )
        try:
            await bot.send_message(uid, "🚫 Sizning botga kirishingiz bloklandi.")
        except: pass
    else:
        await callback.message.edit_text("❌ Bu foydalanuvchi ro'yxatda yo'q.")
    await callback.answer()

# ============================================================
#                  ADMIN — ADMIN QO'SHISH
# ============================================================
@dp.callback_query(F.data == "a_admin_qosh")
async def a_admin_qosh(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Faqat super admin!"); return
    await state.set_state(AdminState.admin_id)
    await callback.message.answer("👑 Yangi adminning Telegram ID sini kiriting:")
    await callback.answer()

@dp.message(AdminState.admin_id)
async def admin_id_qabul(message: Message, state: FSMContext):
    try:
        uid = int(message.text.strip())
        admins.add(uid)
        await message.answer(f"✅ `{uid}` admin qilindi!", parse_mode="Markdown", reply_markup=bosh_tugma())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=bosh_tugma())
    await state.clear()

@dp.callback_query(F.data == "a_adminlar")
async def a_adminlar(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return
    text = "👑 *Adminlar:*\n"
    for a in admins:
        text += f"• `{a}`\n"
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=bosh_tugma())
    await callback.answer()

# ============================================================
#                    ADMIN — NATIJALAR
# ============================================================
@dp.callback_query(F.data == "a_natijalar")
async def a_natijalar(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    if not natijalar:
        await callback.message.answer("📊 Hozircha natijalar yo'q.", reply_markup=bosh_tugma())
    else:
        text = "📊 *Natijalar:*\n\n"
        for uid, fandata in natijalar.items():
            info = allowed_users.get(uid, {})
            ism_familya = f"{info.get('ism','')} {info.get('familya','')}".strip() or str(uid)
            guruh = info.get('guruh', '—')
            text += f"👤 *{ism_familya}* | 🏫 {guruh}\n"
            for fan, ball in fandata.items():
                foiz = round(ball['togri'] / ball['jami'] * 100)
                text += f"  • {FANLAR.get(fan, fan)}: {ball['togri']}/{ball['jami']} ({foiz}%)\n"
            text += "\n"
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=bosh_tugma())
    await callback.answer()

# ============================================================
#                  ADMIN — TESTLARNI KO'RISH
# ============================================================
@dp.callback_query(F.data == "a_testlar")
async def a_testlar(callback: CallbackQuery):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    await callback.message.answer("📚 Testlar ro'yxati:")

    for fan, testlar in TESTLAR.items():
        if not testlar:
            continue
        # Har bir fanni alohida xabarlarga bo'lib yuborish (4096 belgi chegarasi)
        sarlavha = f"📖 *{FANLAR[fan]}* — {len(testlar)} ta test\n\n"
        xabar = sarlavha
        for i, t in enumerate(testlar):
            qator = f"{i+1}. {t['savol']}\n"
            for j, v in enumerate(t['variantlar']):
                harf = ["A","B","C","D"][j]
                mark = "✅" if v == t['togri'] else "◻️"
                qator += f"   {mark} {harf}) {v}\n"
            qator += "\n"
            # 4000 belgidan oshsa yangi xabar boshlash
            if len(xabar) + len(qator) > 4000:
                await callback.message.answer(xabar, parse_mode="Markdown")
                xabar = qator
            else:
                xabar += qator
        if xabar.strip():
            await callback.message.answer(xabar, parse_mode="Markdown")

    await callback.message.answer("✅ Hammasi ko'rsatildi.", reply_markup=bosh_tugma())
    await callback.answer()

# ============================================================
#                  ADMIN — TEST QO'SHISH
# ============================================================
@dp.callback_query(F.data == "a_test_qosh")
async def a_test_qosh(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return
    buttons = [[InlineKeyboardButton(text=nom, callback_data=f"tf_{fan}")] for fan, nom in FANLAR.items()]
    await callback.message.answer("Qaysi fanga test qo'shmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@dp.callback_query(F.data.startswith("tf_"))
async def tf_tanlandi(callback: CallbackQuery, state: FSMContext):
    fan = callback.data[3:]
    await state.update_data(test_fan=fan)
    await state.set_state(AdminState.test_savol)
    await callback.message.answer("✏️ Savol matnini kiriting:")
    await callback.answer()

@dp.message(AdminState.test_savol)
async def ts_savol(message: Message, state: FSMContext):
    await state.update_data(savol=message.text)
    await state.set_state(AdminState.test_var_a)
    await message.answer("🔵 A varianti:")

@dp.message(AdminState.test_var_a)
async def ts_a(message: Message, state: FSMContext):
    await state.update_data(var_a=message.text)
    await state.set_state(AdminState.test_var_b)
    await message.answer("🔵 B varianti:")

@dp.message(AdminState.test_var_b)
async def ts_b(message: Message, state: FSMContext):
    await state.update_data(var_b=message.text)
    await state.set_state(AdminState.test_var_c)
    await message.answer("🔵 C varianti:")

@dp.message(AdminState.test_var_c)
async def ts_c(message: Message, state: FSMContext):
    await state.update_data(var_c=message.text)
    await state.set_state(AdminState.test_var_d)
    await message.answer("🔵 D varianti:")

@dp.message(AdminState.test_var_d)
async def ts_d(message: Message, state: FSMContext):
    await state.update_data(var_d=message.text)
    await state.set_state(AdminState.test_togri)
    await message.answer("✅ To'g'ri javob harfini kiriting (A, B, C yoki D):")

@dp.message(AdminState.test_togri)
async def ts_togri(message: Message, state: FSMContext):
    data = await state.get_data()
    fan = data["test_fan"]
    variantlar = [data["var_a"], data["var_b"], data["var_c"], data["var_d"]]
    harf = message.text.strip().upper()
    harf_index = {"A": 0, "B": 1, "C": 2, "D": 3}
    if harf not in harf_index:
        await message.answer("❌ Faqat A, B, C yoki D kiriting.")
        return
    togri = variantlar[harf_index[harf]]
    TESTLAR[fan].append({"savol": data["savol"], "variantlar": variantlar, "togri": togri})
    await message.answer(
        f"✅ Test qo'shildi!\n\nFan: {FANLAR[fan]}\nSavol: {data['savol']}\nTo'g'ri: {harf}) {togri}",
        reply_markup=bosh_tugma()
    )
    await state.clear()

# ============================================================
#                  ADMIN — TEST O'CHIRISH
# ============================================================
@dp.callback_query(F.data == "a_test_ochir")
async def a_test_ochir(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return
    buttons = [[InlineKeyboardButton(text=nom, callback_data=f"of_{fan}")] for fan, nom in FANLAR.items()]
    await callback.message.answer("Qaysi fandan test o'chirmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@dp.callback_query(F.data.startswith("of_"))
async def of_tanlandi(callback: CallbackQuery, state: FSMContext):
    fan = callback.data[3:]
    await state.update_data(ochir_fan=fan)
    testlar = TESTLAR[fan]
    if not testlar:
        await callback.message.answer("Bu fanda testlar yo'q.")
        await callback.answer(); return
    text = f"{FANLAR[fan]} testlari:\n\n"
    for i, t in enumerate(testlar):
        text += f"{i+1}. {t['savol']}\n"
    text += "\nNecha-nchi testni o'chirishni raqamini kiriting:"
    await state.set_state(AdminState.ochir_index)
    await callback.message.answer(text)
    await callback.answer()

@dp.message(AdminState.ochir_index)
async def ochir_index_qabul(message: Message, state: FSMContext):
    data = await state.get_data()
    fan = data["ochir_fan"]
    try:
        idx = int(message.text.strip()) - 1
        if 0 <= idx < len(TESTLAR[fan]):
            ochirilgan = TESTLAR[fan].pop(idx)
            await message.answer(f"🗑 O'chirildi: {ochirilgan['savol']}", reply_markup=bosh_tugma())
        else:
            await message.answer("❌ Bunday raqamdagi test yo'q.", reply_markup=bosh_tugma())
    except ValueError:
        await message.answer("❌ Raqam kiriting.", reply_markup=bosh_tugma())
    await state.clear()

# ============================================================
#                FOYDALANUVCHI — FAN TANLASH
# ============================================================
@dp.callback_query(F.data.startswith("fan_"))
async def fan_tanlandi(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    if uid not in allowed_users and uid not in admins:
        await callback.answer("❌ Ruxsat yo'q!"); return

    fan = callback.data[4:]
    testlar_asl = TESTLAR.get(fan, [])
    if not testlar_asl:
        await callback.message.answer(f"{FANLAR[fan]} uchun hozircha testlar yo'q.")
        await callback.answer(); return

    # Savollar tartibini aralashtirish
    savol_tartibi = list(range(len(testlar_asl)))
    random.shuffle(savol_tartibi)

    # Har bir savol uchun variantlar tartibini aralashtirish
    variant_tartibi = []
    for idx in savol_tartibi:
        ara = list(range(len(testlar_asl[idx]["variantlar"])))
        random.shuffle(ara)
        variant_tartibi.append(ara)

    jami = len(testlar_asl)
    await state.set_state(UserState.test_jarayoni)
    await state.update_data(
        fan=fan,
        test_index=0,
        togri=0,
        jami=jami,
        savol_tartibi=savol_tartibi,
        variant_tartibi=variant_tartibi
    )

    birinchi_savol_i = savol_tartibi[0]
    test = testlar_asl[birinchi_savol_i]
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"📚 *{FANLAR[fan]}* — Test boshlandi!\n\n"
             f"❓ 1/{jami}-savol:\n{test['savol']}",
        parse_mode="Markdown",
        protect_content=True,
        reply_markup=variant_klaviatura(test['variantlar'], fan, birinchi_savol_i, variant_tartibi[0])
    )
    await callback.answer()

# ============================================================
#                FOYDALANUVCHI — JAVOB
# ============================================================
@dp.callback_query(F.data.startswith("j_"))
async def javob_qabul(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    parts = callback.data.split("_")
    fan = parts[1]
    asl_savol_i = int(parts[2])   # asl TESTLAR dagi index
    tanlangan_i = int(parts[3])   # asl variantlar dagi index

    data = await state.get_data()
    togri_son = data.get("togri", 0)
    jami = data.get("jami", 0)
    savol_tartibi = data.get("savol_tartibi", list(range(jami)))
    variant_tartibi = data.get("variant_tartibi", [])
    test_index = data.get("test_index", 0)  # hozirgi necha-nchi savoldamiz

    variantlar = TESTLAR[fan][asl_savol_i]["variantlar"]
    togri_javob = TESTLAR[fan][asl_savol_i]["togri"]
    togri_i = variantlar.index(togri_javob)
    tanlangan = variantlar[tanlangan_i]
    harflar = ["A", "B", "C", "D"]

    # Ekranda ko'rinadigan harfni topish (aralashtirilgan tartibda)
    ara = variant_tartibi[test_index] if variant_tartibi else list(range(len(variantlar)))
    try:
        ekran_togri_harf = harflar[ara.index(togri_i)]
        ekran_tanlangan_harf = harflar[ara.index(tanlangan_i)]
    except:
        ekran_togri_harf = harflar[togri_i]
        ekran_tanlangan_harf = harflar[tanlangan_i]

    keyingi_index = test_index + 1

    if tanlangan_i == togri_i:
        togri_son += 1
        natija_text = "✅ *To'g'ri!*"
    else:
        natija_text = (
            f"❌ *Noto'g'ri!*\n"
            f"Siz tanladingiz: {ekran_tanlangan_harf}) {tanlangan}\n"
            f"✅ To'g'ri javob: {ekran_togri_harf}) {togri_javob}"
        )

    await state.update_data(togri=togri_son, test_index=keyingi_index)

    # Natija klaviaturasi - aralashtirilgan tartibda ko'rsatish
    try:
        await callback.message.edit_reply_markup(
            reply_markup=natija_klaviatura(togri_i, variantlar, ara)
        )
    except: pass

    if keyingi_index < jami:
        keyingi_asl_i = savol_tartibi[keyingi_index]
        keyingi_test = TESTLAR[fan][keyingi_asl_i]
        keyingi_ara = variant_tartibi[keyingi_index] if variant_tartibi else list(range(len(keyingi_test["variantlar"])))
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"{natija_text}\n\n"
                 f"❓ {keyingi_index+1}/{jami}-savol:\n{keyingi_test['savol']}",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=variant_klaviatura(keyingi_test['variantlar'], fan, keyingi_asl_i, keyingi_ara)
        )
    else:
        if uid not in natijalar:
            natijalar[uid] = {}
        natijalar[uid][fan] = {"togri": togri_son, "jami": jami}
        foiz = round(togri_son / jami * 100)

        if foiz == 100:   baho = "🏆 Ajoyib! 100%!"
        elif foiz >= 80:  baho = "🌟 Yaxshi natija!"
        elif foiz >= 60:  baho = "👍 Qoniqarli"
        else:             baho = "📖 Ko'proq o'qing"

        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"{natija_text}\n\n"
                 f"🏁 *Test yakunlandi!*\n\n"
                 f"📚 Fan: {FANLAR[fan]}\n"
                 f"✅ To'g'ri: {togri_son}/{jami}\n"
                 f"📊 Natija: {foiz}%\n{baho}",
            parse_mode="Markdown",
            protect_content=True
        )
        await state.clear()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="📚 Boshqa fandan ham test topshirmoqchimisiz?",
            protect_content=True,
            reply_markup=fan_klaviatura()
        )

    await callback.answer()

# ============================================================
@dp.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()

# ============================================================
#                  ASOSIY BO'LIM (tugma orqali)
# ============================================================
@dp.callback_query(F.data == "a_bosh")
async def a_bosh(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    uid = callback.from_user.id
    if uid in admins:
        await callback.message.answer(
            f"👑 *Admin paneli*\nID: `{uid}`",
            parse_mode="Markdown",
            reply_markup=admin_klaviatura()
        )
    elif uid in allowed_users:
        info = allowed_users[uid]
        await callback.message.answer(
            f"🏠 *Asosiy bo'lim*\n\n"
            f"👤 {info['ism']} {info['familya']}\n"
            f"🏫 Guruh: {info['guruh']}\n\n"
            f"📚 Qaysi fandan test topshirmoqchisiz?",
            parse_mode="Markdown",
            protect_content=True,
            reply_markup=fan_klaviatura()
        )
    else:
        await callback.message.answer("❌ Sizda ruxsat yo'q.")
    await callback.answer()

# ============================================================
async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
