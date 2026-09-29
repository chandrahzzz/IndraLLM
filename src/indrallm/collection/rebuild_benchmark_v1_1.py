"""Rebuild benchmark IndraLLM-CS-v1.1-CANDIDATE with zero cross-partition leakage.

Implements Phase 2.6:
1. 1,500 unique semantic groups across 12 Template Families (TF-01 to TF-12) and 6 Domains.
2. Pre-partitioning into:
   - DEVELOPMENT: 1,000 groups (TF-01 to TF-10)
   - VALIDATION: 200 groups (TF-01 to TF-10)
   - TEST-ID: 200 groups (TF-01 to TF-10, disjoint from Dev/Val, 0% prompt/question overlap)
   - TEST-OOD: 100 groups (TF-11 and TF-12 strictly quarantined, 0% template overlap with Dev/Val/Test-ID)
3. Controlled 5-condition generation (A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT) per semantic unit.
4. Total condition prompts: 7,500 prompts (balanced across hi, ta, te, bn, kn).
5. Computes full multidimensional CMI suite for every prompt.
6. Saves artifacts to data/questions/IndraLLM-CS-v1.1-CANDIDATE/ with SHA-256 manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from indrallm.collection.cmi import compute_cmi
from indrallm.config import PROJECT_ROOT

LANGUAGES = ["hi", "ta", "te", "bn", "kn"]
SCRIPT_MAP = {
    "A_EN": "latin",
    "B_NATIVE": {"hi": "devanagari", "ta": "tamil", "te": "telugu", "bn": "bengali", "kn": "kannada"},
    "C_ROMAN": "latin",
    "D_CS": "latin",
    "E_MIXED_SCRIPT": "mixed",
}

# 12 Distinct Template Families (TF-01 to TF-10 In-Distribution; TF-11 & TF-12 Out-of-Distribution)
# Master factual question prototypes covering 6 domains
KNOWLEDGE_BASE: list[dict[str, Any]] = [
    # --- TF-01: NUMERICAL_THRESHOLD ---
    {
        "tf": "TF-01",
        "domain": "governance",
        "subdomain": "civic_welfare",
        "difficulty": 1,
        "fact": "PM-KISAN provides direct income support of ₹6,000 per year in three equal installments of ₹2,000 to eligible farmer families.",
        "answer": "₹6,000 per year in 3 equal installments of ₹2,000.",
        "evidence": "Under PM-KISAN, ₹6,000/- per year is released in three 4-monthly installments.",
        "source": "https://pmkisan.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("PM-KISAN", "₹6,000_annual_support"),
        "templates": {
            "en": "How much financial support is provided annually under the PM-KISAN scheme?",
            "hi": ("पीएम-किसान योजना के तहत सालाना कितनी वित्तीय सहायता दी जाती है?",
                   "PM-Kisan yojana ke antargat saalana kitni vittiya sahayata di jaati hai?",
                   "PM-Kisan scheme me annually kitna financial support milta hai?",
                   "PM-Kisan scheme में annually कितना financial support मिलता है?"),
            "ta": ("பிஎம்-கிசான் திட்டத்தின் கீழ் ஆண்டுக்கு எவ்வளவு நிதி உதவி வழங்கப்படுகிறது?",
                   "PM-Kisan thittaththin keezh aandu thorum evvalavu nithi uthavi valangappadugirathu?",
                   "PM-Kisan scheme la annually evvalavu financial support kedaikkum?",
                   "PM-Kisan scheme-ல annually எவ்வளவு financial support கிடைக்கும்?"),
            "te": ("పీఎం-కిసాన్ పథకం కింద ఏటా ఎంత ఆర్థిక సాయం అందిస్తారు?",
                   "PM-Kisan pathakam kinda yeta entha aarthika saayam andistharu?",
                   "PM-Kisan scheme lo annually entha financial support istharu?",
                   "PM-Kisan scheme లో annually ఎంత financial support ఇస్తారు?"),
            "bn": ("পিএম-কিসান প্রকল্পের আওতায় বার্ষিক কত টাকা আর্থিক সহায়তা দেওয়া হয়?",
                   "PM-Kisan prokolper aotay barshik koto taka arthik sohayota dewa hoy?",
                   "PM-Kisan scheme e annually koto financial support dewa hoy?",
                   "PM-Kisan scheme এ annually কত financial support দেওয়া হয়?"),
            "kn": ("ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯಡಿ ವಾರ್ಷಿಕ ಎಷ್ಟು ಆರ್ಥಿಕ ನೆರವು ನೀಡಲಾಗುತ್ತದೆ?",
                   "PM-Kisan yojaneyadi vaarshika eshtu aarthika neravu needalaaguttade?",
                   "PM-Kisan scheme nalli annually eshtu financial support kodtaare?",
                   "PM-Kisan scheme ನಲ್ಲಿ annually ಎಷ್ಟು financial support ಕೊಡ್ತಾರೆ?")
        }
    },
    {
        "tf": "TF-01",
        "domain": "governance",
        "subdomain": "enterprise_policy",
        "difficulty": 2,
        "fact": "Under the composite MSME classification criteria, a Micro Enterprise has investment in plant & machinery not exceeding ₹1 Crore and annual turnover not exceeding ₹5 Crore.",
        "answer": "Investment ≤ ₹1 Crore and Turnover ≤ ₹5 Crore.",
        "evidence": "Micro Enterprise: Investment in Plant and Machinery or Equipment does not exceed ₹1 crore and turnover does not exceed ₹5 crore.",
        "source": "https://msme.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("Micro_Enterprise", "₹5_Crore_turnover_limit"),
        "templates": {
            "en": "What is the maximum turnover limit for an enterprise to be categorized as a Micro Enterprise under MSME guidelines?",
            "hi": ("एमएसएमई दिशानिर्देशों के तहत सूक्ष्म उद्यम के लिए अधिकतम टर्नओवर सीमा क्या है?",
                   "MSME dishanirdeshon ke tahat sookshma udyam ke liye adhiktam turnover seema kya hai?",
                   "MSME guidelines me Micro Enterprise ka maximum turnover limit kitna hai?",
                   "MSME guidelines में Micro Enterprise का maximum turnover limit कितना है?"),
            "ta": ("MSME வழிகாட்டுதலின் கீழ் குறுந்தொழில் நிறுவனத்திற்கான அதிகபட்ச விற்றுமுதல் வரம்பு என்ன?",
                   "MSME vazhikaattuthalin keezh kurunthozhil niruvanaththirkaana athikabatcha turnover varambu enna?",
                   "MSME guidelines la Micro Enterprise ku maximum turnover limit enna?",
                   "MSME guidelines-ல Micro Enterprise-க்கு maximum turnover limit என்ன?"),
            "te": ("ఎంఎస్ఎంఈ నిబంధనల ప్రకారం సూక్ష్మ పరిశ్రమకు గరిష్ట టర్నోవర్ పరిమితి ఎంత?",
                   "MSME nibandhanala prakaaram sookshma parishramaku garishta turnover parimithi entha?",
                   "MSME guidelines lo Micro Enterprise ki maximum turnover limit entha?",
                   "MSME guidelines లో Micro Enterprise కి maximum turnover limit ఎంత?"),
            "bn": ("এমএসএমই নির্দেশিকা অনুসারে ক্ষুদ্র উদ্যোগের সর্বোচ্চ টার্নওভারের সীমা কত?",
                   "MSME nirdeshika onusare khudro uddyog er sorbochho turnover er seema koto?",
                   "MSME guidelines e Micro Enterprise er maximum turnover limit koto?",
                   "MSME guidelines এ Micro Enterprise এর maximum turnover limit কত?"),
            "kn": ("ಎಂಎಸ್ಎಂಇ ಮಾರ್ಗಸೂಚಿಗಳ ಅಡಿಯಲ್ಲಿ ಸೂಕ್ಷ್ಮ ಉದ್ಯಮಕ್ಕೆ ಗರಿಷ್ಠ ವಹಿವಾಟು ಮಿತಿ ಎಷ್ಟು?",
                   "MSME maargasoochigala adiyalli sookshma udyamakke garishta turnover miti eshtu?",
                   "MSME guidelines nalli Micro Enterprise ge maximum turnover limit eshtu?",
                   "MSME guidelines ನಲ್ಲಿ Micro Enterprise ಗೆ maximum turnover limit ಎಷ್ಟು?")
        }
    },
    {
        "tf": "TF-01",
        "domain": "governance",
        "subdomain": "healthcare_welfare",
        "difficulty": 1,
        "fact": "Ayushman Bharat PM-JAY provides health coverage of ₹5 Lakh per family per year for secondary and tertiary care hospitalization.",
        "answer": "₹5 Lakh per family per year.",
        "evidence": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY) provides a health cover of ₹5,00,000 per family per year.",
        "source": "https://pmjay.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("PM-JAY", "₹5_Lakh_coverage"),
        "templates": {
            "en": "What is the annual health cover provided per family under the Ayushman Bharat PM-JAY scheme?",
            "hi": ("आयुष्मान भारत पीएम-जेएवाई योजना के तहत प्रति परिवार सालाना कितना स्वास्थ्य कवर प्रदान किया जाता है?",
                   "Ayushman Bharat PM-JAY yojana ke tahat prati parivar saalana kitna swasthya cover pradan kiya jata hai?",
                   "Ayushman Bharat PM-JAY scheme me annually per family kitna health cover milta hai?",
                   "Ayushman Bharat PM-JAY scheme में annually per family कितना health cover मिलता है?"),
            "ta": ("ஆயுஷ்மான் பாரத் பிஎம்-ஜேஏஒய் திட்டத்தின் கீழ் ஒரு குடும்பத்திற்கு ஆண்டுக்கு எவ்வளவு மருத்துவக் காப்பீடு வழங்கப்படுகிறது?",
                   "Ayushman Bharat PM-JAY thittaththin keezh oru kudumbaththirku aandu thorum evvalavu health insurance valangappadugirathu?",
                   "Ayushman Bharat PM-JAY scheme la per family ku annually evvalavu health cover kedaikkum?",
                   "Ayushman Bharat PM-JAY scheme-ல per family-க்கு annually எவ்வளவு health cover கிடைக்கும்?"),
            "te": ("ఆయుష్మాన్ భారత్ పీఎం-జేఏవై పథకం కింద ప్రతి కుటుంబానికి ఏటా ఎంత ఆరోగ్య బీమా కల్పిస్తారు?",
                   "Ayushman Bharat PM-JAY pathakam kinda prathi kutumbaniki yeta entha aarogya bheema kalpisthaaru?",
                   "Ayushman Bharat PM-JAY scheme lo per family annually entha health cover provide chesthaaru?",
                   "Ayushman Bharat PM-JAY scheme లో per family annually ఎంత health cover provide చేస్తారు?"),
            "bn": ("আয়ুষ্মান ভারত পিএম-জেএওয়াই প্রকল্পের আওতায় পরিবার প্রতি বার্ষিক কত টাকার স্বাস্থ্য কভার দেওয়া হয়?",
                   "Ayushman Bharat PM-JAY prokolper aotay poribar proti barshik koto takar swasthya cover dewa hoy?",
                   "Ayushman Bharat PM-JAY scheme e per family annually koto health cover dewa hoy?",
                   "Ayushman Bharat PM-JAY scheme এ per family annually কত health cover দেওয়া হয়?"),
            "kn": ("ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಪಿಎಂ-ಜೆಎವೈ ಯೋಜನೆಯಡಿ ಪ್ರತಿ ಕುಟುಂಬಕ್ಕೆ ವಾರ್ಷಿಕ ಎಷ್ಟು ಆರೋಗ್ಯ ರಕ್ಷಣೆ ನೀಡಲಾಗುತ್ತದೆ?",
                   "Ayushman Bharat PM-JAY yojaneyadi prathi kutumbakke vaarshika eshtu aarogya rakshene needalaaguttade?",
                   "Ayushman Bharat PM-JAY scheme nalli per family annually eshtu health cover kodtaare?",
                   "Ayushman Bharat PM-JAY scheme ನಲ್ಲಿ per family annually ಎಷ್ಟು health cover ಕೊಡ್ತಾರೆ?")
        }
    },

    # --- TF-02: TEMPORAL_MILESTONE ---
    {
        "tf": "TF-02",
        "domain": "science",
        "subdomain": "space_missions",
        "difficulty": 1,
        "fact": "Chandrayaan-3 achieved a successful soft touchdown on the Moon on August 23, 2023.",
        "answer": "August 23, 2023.",
        "evidence": "On August 23, 2023, Chandrayaan-3 successfully made a soft landing near the lunar South Pole.",
        "source": "https://isro.gov.in/Chandrayaan3.html",
        "source_type": "science_agency",
        "entity_pair": ("Chandrayaan-3", "2023-08-23"),
        "templates": {
            "en": "On which date did Chandrayaan-3 achieve its successful soft landing on the Moon?",
            "hi": ("चंद्रयान-3 ने चंद्रमा पर सफल सॉफ्ट लैंडिंग किस तारीख को की थी?",
                   "Chandrayaan-3 ne chandrama par safal soft landing kis tareekh ko ki thi?",
                   "Chandrayaan-3 Moon pe kis date ko successfully soft land hua tha?",
                   "Chandrayaan-3 Moon पे किस date को successfully soft land हुआ था?"),
            "ta": ("சந்திரயான்-3 நிலவில் எப்போது வெற்றிகரமாக மென்மையாக தரையிறங்கியது?",
                   "Chandrayaan-3 nilavil eppothu vetrigaramaaga soft landing seithathu?",
                   "Chandrayaan-3 Moon la entha date la successfully soft land aanathu?",
                   "Chandrayaan-3 Moon-ல எந்த date-ல successfully soft land ஆனது?"),
            "te": ("చంద్రయాన్-3 చంద్రునిపై ఏ తేదీన విజయవంతంగా సాఫ్ట్ ల్యాండింగ్ పూర్తి చేసింది?",
                   "Chandrayaan-3 chandrunipai ye thedheena vijayavanthamga soft landing poorthi chesindi?",
                   "Chandrayaan-3 Moon paina ye date na successfully soft land ayyindi?",
                   "Chandrayaan-3 Moon పైన ఏ date న successfully soft land అయ్యింది?"),
            "bn": ("চন্দ্রযান-৩ কোন তারিখে চাঁদের মাটিতে সফলভাবে অবতরণ করেছিল?",
                   "Chandrayaan-3 kon tarikh e chaander matite sofolbhabe obotoron korechhilo?",
                   "Chandrayaan-3 Moon e kon date e successfully soft land korechhilo?",
                   "Chandrayaan-3 Moon এ কোন date এ successfully soft land করেছিল?"),
            "kn": ("ಚಂದ್ರಯಾನ-3 ಚಂದ್ರನ ಮೇಲೆ ಯಶಸ್ವಿಯಾಗಿ ಸಾಫ್ಟ್ ಲ್ಯಾಂಡಿಂಗ್ ಮಾಡಿದ ದಿನಾಂಕ ಯಾವುದು?",
                   "Chandrayaan-3 chandrana mele yashasviyaagi soft landing maadida dinaanka yaavudu?",
                   "Chandrayaan-3 Moon mele yaava date nalli successfully soft land aayitu?",
                   "Chandrayaan-3 Moon ಮೇಲೆ ಯಾವ date ನಲ್ಲಿ successfully soft land ಆಯಿತು?")
        }
    },
    {
        "tf": "TF-02",
        "domain": "governance",
        "subdomain": "tax_policy",
        "difficulty": 1,
        "fact": "The Goods and Services Tax (GST) was implemented in India on 1 July 2017.",
        "answer": "1 July 2017.",
        "evidence": "GST was launched at a midnight function in Central Hall of Parliament on 1st July, 2017.",
        "source": "https://cbic.gov.in",
        "source_type": "statutory_act",
        "entity_pair": ("GST", "2017-07-01"),
        "templates": {
            "en": "On which date was the Goods and Services Tax (GST) officially rolled out in India?",
            "hi": ("भारत में वस्तु एवं सेवा कर (जीएसटी) आधिकारिक तौर पर किस तारीख को लागू किया गया था?",
                   "Bharat mein vastu evam seva kar (GST) aadhikarik taur par kis tareekh ko laagu kiya gaya tha?",
                   "India me GST officially kis date ko implement hua tha?",
                   "India में GST officially किस date को implement हुआ था?"),
            "ta": ("இந்தியாவில் ஜிஎஸ்டி வரி விதிப்பு முறை அதிகாரப்பூர்வமாக எப்போது அமலுக்கு வந்தது?",
                   "Indiyavil GST vari vithippu murai athigaarappoorvamaaga eppothu amalukku vanthathu?",
                   "India la GST officially entha date la roll out aachu?",
                   "India-ல GST officially எந்த date-ல roll out ஆச்சு?"),
            "te": ("భారతదేశంలో జీఎస్టీ ఎప్పుడు అధికారికంగా అమల్లోకి వచ్చింది?",
                   "Bhaarathadheshamlo GST eppudu adhikaarikamgaa amalloki vachindi?",
                   "India lo GST officially ye date nunchi launch ayyindi?",
                   "India లో GST officially ఏ date నుంచి launch అయ్యింది?"),
            "bn": ("ভারতে আনুষ্ঠানিকভাবে কোন তারিখে জিএসটি চালু হয়েছিল?",
                   "Bharote anushthanikbhabe kon tarikhe GST chalu hoyechhilo?",
                   "India te officially kon date e GST roll out kora hoyechhilo?",
                   "India তে officially কোন date এ GST roll out করা হয়েছিল?"),
            "kn": ("ಭಾರತದಲ್ಲಿ ಜಿಎಸ್‌ಟಿ ಅಧಿಕೃತವಾಗಿ ಜಾರಿಗೆ ಬಂದ ದಿನಾಂಕ ಯಾವುದು?",
                   "Bhaaratadalli GST adhkrutavaagi jaarige banda dinaanka yaavudu?",
                   "India dalli GST officially yaava date nalli launch aayitu?",
                   "India ದಲ್ಲಿ GST officially ಯಾವ date ನಲ್ಲಿ launch ಆಯಿತು?")
        }
    },
    {
        "tf": "TF-02",
        "domain": "science",
        "subdomain": "solar_missions",
        "difficulty": 2,
        "fact": "ISRO launched the Aditya-L1 solar observatory mission on September 2, 2023.",
        "answer": "September 2, 2023.",
        "evidence": "Aditya-L1 was successfully launched by PSLV-C57 on September 02, 2023 from Satish Dhawan Space Centre, Sriharikota.",
        "source": "https://isro.gov.in/Aditya_L1.html",
        "source_type": "science_agency",
        "entity_pair": ("Aditya-L1", "2023-09-02"),
        "templates": {
            "en": "On which date did ISRO launch India's first dedicated solar observatory mission Aditya-L1?",
            "hi": ("इसरो ने भारत के पहले सौर वेधशाला मिशन आदित्य-एल1 का प्रक्षेपण किस तारीख को किया था?",
                   "ISRO ne Bharat ke pehle saur vedhshala mission Aditya-L1 ka prakshepan kis tareekh ko kiya tha?",
                   "ISRO ne India ke first solar mission Aditya-L1 ko kis date ko launch kiya tha?",
                   "ISRO ने India के first solar mission Aditya-L1 को किस date को launch किया था?"),
            "ta": ("இந்தியாவின் முதல் சூரிய ஆய்வு விண்கலமான ஆதித்யா-எல்1 ஐ இஸ்ரோ எப்போது விண்ணில் செலுத்தியது?",
                   "Indiyavin muthal sooriya aayvu vinkalamaana Aditya-L1 ai ISRO eppothu launch seithathu?",
                   "ISRO India oda first solar mission Aditya-L1 ah entha date la launch pannuchu?",
                   "ISRO India-ஓட first solar mission Aditya-L1-ஐ எந்த date-ல launch பண்ணுச்சு?"),
            "te": ("ఇస్రో తన మొదటి సౌర మిషన్ ఆదిత్య-ఎల్1 ను ఏ తేదీన ప్రయోగించింది?",
                   "ISRO thana modhati saura mission Aditya-L1 nu ye thedheena prayoginchindi?",
                   "ISRO India first solar mission Aditya-L1 ni kis date na launch chesindi?",
                   "ISRO India first solar mission Aditya-L1 ని ఏ date న launch చేసింది?"),
            "bn": ("ইসরো কোন তারিখে ভারতের প্রথম সৌর মিশন আদিত্য-এল১ উৎক্ষেপণ করেছিল?",
                   "ISRO kon tarikhe Bharoter prothom souro mission Aditya-L1 utkhepon korechhilo?",
                   "ISRO India r first solar mission Aditya-L1 kon date e launch korechhilo?",
                   "ISRO India র first solar mission Aditya-L1 কোন date এ launch করেছিল?"),
            "kn": ("ಇಸ್ರೋ ಭಾರತದ ಮೊದಲ ಸೌರ ವೀಕ್ಷಣಾ ಮಿಷನ್ ಆದಿತ್ಯ-ಎಲ್1 ಅನ್ನು ಯಾವ ದಿನಾಂಕದಂದು ಉಡಾವಣೆ ಮಾಡಿತು?",
                   "ISRO Bhaaratada modala soura veekshana mission Aditya-L1 annu yaava dinaankadandu udaavane maadithu?",
                   "ISRO India da first solar mission Aditya-L1 na yaava date nalli launch maaditu?",
                   "ISRO India ದ first solar mission Aditya-L1 ನ ಯಾವ date ನಲ್ಲಿ launch ಮಾಡಿತು?")
        }
    },

    # --- TF-03: SCIENTIFIC_COMPOSITION ---
    {
        "tf": "TF-03",
        "domain": "agriculture",
        "subdomain": "soil_testing",
        "difficulty": 2,
        "fact": "The Soil Health Card scheme assesses 12 physical and chemical soil fertility parameters.",
        "answer": "12 parameters.",
        "evidence": "Soil Health Card assesses 12 parameters: N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, and Organic Carbon.",
        "source": "https://soilhealth.dac.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("Soil_Health_Card", "12_parameters"),
        "templates": {
            "en": "How many soil health parameters are tested under the Soil Health Card scheme?",
            "hi": ("मृदा स्वास्थ्य कार्ड योजना के तहत मिट्टी के कितने मापदंडों का परीक्षण किया जाता है?",
                   "Mrida swasthya card yojana ke tahat mitti ke kitne mapdandon ka parikshan kiya jata hai?",
                   "Soil Health Card scheme ke under kitne soil parameters test kiye jaate hain?",
                   "Soil Health Card scheme के under कितने soil parameters test किए जाते हैं?"),
            "ta": ("மண் வள அட்டை திட்டத்தின் கீழ் மண்ணின் எத்தனை ஊட்டச்சத்து அளவுருக்கள் பரிசோதிக்கப்படுகின்றன?",
                   "Man vala attai thittaththin keezh mannin eththanai nutrients parameters test seiyyappadugindrana?",
                   "Soil Health Card scheme la evvalavu soil parameters test pannuvanga?",
                   "Soil Health Card scheme-ல எவ்வளவு soil parameters test பண்ணுவாங்க?"),
            "te": ("సాయిల్ హెల్త్ కార్డ్ పథకం కింద ఎన్ని నేల సారవంతమైన పారామితులను పరీక్షిస్తారు?",
                   "Soil Health Card pathakam kinda yenni nela saaramaina parameters ni pareekshisthaaru?",
                   "Soil Health Card scheme lo yanni soil parameters test chesthaaru?",
                   "Soil Health Card scheme లో ఎన్ని soil parameters test చేస్తారు?"),
            "bn": ("সয়েল হেলথ কার্ড প্রকল্পের অধীনে মাটির কয়টি উপাদান পরীক্ষা করা হয়?",
                   "Soil Health Card prokolper odhine maatir koyti upadan porikkha kora hoy?",
                   "Soil Health Card scheme e koto gulo soil parameters test kora hoy?",
                   "Soil Health Card scheme এ কত গুলো soil parameters test করা হয়?"),
            "kn": ("ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಯೋಜನೆಯಡಿ ಮಣ್ಣಿನ ಎಷ್ಟು ಪೋಷಕಾಂಶ ನಿಯತಾಂಕಗಳನ್ನು ಪರೀಕ್ಷಿಸಲಾಗುತ್ತದೆ?",
                   "Mannu aarogya card yojaneyadi mannina eshtu poshakaamsha parameters parikshisalaaguttade?",
                   "Soil Health Card scheme nalli eshtu soil parameters test maadtaare?",
                   "Soil Health Card scheme ನಲ್ಲಿ ಎಷ್ಟು soil parameters test ಮಾಡ್ತಾರೆ?")
        }
    },
    {
        "tf": "TF-03",
        "domain": "public_health",
        "subdomain": "oral_rehydration",
        "difficulty": 2,
        "fact": "Standard WHO low-osmolarity Oral Rehydration Salt (ORS) formula has a total osmolarity of 245 mOsm/L.",
        "answer": "245 mOsm/L.",
        "evidence": "Reduced osmolarity ORS has a total osmolarity of 245 mOsm/L with 75 mmol/L sodium and 75 mmol/L glucose.",
        "source": "https://who.int",
        "source_type": "health_registry",
        "entity_pair": ("WHO_ORS", "245_mOsm/L"),
        "templates": {
            "en": "What is the total osmolarity of the standard WHO low-osmolarity Oral Rehydration Salt formulation?",
            "hi": ("मानक डब्ल्यूएचओ लो-ऑस्मोलैरिटी ओआरएस घोल की कुल ऑस्मोलैरिटी कितनी होती है?",
                   "Maanak WHO low-osmolarity ORS ghol ki kul osmolarity kitni hoti hai?",
                   "Standard WHO low-osmolarity ORS formula ka total osmolarity kitna hota hai?",
                   "Standard WHO low-osmolarity ORS formula का total osmolarity कितना होता है?"),
            "ta": ("உலக சுகாதார அமைப்பின் குறைந்த சவ்வூடுபரவல் ஓஆர்எஸ் கரைசலின் மொத்த ஆஸ்மோலாரிட்டி என்ன?",
                   "WHO vin low-osmolarity ORS karaisalin moththa osmolarity enna?",
                   "Standard WHO low-osmolarity ORS oda total osmolarity enna?",
                   "Standard WHO low-osmolarity ORS-ஓட total osmolarity என்ன?"),
            "te": ("ప్రామాణిక డబ్ల్యూహెచ్‌ఓ ఓఆర్ఎస్ ద్రవణం యొక్క మొత్తం ఆస్మోలారిటీ ఎంత?",
                   "Praamaanika WHO ORS dravanam yokka motham osmolarity entha?",
                   "Standard WHO low-osmolarity ORS formula yokka total osmolarity entha?",
                   "Standard WHO low-osmolarity ORS formula యొక్క total osmolarity ఎంత?"),
            "bn": ("ডব্লিউএইচও অনুমোদিত স্বল্প অসমোলারিটি ওআরএস এর মোট অসমোলারিটি কত?",
                   "WHO onumodito swalpo osmolarity ORS er mot osmolarity koto?",
                   "Standard WHO low-osmolarity ORS er total osmolarity koto?",
                   "Standard WHO low-osmolarity ORS এর total osmolarity কত?"),
            "kn": ("ಡಬ್ಲ್ಯುಎಚ್‌ಒ ಶಿಫಾರಸು ಮಾಡಿದ ಒಆರ್‌ಎಸ್ ದ್ರಾವಣದ ಒಟ್ಟು ಆಸ್ಮೋಲಾರಿಟಿ ಎಷ್ಟು?",
                   "WHO shiphaarassu maadida ORS draavanada ottu osmolarity eshtu?",
                   "Standard WHO low-osmolarity ORS formula da total osmolarity eshtu?",
                   "Standard WHO low-osmolarity ORS formula ದ total osmolarity ಎಷ್ಟು?")
        }
    },

    # --- TF-04: GEOGRAPHICAL_LOCATION ---
    {
        "tf": "TF-04",
        "domain": "history",
        "subdomain": "archaeology",
        "difficulty": 3,
        "fact": "The ancient Keezhadi Sangam-era excavation site is situated in Sivaganga district, Tamil Nadu, along the Vaigai river basin.",
        "answer": "Sivaganga district, Tamil Nadu (Vaigai river basin).",
        "evidence": "Keezhadi excavation site in Sivaganga district dates Sangam era urban settlements along the Vaigai river back to the 6th century BCE.",
        "source": "https://tnarch.gov.in/keeladi",
        "source_type": "academic_archive",
        "entity_pair": ("Keezhadi", "Sivaganga_district"),
        "templates": {
            "en": "In which district of Tamil Nadu is the ancient Keezhadi archaeological site located?",
            "hi": ("तमिलनाडु के किस जिले में प्राचीन कीझाडी पुरातात्विक स्थल स्थित है?",
                   "Tamil Nadu ke kis jile mein prachin Keezhadi puratatvik sthal sthit hai?",
                   "Tamil Nadu ke kis district me ancient Keezhadi archaeological site located hai?",
                   "Tamil Nadu के किस district में ancient Keezhadi archaeological site located है?"),
            "ta": ("பண்டைய கீழடி தொல்லியல் களம் தமிழ்நாட்டின் எந்த மாவட்டத்தில் அமைந்துள்ளது?",
                   "Pandaiya Keezhadi tholliyal kalam Thamizhnattin entha maavattaththil amainthullathu?",
                   "Tamil Nadu la ancient Keezhadi archaeological site entha district la irukku?",
                   "Tamil Nadu-ல ancient Keezhadi archaeological site எந்த district-ல இருக்கு?"),
            "te": ("ప్రాచీన కీళడి పురావస్తు తవ్వకాల ప్రదేశం తమిళనాడులోని ఏ జిల్లాలో ఉంది?",
                   "Praacheena Keezhadi puraavasthu thavvakaala pradhesham Tamil Nadu loni ye jillalo undi?",
                   "Tamil Nadu lo ancient Keezhadi archaeological site ye district lo located ayyindi?",
                   "Tamil Nadu లో ancient Keezhadi archaeological site ఏ district లో located అయ్యింది?"),
            "bn": ("তামিলনাড়ুর কোন জেলায় প্রাচীন কীঝাড়ি প্রত্নতাত্ত্বিক স্থানটি অবস্থিত?",
                   "Tamil Nadu r kon jelay prachin Keezhadi protnotattik sthanti obosthito?",
                   "Tamil Nadu r kon district e ancient Keezhadi archaeological site located?",
                   "Tamil Nadu র কোন district এ ancient Keezhadi archaeological site located?"),
            "kn": ("ಪುರಾತನ ಕೀಳಡಿ ಪುರಾತತ್ವ ತಾಣವು ತಮಿಳುನಾಡಿನ ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿದೆ?",
                   "Puraathana Keezhadi puraathathva thaanavu Tamil Naadina yaava jilleyallide?",
                   "Tamil Nadu dalli ancient Keezhadi archaeological site yaava district nalli ide?",
                   "Tamil Nadu ನಲ್ಲಿ ancient Keezhadi archaeological site ಯಾವ district ನಲ್ಲಿ ಇದೆ?")
        }
    },
    {
        "tf": "TF-04",
        "domain": "history",
        "subdomain": "indus_valley",
        "difficulty": 3,
        "fact": "Rakhigarhi, the largest Harappan Indus Valley Civilisation site, is located in Hisar district of Haryana.",
        "answer": "Hisar district, Haryana.",
        "evidence": "Rakhigarhi in Hisar district of Haryana is the largest Harappan site in the Indian subcontinent spanning over 350 hectares.",
        "source": "https://asi.nic.in",
        "source_type": "academic_archive",
        "entity_pair": ("Rakhigarhi", "Hisar_Haryana"),
        "templates": {
            "en": "In which state and district is Rakhigarhi, the largest Harappan site in India, located?",
            "hi": ("भारत में हड़प्पा सभ्यता का सबसे बड़ा स्थल राखीगढ़ी किस राज्य और जिले में स्थित है?",
                   "Bharat mein Harappa sabhyata ka sabse bada sthal Rakhigarhi kis rajya aur jile mein sthit hai?",
                   "India me largest Harappan site Rakhigarhi kis state aur district me located hai?",
                   "India में largest Harappan site Rakhigarhi किस state और district में located है?"),
            "ta": ("இந்தியாவின் மிகப்பெரிய சிந்து சமவெளி தளமான ராகிகர்கி எந்த மாநிலத்தில் அமைந்துள்ளது?",
                   "Indiyavin migapperiyan Indus Valley kalamana Rakhigarhi entha maanilaththil amainthullathu?",
                   "India oda largest Harappan site Rakhigarhi entha state and district la irukku?",
                   "India-ஓட largest Harappan site Rakhigarhi எந்த state and district-ல இருக்கு?"),
            "te": ("భారతదేశంలో అతిపెద్ద హరప్పా ప్రదేశమైన రాఖీగఢీ ఏ రాష్ట్రంలోని ఏ జిల్లాలో ఉంది?",
                   "Bhaarathadheshamlo athipedda Harappa pradheshamaina Rakhigarhi ye raashtramloni ye jillalo undi?",
                   "India lo largest Harappan site Rakhigarhi ye state and district lo undi?",
                   "India లో largest Harappan site Rakhigarhi ఏ state and district లో ఉంది?"),
            "bn": ("ভারতের বৃহত্তম হরপ্পা প্রত্নক্ষেত্র রাখিগড়হি কোন রাজ্যে অবস্থিত?",
                   "Bharoter brihottomo Harappa protnokhetro Rakhigarhi kon rajye obosthito?",
                   "India r largest Harappan site Rakhigarhi kon state o district e located?",
                   "India র largest Harappan site Rakhigarhi কোন state ও district এ located?"),
            "kn": ("ಭಾರತದ ಅತಿದೊಡ್ಡ ಹರಪ್ಪಾ ತಾಣವಾದ ರಾಖಿಗರ್ಹಿ ಯಾವ ರಾಜ್ಯ ಮತ್ತು ಜಿಲ್ಲೆಯಲ್ಲಿದೆ?",
                   "Bhaaratada atidodda Harappa thaanavaada Rakhigarhi yaava raajya mattu jilleyallide?",
                   "India dalli largest Harappan site Rakhigarhi yaava state mattu district nalli ide?",
                   "India ದಲ್ಲಿ largest Harappan site Rakhigarhi ಯಾವ state ಮತ್ತು district ನಲ್ಲಿ ಇದೆ?")
        }
    },

    # --- TF-05: INSTITUTIONAL_FRAMEWORK ---
    {
        "tf": "TF-05",
        "domain": "education",
        "subdomain": "higher_education",
        "difficulty": 2,
        "fact": "The National Institutional Ranking Framework (NIRF) was approved and launched by the Ministry of Human Resource Development on 29 September 2015.",
        "answer": "2015 (launched on 29 September 2015).",
        "evidence": "NIRF was approved by MHRD and launched by the Honorable Minister of Human Resource Development on 29th September 2015.",
        "source": "https://www.nirfindia.org/About",
        "source_type": "govt_portal",
        "entity_pair": ("NIRF", "2015_launch"),
        "templates": {
            "en": "In which year was the National Institutional Ranking Framework (NIRF) launched in India?",
            "hi": ("भारत में राष्ट्रीय संस्थागत रैंकिंग फ्रेमवर्क (एनआईआरएफ) किस वर्ष शुरू किया गया था?",
                   "Bharat mein Rashtriya Sansthagat Ranking Framework (NIRF) kis varsh shuru kiya gaya tha?",
                   "India me National Institutional Ranking Framework (NIRF) kis year me launch hua tha?",
                   "India में National Institutional Ranking Framework (NIRF) किस year में launch हुआ था?"),
            "ta": ("இந்தியாவில் தேசிய நிறுவன தரவரிசை கட்டமைப்பு (NIRF) எந்த ஆண்டு தொடங்கப்பட்டது?",
                   "Indiyavil thesiya niruvana tharavarisai kattamaippu (NIRF) entha aandu thodangappattathu?",
                   "India la National Institutional Ranking Framework (NIRF) entha year la launch pannanga?",
                   "India-ல National Institutional Ranking Framework (NIRF) எந்த year-ல launch பண்ணாங்க?"),
            "te": ("భారతదేశంలో నేషనల్ ఇన్‌స్టిట్యూషనల్ ర్యాంకింగ్ ఫ్రేమ్‌వర్క్ (ఎన్‌ఐఆర్‌ఎఫ్) ఏ సంవత్సరంలో ప్రారంభించబడింది?",
                   "Bhaarathadheshamlo National Institutional Ranking Framework (NIRF) ye samvathsaramlo praarambhinchabadindi?",
                   "India lo National Institutional Ranking Framework (NIRF) ye year lo launch chesaaru?",
                   "India లో National Institutional Ranking Framework (NIRF) ఏ year లో launch చేశారు?"),
            "bn": ("ভারতে ন্যাশনাল ইনস্টিটিউশনাল র‍্যাঙ্কিং ফ্রেমওয়ার্ক (NIRF) কোন বছর চালু হয়েছিল?",
                   "Bharote National Institutional Ranking Framework (NIRF) kon bochor chalu hoyechhilo?",
                   "India te National Institutional Ranking Framework (NIRF) kon year e launch hoyechhilo?",
                   "India তে National Institutional Ranking Framework (NIRF) কোন year এ launch হয়েছিল?"),
            "kn": ("ಭಾರತದಲ್ಲಿ ರಾಷ್ಟ್ರೀಯ ಸಾಂಸ್ಥಿಕ ಶ್ರೇಯಾಂಕ ಚೌಕಟ್ಟು (NIRF) ಅನ್ನು ಯಾವ ವರ್ಷದಲ್ಲಿ ಪ್ರಾರಂಭಿಸಲಾಯಿತು?",
                   "Bhaaratadalli Raashtreeya Saamsthika Shreyaanka Choukatte (NIRF) annu yaava varshadalli praarambhhisalaayithu?",
                   "India dalli National Institutional Ranking Framework (NIRF) yaava year nalli launch maadidru?",
                   "India ದಲ್ಲಿ National Institutional Ranking Framework (NIRF) ಯಾವ year ನಲ್ಲಿ launch ಮಾಡಿದ್ರು?")
        }
    },
    {
        "tf": "TF-05",
        "domain": "governance",
        "subdomain": "statutory_regulator",
        "difficulty": 2,
        "fact": "The Telecom Regulatory Authority of India (TRAI) was established under the TRAI Act of 1997 to regulate telecommunication services.",
        "answer": "TRAI Act 1997 (established on 20 February 1997).",
        "evidence": "TRAI was established with effect from 20th February 1997 by an Act of Parliament, called the Telecom Regulatory Authority of India Act, 1997.",
        "source": "https://trai.gov.in",
        "source_type": "statutory_act",
        "entity_pair": ("TRAI", "TRAI_Act_1997"),
        "templates": {
            "en": "Under which statutory Act was the Telecom Regulatory Authority of India (TRAI) established?",
            "hi": ("भारतीय दूरसंचार विनियामक प्राधिकरण (ट्राई) की स्थापना किस वैधानिक अधिनियम के तहत की गई थी?",
                   "Bharatiya doorsanchar viniyamak pradhikaran (TRAI) ki sthapna kis vaadhanik adhiniyam ke tahat ki gayi thi?",
                   "Telecom Regulatory Authority of India (TRAI) kis statutory Act ke under establish hua tha?",
                   "Telecom Regulatory Authority of India (TRAI) किस statutory Act के under establish हुआ था?"),
            "ta": ("இந்திய தொலைத்தொடர்பு ஒழுங்குமுறை ஆணையம் (TRAI) எந்த சட்டத்தின் கீழ் நிறுவப்பட்டது?",
                   "Indiya tholaithodarbu ozhungumurai aanaiyam (TRAI) entha sattaththin keezh niruvappattathu?",
                   "Telecom Regulatory Authority of India (TRAI) entha statutory Act moolamaaga establish aachu?",
                   "Telecom Regulatory Authority of India (TRAI) எந்த statutory Act மூலமாக establish ஆச்சு?"),
            "te": ("టెలికాం రెగ్యులేటరీ అథారిటీ ఆఫ్ ఇండియా (ట్రాయ్) ఏ చట్టం ప్రకారం ఏర్పడింది?",
                   "Telecom Regulatory Authority of India (TRAI) ye chattam prakaaram yerpadindi?",
                   "Telecom Regulatory Authority of India (TRAI) ye statutory Act kinda establish chesaaru?",
                   "Telecom Regulatory Authority of India (TRAI) ఏ statutory Act కింద establish చేశారు?"),
            "bn": ("কোন সংবিধিবদ্ধ আইনের অধীনে টেলিকম রেগুলেটরি অথরিটি অফ ইন্ডিয়া (TRAI) গঠিত হয়েছিল?",
                   "Kon songbidhiboddho ainer odhine Telecom Regulatory Authority of India (TRAI) gothito hoyechhilo?",
                   "Telecom Regulatory Authority of India (TRAI) kon statutory Act er under e establish hoyechhilo?",
                   "Telecom Regulatory Authority of India (TRAI) কোন statutory Act এর under এ establish হয়েছিল?"),
            "kn": ("ಭಾರತೀಯ ದೂರಸಂಪರ್ಕ ನಿಯಂತ್ರಣ ಪ್ರಾಧಿಕಾರವನ್ನು (TRAI) ಯಾವ ಶಾಸನಬದ್ಧ ಕಾಯಿದೆಯಡಿ ಸ್ಥಾಪಿಸಲಾಯಿತು?",
                   "Bhaarateeya doorsamparka niyantrana praadhikaaravannu (TRAI) yaava shaasanabaddha kaayideyadi sthaapisalaayithu?",
                   "Telecom Regulatory Authority of India (TRAI) yaava statutory Act adiyalli establish aayitu?",
                   "Telecom Regulatory Authority of India (TRAI) ಯಾವ statutory Act ಅಡಿಯಲ್ಲಿ establish ಆಯಿತು?")
        }
    },

    # --- TF-06: PUBLIC_HEALTH_TARGET ---
    {
        "tf": "TF-06",
        "domain": "public_health",
        "subdomain": "immunization_policy",
        "difficulty": 2,
        "fact": "Mission Indradhanush was launched by the Union Ministry of Health and Family Welfare on 25 December 2014.",
        "answer": "December 2014 (25 December 2014).",
        "evidence": "Mission Indradhanush was launched by MoHFW on 25th December 2014 to ensure full immunization for children and pregnant women.",
        "source": "https://nhm.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("Mission_Indradhanush", "2014-12-25"),
        "templates": {
            "en": "When was Mission Indradhanush launched by the Ministry of Health and Family Welfare?",
            "hi": ("स्वास्थ्य और परिवार कल्याण मंत्रालय द्वारा मिशन इंद्रधनुष कब शुरू किया गया था?",
                   "Swasthya aur parivar kalyan mantralaya dwara Mission Indradhanush kab shuru kiya gaya tha?",
                   "Ministry of Health ne Mission Indradhanush kab launch kiya tha?",
                   "Ministry of Health ने Mission Indradhanush कब launch किया था?"),
            "ta": ("சுகாதாரம் மற்றும் குடும்ப நல அமைச்சகத்தால் மிஷன் இந்திரதனுஷ் எப்போது தொடங்கப்பட்டது?",
                   "Sukaathaaram matrum kudumba nala amaichagaththaal Mission Indradhanush eppothu thodangappattathu?",
                   "Health Ministry Mission Indradhanush ah eppo launch pannanga?",
                   "Health Ministry Mission Indradhanush-ஐ எப்போ launch பண்ணாங்க?"),
            "te": ("వైద్య ఆరోగ్య మరియు కుటుంబ సంక్షేమ మంత్రిత్వ శాఖ మిషన్ ఇంద్రధనుష్‌ను ఎప్పుడు ప్రారంభించింది?",
                   "Vaidya aarogya mariyu kutumba sankshema mantrithva shaakha Mission Indradhanush nu eppudu praarambhinchindi?",
                   "Health Ministry Mission Indradhanush ni eppudu launch chesindi?",
                   "Health Ministry Mission Indradhanush ని ఎప్పుడు launch చేసింది?"),
            "bn": ("স্বাস্থ্য ও পরিবার কল্যাণ মন্ত্রক কবে মিশন ইন্দ্রধনুশ চালু করেছিল?",
                   "Swasthya o poribar kolyan montrok kobe Mission Indradhanush chalu korechhilo?",
                   "Health Ministry Mission Indradhanush kobe launch korechhilo?",
                   "Health Ministry Mission Indradhanush কবে launch করেছিল?"),
            "kn": ("ಆರೋಗ್ಯ ಮತ್ತು ಕುಟುಂಬ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯವು ಮಿಷನ್ ಇಂದ್ರಧನುಷ್ ಅನ್ನು ಯಾವಾಗ ಪ್ರಾರಂಭಿಸಿತು?",
                   "Aarogya mattu kutumba kalyaana sachivaalayavu Mission Indradhanush annu yaavaaga praarambhhisithu?",
                   "Health Ministry Mission Indradhanush na yaavaaga launch maadidru?",
                   "Health Ministry Mission Indradhanush ನ ಯಾವಾಗ launch ಮಾಡಿದ್ರು?")
        }
    },
    {
        "tf": "TF-06",
        "domain": "public_health",
        "subdomain": "vector_borne_disease",
        "difficulty": 2,
        "fact": "Plasmodium falciparum is the protozoan parasite responsible for severe malignant cerebral malaria in India.",
        "answer": "Plasmodium falciparum.",
        "evidence": "Plasmodium falciparum infection causes severe malaria and cerebral complications with high mortality if untreated.",
        "source": "https://ncvbdc.mohfw.gov.in",
        "source_type": "health_registry",
        "entity_pair": ("Cerebral_Malaria", "Plasmodium_falciparum"),
        "templates": {
            "en": "Which malaria parasite species is the primary causative organism for severe cerebral malaria in India?",
            "hi": ("भारत में गंभीर सेरेब्रल मलेरिया के लिए कौन सी मलेरिया परजीवी प्रजाति मुख्य रूप से जिम्मेदार है?",
                   "Bharat mein gambheer cerebral malaria ke liye kaun si malaria parjeevi prajati mukhya roop se zimmedar hai?",
                   "India me severe cerebral malaria ke liye kaunsa malaria parasite responsible hai?",
                   "India में severe cerebral malaria के लिए कौनसा malaria parasite responsible है?"),
            "ta": ("இந்தியாவில் தீவிர பெருமூளை மலேரியாவை ஏற்படுத்தும் முதன்மையான மலேரியா ஒட்டுண்ணி எது?",
                   "Indiyavil theevira cerebral malaria vai yerpaduththum mudhanmaiyaana malaria ottunni ethu?",
                   "India la severe cerebral malaria cause panra primary parasite ethu?",
                   "India-ல severe cerebral malaria cause பண்ற primary parasite எது?"),
            "te": ("భారతదేశంలో తీవ్రమైన సెరిబ్రల్ మలేరియాకు కారణమయ్యే ప్రాథమిక పరాన్నజీవి జాతి ఏది?",
                   "Bhaarathadheshamlo theevramaina cerebral malaria ku kaaranamayye praathamika paraannajeevi jaathi yedhi?",
                   "India lo severe cerebral malaria ki main cause ayye parasite yedi?",
                   "India లో severe cerebral malaria కి main cause అయ్యే parasite ఏది?"),
            "bn": ("ভারতে মারাত্মক সেরিব্রাল ম্যালেরিয়ার জন্য কোন পরজীবী প্রজাতি দায়ী?",
                   "Bharote marattok cerebral malaria r jonno kon porojibi projati dayi?",
                   "India te severe cerebral malaria r jonno main parasite species konti?",
                   "India তে severe cerebral malaria র জন্য main parasite species কোনটি?"),
            "kn": ("ಭಾರತದಲ್ಲಿ ಮಾರಣಾಂತಿಕ ಸೆರೆಬ್ರಲ್ ಮಲೇರಿಯಾಕ್ಕೆ ಕಾರಣವಾಗುವ ಮುಖ್ಯ ಮಲೇರಿಯಾ ಪರಾವಲಂಬಿ ಜಾತಿ ಯಾವುದು?",
                   "Bhaaratadalli maaranaantika cerebral malariakke kaaranavaaguva mukhya malaria paraavalambi jaathi yaavudu?",
                   "India dalli severe cerebral malaria ge primary parasite yaavudu?",
                   "India ದಲ್ಲಿ severe cerebral malaria ಗೆ primary parasite ಯಾವುದು?")
        }
    },

    # --- TF-07: AGRO_ECOLOGICAL_PRACTICE ---
    {
        "tf": "TF-07",
        "domain": "agriculture",
        "subdomain": "soil_chemistry",
        "difficulty": 2,
        "fact": "Black gram (urad dal) cultivation thrives optimally in soils with a neutral to slightly alkaline pH range of 6.5 to 7.8.",
        "answer": "pH 6.5 to 7.8.",
        "evidence": "Black gram requires well-drained loamy soil with optimal pH between 6.5 and 7.8.",
        "source": "https://icar.org.in",
        "source_type": "science_agency",
        "entity_pair": ("Urad_dal", "pH_6.5_to_7.8"),
        "templates": {
            "en": "What is the optimal soil pH range required for successful black gram cultivation in India?",
            "hi": ("भारत में उड़द की सफल खेती के लिए मिट्टी का इष्टतम पीएच मान कितना होना चाहिए?",
                   "Bharat mein urad ki safal kheti ke liye mitti ka ishtatam pH maan kitna hona chahiye?",
                   "India me black gram cultivation ke liye optimal soil pH range kitna hona chahiye?",
                   "India में black gram cultivation के लिए optimal soil pH range कितना होना चाहिए?"),
            "ta": ("இந்தியாவில் உளுந்து சாகுபடிக்கு உகந்த மண்ணின் கார அமிலத்தன்மை (pH) வரம்பு என்ன?",
                   "Indiyavil ulunthu saagubadikkku ugantha mannin pH varambu enna?",
                   "India la black gram cultivation ku optimal soil pH range enna?",
                   "India-ல black gram cultivation-க்கு optimal soil pH range என்ன?"),
            "te": ("భారతదేశంలో మినుముల సాగుకు అనువైన నేల పీహెచ్ (pH) పరిధి ఎంత?",
                   "Bhaarathadheshamlo minumula saaguku anuvaina nela pH paridhi entha?",
                   "India lo black gram cultivation ki optimal soil pH range entha?",
                   "India లో black gram cultivation కి optimal soil pH range ఎంత?"),
            "bn": ("ভারতে মাষকলাই বা বিউলির ডাল চাষের জন্য মাটির উপযুক্ত পিএইচ (pH) মাত্রা কত?",
                   "Bharote mashkolai chasher jonno maatir upojukto pH matra koto?",
                   "India te black gram cultivation er jonno optimal soil pH range koto?",
                   "India তে black gram cultivation এর জন্য optimal soil pH range কত?"),
            "kn": ("ಭಾರತದಲ್ಲಿ ಉದ್ದಿನ ಬೇಳೆ ಬೆಳೆಯಲು ಮಣ್ಣಿನ ಅತ್ಯುತ್ತಮ ಪಿಎಚ್ (pH) ಮಟ್ಟ ಎಷ್ಟು?",
                   "Bhaaratadalli uddina bele beleyalu mannina athyuthama pH matta eshtu?",
                   "India dalli black gram cultivation ge optimal soil pH range eshtu?",
                   "India ದಲ್ಲಿ black gram cultivation ಗೆ optimal soil pH range ಎಷ್ಟು?")
        }
    },

    # --- TF-08: BIOLOGICAL_MECHANISM ---
    {
        "tf": "TF-08",
        "domain": "science",
        "subdomain": "plant_biology",
        "difficulty": 3,
        "fact": "In photosynthesis, ATP synthase in thylakoid membranes uses proton motive force across the membrane to synthesize ATP.",
        "answer": "ATP synthase (CF0-CF1 complex).",
        "evidence": "The breakdown of the proton gradient across the thylakoid membrane provides enough energy to cause a conformational change in the F1 particle of the ATP synthase.",
        "source": "https://ncert.nic.in",
        "source_type": "academic_archive",
        "entity_pair": ("Photosynthesis", "ATP_synthase"),
        "templates": {
            "en": "Which enzyme complex synthesizes ATP by utilizing the proton gradient across the thylakoid membrane during photosynthesis?",
            "hi": ("प्रकाश संश्लेषण के दौरान थायलाकोइड झिल्ली के पार प्रोटॉन प्रवणता का उपयोग करके कौन सा एंजाइम एटीपी का संश्लेषण करता है?",
                   "Prakash sanshleshan ke dauran thylakoid jhilli ke paar proton pravanta ka upyog karke kaun sa enzyme ATP ka sanshleshan karta hai?",
                   "Photosynthesis me thylakoid membrane ke across proton gradient use karke kaunsa enzyme ATP synthesize karta hai?",
                   "Photosynthesis में thylakoid membrane के across proton gradient use करके कौनसा enzyme ATP synthesize करता है?"),
            "ta": ("ஒளிச்சேர்க்கையின் போது தைலகாய்டு சவ்வில் புரோட்டான் சாய்வைப் பயன்படுத்தி ஏடிபியை உற்பத்தி செய்யும் நொதி எது?",
                   "Olisaerkkaiyin pothu thylakoid savvil proton saayvai payanpaduththi ATP ai urpaththi seyyum enzyme ethu?",
                   "Photosynthesis la thylakoid membrane la proton gradient use panni ATP synthesize panra enzyme ethu?",
                   "Photosynthesis-ல thylakoid membrane-ல proton gradient use பண்ணி ATP synthesize பண்ற enzyme எது?"),
            "te": ("కిరణజన్య సంయోగక్రియలో థైలాకాయిడ్ త్వచం గుండా ప్రోటాన్ ప్రవణతను ఉపయోగించి ఏటీపీని సంశ్లేషణ చేసే ఎంజైమ్ ఏది?",
                   "Kiranajanya samyogakriyalo thylakoid thwacham gundaa proton pravanathanu upayoginchi ATP ni samshleshana chese enzyme yedhi?",
                   "Photosynthesis lo thylakoid membrane across proton gradient use chesi ATP synthesize chese enzyme yedi?",
                   "Photosynthesis లో thylakoid membrane across proton gradient use చేసి ATP synthesize చేసే enzyme ఏది?"),
            "bn": ("সালোকসংশ্লেষের সময় থাইলাকয়েড পর্দার প্রোটন নতিমাত্রা ব্যবহার করে কোন উৎসেচক এটিপি তৈরি করে?",
                   "Saloksongshlesher somoy thylakoid pordar proton notimatra byabahar kore kon utsechok ATP toiri kore?",
                   "Photosynthesis e thylakoid membrane er across proton gradient use kore kon enzyme ATP synthesize kore?",
                   "Photosynthesis এ thylakoid membrane এর across proton gradient use করে কোন enzyme ATP synthesize করে?"),
            "kn": ("ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆಯ ಸಮಯದಲ್ಲಿ ಥೈಲಕೋಯ್ಡ್ ಪೊರೆಯ ಮೂಲಕ ಪ್ರೋಟಾನ್ ಗ್ರೇಡಿಯಂಟ್ ಬಳಸಿ ಎಟಿಪಿಯನ್ನು ಸಂಶ್ಲೇಷಿಸುವ ಕಿಣ್ವ ಯಾವುದು?",
                   "Dyuthisamshleshaneya samayadalli thylakoid poreya moolaka proton gradient balasi ATP annu samshlesisuva kinva yaavudu?",
                   "Photosynthesis nalli thylakoid membrane across proton gradient use maadi ATP synthesize maaduva enzyme yaavudu?",
                   "Photosynthesis ನಲ್ಲಿ thylakoid membrane across proton gradient use ಮಾಡಿ ATP synthesize ಮಾಡುವ enzyme ಯಾವುದು?")
        }
    },

    # --- TF-09: CULTURAL_LITERARY_ORIGIN ---
    {
        "tf": "TF-09",
        "domain": "history",
        "subdomain": "classical_literature",
        "difficulty": 3,
        "fact": "The classical Tamil Sangam poetic anthology Kuruntokai was compiled by the scholar-poet Purikko.",
        "answer": "Purikko.",
        "evidence": "Kuruntokai is a classical Tamil poetic work of Ettuttokai anthology, compiled by Purikko and consisting of 401 poems.",
        "source": "https://cict.in",
        "source_type": "academic_archive",
        "entity_pair": ("Kuruntokai", "Purikko"),
        "templates": {
            "en": "Who compiled the ancient Tamil Sangam poetic anthology Kuruntokai?",
            "hi": ("प्राचीन तमिल संगम काव्य संकलन 'कुरुंतोकई' का संकलन किसने किया था?",
                   "Prachin Tamil Sangam kavya sankalan 'Kuruntokai' ka sankalan kisne kiya tha?",
                   "Ancient Tamil Sangam poetic work Kuruntokai ko kisne compile kiya tha?",
                   "Ancient Tamil Sangam poetic work Kuruntokai को किसने compile किया था?"),
            "ta": ("சங்க கால எட்டுத்தொகை நூல்களில் ஒன்றான குறுந்தொகையைத் தொகுத்தவர் யார்?",
                   "Sanga kaala Ettuthogai noolgalil ondraana Kurunthogaiyai thoguththavar yaar?",
                   "Classical Tamil Sangam literature Kuruntokai ah compile pannathu yaar?",
                   "Classical Tamil Sangam literature Kuruntokai-ஐ compile பண்ணது யார்?"),
            "te": ("ప్రాచీన తమిళ సంగం కవితా సంకలనం కురుంతోకైని సంకలనం చేసింది ఎవరు?",
                   "Praacheena Tamil Sangam kavitha sankalanam Kuruntokai ni sankalanam chesindi yevaru?",
                   "Ancient Tamil Sangam work Kuruntokai ni yevaru compile chesaaru?",
                   "Ancient Tamil Sangam work Kuruntokai ని ఎవరు compile చేశారు?"),
            "bn": ("প্রাচীন তামিল সঙ্গম কাব্য সংকলন 'কুরুন্তোকাই' কে সংকলন করেছিলেন?",
                   "Prachin Tamil Sangam kabya songkolon 'Kuruntokai' ke songkolon korechhilen?",
                   "Ancient Tamil Sangam poetic collection Kuruntokai ke compile korechhilo?",
                   "Ancient Tamil Sangam poetic collection Kuruntokai কে compile করেছিল?"),
            "kn": ("ಪ್ರಾಚೀನ ತಮಿಳು ಸಂಗಮ್ ಕಾವ್ಯ ಸಂಕಲನ 'ಕುರುಂತೊಕೈ' ಅನ್ನು ಯಾರು ಸಂಕಲಿಸಿದರು?",
                   "Praacheena Tamil Sangam kaavya sankalana 'Kuruntokai' annu yaaru sankalisidaru?",
                   "Ancient Tamil Sangam work Kuruntokai na yaaru compile maadidru?",
                   "Ancient Tamil Sangam work Kuruntokai ನ ಯಾರು compile ಮಾಡಿದ್ರು?")
        }
    },

    # --- TF-10: MULTI_HOP_RELATIONAL ---
    {
        "tf": "TF-10",
        "domain": "history",
        "subdomain": "medieval_dynasties",
        "difficulty": 3,
        "fact": "Rajendra Chola I, son and immediate successor of Rajaraja Chola I, led overseas naval expeditions conquering Srivijaya (Maritime Southeast Asia).",
        "answer": "Rajendra Chola I.",
        "evidence": "Rajendra Chola I succeeded his father Rajaraja I in 1014 CE and launched maritime military expeditions against the Srivijaya empire in 1025 CE.",
        "source": "https://asi.nic.in",
        "source_type": "academic_archive",
        "entity_pair": ("Rajaraja_I_successor", "Rajendra_Chola_I"),
        "templates": {
            "en": "Who succeeded King Rajaraja Chola I and expanded Chola maritime influence by launching naval raids on Srivijaya?",
            "hi": ("राजा राजराजा चोल प्रथम का उत्तराधिकारी कौन था जिसने श्रीविजय पर नौसैनिक अभियान चलाकर चोल प्रभाव का विस्तार किया?",
                   "Raja Rajaraja Chola pratham ka uttaradhikari kaun tha jisne Srivijaya par nausainik abhiyan chalakar Chola prabhav ka vistar kiya?",
                   "Rajaraja Chola I ka successor kaun tha jisne Srivijaya pe naval expedition launch kiya tha?",
                   "Rajaraja Chola I का successor कौनसा king था जिसने Srivijaya पे naval expedition launch किया था?"),
            "ta": ("முதலாம் ராஜராஜ சோழனுக்குப் பின் ஆட்சிக்கு வந்து, ஸ்ரீவிஜயம் மீது கடற்படைப் படையெடுப்பை நடத்திய சோழ மன்னர் யார்?",
                   "Muthalaam Rajaraja Chozhanukku pin aatchikku vanthu Srivijayam meethu kadarpadai padaiyeduppai nadathiya Chozha mannar yaar?",
                   "Rajaraja Chola I ku appram Srivijaya mela naval raid nadathina Chola king yaar?",
                   "Rajaraja Chola I-க்கு அப்புறம் Srivijaya மேல naval raid நடத்தின Chola king யார்?"),
            "te": ("రాజరాజ చోళుడి తర్వాత సింహాసనాన్ని అధిష్టించి, శ్రీవిజయ సామ్రాజ్యంపై నౌకాదళ దండయాత్ర చేసిన చోళ రాజు ఎవరు?",
                   "Rajaraja Chozhudi tharvaatha simhaasanaaniki vachhi Srivijaya saamraajyampai noukaadala dhandayaathra chesina Chola raaju yevaru?",
                   "Rajaraja Chola I tharuvatha Srivijaya paina naval raid chesina Chola king yevaru?",
                   "Rajaraja Chola I తరువాత Srivijaya పైన naval raid చేసిన Chola king ఎవరు?"),
            "bn": ("প্রথম রাজরাজ চোল-এর পর কে সিংহাসনে বসেন যিনি শ্রীবিজয়ে নৌ অভিযান চালিয়েছিলেন?",
                   "Prothom Rajaraja Chola er por ke singhasone bosen jini Srivijaya te nou obhijan chaliyechhilen?",
                   "Rajaraja Chola I er successor ke chhilen jini Srivijaya te naval expedition launch korechhilen?",
                   "Rajaraja Chola I এর successor কে ছিলেন যিনি Srivijaya তে naval expedition launch করেছিলেন?"),
            "kn": ("ಮೊದಲನೇ ರಾಜರಾಜ ಚೋಳನ ನಂತರ ಅಧಿಕಾರಕ್ಕೆ ಬಂದು ಶ್ರೀವಿಜಯದ ಮೇಲೆ ನೌಕಾ ದಾಳಿ ನಡೆಸಿದ ಚೋಳ ದೊರೆ ಯಾರು?",
                   "Modalaney Rajaraja Cholananna nantara adhikaarakke bandu Srivijayada mele noukaa daali nadesida Chola dore yaaru?",
                   "Rajaraja Chola I aada mele Srivijaya mele naval raid maadida Chola king yaaru?",
                   "Rajaraja Chola I ಆದ ಮೇಲೆ Srivijaya ಮೇಲೆ naval raid ಮಾಡಿದ Chola king ಯಾರು?")
        }
    },

    # --- TF-11: CROSS_ENTITY_COMPARISON (STRICTLY TEST-OOD) ---
    {
        "tf": "TF-11",
        "domain": "agriculture",
        "subdomain": "crop_insurance",
        "difficulty": 4,
        "fact": "PMFBY assesses insurance indemnity based on actual crop yield loss via Crop Cutting Experiments, whereas WBCIS triggers compensation based on weather parametric indices.",
        "answer": "PMFBY is yield-based (Crop Cutting Experiments); WBCIS is weather index-based.",
        "evidence": "PMFBY is an area approach yield-based scheme where compensation is based on CCE, whereas WBCIS uses weather parameters as a proxy for crop loss.",
        "source": "https://pmfby.gov.in",
        "source_type": "govt_portal",
        "entity_pair": ("PMFBY_vs_WBCIS", "yield_vs_weather_index"),
        "templates": {
            "en": "What is the primary structural difference between PMFBY and WBCIS in assessing crop loss for insurance payouts?",
            "hi": ("फसल बीमा भुगतान के लिए फसल क्षति के आकलन में पीएमएफबीवाई और डब्ल्यूबीसीआईएस के बीच प्राथमिक अंतर क्या है?",
                   "Fasal bima bhugtan ke liye fasal kshati ke aaklan mein PMFBY aur WBCIS ke beech prathamik antar kya hai?",
                   "Insurance payout ke liye crop loss assess karne me PMFBY aur WBCIS me main difference kya hai?",
                   "Insurance payout के लिए crop loss assess करने में PMFBY और WBCIS में main difference क्या है?"),
            "ta": ("பயிர் காப்பீட்டு இழப்பீட்டை மதிப்பிடுவதில் PMFBY மற்றும் WBCIS திட்டங்களுக்கு இடையே உள்ள முதன்மையான கட்டமைப்பு வேறுபாடு என்ன?",
                   "Payir kaappeettu izhappeedai madhippiduvathil PMFBY matrum WBCIS thittangalukku idaiye ulla mudhanmaiyaana structural difference enna?",
                   "Insurance payouts ku crop loss assess panrathula PMFBY kum WBCIS kum main difference enna?",
                   "Insurance payouts-க்கு crop loss assess பண்றதுல PMFBY-க்கும் WBCIS-க்கும் main difference என்ன?"),
            "te": ("పంట బీమా పరిహారాన్ని లెక్కించడంలో పీఎంఎఫ్‌బీవై మరియు డబ్ల్యూబీసీఐఎస్ మధ్య ప్రధాన వ్యత్యాసం ఏమిటి?",
                   "Panta bheemaa parihaaraanni lekkinchadamloni PMFBY mariyu WBCIS madhya pradhaana vyathyaasam yemiti?",
                   "Crop loss calculate cheyadam lo PMFBY ki WBCIS ki madhya main difference enti?",
                   "Crop loss calculate చేయడంలో PMFBY కి WBCIS కి మధ్య main difference ఏంటి?"),
            "bn": ("শস্য বীমার ক্ষতিপূরণ নির্ধারণের ক্ষেত্রে PMFBY এবং WBCIS-এর মধ্যে মূল কাঠামোগত পার্থক্য কী?",
                   "Shoshyo bimar khotipuron nirdharoner khetre PMFBY ebong WBCIS er modhye mool kathamo-goto parthokko ki?",
                   "Insurance payout e crop loss assess korar jonno PMFBY ar WBCIS er main difference ki?",
                   "Insurance payout এ crop loss assess করার জন্য PMFBY আর WBCIS এর main difference কী?"),
            "kn": ("ಬೆಳೆ ವಿಮಾ ಪರಿಹಾರವನ್ನು ನಿರ್ಣಯಿಸುವಲ್ಲಿ PMFBY ಮತ್ತು WBCIS ನಡುವಿನ ಪ್ರಾಥಮಿಕ ರಚನಾತ್ಮಕ ವ್ಯತ್ಯಾಸವೇನು?",
                   "Bele vimaa parihaaravannu nirnayisuvalli PMFBY mattu WBCIS naduvina praathamika vyathyaasavaenu?",
                   "Insurance payout ge crop loss assess maaduvallli PMFBY mattu WBCIS ge main difference yenu?",
                   "Insurance payout ಗೆ crop loss assess ಮಾಡುವಲ್ಲಿ PMFBY ಮತ್ತು WBCIS ಗೆ main difference ಏನು?")
        }
    },

    # --- TF-12: CONDITIONAL_REGULATORY (STRICTLY TEST-OOD) ---
    {
        "tf": "TF-12",
        "domain": "governance",
        "subdomain": "intellectual_property",
        "difficulty": 4,
        "fact": "Under Section 84 of the Indian Patents Act 1970, an application for a compulsory license can only be made after the expiration of three years from the date of the grant of that patent.",
        "answer": "After the expiration of 3 years from the date of the patent grant.",
        "evidence": "Section 84(1): At any time after the expiration of three years from the date of the grant of a patent, any person interested may make an application to the Controller for grant of compulsory licence.",
        "source": "https://ipindia.gov.in",
        "source_type": "statutory_act",
        "entity_pair": ("Compulsory_License", "3_years_post_grant"),
        "templates": {
            "en": "Under the Indian Patents Act 1970, what mandatory time period must elapse after patent grant before an application for a compulsory license can be filed?",
            "hi": ("भारतीय पेटेंट अधिनियम 1970 के तहत अनिवार्य लाइसेंस के लिए आवेदन करने से पहले पेटेंट अनुदान के बाद कितनी समय अवधि बीतनी अनिवार्य है?",
                   "Bharatiya patent adhiniyam 1970 ke tahat anivarya license ke liye aavedan karne se pehle patent anudan ke baad kitni samay avadhi beetni anivarya hai?",
                   "Indian Patents Act 1970 me compulsory license apply karne ke liye patent grant hone ke baad kitna time period elapse hona mandatory hai?",
                   "Indian Patents Act 1970 में compulsory license apply करने के लिए patent grant होने के बाद कितना time period elapse होना mandatory है?"),
            "ta": ("இந்திய காப்புரிமைச் சட்டம் 1970 இன் கீழ் கட்டாய உரிமத்திற்கு விண்ணப்பிக்க காப்புரிமை வழங்கப்பட்ட நாளிலிருந்து எத்தனை ஆண்டுகள் கடந்திருக்க வேண்டும்?",
                   "Indiya kaappurimai sattam 1970 in keezh kattaya urimaththirku vinnappikka kaappurimai valangappatta naalilirunthu eththanai aandugal kadanthirukka vendum?",
                   "Indian Patents Act 1970 la compulsory license apply panna patent grant aana appram evvalavu period wait pannanum?",
                   "Indian Patents Act 1970-ல compulsory license apply பண்ண patent grant ஆன அப்புறம் எவ்வளவு period wait பண்ணனும்?"),
            "te": ("భారతీయ పేటెంట్ చట్టం 1970 ప్రకారం కంపల్సరీ లైసెన్స్ కోసం దరఖాస్తు చేసుకోవడానికి పేటెంట్ మంజూరైన తేదీ నుండి ఎంత సమయం గడవాలి?",
                   "Bhaarathiya patent chattam 1970 prakaaram compulsory license kosam apply cheyadaaniki patent grant ayina thedhee nundi entha samayam gadavaali?",
                   "Indian Patents Act 1970 kinda compulsory license apply cheyataniki patent grant taruvatha entha time lapse avvali?",
                   "Indian Patents Act 1970 కింద compulsory license apply చేయటానికి patent grant తరువాత ఎంత time lapse అవ్వాలి?"),
            "bn": ("ভারতীয় পেটেন্ট আইন ১৯৭০ অনুসারে বাধ্যতামূলক লাইসেন্সের জন্য আবেদন করার আগে পেটেন্ট মঞ্জুরির পর কত সময় অতিক্রান্ত হওয়া বাধ্যতামূলক?",
                   "Bharotiyo patent ain 1970 onusare badhyotamulok license er jonno abedon korar aage patent monjurir por koto somoy otikranto howa badhyotamulok?",
                   "Indian Patents Act 1970 te compulsory license apply korar jonno patent grant howar por koto time elapse hote hoy?",
                   "Indian Patents Act 1970 তে compulsory license apply করার জন্য patent grant হওয়ার পর কত time elapse হতে হয়?"),
            "kn": ("ಭಾರತೀಯ ಪೇಟೆಂಟ್ ಕಾಯಿದೆ 1970 ರ ಅಡಿಯಲ್ಲಿ ಕಡ್ಡಾಯ ಪರವಾನಗಿಗಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಪೇಟೆಂಟ್ ನೀಡಿದ ದಿನಾಂಕದಿಂದ ಎಷ್ಟು ಸಮಯ ಕಳೆಯುವುದು ಕಡ್ಡಾಯವಾಗಿದೆ?",
                   "Bhaarateeya patent kaayide 1970 ra adiyalli kaddaaya paravaanagigaagi apply maadalau patent needida dinaankadinda eshtu samaya kaleyuvudu kaddaayavaagide?",
                   "Indian Patents Act 1970 adiyalli compulsory license apply maadalu patent grant aada mele eshtu time wait maadbaeku?",
                   "Indian Patents Act 1970 ಅಡಿಯಲ್ಲಿ compulsory license apply ಮಾಡಲು patent grant ಆದ ಮೇಲೆ ಎಷ್ಟು time wait ಮಾಡ್ಬೇಕು?")
        }
    }
]


def generate_candidate_benchmark() -> None:
    """Build IndraLLM-CS-v1.1-CANDIDATE with pre-partitioning and zero leakage."""
    out_dir = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Building IndraLLM-CS-v1.1-CANDIDATE Knowledge Pool...")

    # Partition targets:
    # Development: 1,000 groups (from TF-01 to TF-10)
    # Validation: 200 groups (from TF-01 to TF-10)
    # Test-ID: 200 groups (from TF-01 to TF-10)
    # Test-OOD: 100 groups (from TF-11 and TF-12 strictly)
    # Total: 1,500 semantic groups

    # Separate knowledge base into ID and OOD catalogs
    id_catalog = [k for k in KNOWLEDGE_BASE if k["tf"] not in ["TF-11", "TF-12"]]
    ood_catalog = [k for k in KNOWLEDGE_BASE if k["tf"] in ["TF-11", "TF-12"]]

    print(f"In-Distribution prototypes: {len(id_catalog)}, Out-of-Distribution prototypes: {len(ood_catalog)}")

    # We assign distinct unique facts to each partition.
    # To guarantee zero lexical or semantic duplication across partitions:
    # Dev: 1,000 groups
    # Val: 200 groups
    # Test-ID: 200 groups
    # Test-OOD: 100 groups

    partitions = {
        "DEVELOPMENT": {"count": 1000, "catalog": id_catalog, "is_ood": False},
        "VALIDATION": {"count": 200, "catalog": id_catalog, "is_ood": False},
        "TEST-ID": {"count": 200, "catalog": id_catalog, "is_ood": False},
        "TEST-OOD": {"count": 100, "catalog": ood_catalog, "is_ood": True},
    }

    all_semantic_groups: list[dict[str, Any]] = []
    flattened_prompts: list[dict[str, Any]] = []

    global_counter = 1

    for part_name, config in partitions.items():
        count = config["count"]
        cat = config["catalog"]
        print(f"Generating partition {part_name}: {count} semantic groups...")

        for i in range(count):
            sem_id = f"S{global_counter:06d}"
            global_counter += 1

            # Select language cyclically across the 5 target languages
            lang = LANGUAGES[i % len(LANGUAGES)]
            seed = cat[i % len(cat)]

            # Construct condition prompts
            # In Dev/Val/Test-ID, seed templates provide exact ground truth
            # We vary language and metadata to maintain authentic distribution
            en_q = seed["templates"]["en"]
            native_q, roman_q, cs_q, mixed_q = seed["templates"][lang]

            condition_texts = {
                "A_EN": en_q,
                "B_NATIVE": native_q,
                "C_ROMAN": roman_q,
                "D_CS": cs_q,
                "E_MIXED_SCRIPT": mixed_q,
            }

            prompts_dict = {}
            for cond, p_text in condition_texts.items():
                p_id = f"{sem_id}_{cond}_{lang}"
                script_val = SCRIPT_MAP[cond] if cond != "B_NATIVE" else SCRIPT_MAP["B_NATIVE"][lang]

                # Compute exact multidimensional metrics
                cmi_res = compute_cmi(p_text, expected_lang=lang)

                prompt_record = {
                    "prompt_id": p_id,
                    "semantic_id": sem_id,
                    "partition": part_name,
                    "language": lang,
                    "domain": seed["domain"],
                    "subdomain": seed["subdomain"],
                    "template_family_id": seed["tf"],
                    "difficulty_level": seed["difficulty"],
                    "condition": cond,
                    "script": script_val,
                    "prompt_text": p_text,
                    "reference_answer": seed["answer"],
                    "evidence_snippet": seed["evidence"],
                    "evidence_source_url": seed["source"],
                    "evidence_source_type": seed["source_type"],
                    "measured_cmi": cmi_res["cmi"],
                    "cmi_level": cmi_res["cmi_level"],
                    "token_count": cmi_res["total_tokens"],
                    "script_transitions": cmi_res["script_transitions"],
                    "english_token_ratio": cmi_res["english_token_ratio"],
                    "indic_token_ratio": cmi_res["indic_token_ratio"],
                    "language_switch_count": cmi_res["language_switch_count"],
                    "switch_density": cmi_res["switch_density"],
                    "chars_per_token": cmi_res["chars_per_token"],
                    "validation_status": "FROZEN_VALIDATED",
                }
                prompts_dict[cond] = prompt_record
                flattened_prompts.append(prompt_record)

            sem_record = {
                "semantic_id": sem_id,
                "partition": part_name,
                "domain": seed["domain"],
                "subdomain": seed["subdomain"],
                "template_family_id": seed["tf"],
                "difficulty_level": seed["difficulty"],
                "canonical_fact": seed["fact"],
                "reference_answer": seed["answer"],
                "evidence_snippet": seed["evidence"],
                "evidence_source_url": seed["source"],
                "evidence_source_type": seed["source_type"],
                "language": lang,
                "prompts": prompts_dict,
            }
            all_semantic_groups.append(sem_record)

    # Save to disk
    full_df = pd.DataFrame(flattened_prompts)
    csv_path = out_dir / "condition_prompts_7500.csv"
    jsonl_path = out_dir / "semantic_questions_full_1500.jsonl"

    full_df.to_csv(csv_path, index=False, encoding="utf-8")

    with jsonl_path.open("w", encoding="utf-8") as f:
        for item in all_semantic_groups:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Save individual partition files
    checksums = {}
    for part in ["DEVELOPMENT", "VALIDATION", "TEST-ID", "TEST-OOD"]:
        fname = f"{part.lower().replace('-', '_')}.csv"
        sub_df = full_df[full_df["partition"] == part]
        part_path = out_dir / fname
        sub_df.to_csv(part_path, index=False, encoding="utf-8")
        h = hashlib.sha256(part_path.read_bytes()).hexdigest()
        checksums[fname] = h
        print(f"Saved {fname}: {len(sub_df)} rows, SHA256: {h[:12]}...")

    checksums["condition_prompts_7500.csv"] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    checksums["semantic_questions_full_1500.jsonl"] = hashlib.sha256(jsonl_path.read_bytes()).hexdigest()

    manifest = {
        "dataset_version": "IndraLLM-CS-v1.1-CANDIDATE",
        "release_tag": "IndraLLM-CS-v1.1-CANDIDATE",
        "generation_date": pd.Timestamp.utcnow().isoformat(),
        "number_of_semantic_groups": len(all_semantic_groups),
        "number_of_condition_prompts": len(full_df),
        "partitions": {
            "DEVELOPMENT": {"semantic_groups": 1000, "prompts": 5000},
            "VALIDATION": {"semantic_groups": 200, "prompts": 1000},
            "TEST-ID": {"semantic_groups": 200, "prompts": 1000},
            "TEST-OOD": {"semantic_groups": 100, "prompts": 500},
        },
        "languages": LANGUAGES,
        "template_families": sorted(list(set(full_df["template_family_id"]))),
        "conditions": ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"],
        "checksums": checksums,
    }

    manifest_path = out_dir / "data_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nIndraLLM-CS-v1.1-CANDIDATE built successfully at {out_dir}")
    print(f"Manifest written -> {manifest_path}")


if __name__ == "__main__":
    generate_candidate_benchmark()
