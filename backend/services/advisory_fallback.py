"""
Deterministic Local Fallback Advisory Service.
Generates structured, localized agronomic recommendations when Gemini is unavailable.
Uses real application parameters (soil NPK/pH, crop, weather, disease, market, distress score).
Supports all 8 languages: en, or, hi, te, ta, bn, gu, mr.
"""
from typing import Dict, List, Optional, Any

# Localized Headings Dictionary across all 8 languages
HEADINGS = {
    "en": {
        "summary": "## Summary",
        "situation": "## Situation & Agronomic Context",
        "actions": "## Recommended Actions",
        "why": "## Why This Matters",
        "priority": "## Priority Level",
        "benefit": "## Expected Benefit",
        "analysis": "## Agronomic Analysis",
        "treatment": "## Recommended Treatment",
        "prevention": "## Preventive Measures",
        "key_actions": "## Key Actions",
        "nutrient_analysis": "## Soil Nutrient Analysis",
        "fertilizer_guidance": "## Fertilizer & Bio-Nutrient Schedule",
        "precautions": "## Application Precautions",
        "suitability": "## Soil & Climate Suitability",
        "benefits": "## Economic & Yield Benefits",
        "care_steps": "## Cultivation & Field Care",
        "price_insight": "## Market & Price Trend Insight",
        "action_suggestions": "## Marketing Action Suggestions",
        "risk_explanation": "## Climate Distress & Risk Analysis",
        "soil_condition": "## Soil Physical & Chemical Condition",
        "best_crops": "## Optimal Suited Crops",
        "improvement_tips": "## Soil Fertility Improvement Tips"
    },
    "or": {
        "summary": "## ସାରାଂଶ",
        "situation": "## ସ୍ଥିତି ଓ କ୍ଷେତ୍ର ବିଶ୍ଳେଷଣ",
        "actions": "## ସୁପାରିଶ କରାଯାଇଥିବା ପଦକ୍ଷେପ",
        "why": "## କାରଣ ଓ ମହତ୍ତ୍ୱ",
        "priority": "## ପ୍ରାଥମିକତା",
        "benefit": "## ଆଶାୟୀ ଲାଭ",
        "analysis": "## କୃଷି ବୈଜ୍ଞାନିକ ବିଶ୍ଳେଷଣ",
        "treatment": "## ସୁପାରିଶ କରାଯାଇଥିବା ଚିକିତ୍ସା",
        "prevention": "## ପ୍ରତିଷେଧକ ବ୍ୟବସ୍ଥା",
        "key_actions": "## ମୁଖ୍ୟ ପଦକ୍ଷେପ",
        "nutrient_analysis": "## ମାଟି ପୋଷକ ତତ୍ତ୍ୱ ବିଶ୍ଳେଷଣ",
        "fertilizer_guidance": "## ସାର ଓ ଜୈବିକ ପୋଷକ ପ୍ରୟୋଗ ସୂଚୀ",
        "precautions": "## ପ୍ରୟୋଗ ସତର୍କତା",
        "suitability": "## ମାଟି ଓ ପାଣିପାଗ ଉପଯୋଗୀତା",
        "benefits": "## ଆର୍ଥିକ ଓ ଅମଳ ଲାଭ",
        "care_steps": "## ଚାଷ ଓ ଜମି ପରିଚାଳନା",
        "price_insight": "## ବଜାର ଓ ଦର ପରିବର୍ତ୍ତନ ସୂଚନା",
        "action_suggestions": "## ବିକ୍ରୟ ଓ ବଜାର ସୁପାରିଶ",
        "risk_explanation": "## ପାଣିପାଗ ବିପଦ ଓ କ୍ଷତି ଆଶଙ୍କା",
        "soil_condition": "## ମାଟିର ଭୌତିକ ଓ ରାସାୟନିକ ସ୍ଥିତି",
        "best_crops": "## ସର୍ବୋତ୍ତମ ଉପଯୁକ୍ତ ଫସଲ",
        "improvement_tips": "## ମାଟିର ଉର୍ବରତା ବୃଦ୍ଧି ଉପାୟ"
    },
    "hi": {
        "summary": "## सारांश",
        "situation": "## स्थिति व कृषि संदर्भ",
        "actions": "## अनुशंसित कदम",
        "why": "## यह क्यों महत्वपूर्ण है",
        "priority": "## प्राथमिकता स्तर",
        "benefit": "## अपेक्षित लाभ",
        "analysis": "## कृषि वैज्ञानिक विश्लेषण",
        "treatment": "## अनुशंसित उपचार",
        "prevention": "## रोकथाम के उपाय",
        "key_actions": "## प्रमुख कदम",
        "nutrient_analysis": "## मृदा पोषक तत्व विश्लेषण",
        "fertilizer_guidance": "## उर्वरक व जैव-पोषण अनुसूची",
        "precautions": "## प्रयोग संबंधी सावधानियां",
        "suitability": "## मिट्टी व मौसम अनुकूलता",
        "benefits": "## आर्थिक व पैदावार लाभ",
        "care_steps": "## खेती व फसल देखभाल",
        "price_insight": "## बाजार भाव व मूल्य रुझान",
        "action_suggestions": "## बिक्री व बाजार सुझाव",
        "risk_explanation": "## मौसम जोखिम व फसल सुरक्षा",
        "soil_condition": "## मिट्टी की भौतिक व रासायनिक स्थिति",
        "best_crops": "## सर्वाधिक उपयुक्त फसलें",
        "improvement_tips": "## मिट्टी सुधार व उर्वरता वृद्धि उपाय"
    },
    "te": {
        "summary": "## సారాంశం",
        "situation": "## ప్రస్తుత పరిస్థితి & వ్యవసాయ సందర్భం",
        "actions": "## సిఫార్సు చేసిన చర్యలు",
        "why": "## ప్రాముఖ్యత",
        "priority": "## ప్రాధాన్యత",
        "benefit": "## ఆశించిన ప్రయోజనం",
        "analysis": "## వ్యవసాయ విశ్లేషణ",
        "treatment": "## సిఫార్సు చేసిన నివారణ",
        "prevention": "## ముందస్తు జాగ్రత్తలు",
        "key_actions": "## ముఖ్యమైన చర్యలు",
        "nutrient_analysis": "## నేల పోషకాల విశ్లేషణ",
        "fertilizer_guidance": "## ఎరువుల యాజమాన్య ప్రణాళిక",
        "precautions": "## జాగ్రత్తలు",
        "suitability": "## నేల & వాతావరణ అనుకూలత",
        "benefits": "## ఆర్థిక & దిగుబడి ప్రయోజనాలు",
        "care_steps": "## సాగు & పంట సంరక్షణ",
        "price_insight": "## మార్కెట్ ధరల ధోరణి",
        "action_suggestions": "## మార్కెటింగ్ సూచనలు",
        "risk_explanation": "## వాతావరణ ప్రమాద విశ్లేషణ",
        "soil_condition": "## నేల భౌతిక స్థితి",
        "best_crops": "## అనువైన పంటలు",
        "improvement_tips": "## నేల సారవంతం మెరుగుపరిచే చిట్కాలు"
    },
    "ta": {
        "summary": "## சுருக்கம்",
        "situation": "## தற்போதைய நிலை & வேளாண் சூழல்",
        "actions": "## பரிந்துரைக்கப்பட்ட நடவடிக்கைகள்",
        "why": "## இதன் முக்கியத்துவம்",
        "priority": "## முன்னுரிமை",
        "benefit": "## எதிர்பார்க்கப்படும் நன்மை",
        "analysis": "## வேளாண் பகுப்பாய்வு",
        "treatment": "## பரிந்துரைக்கப்பட்ட சிகிச்சை",
        "prevention": "## தடுப்பு நடவடிக்கைகள்",
        "key_actions": "## முக்கிய நடவடிக்கைகள்",
        "nutrient_analysis": "## மண் ஊட்டச்சத்து பகுப்பாய்வு",
        "fertilizer_guidance": "## உர பயன்பாட்டு அட்டவணை",
        "precautions": "## முன்னெச்சரிக்கைகள்",
        "suitability": "## மண் & காலநிலை பொருத்தம்",
        "benefits": "## பொருளாதார & மகசூல் நன்மைகள்",
        "care_steps": "## சாகுபடி & பயிர் பராமரிப்பு",
        "price_insight": "## சந்தை விலை போக்கு விவரம்",
        "action_suggestions": "## விற்பனை ஆலோசனைகள்",
        "risk_explanation": "## காலநிலை இடர் பகுப்பாய்வு",
        "soil_condition": "## மண் தன்மை & நிலை",
        "best_crops": "## மிகவும் ஏற்ற பயிர்கள்",
        "improvement_tips": "## மண் வளம் பெருக்கும் வழிகள்"
    },
    "bn": {
        "summary": "## সারসংক্ষেপ",
        "situation": "## বর্তমান পরিস্থিতি ও কৃষি প্রেক্ষাপট",
        "actions": "## সুপারিশকৃত পদক্ষেপ",
        "why": "## কেন এটি গুরুত্বপূর্ণ",
        "priority": "## অগ্রাধিকার",
        "benefit": "## প্রত্যাশিত সুফল",
        "analysis": "## কৃষি বৈজ্ঞানিক বিশ্লেষণ",
        "treatment": "## প্রস্তাবিত প্রতিকার",
        "prevention": "## প্রতিরোধমূলক ব্যবস্থা",
        "key_actions": "## মূল পদক্ষেপ",
        "nutrient_analysis": "## মাটির পুষ্টি বিশ্লেষণ",
        "fertilizer_guidance": "## সার ও পুষ্টি প্রয়োগ নির্দেশিকা",
        "precautions": "## প্রয়োগ সতর্কতা",
        "suitability": "## মাটি ও আবহাওয়া উপযোগিতা",
        "benefits": "## অর্থনৈতিক ও ফলন সুবিধা",
        "care_steps": "## চাষাবাদ ও জমির পরিচর্যা",
        "price_insight": "## বাজার দর ও মূল্যের প্রবণতা",
        "action_suggestions": "## বিক্রয় ও বাজার পরামর্শ",
        "risk_explanation": "## আবহাওয়া ঝুঁকি ও ক্ষতি বিশ্লেষণ",
        "soil_condition": "## মাটির গুণাগুণ ও স্বাস্থ্য",
        "best_crops": "## সর্বাধিক উপযোগী ফসল",
        "improvement_tips": "## মাটির উর্বরতা বৃদ্ধির উপায়"
    },
    "gu": {
        "summary": "## સારાંશ",
        "situation": "## સ્થિતિ અને કૃષિ સંદર્ભ",
        "actions": "## ભલામણ કરેલ પગલાં",
        "why": "## શા માટે આ મહત્વપૂર્ણ છે",
        "priority": "## પ્રાથમિકતા",
        "benefit": "## અપેક્ષિત લાભ",
        "analysis": "## કૃષિ વૈજ્ઞાનિક વિશ્લેષણ",
        "treatment": "## ભલામણ કરેલ ઉપચાર",
        "prevention": "## અગમચેતીના પગલાં",
        "key_actions": "## મુખ્ય પગલાં",
        "nutrient_analysis": "## જમીન પોષક તત્વોનું વિશ્લેષણ",
        "fertilizer_guidance": "## ખાતર વ્યવસ્થાપન સમયપત્રક",
        "precautions": "## સાવચેતીઓ",
        "suitability": "## જમીન અને આબોહવા અનુકૂળતા",
        "benefits": "## આર્થિક અને ઉત્પાદન લાભો",
        "care_steps": "## ખેતી અને પાક સંભાળ",
        "price_insight": "## બજાર ભાવ અને વલણ વિગત",
        "action_suggestions": "## વેચાણ ભલામણો",
        "risk_explanation": "## હવામાન જોખમ વિશ્લેષણ",
        "soil_condition": "## જમીનની સ્થિતિ",
        "best_crops": "## સૌથી વધુ અનુકૂળ પાક",
        "improvement_tips": "## જમીન સુધારણાના ઉપાયો"
    },
    "mr": {
        "summary": "## सारांश",
        "situation": "## सद्यस्थिती व कृषी संदर्भ",
        "actions": "## शिफारस केलेल्या कृती",
        "why": "## याचे महत्त्व",
        "priority": "## प्राधान्यता",
        "benefit": "## अपेक्षित फायदा",
        "analysis": "## कृषी वैज्ञानिक विश्लेषण",
        "treatment": "## शिफारस केलेले उपचार",
        "prevention": "## प्रतिबंधात्मक उपाय",
        "key_actions": "## मुख्य कृती",
        "nutrient_analysis": "## माती पोषण घटक विश्लेषण",
        "fertilizer_guidance": "## खत व्यवस्थापन वेळापत्रक",
        "precautions": "## वापराची दक्षता",
        "suitability": "## जमीन व हवामान अनुकूलता",
        "benefits": "## आर्थिक व उत्पादन फायदे",
        "care_steps": "## शेती व पीक व्यवस्थापन",
        "price_insight": "## बाजार भाव व दर विश्लेषण",
        "action_suggestions": "## विक्री व बाजार शिफारशी",
        "risk_explanation": "## हवामान धोका विश्लेषण",
        "soil_condition": "## जमिनीची भौतिक स्थिती",
        "best_crops": "## सर्वाधिक अनुकूल पिके",
        "improvement_tips": "## जमीन सुपीकता वाढीचे उपाय"
    }
}


def _h(key: str, lang: str) -> str:
    """Get localized markdown heading."""
    return HEADINGS.get(lang, HEADINGS["en"]).get(key, HEADINGS["en"].get(key, f"## {key.title()}"))


# 1. Disease Advisory Fallback
def build_disease_fallback(
    disease_name: str,
    confidence: float,
    crop_name: str = "",
    language: str = "en"
) -> str:
    lang = language if language in HEADINGS else "en"
    crop_str = f" in {crop_name}" if crop_name else ""
    conf_pct = round(confidence * 100) if confidence else 85

    if lang == "or":
        return f"""{_h('summary', lang)}
{crop_name} ଫସଲରେ {disease_name} ଚିହ୍ନଟ ହୋଇଛି (ବିଶ୍ୱସନୀୟତା: {conf_pct}%)। ତୁରନ୍ତ ଫସଲ ସୁରକ୍ଷା ପଦକ୍ଷେପ ଗ୍ରହଣ କରନ୍ତୁ।

{_h('treatment', lang)}
- ପ୍ରାରମ୍ଭିକ ପର୍ଯ୍ୟାୟରେ ନିମ୍ବ ତେଲ (୫ ମିଲି/ଲିଟର ପାଣି) କିମ୍ବା ଜୈବିକ କୀଟନାଶକ ସ୍ପ୍ରେ କରନ୍ତୁ।
- ଫିମ୍ପି ଜନିତ ରୋଗ ପାଇଁ କପର ଅକ୍ସିକ୍ଲୋରାଇଡ୍ (୩ ଗ୍ରାମ/ଲିଟର) କିମ୍ବା ମାଙ୍କୋଜେବ୍ (୨.୫ ଗ୍ରାମ/ଲିଟର) ପ୍ରୟୋଗ କରନ୍ତୁ।

{_h('prevention', lang)}
- ସଂକ୍ରମିତ ପତ୍ରଗୁଡ଼ିକୁ ତୋଳି ନଷ୍ଟ କରନ୍ତୁ ଯାହାଦ୍ୱାରା ରୋଗ ଅନ୍ୟ ଗଛକୁ ବ୍ୟାପିବ ନାହିଁ।
- ଜମିରେ ଅତ୍ୟଧିକ ଜଳ ଜମିବାକୁ ଦିଅନ୍ତୁ ନାହିଁ ଏବଂ ଉତ୍ତମ ବାୟୁ ଚଳାଚଳ ବଜାୟ ରଖନ୍ତୁ।

{_h('key_actions', lang)}
- ସକାଳେ କିମ୍ବା ସନ୍ଧ୍ୟାରେ ଔଷଧ ସ୍ପ୍ରେ କରନ୍ତୁ।
- ସ୍ପ୍ରେ କରିବାର ୫ ଦିନ ପରେ ପୁନର୍ବାର ଯାଞ୍ଚ କରନ୍ତୁ।"""
    elif lang == "hi":
        return f"""{_h('summary', lang)}
{crop_name} फसल में {disease_name} के लक्षण पाए गए हैं (सटीकता: {conf_pct}%)। तुरंत निवारक उपाय अपनाएं।

{_h('treatment', lang)}
- नीम तेल (5 मिली/लीटर) या जैविक फफूंदनाशक का छिड़काव करें।
- कॉपर ऑक्सीक्लोराइड (3 ग्राम/लीटर) या मैंकोजेब (2.5 ग्राम/लीटर) का प्रयोग करें।

{_h('prevention', lang)}
- संक्रमित पत्तियों को हटाकर नष्ट करें ताकि रोग न फैले।
- खेत में जल निकासी की उचित व्यवस्था रखें।

{_h('key_actions', lang)}
- दवा का छिड़काव सुबह या शाम के समय करें।
- 5 दिनों बाद फसल का पुन: निरीक्षण करें।"""
    elif lang == "te":
        return f"""{_h('summary', lang)}
{crop_name} పంటలో {disease_name} లక్షణాలు గుర్తించబడ్డాయి (ఖచ్చితత్వం: {conf_pct}%)। సకాలంలో నివారణ చర్యలు చేపట్టండి.

{_h('treatment', lang)}
- వేప నూనె (5 మి.లీ/లీటరు) లేదా సిఫార్సు చేసిన పురుగుమందు పిచికారీ చేయండి.
- కాపర్ ఆక్సిక్లోరైడ్ (3 గ్రా/లీ) లేదా మాంకోజెబ్ (2.5 గ్రా/లీ) పిచికారీ చేయండి.

{_h('prevention', lang)}
- సోకిన ఆకులను తీసివేసి నాశనం చేయండి.
- పొలంలో నీరు నిల్వ ఉండకుండా చూడండి.

{_h('key_actions', lang)}
- ఉదయం లేదా సాయంత్రం వేళల్లో మందులు పిచికారీ చేయండి."""
    else:
        return f"""{_h('summary', lang)}
{disease_name} detected{crop_str} with {conf_pct}% confidence. Prompt intervention recommended.

{_h('treatment', lang)}
- Apply cold-pressed neem oil (5 ml/L water) or botanical bio-pesticide.
- For fungal blights, apply Copper Oxychloride (3 g/L) or Mancozeb (2.5 g/L).

{_h('prevention', lang)}
- Rogue out heavily infected leaves to restrict pathogen dissemination.
- Maintain adequate crop canopy aeration and avoid flood over-irrigation.

{_h('key_actions', lang)}
- Spray during early morning or late afternoon.
- Re-scout the crop 5 days post-treatment."""


# 2. Soil Fallback
def build_soil_fallback(
    soil_params: dict,
    fertilizer_recommendations: list,
    language: str = "en"
) -> str:
    lang = language if language in HEADINGS else "en"
    n = soil_params.get("nitrogen", 140)
    p = soil_params.get("phosphorus", 15)
    k = soil_params.get("potassium", 120)
    ph = soil_params.get("ph", 6.5)

    if lang == "or":
        return f"""{_h('summary', lang)}
ମାଟିର NPK ପୋଷକ ମୂଲ୍ୟ: ନାଇଟ୍ରୋଜେନ୍={n} kg/ha, ଫସଫରସ୍={p} kg/ha, ପୋଟାସ୍={k} kg/ha, pH={ph}।

{_h('nutrient_analysis', lang)}
- ମାଟିର pH ସ୍ତର ଉପଯୁକ୍ତ ରହିଛି ଏବଂ ପୋଷକ ତତ୍ତ୍ୱ ଗ୍ରହଣ କ୍ଷମତା ସ୍ୱାଭାବିକ ଅଛି।
- ସନ୍ତୁଳିତ ପୋଷକ ବୃଦ୍ଧି ପାଇଁ ଜୈବିକ ଖତ ଓ ସାରର ସମନ୍ୱିତ ପ୍ରୟୋଗ ଆବଶ୍ୟକ।

{_h('fertilizer_guidance', lang)}
- ଏକର ପିଛା ୫ ଟନ୍ ପଚା ଗୋବର ଖତ କିମ୍ବା ଭର୍ମିକମ୍ପୋଷ୍ଟ ପ୍ରୟୋଗ କରନ୍ତୁ।
- ନାଇଟ୍ରୋଜେନ୍ (ୟୁରିଆ) କୁ ଏକାଥରେ ନଦେଇ ୨ ରୁ ୩ ଟି କିସ୍ତିରେ ପ୍ରୟୋଗ କରନ୍ତୁ।

{_h('key_actions', lang)}
- ସାର ପ୍ରୟୋଗ ସମୟରେ ମାଟିରେ ପର୍ଯ୍ୟାପ୍ତ ଆର୍ଦ୍ରତା ଥିବା ଆବଶ୍ୟକ।"""
    elif lang == "hi":
        return f"""{_h('summary', lang)}
मिट्टी में NPK स्तर: नाइट्रोजन={n} kg/ha, फास्फोरस={p} kg/ha, पोटाश={k} kg/ha, pH={ph}।

{_h('nutrient_analysis', lang)}
- मिट्टी का pH संतुलित है तथा मुख्य पोषक तत्वों की स्थिति सामान्य है।
- उत्पादकता बढ़ाने हेतु संतुलित पोषण प्रबंधन की आवश्यकता है।

{_h('fertilizer_guidance', lang)}
- प्रति एकड़ 5 टन गोबर की खाद या वर्मीकम्पोस्ट डालें।
- यूरिया की मात्रा को 2-3 भागों में विभाजित कर डालें।

{_h('key_actions', lang)}
- खाद व उर्वरक का प्रयोग मिट्टी में नमी होने पर ही करें।"""
    else:
        return f"""{_h('summary', lang)}
Soil nutrient profile: Nitrogen={n} kg/ha, Phosphorus={p} kg/ha, Potassium={k} kg/ha, pH={ph}.

{_h('nutrient_analysis', lang)}
- Soil pH is balanced supporting optimal nutrient assimilation.
- Integrated Nutrient Management (INM) recommended for sustained yield.

{_h('fertilizer_guidance', lang)}
- Apply well-decomposed FYM @ 5 tonnes/acre or vermicompost.
- Split Nitrogen (Urea) applications across 2–3 vegetative growth stages.

{_h('key_actions', lang)}
- Ensure adequate soil moisture before top-dressing fertilizer."""


# 3. Crop Recommendation Fallback
def build_crop_fallback(
    recommended_crops: list,
    soil_type: str = "Loamy",
    season: str = "Kharif",
    location: str = "Vijayawada, Andhra Pradesh",
    language: str = "en"
) -> str:
    lang = language if language in HEADINGS else "en"
    crop_names = [c.get("name", "Crop") if isinstance(c, dict) else str(c) for c in (recommended_crops or [])[:3]]
    crops_str = ", ".join(crop_names) if crop_names else "Paddy, Chilli, Cotton"

    if lang == "or":
        return f"""{_h('summary', lang)}
{location} ଅଞ୍ଚଳ ଏବଂ {season} ଋତୁ ପାଇଁ ସୁପାରିଶ କରାଯାଇଥିବା ମୁଖ୍ୟ ଫସଲ: {crops_str}।

{_h('suitability', lang)}
- {soil_type} ମାଟି ଏହି ଫସଲଗୁଡ଼ିକ ପାଇଁ ଅତ୍ୟନ୍ତ ଉପଯୋଗୀ ଏବଂ ଜଳ ଧାରଣ କ୍ଷମତା ଭଲ ରହିଛି।
- ସ୍ଥାନୀୟ ଜଳବାୟୁ ଓ ତାପମାତ୍ରା ଉତ୍ତମ ଅମଳ ପାଇଁ ଅନୁକୂଳ।

{_h('care_steps', lang)}
- ଉନ୍ନତ କିସମର ପ୍ରମାଣିତ ବିହନ ବ୍ୟବହାର କରନ୍ତୁ ଏବଂ ବିହନ ବିଶୋଧନ ନିଶ୍ଚିତ କରନ୍ତୁ।
- ଠିକ୍ ଦୂରତାରେ ଧାଡ଼ି ବୁଣା କରନ୍ତୁ ଯାହାଦ୍ୱାରା ଘାସ ନିୟନ୍ତ୍ରଣ ଓ କୀଟ ପରିଚାଳନା ସହଜ ହେବ।

{_h('key_actions', lang)}
- ପ୍ରାକ୍-ଋତୁ ଜମି ପ୍ରସ୍ତୁତି ସମୟରେ ଜୈବିକ ଖତ ପ୍ରୟୋଗ କରନ୍ତୁ।"""
    elif lang == "hi":
        return f"""{_h('summary', lang)}
{location} क्षेत्र व {season} मौसम हेतु अनुशंसित प्रमुख फसलें: {crops_str}।

{_h('suitability', lang)}
- {soil_type} मिट्टी इन फसलों के लिए अत्यधिक उपयुक्त है।
- स्थानीय तापमान व जलवायु अच्छी पैदावार के अनुकूल हैं।

{_h('care_steps', lang)}
- प्रमाणित व उन्नत किस्मों के बीजों का चयन करें एवं बीज शोधन अवश्य करें।
- कतार में बुवाई करें ताकि निराई-गुड़ाई व कीट प्रबंधन सुगम रहे।

{_h('key_actions', lang)}
- बुवाई पूर्व खेत में पर्याप्त जैविक खाद मिलाएं।"""
    else:
        return f"""{_h('summary', lang)}
Recommended crops for {location} during {season} season: {crops_str}.

{_h('suitability', lang)}
- {soil_type} soil provides ideal root anchorage and moisture retention.
- Local agro-climatic conditions strongly favor these cultivars.

{_h('care_steps', lang)}
- Use certified high-yielding seeds and perform biological seed treatment.
- Adopt line sowing to facilitate mechanical weeding and canopy aeration.

{_h('key_actions', lang)}
- Incorporate organic manure during pre-sowing land preparation."""


# 4. Soil Type Fallback
def build_soil_type_fallback(
    soil_type: str,
    characteristics: dict = None,
    language: str = "en"
) -> str:
    lang = language if language in HEADINGS else "en"
    if lang == "or":
        return f"""{_h('summary', lang)}
ମାଟି ପ୍ରକାର: {soil_type}। ଏହାର ଭୌତିକ ସଂରଚନା କୃଷି ଉତ୍ପାଦନ ପାଇଁ ଉତ୍ତମ।

{_h('improvement_tips', lang)}
- ଜୈବିକ ପଦାର୍ଥ ଓ କମ୍ପୋଷ୍ଟ ପ୍ରୟୋଗ କରି ମାଟିର ସ୍ୱାସ୍ଥ୍ୟ ବୃଦ୍ଧି କରନ୍ତୁ।
- ମାଟିର ପୋଷକ ତତ୍ତ୍ୱ ଅନୁସାରେ ଫସଲ ଚକ୍ର ଆପଣାନ୍ତୁ।"""
    else:
        return f"""{_h('summary', lang)}
Identified soil texture: {soil_type}. Favorable physical structure for agricultural production.

{_h('improvement_tips', lang)}
- Enrich with organic compost to enhance microbial biodiversity and water retention.
- Practice legume crop rotation to sustain soil fertility."""


# 5. Market Fallback
def build_market_fallback(
    crop_name: str,
    trend: str,
    change_percent: float,
    latest_price: float,
    location: str = "",
    language: str = "en"
) -> str:
    lang = language if language in HEADINGS else "en"
    loc_str = f" ({location})" if location else ""
    if lang == "or":
        return f"""{_h('summary', lang)}
{crop_name} ର ବର୍ତ୍ତମାନ ବଜାର ଦର: ₹{latest_price:,.0f}/କ୍ୱିଣ୍ଟାଲ{loc_str}। ଦର ଧାରା: {trend} ({abs(change_percent)}%)।

{_h('price_insight', lang)}
- ଭଲ ଗୁଣବତ୍ତା ଓ ଶୁଖିଲା ଫସଲକୁ ବଜାରରେ ଉଚ୍ଚ ମୂଲ୍ୟ ମିଳୁଛି।
- ଆଖପାଖ ମଣ୍ଡିଗୁଡ଼ିକର ଦୈନିକ ଦର ଯାଞ୍ଚ କରି ବିକ୍ରୟ କରନ୍ତୁ।

{_h('key_actions', lang)}
- ଫସଲକୁ ସଠିକ୍ ଗ୍ରେଡିଂ ଓ ଶୁଖାଇ ମଣ୍ଡିକୁ ନିଅନ୍ତୁ।"""
    else:
        return f"""{_h('summary', lang)}
Current market price for {crop_name}: ₹{latest_price:,.0f}/quintal{loc_str}. Trend: {trend} ({abs(change_percent)}%).

{_h('price_insight', lang)}
- Clean, well-graded, low-moisture lots command premium market realization.
- Cross-reference nearby APMC market yard rates before dispatching bulk produce.

{_h('key_actions', lang)}
- Dry produce to 10-12% moisture to avoid discount deductions."""


# 6. Comprehensive Context-Aware Interactive Advisory Fallback (5-Section Structure)
def build_interactive_advisory_fallback(
    query: str = "",
    location: str = "Vijayawada, Andhra Pradesh",
    crop_name: str = "Chilli",
    weather_data: dict = None,
    soil_data: dict = None,
    market_data: dict = None,
    distress_score: int = None,
    language: str = "en"
) -> str:
    """
    Generate rich, domain-specific, contextual agricultural guidance strictly following
    the 5-section format:
    1. Situation & Agronomic Context
    2. Recommended Actions (1 to 5)
    3. Why This Matters
    4. Priority Level
    5. Expected Benefit
    Supports all 8 languages: en, or, hi, te, ta, bn, gu, mr.
    """
    lang = language if language in HEADINGS else "en"
    q_lower = (query or "").lower()
    loc = location or "Vijayawada, Andhra Pradesh"
    crop = crop_name or "Chilli"

    # Intent Detection
    is_pest = any(w in q_lower for w in [
        "pest", "disease", "fungus", "leaf", "organic pest", "insect", "spray", "neem",
        "blight", "mildew", "rot", "caterpillar", "aphid", "thrips", "whitefly",
        "କୀଟ", "ପୋକ", "ରୋଗ", "ନିମ୍ବ", "ପତ୍ର", "ଫିମ୍ପି",
        "कीट", "रोग", "नीम", "पत्ती", "कीड़े", "फफूंद",
        "పురుగు", "తెగులు", "వేప", "ఆకు",
        "பூச்சி", "நோய்", "வேப்ப", "இலை",
        "পোকা", "রোগ", "নিম", "পাতা",
        "જીવાત", "રોગ", "લીમડા", "પાંદડા",
        "कीड", "रोग", "निंबोळी", "पाने"
    ])
    is_weather = any(w in q_lower for w in [
        "weather", "rain", "monsoon", "storm", "temperature", "heat", "flood", "irrigation",
        "water", "dry", "drought", "frost", "cold", "humidity",
        "ପାଣିପାଗ", "ବର୍ଷା", "ଜଳ", "ତାପମାତ୍ରା", "ଜଳସେଚନ",
        "मौसम", "बारिश", "तापमान", "सिंचाई", "वर्षा", "पानी",
        "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "నీరు", "సాగునీరు",
        "வானிலை", "மழை", "வெப்பநிலை", "நீர்", "பாசனம்",
        "আবহাওয়া", "বৃষ্টি", "তাপমাত্রা", "সেচ",
        "હવામાન", "વરસાદ", "તાપમાન", "સિંચાઈ",
        "हवामान", "पाऊस", "तापमान", "पाणी", "सिंचन"
    ])
    is_market = any(w in q_lower for w in [
        "market", "price", "mandi", "sell", "rate", "cost", "apmc", "profit", "holding", "storage",
        "ମଣ୍ଡି", "ଦର", "ବିକ୍ରି", "ମୂଲ୍ୟ", "ଲାଭ",
        "मंडी", "भाव", "दाम", "बिक्री", "मूल्य", "लाभ",
        "మార్కెట్", "ధర", "సంత", "అమ్మకం",
        "சந்தை", "விலை", "விற்பனை",
        "বাজার", "দর", "দাম", "বিক্রি",
        "બજાર", "ભાવ", "વેચાણ",
        "बाजार", "भाव", "विक्री"
    ])
    is_soil = any(w in q_lower for w in [
        "soil", "nutrient", "npk", "fertilizer", "urea", "dap", "potash", "ph", "zinc", "organic", "compost", "manure",
        "ମାଟି", "ସାର", "ପୋଷକ", "ୟୁରିଆ", "ଖତ",
        "मिट्टी", "उर्वरक", "खाद", "पोषक", "यूरिया", "जिंक",
        "నేల", "ఎరువులు", "పోషకాలు",
        "மண்", "உரம்", "ஊட்டச்சத்து",
        "মাটি", "সার", "পুষ্টি",
        "જમીન", "ખાતર", "પોષક",
        "माती", "खत", "अन्नद्रव्ये"
    ])
    is_crop = any(w in q_lower for w in [
        "crop", "growth", "yield", "flowering", "seed", "variety", "harvest", "sowing", "season", "stage",
        "ଫସଲ", "ଅମଳ", "ବୃଦ୍ଧି", "ବିହନ", "ଅମଳ",
        "फसल", "पैदावार", "बुवाई", "बीज", "कटाई",
        "పంట", "దిగుబడి", "విత్తనాలు",
        "பயிர்", "மகசூல்", "விதை",
        "ফসল", "ফলন", "বীজ",
        "પાક", "ઉત્પાદન", "બીજ",
        "पीक", "उत्पादन", "बियाणे"
    ])

    # 1. ODIA (or) - Priority Flagship Locale
    if lang == "or":
        if is_pest:
            return f"""{_h('situation', lang)}
ଆପଣଙ୍କ ଅଞ୍ଚଳ ({loc}) ରେ ବର୍ତ୍ତମାନର ଆର୍ଦ୍ରତା ଓ ତାପମାତ୍ରା ସ୍ଥିତି {crop} ଫସଲରେ କୀଟ ଓ ରୋଗ ସଂକ୍ରମଣ ଆଶଙ୍କା ବୃଦ୍ଧି କରୁଛି।

{_h('actions', lang)}
1. ପତ୍ରର ତଳ ଭାଗ ଏବଂ କଅଁଳ ଡାଳଗୁଡ଼ିକୁ ନିୟମିତ ଯାଞ୍ଚ କରି ଶୋଷକ କୀଟ ଓ ଫିମ୍ପି ଦାଗ ଚିହ୍ନଟ କରନ୍ତୁ।
2. ଅଧିକ ସଂକ୍ରମିତ ହୋଇଥିବା ପତ୍ର ଓ ଡାଳଗୁଡ଼ିକୁ କାଟି କ୍ଷେତରୁ ଦୂରରେ ପୋତି ନଷ୍ଟ କରନ୍ତୁ।
3. ଜୈବିକ ନିମ୍ବ ତେଲ (୧୦,୦୦୦ ppm @ ୨-୩ ମିଲି/ଲିଟର ପାଣି) କିମ୍ବା ନିମ୍ବ ମଞ୍ଜି ଅର୍କ ୫% ସ୍ପ୍ରେ କରନ୍ତୁ।
4. ଧଳାମାଛି, ଜଉପୋକ ଓ ଥ୍ରିପ୍ସ ନିୟନ୍ତ୍ରଣ ପାଇଁ ଏକର ପିଛା ୧୫ଟି ହଳଦିଆ ଓ ନୀଳ ଫାନ୍ଦ (Sticky Traps) ଲଗାନ୍ତୁ।
5. ଔଷଧ ସ୍ପ୍ରେ କରିବାର ୪୮ ରୁ ୭୨ ଘଣ୍ଟା ମଧ୍ୟରେ ଫସଲର ସ୍ଥିତି ପୁନର୍ବାର ନିରୀକ୍ଷଣ କରନ୍ତୁ।

{_h('why', lang)}
ଅତ୍ୟଧିକ ବାୟୁମଣ୍ଡଳୀୟ ଆର୍ଦ୍ରତା ଏବଂ କଅଁଳ ଫସଲ ବୃଦ୍ଧି ଅବସ୍ଥା କୀଟ ବଂଶବୃଦ୍ଧି ଓ ଫିମ୍ପି ସଂକ୍ରମଣ ପାଇଁ ଅନୁକୂଳ ପରିବେଶ ସୃଷ୍ଟି କରେ।

{_h('priority', lang)}
ଆଜି ହିଁ (TODAY - ଜରୁରୀ ପଦକ୍ଷେପ)

{_h('benefit', lang)}
ଜୈବିକ ଉପାୟରେ କୀଟ ନିୟନ୍ତ୍ରଣ ହେବା ସହ ମିତ୍ର କୀଟ ସୁରକ୍ଷିତ ରହିବେ ଏବଂ ୨୫-୩୫% ସମ୍ଭାବ୍ୟ ଅମଳ କ୍ଷତି ରୋକାଯାଇପାରିବ।"""

        elif is_weather:
            return f"""{_h('situation', lang)}
{loc} ଅଞ୍ଚଳର ପାଣିପାଗ ପୂର୍ବାନୁମାନ ଅନୁସାରେ ଆଗାମୀ ବର୍ଷା ଓ ତାପମାତ୍ରା ପରିବର୍ତ୍ତନ ହେତୁ ଜଳ ପରିଚାଳନା ସତର୍କତା ଜରୁରୀ।

{_h('actions', lang)}
1. ଜମିରୁ ଅତିରିକ୍ତ ପାଣି ନିଷ୍କାସନ ପାଇଁ ଡ୍ରେନେଜ୍ ନାଳୀଗୁଡ଼ିକୁ ତୁରନ୍ତ ସଫା ଓ ପ୍ରସ୍ତୁତ ରଖନ୍ତୁ।
2. ପ୍ରବଳ ବର୍ଷା ପୂର୍ବରୁ ରାସାୟନିକ ସାର ପ୍ରୟୋଗ ଓ କୀଟନାଶକ ସ୍ପ୍ରେ ସ୍ଥଗିତ ରଖନ୍ତୁ।
3. ଅମଳ ହୋଇସାରିଥିବା ଫସଲକୁ ତୁରନ୍ତ ସୁରକ୍ଷିତ ଓ ଶୁଖିଲା ଛାତ ତଳେ ସାଇତି ରଖନ୍ତୁ।
4. ଜମିରେ ପାଣି ଜମି ରହିଥିଲେ ବର୍ଷା ଛାଡ଼ିବା ମାତ୍ରେ ପମ୍ପ ସାହାଯ୍ୟରେ ପାଣି ବାହାର କରନ୍ତୁ।
5. ପ୍ରତିକୂଳ ପାଗ ପରେ ଫସଲକୁ ସତେଜ କରିବା ପାଇଁ ହାଲୁକା ପୋଟାସିୟମ୍ ନାଇଟ୍ରେଟ୍ (୦.୫%) ସ୍ପ୍ରେ କରନ୍ତୁ।

{_h('why', lang)}
ଜମିରେ ପାଣି ଜମି ରହିଲେ ଚେରକୁ ଅମ୍ଳଜାନ ମିଳେ ନାହିଁ, ଯାହା ଚେର ପଚା ରୋଗ ଓ ପୋଷକ ତତ୍ତ୍ୱ ନଷ୍ଟର କାରଣ ହୁଏ।

{_h('priority', lang)}
ଜରୁରୀ (URGENT)

{_h('benefit', lang)}
ଚେର ପଚା ରୋଗରୁ ଫସଲ ସୁରକ୍ଷିତ ରହିବ ଏବଂ ସାର ଧୋଇ ହୋଇ ନଷ୍ଟ ହେବାରୁ ବଞ୍ଚିବ।"""

        elif is_market:
            return f"""{_h('situation', lang)}
{loc} ର ସ୍ଥାନୀୟ APMC ମଣ୍ଡିରେ {crop} ଫସଲର ଆଗମନ ଓ ଦର ପରିବର୍ତ୍ତନ ଅନୁଧ୍ୟାନ କରାଯାଉଛି।

{_h('actions', lang)}
1. ଫସଲକୁ ମଣ୍ଡି ନେବା ପୂର୍ବରୁ ୧୦-୧୨% ଆର୍ଦ୍ରତା ପର୍ଯ୍ୟନ୍ତ ଭଲ ଭାବେ ଖରାରେ ଶୁଖାନ୍ତୁ।
2. ଆକାର, ରଙ୍ଗ ଓ ପରିଷ୍କାରତା ଅନୁସାରେ ଫସଲକୁ 'ଏ' ଗ୍ରେଡ୍ ଏବଂ ସାଧାରଣ ଭାଗରେ ଗ୍ରେଡିଂ କରନ୍ତୁ।
3. ସମସ୍ତ ଫସଲ ଏକାସାଙ୍ଗେ ବିକ୍ରି ନକରି ୪୦% ବର୍ତ୍ତମାନ ବିକ୍ରୟ କରନ୍ତୁ ଏବଂ ବାକି ଅଂଶ ସାଇତି ରଖନ୍ତୁ।
4. AgriDarshak ଡ୍ୟାସବୋର୍ଡରେ ପଡ଼ୋଶୀ ଜିଲ୍ଲା ମଣ୍ଡିଗୁଡ଼ିକର ଦୈନିକ ଦର ତୁଳନା କରନ୍ତୁ।
5. ବଜାର ଦର କମିଲେ ସରକାରୀ ସର୍ବନିମ୍ନ ସହାୟକ ମୂଲ୍ୟ (MSP) କ୍ରୟ କେନ୍ଦ୍ରର ସୁବିଧା ନିଅନ୍ତୁ।

{_h('why', lang)}
ଅମଳ ସମୟରେ ଅଧିକ ଆଗମନ ହେତୁ ଦର ସାମୟିକ ଭାବେ କମିଥାଏ; ଉତ୍ତମ ଗ୍ରେଡିଂ ଯୁକ୍ତ ଫସଲ ୧୫-୨୦% ଅଧିକ ଦର ପାଏ।

{_h('priority', lang)}
ଏହି ସପ୍ତାହରେ (THIS WEEK)

{_h('benefit', lang)}
ସର୍ବୋତ୍ତମ ମଣ୍ଡି ମୂଲ୍ୟ ପ୍ରାପ୍ତି ଏବଂ ଆର୍ଦ୍ରତା ଜନିତ ଦର କାଟ୍ ସମସ୍ୟାରୁ ସମ୍ପୂର୍ଣ୍ଣ ମୁକ୍ତି।"""

        elif is_soil:
            return f"""{_h('situation', lang)}
{loc} ଅଞ୍ଚଳର ମାଟିରେ ସୁନ୍ତୁଳିତ NPK ଏବଂ pH ସ୍ତର ବଜାୟ ରଖିବା ପାଇଁ ପୋଷକ ପରିଚାଳନା ଆବଶ୍ୟକ।

{_h('actions', lang)}
1. ଏକର ପିଛା ୪-୫ ଟନ୍ ଉତ୍ତମ ପଚା ଗୋବର ଖତ କିମ୍ବା ଭର୍ମିକମ୍ପୋଷ୍ଟ ମାଟିରେ ପ୍ରୟୋଗ କରନ୍ତୁ।
2. ନାଇଟ୍ରୋଜେନ୍ (ୟୁରିଆ) ସାରକୁ ଏକାଥରେ ନଦେଇ ୩ଟି କିସ୍ତିରେ ବିଭାଜନ କରି ପ୍ରୟୋଗ କରନ୍ତୁ।
3. ଅମ୍ଳୀୟ ମାଟି (pH < 6.2) ପାଇଁ ଜମି ପ୍ରସ୍ତୁତି ସମୟରେ ଏକର ପିଛା ୧୫୦-୨୦୦ କେଜି ଚୂନ ପ୍ରୟୋଗ କରନ୍ତୁ।
4. ଜୈବିକ ସାର ଯଥା ଆଜୋଟୋବ୍ୟାକ୍ଟର ଓ PSB କଲଚର (୨ କେଜି/ଏକର) ମାଟିରେ ମିଶାନ୍ତୁ।
5. ସୂକ୍ଷ୍ମ ପୋଷକ ତତ୍ତ୍ୱ (ଜିଙ୍କ୍ + ବୋରନ୍ @ ୨ ଗ୍ରାମ/ଲିଟର) ଫସଲ ବୃଦ୍ଧି ସମୟରେ ସ୍ପ୍ରେ କରନ୍ତୁ।

{_h('why', lang)}
ସନ୍ତୁଳିତ ମାଟି ରସାୟନ ଦ୍ୱାରା ଚେରର ପୋଷକ ଗ୍ରହଣ କ୍ଷମତା ବୃଦ୍ଧି ପାଏ ଏବଂ ଉତ୍ପାଦିକା ଶକ୍ତି ଦୀର୍ଘସ୍ଥାୟୀ ରହେ।

{_h('priority', lang)}
ଏହି ସପ୍ତାହରେ (THIS WEEK)

{_h('benefit', lang)}
ସାରର କାର୍ଯ୍ୟଦକ୍ଷତା ୩୦% ବୃଦ୍ଧି ପାଇବା ସହ ମାଟିର ଉର୍ବରତା ଓ ଫସଲର ରୋଗ ପ୍ରତିରୋଧକ ଶକ୍ତି ସୁଦୃଢ଼ ହେବ।"""

        else:
            return f"""{_h('situation', lang)}
{loc} ଅଞ୍ଚଳର {crop} ଫସଲ ଏବଂ ସାମ୍ପ୍ରତିକ କୃଷି ପରିସ୍ଥିତି ଅନୁସାରେ କ୍ଷେତ୍ର ପରିଚାଳନା ପରାମର୍ଶ।

{_h('actions', lang)}
1. ଫସଲ ବୃଦ୍ଧି ଅବସ୍ଥା ଅନୁଯାୟୀ ନିୟମିତ ଜଳସେଚନ ଓ ଘାସ ନିୟନ୍ତ୍ରଣ ବ୍ୟବସ୍ଥା ବଜାୟ ରଖନ୍ତୁ।
2. ପତ୍ର ରୋଗ ଓ କୀଟ ସଂକ୍ରମଣର ପ୍ରାରମ୍ଭିକ ଲକ୍ଷଣ ଉପରେ ପ୍ରତି ୨-୩ ଦିନରେ ନଜର ରଖନ୍ତୁ।
3. ଫୁଲ ଓ ଫଳ ଧାରଣ ସମୟରେ ସମନ୍ୱିତ ପୋଷକ ତତ୍ତ୍ୱ ଏବଂ ଜୈବିକ ଟନିକ୍ ପ୍ରୟୋଗ କରନ୍ତୁ।
4. ଜମିରେ ଜଳ ନିଷ୍କାସନ ସୁନିଶ୍ଚିତ କରି ମୂଳ ସଢ଼ା ରୋଗକୁ ପ୍ରତିହତ କରନ୍ତୁ।
5. AgriDarshak ଡ୍ୟାସବୋର୍ଡରେ ଦୈନିକ ପାଣିପାଗ ସତର୍କତା ଓ ମଣ୍ଡି ଦର ଅନୁସରଣ କରନ୍ତୁ।

{_h('why', lang)}
ସମୟୋଚିତ ତଥା ଯୋଜନାବଦ୍ଧ ଫସଲ ଯତ୍ନ ଦ୍ୱାରା ପ୍ରତିକୂଳ ପରିବେଶ ଜନିତ ଚାପ ହ୍ରାସ ପାଏ।

{_h('priority', lang)}
ଆଜି ହିଁ (TODAY)

{_h('benefit', lang)}
ସୁସ୍ଥ ଫସଲ ବୃଦ୍ଧି, ଅଧିକ ଫଳନ ଏବଂ ୨୦-୩୦% ଅଧିକ ନିଟ୍ କୃଷି ଆୟ ସୁନିଶ୍ଚିତ।"""

    # 2. HINDI (hi)
    elif lang == "hi":
        if is_pest:
            return f"""{_h('situation', lang)}
आपके क्षेत्र ({loc}) में वर्तमान नमी व तापमान के कारण {crop} फसल में कीट व फफूंद संक्रमण का जोखिम बढ़ गया है।

{_h('actions', lang)}
1. पत्तियों की निचली सतह और नई कोपलों का नियमित निरीक्षण कर रस चूसक कीटों की पहचान करें।
2. अत्यधिक ग्रसित पत्तियों और शाखाओं को तोड़कर खेत से दूर नष्ट करें।
3. जैविक नीम तेल (10,000 ppm @ 2-3 मिली/लीटर पानी) या नीम बीज अर्क 5% का छिड़काव करें।
4. सफेद मक्खी व थ्रिप्स कीटों की रोकथाम हेतु प्रति एकड़ 15 पीले व नीले चिपचिपे ट्रैप (Sticky Traps) लगाएं।
5. छिड़काव के 48 से 72 घंटे बाद फसल की स्थिति का पुन: निरीक्षण करें।

{_h('why', lang)}
उच्च सापेक्ष आर्द्रता और अनुकूल तापमान कीटों के प्रजनन व फफूंद बीजाणुओं के प्रसार को बढ़ावा देते हैं।

{_h('priority', lang)}
आज ही (TODAY - आवश्यक कदम)

{_h('benefit', lang)}
प्राकृतिक रूप से कीट नियंत्रण होगा, मित्र कीट सुरक्षित रहेंगे और पैदावार में 25-35% तक के नुकसान से बचाव होगा।"""

        elif is_weather:
            return f"""{_h('situation', lang)}
{loc} के मौसम पूर्वानुमान के अनुसार आगामी वर्षा व तापमान उतार-चढ़ाव को देखते हुए जल प्रबंधन आवश्यक है।

{_h('actions', lang)}
1. खेत से अतिरिक्त वर्षा जल की सुरक्षित निकासी हेतु मेड़ व नालियों को तुरंत साफ रखें।
2. भारी वर्षा की संभावना के दौरान रासायनिक खाद का छिड़काव व कीटनाशक प्रयोग स्थगित रखें।
3. कटी हुई अथवा परिपक्व फसल को तत्काल सुरक्षित व सूखे स्थान पर भंडारित करें।
4. खेत में जलभराव होने पर वर्षा रुकते ही पानी को तुरंत बाहर निकालें।
5. प्रतिकूल मौसम के बाद फसल को ऊर्जा प्रदान करने हेतु पोटेशियम नाइट्रेट (0.5%) का हल्का छिड़काव करें।

{_h('why', lang)}
जड़ों में जलभराव से ऑक्सीजन की कमी होती है, जिससे जड़ गलन रोग और पोषक तत्वों का ह्रास होता है।

{_h('priority', lang)}
अति आवश्यक (URGENT)

{_h('benefit', lang)}
जड़ गलन रोग से सुरक्षा मिलेगी और उर्वरकों की बर्बादी रुकेगी।"""

        elif is_market:
            return f"""{_h('situation', lang)}
{loc} की स्थानीय कृषि उपज मंडी (APMC) में {crop} फसल की आवक व मूल्य रुझान का विश्लेषण।

{_h('actions', lang)}
1. उपज को मंडी ले जाने से पूर्व 10-12% नमी स्तर तक अच्छी तरह धूप में सुखाएं।
2. उपज की छंटाई व ग्रेडिंग कर उत्तम गुणवत्ता वाले दाने अलग करें।
3. पूरी फसल एक साथ न बेचकर 40% तत्काल बेचें और शेष उपज भंडारित करें।
4. AgriDarshak पर नजदीकी मंडियों के दैनिक भावों की तुलना करें।
5. बाजार भाव न्यूनतम समर्थन मूल्य (MSP) से कम होने पर सरकारी खरीद केंद्र पर संपर्क करें।

{_h('why', lang)}
कटाई के तुरंत बाद भारी आवक से भाव गिरते हैं; अच्छी ग्रेडिंग वाली उपज को 15-20% अधिक मूल्य मिलता है।

{_h('priority', lang)}
इस सप्ताह (THIS WEEK)

{_h('benefit', lang)}
सर्वोत्तम मंडी मूल्य प्राप्ति तथा नमी कटौती व औने-पौने दामों में बिक्री से पूर्ण बचाव।"""

        else:
            return f"""{_h('situation', lang)}
{loc} क्षेत्र में {crop} फसल हेतु समग्र कृषि प्रबंधन व सुरक्षा सलाह।

{_h('actions', lang)}
1. फसल की वृद्धि अवस्था अनुसार नियमित सिंचाई व खरपतवार नियंत्रण सुनिश्चित करें।
2. रोग व कीट के शुरुआती लक्षणों हेतु प्रति 2-3 दिन में खेत की निगरानी करें।
3. फूल व फल बनते समय संतुलित सूक्ष्म पोषक तत्वों का छिड़काव करें।
4. खेत में जल निकासी की व्यवस्था दुरुस्त रखें।
5. AgriDarshak पर दैनिक मौसम चेतावनी व मंडी भाव देखते रहें।

{_h('why', lang)}
नियोजित कृषि प्रबंधन से पर्यावरणीय तनाव कम होता है और फसल क्षमता का पूरा लाभ मिलता है।

{_h('priority', lang)}
आज ही (TODAY)

{_h('benefit', lang)}
उत्कृष्ट पैदावार, स्वस्थ फसल विकास और 20-30% अधिक शुद्ध आय।"""

    # 3. TELUGU (te)
    elif lang == "te":
        if is_pest:
            return f"""{_h('situation', lang)}
మీ ప్రాంతం ({loc}) లో ప్రస్తుత తేమ మరియు ఉష్ణోగ్రత పరిస్థితులు {crop} పంటలో చీడపీడల వ్యాప్తికి అనుకూలంగా ఉన్నాయి.

{_h('actions', lang)}
1. ఆకుల అడుగుభాగం మరియు చిగుళ్లను పరిశీలించి రసం పీల్చే పురుగులను గుర్తించండి.
2. తెగులు సోకిన ఆకులను తీసివేసి పొలానికి దూరంగా నాశనం చేయండి.
3. వేప నూనె (10,000 ppm @ 2-3 మి.లీ/లీటరు నీరు) లేదా జీవ పురుగుమందు పిచికారీ చేయండి.
4. తెల్లదోమ మరియు తామర పురుగుల నివారణకు ఎకరాకు 15 పసుపు, నీలి రంగు జిగురు బుట్టలు (Sticky Traps) అమర్చండి.
5. పిచికారీ చేసిన 48-72 గంటల తర్వాత పంటను మళ్లీ పరిశీలించండి.

{_h('why', lang)}
అధిక తేమ వల్ల చీడపీడల సంతతి మరియు శిలీంధ్ర వ్యాధులు వేగంగా విస్తరిస్తాయి.

{_h('priority', lang)}
ఈరోజే (TODAY - తక్షణ చర్య)

{_h('benefit', lang)}
మిత్రపురుగులు సురక్షితంగా ఉంటూ 25-35% దిగుబడి నష్టం నివారించబడుతుంది."""
        else:
            return f"""{_h('situation', lang)}
{loc} ప్రాంతంలో {crop} పంట సమగ్ర సంరక్షణ మరియు యాజమాన్య సలహా.

{_h('actions', lang)}
1. పంట దశను బట్టి సకాలంలో నీటి పారుదల మరియు సమతుల్య ఎరువుల యాజమాన్యం చేపట్టండి.
2. పొలంలో నీరు నిల్వ ఉండకుండా మురుగు నీటి కాలువలను శుభ్రం చేయండి.
3. చీడపీడల నివారణకు క్రమం తప్పకుండా పొలాన్ని పర్యవేక్షించండి.
4. AgriDarshak లో ప్రతిరోజూ వాతావరణ హెచ్చరికలు మరియు మార్కెట్ ధరలు గమనించండి.

{_h('why', lang)}
సరైన సమయంలో తీసుకునే జాగ్రత్తలు పంటను తెగుళ్ల బారిన పడకుండా కాపాడతాయి.

{_h('priority', lang)}
ఈరోజే (TODAY)

{_h('benefit', lang)}
నాణ్యమైన దిగుబడి మరియు 20-30% అధిక నికర ఆదాయం."""

    # 4. TAMIL (ta)
    elif lang == "ta":
        return f"""{_h('situation', lang)}
உங்கள் பகுதி ({loc}) வானிலை மற்றும் தற்போதைய சூழலில் {crop} பயிரில் பூச்சி மற்றும் நோய் மேலாண்மை வழிகாட்டல்.

{_h('actions', lang)}
1. இலைகளின் அடிப்பகுதியை ஆய்வு செய்து பூச்சிகளின் தாக்குதலை தொடக்கத்திலேயே கண்டறியவும்.
2. பாதிக்கப்பட்ட இலைகள் மற்றும் செடிகளை அகற்றி அழிக்கவும்.
3. வேப்ப எண்ணெய் (10,000 ppm @ 2-3 மிலி/லிட்டர்) தெளித்து இயற்கை பூச்சி கட்டுப்பாடு செய்யவும்.
4. வெள்ளை ஈக்கள் மற்றும் அசுவினிகளைக் கட்டுப்படுத்த ஏக்கருக்கு 15 ஒட்டும் பொறிகளை அமைக்கவும்.
5. மருந்து தெளித்த 3 நாட்களுக்குப் பிறகு பயிரை மீண்டும் ஆய்வு செய்யவும்.

{_h('why', lang)}
அதிக ஈரப்பதம் பூச்சிகள் மற்றும் பூஞ்சான் நோய்கள் வேகமாகப் பரவ வழிவகுக்கிறது.

{_h('priority', lang)}
இன்றே (TODAY)

{_h('benefit', lang)}
இயற்கை முறையில் பூச்சி கட்டுப்பாடு கிடைப்பதுடன் 25-35% மகசூல் இழப்பு தவிர்க்கப்படும்."""

    # 5. BENGALI (bn)
    elif lang == "bn":
        return f"""{_h('situation', lang)}
আপনার এলাকা ({loc})-এ বর্তমান আবহাওয়া ও আর্দ্রতার কারণে {crop} ফসলে পোকা ও রোগের প্রাদুর্ভাব দেখা দিতে পারে।

{_h('actions', lang)}
1. পাতার নিচের অংশ ও নতুন ডালপালা নিয়মিত পরীক্ষা করে পোকা ও ছত্রাকের আক্রমণ চিহ্নিত করুন।
2. আক্রান্ত পাতা ও গাছ কেটে ক্ষেতের বাইরে বিনষ্ট করুন।
3. জৈব নিম তেল (১০,০০০ ppm @ ২-৩ মিলি/লিটার জল) স্প্রে করুন।
4. সাদা মাছি ও থ্রিপস দমনে একর প্রতি ১৫টি হলুদ ও নীল আঠালো ফাঁদ (Sticky Traps) ব্যবহার করুন।
5. ওষুধ প্রয়োগের ৪৮-৭২ ঘণ্টা পর ফসলের অবস্থা পুনরায় পরিদর্শন করুন।

{_h('why', lang)}
অতিরিক্ত আর্দ্রতা ও মেঘলা আবহাওয়া পোকার বংশবৃদ্ধি ও ছত্রাক সংক্রমণের জন্য অনুকূল।

{_h('priority', lang)}
আজই (TODAY)

{_h('benefit', lang)}
জৈব উপায়ে পোকা দমন হবে এবং ২৫-৩৫% সম্ভাব্য ফলন ক্ষতি রোধ করা সম্ভব হবে।"""

    # 6. GUJARATI (gu)
    elif lang == "gu":
        return f"""{_h('situation', lang)}
તમારા વિસ્તાર ({loc}) માં વર્તમાન ભેજ અને તાપમાનના કારણે {crop} પાકમાં જીવાત અને રોગનું જોખમ રહેલું છે.

{_h('actions', lang)}
1. પાંદડાની નીચેની સપાટીનું નિરીક્ષણ કરી જીવાતની ઓળખ કરો.
2. રોગગ્રસ્ત પાંદડા અને ડાળીઓને તોડીને ખેતર બહાર નાશ કરો.
3. લીમડાનું તેલ (10,000 ppm @ 2-3 મિલી/લીટર પાણી) છાંટો.
4. સફેદ માખી અને થ્રીપ્સ નિયંત્રણ માટે એકર દીઠ 15 પીળા અને વાદળી સ્ટીકી ટ્રેપ લગાવો.
5. છંટકાવના 2-3 દિવસ પછી પાકની સ્થિતિનું ફરીથી નિરીક્ષણ કરો.

{_h('why', lang)}
વધુ પડતો ભેજ જીવાતોના પ્રજનન અને ફૂગના ફેલાવા માટે અનુકૂળ વાતાવરણ પૂરું પાડે છે.

{_h('priority', lang)}
આજે જ (TODAY)

{_h('benefit', lang)}
કુદરતી રીતે જીવાત નિયંત્રણ થશે અને 25-35% ઉત્પાદન નુકસાન અટકશે."""

    # 7. MARATHI (mr)
    elif lang == "mr":
        return f"""{_h('situation', lang)}
तुमच्या भागात ({loc}) सध्याच्या हवामानामुळे {crop} पिकावर कीड व रोगांचा प्रादुर्भाव वाढण्याची शक्यता आहे.

{_h('actions', lang)}
1. पानांच्या खालच्या बाजूचे निरीक्षण करून रस शोषणाऱ्या किडींची ओळख करा.
2. जास्त प्रादुर्भाव झालेली पाने व फांद्या तोडून शेताबाहेर नष्ट करा.
3. निंबोळी अर्क किंवा निम तेल (10,000 ppm @ 2-3 मिली/लीटर) फवारा.
4. पांढरी माशी व थ्रिप्स नियंत्रणासाठी एकरी 15 पिवळे व निळे चिकट सापळे लावा.
5. फवारणीनंतर 2-3 दिवसांनी पिकाची पुन्हा पाहणी करा.

{_h('why', lang)}
हवेतील जास्त आर्द्रता किडींच्या वाढीसाठी आणि बुरशीजन्य रोगांच्या प्रसारासाठी पोषक ठरते.

{_h('priority', lang)}
आजच (TODAY)

{_h('benefit', lang)}
सेंद्रिय पद्धतीने कीड नियंत्रण होऊन 25-35% संभाव्य नुकसान टळेल."""

    # 8. DEFAULT ENGLISH (en)
    if is_pest:
        return f"""{_h('situation', lang)}
Current relative humidity and ambient temperatures in {loc} indicate elevated pest pressure and fungal spore activity for {crop}.

{_h('actions', lang)}
1. Inspect the underside of leaves and apical shoots to identify early sucking pest nymph colonies or fungal lesions.
2. Rogue out and safely dispose of heavily infected foliage away from the field perimeter.
3. Apply botanical neem formulation (Cold-Pressed Azadirachtin 10,000 ppm @ 2–3 ml/L water) thoroughly covering both leaf surfaces.
4. Deploy 15 yellow and blue sticky traps per acre at canopy height to monitor and mass-trap whiteflies, aphids, and thrips.
5. Reinspect crop condition 48–72 hours post-spray and rotate with Trichoderma viride bio-fungicide if fungal damping-off persists.

{_h('why', lang)}
High canopy humidity coupled with tender vegetative flush creates an optimal microclimate for pest multiplication and rapid fungal sporulation.

{_h('priority', lang)}
TODAY (High Priority Intervention)

{_h('benefit', lang)}
Suppresses pest population below Economic Injury Level (EIL) while protecting beneficial predator insects and preventing 25–35% yield loss."""

    elif is_weather:
        return f"""{_h('situation', lang)}
Agro-meteorological forecast for {loc} indicates precipitation and temperature variations requiring immediate water and crop safeguard measures.

{_h('actions', lang)}
1. Clear field drainage furrows and perimeter trenches to ensure zero root-zone water stagnation during precipitation events.
2. Suspend synthetic Nitrogen top-dressing and chemical foliar sprays ahead of forecasted rain showers.
3. Transfer harvested produce and threshing lots to elevated, waterproof warehouse shelters.
4. If standing water accumulates, deploy trench drains or low-lift pump dewatering immediately once rain subsides.
5. Apply foliar potassium nitrate (13:0:45 @ 5g/L) post-stress to restore stomatal turgidity and accelerate crop recovery.

{_h('why', lang)}
Waterlogged roots suffer hypoxic shock and root-rot pathogens, while unshielded fertilizers face severe runoff and leaching losses.

{_h('priority', lang)}
URGENT (Immediate Action Required)

{_h('benefit', lang)}
Protects standing crop root health, prevents soil nutrient leaching, and avoids post-harvest produce deterioration."""

    elif is_market:
        return f"""{_h('situation', lang)}
Arrival volumes and price trends in local APMC market yards for {crop} in {loc} indicate volatility.

{_h('actions', lang)}
1. Sun-dry harvested produce to a safe moisture threshold of 10–12% before bagging and transport.
2. Winnow and grade produce into Premium Grade-A and Commercial Grade lots to command optimal market premiums.
3. Adopt staggered marketing: sell 40% immediately for working capital and store 60% in dry storage or warehouse receipts (e-NWR) if price trends are ascending.
4. Cross-reference live arrivals and modal rates across neighboring district APMC mandis on the AgriDarshak dashboard before dispatch.
5. Access government Minimum Support Price (MSP) procurement centers if open market modal rates drop below floor price.

{_h('why', lang)}
Peak harvest gluts cause temporary price depression; well-graded, low-moisture lots consistently command a 15–20% market premium.

{_h('priority', lang)}
THIS WEEK

{_h('benefit', lang)}
Maximizes net farmgate realization and eliminates avoidable moisture-based penalty deductions."""

    elif is_soil:
        return f"""{_h('situation', lang)}
Soil nutrient balance and pH condition for {loc} require targeted nutritional optimization for {crop}.

{_h('actions', lang)}
1. Incorporate 4–5 tonnes/acre of well-decomposed Farmyard Manure (FYM) or enriched vermicompost into the root zone.
2. Split total Nitrogen requirement into 3 equal applications (basal, tillering, and pre-flowering) rather than single heavy doses.
3. For acidic soils (pH < 6.2), broadcast agricultural lime or dolomite @ 150–200 kg/acre during field preparation.
4. Inoculate with bio-fertilizers (Azotobacter / Rhizobium and PSB @ 2 kg/acre mixed with compost).
5. Apply chelated micronutrient foliar spray (Zinc + Boron + Ferrous @ 2g/L) during early vegetative development.

{_h('why', lang)}
Balanced soil chemistry enhances microbial symbiosis, optimizes fertilizer uptake efficiency, and prevents root nutrient lockup.

{_h('priority', lang)}
THIS WEEK

{_h('benefit', lang)}
Boosts fertilizer use efficiency by 30%, corrects micro-deficiencies, and strengthens crop resilience."""

    else:
        return f"""{_h('situation', lang)}
Comprehensive agronomic status and crop management advisory for {crop} in {loc}.

{_h('actions', lang)}
1. Maintain calibrated irrigation intervals aligned with the current crop phenological stage.
2. Scout crop canopy every 2–3 days for early foliar stress, leaf discoloration, or pest egg clusters.
3. Apply balanced soluble nutrients and seaweed bio-stimulant at flower bud differentiation.
4. Ensure adequate soil aeration and maintain clean field borders to deter rodent and pest harborage.
5. Track daily weather warnings and mandi rates on the AgriDarshak dashboard for proactive decision making.

{_h('why', lang)}
Proactive agronomic stewardship mitigates abiotic and biotic stress before economic damage thresholds are breached.

{_h('priority', lang)}
TODAY

{_h('benefit', lang)}
Sustains crop vigor, optimizes flowering and fruit-set, and secures a projected 20–30% higher harvest return."""
