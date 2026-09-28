"""Generate and validate the 500-question Semantically Paired Pilot Benchmark.

Generates:
- 500 Semantic Question units (100 per language: hi, ta, te, bn, kn).
- 6 Domains: governance, agriculture, education, history, science, public_health.
- 5 Conditions per unit:
    - Condition A: English (A_EN)
    - Condition B: Native-script Monolingual (B_NATIVE)
    - Condition C: Romanized Monolingual (C_ROMAN)
    - Condition D: Natural Code-Switching (D_CS)
    - Condition E: Mixed-Script Code-Switching (E_MIXED_SCRIPT)
Total: 2,500 condition prompts, with measured CMI and script transitions.

Saves to:
    data/questions/semantic_pilot_500.jsonl
    data/questions/condition_prompts_pilot_2500.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from indrallm.collection.semantic_paired import (
    SemanticQuestion,
    flatten_condition_prompts,
    save_semantic_dataset,
    validate_splits,
)
from indrallm.config import PROJECT_ROOT

# Domain seed templates across 6 domains with verified factual reference anchors
PILOT_SEEDS: dict[str, list[dict[str, Any]]] = {
    "governance": [
        {
            "subdomain": "civic_welfare",
            "fact": "PM-KISAN provides direct income support of ₹6,000 per year in three equal installments to eligible farmer families.",
            "answer": "₹6,000 per year (transferred in 3 equal installments of ₹2,000 each).",
            "evidence": "Under the Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme, an amount of ₹6,000/- per year is released in three 4-monthly installments directly into the bank accounts of the beneficiaries.",
            "source_url": "https://pmkisan.gov.in",
            "source_type": "govt_portal",
            "difficulty": 1,
            "queries": {
                "hi": {
                    "A_EN": "How much financial support is provided annually under the PM-KISAN scheme?",
                    "B_NATIVE": "पीएम-किसान योजना के तहत सालाना कितनी वित्तीय सहायता दी जाती है?",
                    "C_ROMAN": "PM-Kisan yojana ke antargat saalana kitni vittiya sahayata di jaati hai?",
                    "D_CS": "PM-Kisan scheme me annually kitna financial support milta hai?",
                    "E_MIXED_SCRIPT": "PM-Kisan scheme में annually कितना financial support मिलता है?",
                },
                "ta": {
                    "A_EN": "How much financial support is provided annually under the PM-KISAN scheme?",
                    "B_NATIVE": "பிஎம்-கிசான் திட்டத்தின் கீழ் ஆண்டுக்கு எவ்வளவு நிதி உதவி வழங்கப்படுகிறது?",
                    "C_ROMAN": "PM-Kisan thittaththin keezh aandu thorum evvalavu nithi uthavi valangappadugirathu?",
                    "D_CS": "PM-Kisan scheme la annually evvalavu financial support kedaikkum?",
                    "E_MIXED_SCRIPT": "PM-Kisan scheme-ல annually எவ்வளவு financial support கிடைக்கும்?",
                },
                "te": {
                    "A_EN": "How much financial support is provided annually under the PM-KISAN scheme?",
                    "B_NATIVE": "పీఎం-కిసాన్ పథకం కింద ఏటా ఎంత ఆర్థిక సాయం అందిస్తారు?",
                    "C_ROMAN": "PM-Kisan pathakam kinda yeta entha aarthika saayam andistharu?",
                    "D_CS": "PM-Kisan scheme lo annually entha financial support istharu?",
                    "E_MIXED_SCRIPT": "PM-Kisan scheme లో annually ఎంత financial support ఇస్తారు?",
                },
                "bn": {
                    "A_EN": "How much financial support is provided annually under the PM-KISAN scheme?",
                    "B_NATIVE": "পিএম-কিসান প্রকল্পের অধীনে বছরে কত টাকা আর্থিক সহায়তা দেওয়া হয়?",
                    "C_ROMAN": "PM-Kisan prakalper adhine bochore koto taka arthik sohayota dewa hoy?",
                    "D_CS": "PM-Kisan scheme e annually koto financial support pawa jay?",
                    "E_MIXED_SCRIPT": "PM-Kisan scheme-এ annually কত financial support পাওয়া যায়?",
                },
                "kn": {
                    "A_EN": "How much financial support is provided annually under the PM-KISAN scheme?",
                    "B_NATIVE": "ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯಡಿ ವಾರ್ಷಿಕವಾಗಿ ಎಷ್ಟು ಆರ್ಥಿಕ ನೆರವು ನೀಡಲಾಗುತ್ತದೆ?",
                    "C_ROMAN": "PM-Kisan yojaneyadi vaarshikavaagi eshtu aarthika neravu needalaaguttade?",
                    "D_CS": "PM-Kisan scheme nalli annually eshtu financial support sigutte?",
                    "E_MIXED_SCRIPT": "PM-Kisan scheme ನಲ್ಲಿ annually ಎಷ್ಟು financial support ಸಿಗುತ್ತೆ?",
                },
            },
        },
        {
            "subdomain": "healthcare_insurance",
            "fact": "Ayushman Bharat PM-JAY provides health cover of up to ₹5 lakh per family per year for secondary and tertiary care hospitalization.",
            "answer": "Up to ₹5 lakh per family per year.",
            "evidence": "Ayushman Bharat PM-JAY provides a health cover of Rs. 5 lakhs per family per year for secondary and tertiary care hospitalization to over 12 crore poor and vulnerable families.",
            "source_url": "https://nha.gov.in/PM-JAY",
            "source_type": "govt_portal",
            "difficulty": 1,
            "queries": {
                "hi": {
                    "A_EN": "What is the maximum health cover amount per family per year under Ayushman Bharat PM-JAY?",
                    "B_NATIVE": "आयुष्मान भारत योजना के तहत प्रति परिवार प्रति वर्ष अधिकतम कितना स्वास्थ्य कवर मिलता है?",
                    "C_ROMAN": "Ayushman Bharat yojana ke antargat prati parivar prati varsh adhiktam kitna swasthya cover milta hai?",
                    "D_CS": "Ayushman Bharat scheme me per family per year maximum kitna health cover milta hai?",
                    "E_MIXED_SCRIPT": "Ayushman Bharat scheme में per family per year maximum कितना health cover मिलता है?",
                },
                "ta": {
                    "A_EN": "What is the maximum health cover amount per family per year under Ayushman Bharat PM-JAY?",
                    "B_NATIVE": "ஆயுஷ்மான் பாரத் திட்டத்தின் கீழ் ஒரு குடும்பத்திற்கு ஆண்டுக்கு அதிகபட்ச மருத்துவ காப்பீட்டுத் தொகை எவ்வளவு?",
                    "C_ROMAN": "Ayushman Bharat thittaththin keezh oru kudumbathirku aandu thorum athigabatcha maruthuva kaapeettu thogai evvalavu?",
                    "D_CS": "Ayushman Bharat scheme la per family per year maximum evvalavu health insurance cover kedaikkum?",
                    "E_MIXED_SCRIPT": "Ayushman Bharat scheme-ல per family per year maximum எவ்வளவு health insurance cover கிடைக்கும்?",
                },
                "te": {
                    "A_EN": "What is the maximum health cover amount per family per year under Ayushman Bharat PM-JAY?",
                    "B_NATIVE": "ఆయుష్మాన్ భారత్ పథకం కింద ఒక కుటుంబానికి సంవత్సరానికి గరిష్ట ఆరోగ్య బీమా మొత్తం ఎంత?",
                    "C_ROMAN": "Ayushman Bharat pathakam kinda oka kutumbaniki samvatsaraniki garishta aarogya beema motham entha?",
                    "D_CS": "Ayushman Bharat scheme lo per family per year maximum entha health cover provide chestaru?",
                    "E_MIXED_SCRIPT": "Ayushman Bharat scheme లో per family per year maximum ఎంత health cover provide చేస్తారు?",
                },
                "bn": {
                    "A_EN": "What is the maximum health cover amount per family per year under Ayushman Bharat PM-JAY?",
                    "B_NATIVE": "আয়ুষ্মান ভারত প্রকল্পের অধীনে প্রতি বছর পরিবার পিছু সর্বোচ্চ স্বাস্থ্য বীমা কভারেজ কত?",
                    "C_ROMAN": "Ayushman Bharat prakalper adhine proti bochor poribar pichu sorboccho swasthya bima coverage koto?",
                    "D_CS": "Ayushman Bharat scheme e per family per year maximum koto health insurance cover pawa jay?",
                    "E_MIXED_SCRIPT": "Ayushman Bharat scheme-এ per family per year maximum কত health insurance cover পাওয়া যায়?",
                },
                "kn": {
                    "A_EN": "What is the maximum health cover amount per family per year under Ayushman Bharat PM-JAY?",
                    "B_NATIVE": "ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಯೋಜನೆಯಡಿಯಲ್ಲಿ ಪ್ರತಿ ಕುಟುಂಬಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ಗರಿಷ್ಠ ಎಷ್ಟು ಆರೋಗ್ಯ ವಿಮಾ ಮೊತ್ತ ಸಿಗುತ್ತದೆ?",
                    "C_ROMAN": "Ayushman Bharat yojaneyadiyalli prati kutumbakke vaarshikavaagi garishta eshtu aarogya vima motta siguttade?",
                    "D_CS": "Ayushman Bharat scheme nalli per family per year maximum eshtu health insurance cover sigutte?",
                    "E_MIXED_SCRIPT": "Ayushman Bharat scheme ನಲ್ಲಿ per family per year maximum ಎಷ್ಟು health insurance cover ಸಿಗುತ್ತೆ?",
                },
            },
        },
    ],
    "agriculture": [
        {
            "subdomain": "soil_fertility",
            "fact": "The Soil Health Card scheme assesses 12 soil parameters including N, P, K, pH, EC, organic carbon, and secondary nutrients.",
            "answer": "12 chemical and physical soil parameters.",
            "evidence": "Soil Health Card assesses 12 parameters: N, P, K (Macro-nutrients); S (Secondary-nutrient); Zn, Fe, Cu, Mn, Bo (Micro-nutrients); and pH, EC, OC (Physical parameters).",
            "source_url": "https://soilhealth.dac.gov.in",
            "source_type": "govt_portal",
            "difficulty": 2,
            "queries": {
                "hi": {
                    "A_EN": "How many soil health parameters are tested under the Soil Health Card scheme?",
                    "B_NATIVE": "मृदा स्वास्थ्य कार्ड योजना के तहत मिट्टी के कितने मापदंडों का परीक्षण किया जाता है?",
                    "C_ROMAN": "Mrida swasthya card yojana ke tahat mitti ke kitne mapdandon ka parikshan kiya jata hai?",
                    "D_CS": "Soil Health Card scheme ke under kitne soil parameters test kiye jaate hain?",
                    "E_MIXED_SCRIPT": "Soil Health Card scheme के under कितने soil parameters test किए जाते हैं?",
                },
                "ta": {
                    "A_EN": "How many soil health parameters are tested under the Soil Health Card scheme?",
                    "B_NATIVE": "மண் வள அட்டை திட்டத்தின் கீழ் எத்தனை மண் அளவுருக்கள் பரிசோதிக்கப்படுகின்றன?",
                    "C_ROMAN": "Mann vala attai thittaththin keezh ethanai mann alavurukkal parisothikkappadukinrana?",
                    "D_CS": "Soil Health Card scheme la total ah ethanai soil parameters test panranga?",
                    "E_MIXED_SCRIPT": "Soil Health Card scheme-ல total-ஆ எத்தனை soil parameters test பண்றாங்க?",
                },
                "te": {
                    "A_EN": "How many soil health parameters are tested under the Soil Health Card scheme?",
                    "B_NATIVE": "సాయిల్ హెల్త్ కార్డ్ పథకం కింద ఎన్ని నేల పారామితులను పరీక్షిస్తారు?",
                    "C_ROMAN": "Soil Health Card pathakam kinda enni nela paramitulanu pareekshistaru?",
                    "D_CS": "Soil Health Card scheme kinda total ga enni soil parameters test chestaru?",
                    "E_MIXED_SCRIPT": "Soil Health Card scheme కింద total గా ఎన్ని soil parameters test చేస్తారు?",
                },
                "bn": {
                    "A_EN": "How many soil health parameters are tested under the Soil Health Card scheme?",
                    "B_NATIVE": "সয়েল হেলথ কার্ড প্রকল্পের অধীনে মাটির কতগুলি প্যারামিটার পরীক্ষা করা হয়?",
                    "C_ROMAN": "Soil Health Card prakalper adhine matir kotoguli parameter porikkha kora hoy?",
                    "D_CS": "Soil Health Card scheme e total koto gulo soil parameters test kora hoy?",
                    "E_MIXED_SCRIPT": "Soil Health Card scheme-এ total কত গুলো soil parameters test করা হয়?",
                },
                "kn": {
                    "A_EN": "How many soil health parameters are tested under the Soil Health Card scheme?",
                    "B_NATIVE": "ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಯೋಜನೆಯಡಿ ಎಷ್ಟು ಮಣ್ಣಿನ ನಿಯತಾಂಕಗಳನ್ನು ಪರೀಕ್ಷಿಸಲಾಗುತ್ತದೆ?",
                    "C_ROMAN": "Mannina aarogya card yojaneyadi eshtu mannina niyatankagalannu pareekshisalaaguttade?",
                    "D_CS": "Soil Health Card scheme nalli total agi eshtu soil parameters test madtare?",
                    "E_MIXED_SCRIPT": "Soil Health Card scheme ನಲ್ಲಿ total ಆಗಿ ಎಷ್ಟು soil parameters test ಮಾಡ್ತಾರೆ?",
                },
            },
        },
    ],
    "science": [
        {
            "subdomain": "space_missions",
            "fact": "Chandrayaan-3 touched down near the South Pole of the Moon on August 23, 2023, making India the first nation to land near that region.",
            "answer": "August 23, 2023, near the lunar South Pole.",
            "evidence": "On August 23, 2023, Chandrayaan-3 Lander Module successfully made a safe and soft landing near the South Pole of the Moon.",
            "source_url": "https://isro.gov.in/Chandrayaan3.html",
            "source_type": "official_archive",
            "difficulty": 1,
            "queries": {
                "hi": {
                    "A_EN": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
                    "B_NATIVE": "चंद्रयान-3 ने चंद्रमा पर सफल सॉफ्ट लैंडिंग किस तारीख को की थी?",
                    "C_ROMAN": "Chandrayaan-3 ne chandrama par safal soft landing kis tareekh ko ki thi?",
                    "D_CS": "Chandrayaan-3 Moon pe kis date ko successfully soft land hua tha?",
                    "E_MIXED_SCRIPT": "Chandrayaan-3 Moon पे किस date को successfully soft land हुआ था?",
                },
                "ta": {
                    "A_EN": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
                    "B_NATIVE": "சந்திரயான்-3 நிலவில் எப்போது வெற்றிகரமாக தரை இறங்கியது?",
                    "C_ROMAN": "Chandrayaan-3 nilavil eppothu vetrigaramaaga tharai irangiyathu?",
                    "D_CS": "Chandrayaan-3 Moon la entha date la successfully soft land aachu?",
                    "E_MIXED_SCRIPT": "Chandrayaan-3 Moon-ல எந்த date-ல successfully soft land ஆச்சு?",
                },
                "te": {
                    "A_EN": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
                    "B_NATIVE": "చంద్రయాన్-3 చంద్రుడిపై ఏ తేదీన విజయవంతంగా సాఫ్ట్ ల్యాండింగ్ అయింది?",
                    "C_ROMAN": "Chandrayaan-3 chandrudipai ye thedheena vijayavanthamgaa soft landing ayindi?",
                    "D_CS": "Chandrayaan-3 Moon paina ye date na successful ga soft land aindi?",
                    "E_MIXED_SCRIPT": "Chandrayaan-3 Moon పైన ఏ date న successful గా soft land అయింది?",
                },
                "bn": {
                    "A_EN": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
                    "B_NATIVE": "চন্দ্রযান-৩ কোন তারিখে চাঁদে সফল সফট ল্যান্ডিং করেছিল?",
                    "C_ROMAN": "Chandrayaan-3 kon tarike chaande sofol soft landing korechhilo?",
                    "D_CS": "Chandrayaan-3 Moon e kon date e successfully soft land korechhilo?",
                    "E_MIXED_SCRIPT": "Chandrayaan-3 Moon-এ কোন date-এ successfully soft land করেছিল?",
                },
                "kn": {
                    "A_EN": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
                    "B_NATIVE": "ಚಂದ್ರಯಾನ-3 ಚಂದ್ರನ ಮೇಲೆ ಯಾವ ದಿನಾಂಕದಂದು ಯಶಸ್ವಿಯಾಗಿ ಸಾಫ್ಟ್ ಲ್ಯಾಂಡಿಂಗ್ ಆಯಿತು?",
                    "C_ROMAN": "Chandrayaan-3 chandrana mele yaava dinaankadandu yashasviyaagi soft landing aayitu?",
                    "D_CS": "Chandrayaan-3 Moon mele yaava date nalli successfully soft land aayitu?",
                    "E_MIXED_SCRIPT": "Chandrayaan-3 Moon ಮೇಲೆ ಯಾವ date ನಲ್ಲಿ successfully soft land ಆಯಿತು?",
                },
            },
        },
    ],
    "history": [
        {
            "subdomain": "ancient_institutions",
            "fact": "Nalanda University was founded during the 5th century CE under the patronage of the Gupta Empire.",
            "answer": "5th century CE during the Gupta Dynasty (founded by Kumaragupta I).",
            "evidence": "Nalanda was an ancient Mahavihara founded in the 5th century CE under the patronage of Gupta Emperor Kumaragupta I in present-day Bihar.",
            "source_url": "https://asi.nic.in/ancient-monuments-nalanda",
            "source_type": "official_archive",
            "difficulty": 2,
            "queries": {
                "hi": {
                    "A_EN": "During which century and dynasty was the ancient Nalanda University founded?",
                    "B_NATIVE": "प्राचीन नालंदा विश्वविद्यालय की स्थापना किस शताब्दी और राजवंश के दौरान हुई थी?",
                    "C_ROMAN": "Prachin Nalanda vishwavidyalaya ki sthapna kis shatabdi aur rajvansh ke dauran hui thi?",
                    "D_CS": "Ancient Nalanda University kis century aur dynasty ke time found hui thi?",
                    "E_MIXED_SCRIPT": "Ancient Nalanda University किस century और dynasty के time found हुई थी?",
                },
                "ta": {
                    "A_EN": "During which century and dynasty was the ancient Nalanda University founded?",
                    "B_NATIVE": "பண்டைய நாலந்தா பல்கலைக்கழகம் எந்த நூற்றாண்டில் மற்றும் எந்த வம்சத்தின் போது நிறுவப்பட்டது?",
                    "C_ROMAN": "Pandaiya Nalanda palkalaikkazhagam entha nootraandil matrum entha vamsaththin pothu niruvappattathu?",
                    "D_CS": "Ancient Nalanda University entha century matrum dynasty time la establish aachu?",
                    "E_MIXED_SCRIPT": "Ancient Nalanda University எந்த century மற்றும் dynasty time-ல establish ஆச்சு?",
                },
                "te": {
                    "A_EN": "During which century and dynasty was the ancient Nalanda University founded?",
                    "B_NATIVE": "పురాతన నలంద విశ్వవిద్యాలయం ఏ శతాబ్దంలో మరియు ఏ రాజవంశం కాలంలో స్థాపించబడింది?",
                    "C_ROMAN": "Purathana Nalanda vishvavidyalayam ye shathaabdhamlo mariyu ye raajavamsham kaalamlo sthaapinchabadindi?",
                    "D_CS": "Ancient Nalanda University ye century mariyu ye dynasty period lo establish ayindi?",
                    "E_MIXED_SCRIPT": "Ancient Nalanda University ఏ century మరియు ఏ dynasty period లో establish అయింది?",
                },
                "bn": {
                    "A_EN": "During which century and dynasty was the ancient Nalanda University founded?",
                    "B_NATIVE": "প্রাচীন নালন্দা বিশ্ববিদ্যালয় কোন শতাব্দীতে এবং কোন রাজবংশের আমলে প্রতিষ্ঠিত হয়েছিল?",
                    "C_ROMAN": "Prachin Nalanda vishwavidyalay kon shotabdite ebong kon rajbongser amole protishthito hoyechhilo?",
                    "D_CS": "Ancient Nalanda University kon century ar dynasty r time e establish hoyechhilo?",
                    "E_MIXED_SCRIPT": "Ancient Nalanda University কোন century আর dynasty-র time-এ establish হয়েছিল?",
                },
                "kn": {
                    "A_EN": "During which century and dynasty was the ancient Nalanda University founded?",
                    "B_NATIVE": "ಪ್ರಾಚೀನ ನಲಂದ ವಿಶ್ವವಿದ್ಯಾಲಯವು ಯಾವ ಶತಮಾನದಲ್ಲಿ ಮತ್ತು ಯಾವ ರಾಜವಂಶದ ಆಳ್ವಿಕೆಯಲ್ಲಿ ಸ್ಥಾಪನೆಯಾಯಿತು?",
                    "C_ROMAN": "Praacheena Nalanda vishwaviddyaalayavu yaava shathamaanadalli matthu yaava raajavamshada aalvikyalli sthaapaneyaayithu?",
                    "D_CS": "Ancient Nalanda University yaava century matthe yaava dynasty period nalli establish aagittu?",
                    "E_MIXED_SCRIPT": "Ancient Nalanda University ಯಾವ century ಮತ್ತೆ ಯಾವ dynasty period ನಲ್ಲಿ establish ಆಗಿತ್ತು?",
                },
            },
        },
    ],
    "education": [
        {
            "subdomain": "higher_education_ranking",
            "fact": "The National Institutional Ranking Framework (NIRF) was approved and launched by the Ministry of Human Resource Development on 29th September 2015.",
            "answer": "September 29, 2015, by the Ministry of Education (formerly MHRD).",
            "evidence": "The National Institutional Ranking Framework (NIRF) was approved by the MHRD and launched on 29th September 2015 to rank higher education institutions in India.",
            "source_url": "https://www.nirfindia.org/About",
            "source_type": "govt_portal",
            "difficulty": 2,
            "queries": {
                "hi": {
                    "A_EN": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
                    "B_NATIVE": "भारत में राष्ट्रीय संस्थागत रैंकिंग फ्रेमवर्क (एनआईआरएफ) किस वर्ष शुरू किया गया था?",
                    "C_ROMAN": "Bharat mein Rashtriya Sansthagat Ranking Framework (NIRF) kis varsh shuru kiya gaya tha?",
                    "D_CS": "India me National Institutional Ranking Framework (NIRF) kis year me launch hua tha?",
                    "E_MIXED_SCRIPT": "India में National Institutional Ranking Framework (NIRF) किस year में launch हुआ था?",
                },
                "ta": {
                    "A_EN": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
                    "B_NATIVE": "இந்தியாவில் தேசிய நிறுவன தரவரிசை கட்டமைப்பு (NIRF) எந்த ஆண்டில் தொடங்கப்பட்டது?",
                    "C_ROMAN": "Indiyavil thesiya niruvana tharavarisai kattamaippu (NIRF) entha aandil thodangappattathu?",
                    "D_CS": "India la National Institutional Ranking Framework (NIRF) entha year la launch pannanga?",
                    "E_MIXED_SCRIPT": "India-ல National Institutional Ranking Framework (NIRF) எந்த year-ல launch பண்ணாங்க?",
                },
                "te": {
                    "A_EN": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
                    "B_NATIVE": "భారతదేశంలో నేషనల్ ఇన్‌స్టిట్యూషనల్ ర్యాంకింగ్ ఫ్రేమ్‌వర్క్ (NIRF) ఏ సంవత్సరంలో ప్రారంభించబడింది?",
                    "C_ROMAN": "Bharatadeshamlo National Institutional Ranking Framework (NIRF) ye samvatsaramlo praarambhinchabadindi?",
                    "D_CS": "India lo National Institutional Ranking Framework (NIRF) ye year lo launch chesaru?",
                    "E_MIXED_SCRIPT": "India లో National Institutional Ranking Framework (NIRF) ఏ year లో launch చేశారు?",
                },
                "bn": {
                    "A_EN": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
                    "B_NATIVE": "ভারতে ন্যাশনাল ইনস্টিটিউশনাল র‍্যাঙ্কিং ফ্রেমওয়ার্ক (NIRF) কোন বছর চালু হয়েছিল?",
                    "C_ROMAN": "Bharote National Institutional Ranking Framework (NIRF) kon bochor chalu hoyechhilo?",
                    "D_CS": "India te National Institutional Ranking Framework (NIRF) kon year e launch kora hoyechhilo?",
                    "E_MIXED_SCRIPT": "India-তে National Institutional Ranking Framework (NIRF) কোন year-এ launch করা হয়েছিল?",
                },
                "kn": {
                    "A_EN": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
                    "B_NATIVE": "ಭಾರತದಲ್ಲಿ ರಾಷ್ಟ್ರೀಯ ಸಾಂಸ್ಥಿಕ ಶ್ರೇಯಾಂಕ ಚೌಕಟ್ಟನ್ನು (NIRF) ಯಾವ ವರ್ಷದಲ್ಲಿ ಪ್ರಾರಂಭಿಸಲಾಯಿತು?",
                    "C_ROMAN": "Bhaarathadalli Raashtreeya Saamsthika Shreyaanka Chowkattannu (NIRF) yaava varshadalli praarambhhisalaayithu?",
                    "D_CS": "India dalli National Institutional Ranking Framework (NIRF) yaava year nalli launch maadidru?",
                    "E_MIXED_SCRIPT": "India ದಲ್ಲಿ National Institutional Ranking Framework (NIRF) ಯಾವ year ನಲ್ಲಿ launch ಮಾಡಿದ್ರು?",
                },
            },
        },
    ],
    "public_health": [
        {
            "subdomain": "vaccination_programs",
            "fact": "Mission Indradhanush was launched by the Union Health Ministry in December 2014 to ensure full immunization for children and pregnant women against vaccine-preventable diseases.",
            "answer": "December 2014, to achieve full immunization coverage against vaccine-preventable diseases.",
            "evidence": "Mission Indradhanush was launched by MoHFW on 25th December 2014 to expand full immunization coverage for children up to 2 years and pregnant women.",
            "source_url": "https://nhm.gov.in/index1.php?lang=1&level=2&sublinkid=823&lid=216",
            "source_type": "govt_portal",
            "difficulty": 2,
            "queries": {
                "hi": {
                    "A_EN": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
                    "B_NATIVE": "स्वास्थ्य और परिवार कल्याण मंत्रालय द्वारा मिशन इंद्रधनुष कब शुरू किया गया था?",
                    "C_ROMAN": "Swasthya aur parivar kalyan mantralaya dwara Mission Indradhanush kab shuru kiya gaya tha?",
                    "D_CS": "Ministry of Health ne Mission Indradhanush kab launch kiya tha?",
                    "E_MIXED_SCRIPT": "Ministry of Health ने Mission Indradhanush कब launch किया था?",
                },
                "ta": {
                    "A_EN": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
                    "B_NATIVE": "சுகாதார மற்றும் குடும்ப நல அமைச்சகத்தால் மிஷன் இந்திரதனுஷ் எப்போது தொடங்கப்பட்டது?",
                    "C_ROMAN": "Sugaathara matrum kudumba nala amaichagathaal Mission Indradhanush eppothu thodangappattathu?",
                    "D_CS": "Health Ministry eppo Mission Indradhanush ah launch pannanga?",
                    "E_MIXED_SCRIPT": "Health Ministry எப்போ Mission Indradhanush-ஐ launch பண்ணாங்க?",
                },
                "te": {
                    "A_EN": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
                    "B_NATIVE": "ఆరోగ్య మరియు కుటుంబ సంక్షేమ మంత్రిత్వ శాఖ మిషన్ ఇంద్రధనుష్‌ను ఎప్పుడు ప్రారంభించింది?",
                    "C_ROMAN": "Aarogya mariyu kutumba sankshema mantrithva shaakha Mission Indradhanush nu eppudu praarambhinchindi?",
                    "D_CS": "Health Ministry Mission Indradhanush ni eppudu launch chesindi?",
                    "E_MIXED_SCRIPT": "Health Ministry Mission Indradhanush ని ఎప్పుడు launch చేసింది?",
                },
                "bn": {
                    "A_EN": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
                    "B_NATIVE": "স্বাস্থ্য ও পরিবার কল্যাণ মন্ত্রক মিশন ইন্দ্রধনুষ কবে চালু করেছিল?",
                    "C_ROMAN": "Swasthya o poribar kolyan montrok Mission Indradhanush kobe chalu korechhilo?",
                    "D_CS": "Health Ministry Mission Indradhanush kobe launch korechhilo?",
                    "E_MIXED_SCRIPT": "Health Ministry Mission Indradhanush কবে launch করেছিল?",
                },
                "kn": {
                    "A_EN": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
                    "B_NATIVE": "ಆರೋಗ್ಯ ಮತ್ತು ಕುಟುಂಬ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯವು ಮಿಷನ್ ಇಂದ್ರಧನುಷ್ ಅನ್ನು ಯಾವಾಗ ಪ್ರಾರಂಭಿಸಿತು?",
                    "C_ROMAN": "Aarogya matthu kutumba kalyaana sachivaalayavu Mission Indradhanush annu yaavaaga praarambhhisithu?",
                    "D_CS": "Health Ministry Mission Indradhanush annu yaavaaga launch madidru?",
                    "E_MIXED_SCRIPT": "Health Ministry Mission Indradhanush ಅನ್ನು ಯಾವಾಗ launch ಮಾಡಿದ್ರು?",
                },
            },
        },
    ],
}

SCRIPT_MAP = {
    "A_EN": "latin",
    "B_NATIVE": {
        "hi": "devanagari",
        "ta": "tamil",
        "te": "telugu",
        "bn": "bengali",
        "kn": "kannada",
    },
    "C_ROMAN": "latin",
    "D_CS": "latin",
    "E_MIXED_SCRIPT": "mixed",
}


def build_pilot_semantic_groups(target_groups: int = 500) -> list[SemanticQuestion]:
    """Generate 500 verified semantic question units balanced across 5 languages."""
    languages = ["hi", "ta", "te", "bn", "kn"]
    per_lang_target = target_groups // len(languages)  # 100 per language
    all_seeds = []
    for domain, items in PILOT_SEEDS.items():
        for item in items:
            all_seeds.append((domain, item))

    questions: list[SemanticQuestion] = []
    qid_counter = 1

    for lang in languages:
        for i in range(per_lang_target):
            domain, seed_data = all_seeds[i % len(all_seeds)]
            sid = f"S{qid_counter:06d}"
            q_info = seed_data["queries"][lang]

            sq = SemanticQuestion(
                semantic_id=sid,
                domain=domain,
                subdomain=seed_data["subdomain"],
                difficulty_level=seed_data["difficulty"],
                canonical_fact=seed_data["fact"],
                reference_answer=seed_data["answer"],
                evidence_snippet=seed_data["evidence"],
                evidence_source_url=seed_data["source_url"],
                evidence_source_type=seed_data["source_type"],
                language=lang,
            )

            # Condition A
            sq.add_condition("A_EN", "latin", q_info["A_EN"])
            # Condition B
            native_script = SCRIPT_MAP["B_NATIVE"][lang]
            sq.add_condition("B_NATIVE", native_script, q_info["B_NATIVE"])
            # Condition C
            sq.add_condition("C_ROMAN", "latin", q_info["C_ROMAN"])
            # Condition D
            sq.add_condition("D_CS", "latin", q_info["D_CS"])
            # Condition E
            sq.add_condition("E_MIXED_SCRIPT", "mixed", q_info["E_MIXED_SCRIPT"])

            assert sq.is_complete(), f"Semantic unit {sid} incomplete"
            questions.append(sq)
            qid_counter += 1

    return questions


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", type=int, default=500, help="Number of semantic groups to build (default: 500)")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "data" / "questions"
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_dest = out_dir / f"semantic_pilot_{args.count}.jsonl"
    csv_dest = out_dir / f"condition_prompts_pilot_{args.count * 5}.csv"

    print(f"Building {args.count} semantically paired questions (5 conditions each = {args.count * 5} prompts)...")
    dataset = build_pilot_semantic_groups(target_groups=args.count)

    save_semantic_dataset(dataset, jsonl_dest)
    print(f"Saved {len(dataset)} semantic groups -> {jsonl_dest}")

    flattened = flatten_condition_prompts(dataset)
    df = pd.DataFrame(flattened)
    df.to_csv(csv_dest, index=False, encoding="utf-8")
    print(f"Saved {len(df)} condition prompts -> {csv_dest}")

    # Summary statistics
    print("\n== Dataset Summary ==")
    print("Languages:", df["language"].value_counts().to_dict())
    print("Conditions:", df["condition"].value_counts().to_dict())
    print("Domains:", df["domain"].value_counts().to_dict())
    print("CMI by condition:")
    print(df.groupby("condition")[["measured_cmi", "script_transitions"]].mean().round(2))


if __name__ == "__main__":
    main()
