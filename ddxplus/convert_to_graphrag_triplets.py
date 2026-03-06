"""
convert_to_graphrag_triplets.py
================================
Script chuyển đổi dữ liệu từ DDXPLUS (transfer.csv) sang định dạng triplet (Subject - Relation - Object)
phù hợp với mô hình GraphRAG.

Các mã E_x (evidence) và V_x (value) được thay thế bằng mô tả tiếng Anh đầy đủ
từ release_evidences.json và release_conditions.json.

Output: graphrag_triplets.csv
"""

import csv
import ast
import re
import os

# =============================================================================
# 1. NHÚNG NỘI DUNG INLINE CỦA release_evidences.json
#    (Chỉ trích các trường cần thiết: question_en và value_meaning)
# =============================================================================

EVIDENCES = {
    "E_0": {"question_en": "Have you recently had a viral infection?", "value_meaning": {}, "data_type": "binary"},
    "E_1": {"question_en": "Are you currently being treated or have you recently been treated with an oral antibiotic for an ear infection?", "value_meaning": {}, "data_type": "binary"},
    "E_2": {"question_en": "Are you infected with the human immunodeficiency virus (HIV)?", "value_meaning": {}, "data_type": "binary"},
    "E_3": {"question_en": "Have you ever had a pericarditis?", "value_meaning": {}, "data_type": "binary"},
    "E_4": {"question_en": "Have you or any member of your family ever had croup?", "value_meaning": {}, "data_type": "binary"},
    "E_5": {"question_en": "Have you ever had fluid in your lungs?", "value_meaning": {}, "data_type": "binary"},
    "E_6": {"question_en": "Do you have chronic pancreatitis?", "value_meaning": {}, "data_type": "binary"},
    "E_7": {"question_en": "Do you have a poor diet?", "value_meaning": {}, "data_type": "binary"},
    "E_8": {"question_en": "Do you currently undergo dialysis?", "value_meaning": {}, "data_type": "binary"},
    "E_9": {"question_en": "Do you have swollen or painful lymph nodes?", "value_meaning": {}, "data_type": "binary"},
    "E_10": {"question_en": "Are you currently taking or have you recently taken anti-inflammatory drugs (NSAIDs)?", "value_meaning": {}, "data_type": "binary"},
    "E_11": {"question_en": "Have you breastfed one of your children for more than 9 months?", "value_meaning": {}, "data_type": "binary"},
    "E_12": {"question_en": "Do you have a known severe food allergy?", "value_meaning": {}, "data_type": "binary"},
    "E_13": {"question_en": "Do you find that your symptoms have worsened over the last 2 weeks and that progressively less effort is required to cause the symptoms?", "value_meaning": {}, "data_type": "binary"},
    "E_14": {"question_en": "Do you have chest pain even at rest?", "value_meaning": {}, "data_type": "binary"},
    "E_15": {"question_en": "Have you started or taken any antipsychotic medication within the last 7 days?", "value_meaning": {}, "data_type": "binary"},
    "E_16": {"question_en": "Do you feel anxious?", "value_meaning": {}, "data_type": "binary"},
    "E_17": {"question_en": "Are you of Asian descent?", "value_meaning": {}, "data_type": "binary"},
    "E_18": {"question_en": "Do you have cystic fibrosis?", "value_meaning": {}, "data_type": "binary"},
    "E_19": {"question_en": "Have you been diagnosed with hyperthyroidism?", "value_meaning": {}, "data_type": "binary"},
    "E_20": {"question_en": "Do you have Rheumatoid Arthritis?", "value_meaning": {}, "data_type": "binary"},
    "E_21": {"question_en": "Have you ever had a spontaneous pneumothorax?", "value_meaning": {}, "data_type": "binary"},
    "E_22": {"question_en": "Do you have a known issue with one of your heart valves?", "value_meaning": {}, "data_type": "binary"},
    "E_23": {"question_en": "Do you ever temporarily stop breathing while you're asleep?", "value_meaning": {}, "data_type": "binary"},
    "E_24": {"question_en": "Have you ever had a diagnosis of anemia?", "value_meaning": {}, "data_type": "binary"},
    "E_25": {"question_en": "Have any of your family members been diagnosed with cluster headaches?", "value_meaning": {}, "data_type": "binary"},
    "E_26": {"question_en": "Do you have any family members who have been diagnosed with anemia?", "value_meaning": {}, "data_type": "binary"},
    "E_27": {"question_en": "Have you ever had a sexually transmitted infection?", "value_meaning": {}, "data_type": "binary"},
    "E_28": {"question_en": "Are there any members of your family who have been diagnosed myasthenia gravis?", "value_meaning": {}, "data_type": "binary"},
    "E_29": {"question_en": "Do any members of your immediate family have a psychiatric illness?", "value_meaning": {}, "data_type": "binary"},
    "E_30": {"question_en": "Do you feel your abdomen is bloated or distended (swollen due to pressure from inside)?", "value_meaning": {}, "data_type": "binary"},
    "E_31": {"question_en": "Do you have severe Chronic Obstructive Pulmonary Disease (COPD)?", "value_meaning": {}, "data_type": "binary"},
    "E_32": {"question_en": "Do you have a decrease in appetite?", "value_meaning": {}, "data_type": "binary"},
    "E_33": {"question_en": "Do you have pain that improves when you lean forward?", "value_meaning": {}, "data_type": "binary"},
    "E_34": {"question_en": "Do you have an active cancer?", "value_meaning": {}, "data_type": "binary"},
    "E_35": {"question_en": "Do you regularly drink coffee or tea?", "value_meaning": {}, "data_type": "binary"},
    "E_37": {"question_en": "Do you have metastatic cancer?", "value_meaning": {}, "data_type": "binary"},
    "E_38": {"question_en": "Do you have pain or weakness in your jaw?", "value_meaning": {}, "data_type": "binary"},
    "E_39": {"question_en": "Have you felt confused or disorientated lately?", "value_meaning": {}, "data_type": "binary"},
    "E_40": {"question_en": "Have you been in contact with someone who has had pertussis (whooping cough)?", "value_meaning": {}, "data_type": "binary"},
    "E_41": {"question_en": "Have you been in contact with a person with similar symptoms in the past 2 weeks?", "value_meaning": {}, "data_type": "binary"},
    "E_42": {"question_en": "Have you been in contact with or ate something that you have an allergy to?", "value_meaning": {}, "data_type": "binary"},
    "E_43": {"question_en": "Have you lost consciousness associated with violent and sustained muscle contractions or had an absence episode?", "value_meaning": {}, "data_type": "binary"},
    "E_44": {"question_en": "Do you take corticosteroids?", "value_meaning": {}, "data_type": "binary"},
    "E_45": {"question_en": "Have you been coughing up blood?", "value_meaning": {}, "data_type": "binary"},
    "E_46": {"question_en": "Have you had 2 or more asthma attacks in the past year?", "value_meaning": {}, "data_type": "binary"},
    "E_47": {"question_en": "Do you suffer from Crohn's disease or ulcerative colitis (UC)?", "value_meaning": {}, "data_type": "binary"},
    "E_48": {"question_en": "Do you live with 4 or more people?", "value_meaning": {}, "data_type": "binary"},
    "E_49": {"question_en": "Do you attend or work in a daycare?", "value_meaning": {}, "data_type": "binary"},
    "E_50": {"question_en": "Have you had significantly increased sweating?", "value_meaning": {}, "data_type": "binary"},
    "E_51": {"question_en": "Have you had diarrhea or an increase in stool frequency?", "value_meaning": {}, "data_type": "binary"},
    "E_52": {"question_en": "Do you have the perception of seeing two images of a single object seen overlapping or adjacent to each other (double vision)?", "value_meaning": {}, "data_type": "binary"},
    "E_53": {"question_en": "Do you have pain somewhere, related to your reason for consulting?", "value_meaning": {}, "data_type": "binary"},
    "E_54": {
        "question_en": "Characterize your pain:",
        "value_meaning": {
            "V_11": "NA", "V_71": "heartbreaking", "V_112": "haunting", "V_154": "tedious",
            "V_161": "sensitive", "V_179": "a knife stroke", "V_180": "tugging",
            "V_181": "burning", "V_182": "a cramp", "V_183": "heavy",
            "V_184": "a pulse", "V_191": "violent", "V_192": "sharp",
            "V_193": "sickening", "V_196": "scary", "V_198": "exhausting"
        },
        "data_type": "multi-choice"
    },
    "E_55": {
        "question_en": "Do you feel pain somewhere?",
        "value_meaning": {
            "V_123": "nowhere", "V_14": "iliac wing(R)", "V_15": "iliac wing(L)",
            "V_16": "groin(R)", "V_17": "groin(L)", "V_18": "axilla(R)", "V_19": "axilla(L)",
            "V_20": "tonsil(R)", "V_21": "tonsil(L)", "V_22": "anus",
            "V_25": "back of head", "V_26": "back of the neck",
            "V_29": "lower chest", "V_30": "biceps(R)", "V_31": "biceps(L)",
            "V_32": "mouth", "V_33": "thyroid cartilage", "V_34": "ankle(R)", "V_35": "ankle(L)",
            "V_36": "clitoris", "V_37": "coccyx", "V_38": "cervical spine",
            "V_39": "thoracic spine", "V_40": "lumbar spine",
            "V_41": "commissure(R)", "V_42": "commissure(L)",
            "V_43": "lateral side of the foot(R)", "V_44": "lateral side of the foot(L)",
            "V_45": "elbow(R)", "V_46": "elbow(L)",
            "V_47": "popliteal fossa(R)", "V_48": "popliteal fossa(L)",
            "V_49": "iliac crest(R)", "V_50": "iliac crest(L)",
            "V_51": "thigh(R)", "V_52": "thigh(L)",
            "V_53": "side of the neck(R)", "V_54": "side of the neck(L)",
            "V_55": "side of the chest(R)", "V_56": "side of the chest(L)",
            "V_57": "lower teeth(R)", "V_58": "lower teeth(L)",
            "V_59": "upper teeth(R)", "V_60": "upper teeth(L)",
            "V_61": "above the tongue", "V_62": "top of the head",
            "V_63": "finger (ring finger)(R)", "V_64": "finger (ring finger)(L)",
            "V_65": "finger (little finger)(R)", "V_66": "finger (little finger)(L)",
            "V_67": "finger (index)(R)", "V_68": "finger (index)(L)",
            "V_69": "finger (middle)(R)", "V_70": "finger (middle)(L)",
            "V_72": "dorsal aspect of the foot(R)", "V_73": "dorsal aspect of the foot(L)",
            "V_74": "dorsal aspect of the wrist(R)", "V_75": "dorsal aspect of the wrist(L)",
            "V_76": "dorsal aspect of the hand(R)", "V_77": "dorsal aspect of the hand(L)",
            "V_78": "palmar side of the forearm(R)", "V_79": "palmar side of the forearm(L)",
            "V_80": "palmar face of the wrist(R)", "V_81": "palmar face of the wrist(L)",
            "V_82": "buttock(R)", "V_83": "buttock(L)",
            "V_84": "flank(R)", "V_85": "flank(L)",
            "V_87": "iliac fossa(R)", "V_88": "iliac fossa(L)",
            "V_89": "forehead",
            "V_90": "lower gum", "V_91": "upper gum",
            "V_92": "knee(R)", "V_93": "knee(L)",
            "V_94": "glans", "V_95": "labia majora(R)", "V_96": "labia majora(L)",
            "V_97": "big toe(R)", "V_98": "big toe(L)",
            "V_99": "hip(R)", "V_100": "hip(L)",
            "V_101": "upper chest", "V_102": "hymen",
            "V_103": "hypochondrium(R)", "V_104": "hypochondrium(L)",
            "V_105": "ischio jambier(R)", "V_106": "ischio jambier(L)",
            "V_108": "cheek(R)", "V_109": "cheek(L)",
            "V_110": "internal cheek(R)", "V_111": "internal cheek(L)",
            "V_113": "renal fossa(R)", "V_114": "renal fossa(L)",
            "V_115": "uvula", "V_116": "bottom lip(R)", "V_117": "upper lip(R)",
            "V_118": "chin", "V_119": "calf(R)", "V_120": "calf(L)",
            "V_121": "jaw", "V_122": "nose",
            "V_124": "occiput", "V_125": "eye(R)", "V_126": "eye(L)",
            "V_127": "scapula(R)", "V_128": "scapula(L)",
            "V_129": "ear(R)", "V_130": "ear(L)",
            "V_131": "toe (1)(R)", "V_132": "toe (1)(L)",
            "V_133": "toe (2)(R)", "V_134": "toe (2)(L)",
            "V_135": "toe (3)(R)", "V_136": "toe (3)(L)",
            "V_137": "palace",
            "V_139": "vaginal wall", "V_140":"vaginal wall(R)", "V_141": "vaginal wall(L)",
            "V_142": "palm(R)", "V_143": "palm(L)",
            "V_144": "little toe (4)(R)", "V_145": "little toe (4)(L)",
            "V_146": "labia minora(R)", "V_147": "labia minora(L)",
            "V_148": "pharynx",
            "V_149": "sole(R)", "V_150": "sole(L)",
            "V_151": "thumb(R)", "V_152": "thumb(L)",
            "V_153": "pubis", "V_155": "penis",
            "V_158": "scrotum",
            "V_159": "breast(R)", "V_160": "breast(L)",
            "V_162": "under the tongue", "V_163": "under the jaw",
            "V_164": "heel(R)", "V_165": "heel(L)",
            "V_166": "temple(R)", "V_167": "temple(L)",
            "V_168": "testicle(R)", "V_169": "testicle(L)",
            "V_170": "posterior chest wall(R)", "V_171": "posterior chest wall(L)",
            "V_172": "tibia(R)", "V_173": "tibia(L)",
            "V_174": "trachea",
            "V_175": "trapezius(R)", "V_176": "trapezius(L)",
            "V_177": "triceps(R)", "V_178": "triceps(L)",
            "V_185": "urethra", "V_186": "vagina", "V_187": "belly",
            "V_188": "vermilion(R)", "V_189": "vermilion(L)",
            "V_190": "vulval vestibule",
            "V_194": "shoulder(R)", "V_195": "shoulder(L)", "V_197": "epigastric"
        },
        "data_type": "multi-choice"
    },
    "E_56": {"question_en": "How intense is the pain? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_57": {
        "question_en": "Does the pain radiate to another location?",
        "value_meaning": {},  # Same mapping as E_55
        "data_type": "multi-choice"
    },
    "E_58": {"question_en": "How precisely is the pain located? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_59": {"question_en": "How fast did the pain appear? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_60": {"question_en": "Do you consume energy drinks regularly?", "value_meaning": {}, "data_type": "binary"},
    "E_61": {"question_en": "Are you currently using intravenous drugs?", "value_meaning": {}, "data_type": "binary"},
    "E_62": {"question_en": "Do you regularly take stimulant drugs?", "value_meaning": {}, "data_type": "binary"},
    "E_63": {"question_en": "Do you have difficulty articulating words/speaking?", "value_meaning": {}, "data_type": "binary"},
    "E_64": {"question_en": "Do you feel out of breath with minimal physical effort?", "value_meaning": {}, "data_type": "binary"},
    "E_65": {"question_en": "Do you have difficulty swallowing, or have a feeling of discomfort/blockage when swallowing?", "value_meaning": {}, "data_type": "binary"},
    "E_66": {"question_en": "Are you experiencing shortness of breath or difficulty breathing in a significant way?", "value_meaning": {}, "data_type": "binary"},
    "E_67": {"question_en": "Do you have bouts of choking or shortness of breath that wake you up at night?", "value_meaning": {}, "data_type": "binary"},
    "E_69": {"question_en": "Do you have diabetes?", "value_meaning": {}, "data_type": "binary"},
    "E_70": {"question_en": "Are you significantly overweight compared to people of the same height as you?", "value_meaning": {}, "data_type": "binary"},
    "E_71": {"question_en": "Do you have high cholesterol or do you take medications to treat high cholesterol?", "value_meaning": {}, "data_type": "binary"},
    "E_72": {"question_en": "Have you had one or several flare ups of chronic obstructive pulmonary disease (COPD) in the past year?", "value_meaning": {}, "data_type": "binary"},
    "E_73": {"question_en": "In the last month, have you been in contact with anyone infected with the Ebola virus?", "value_meaning": {}, "data_type": "binary"},
    "E_74": {"question_en": "Have you noticed a diffuse (widespread) redness in one or both eyes?", "value_meaning": {}, "data_type": "binary"},
    "E_75": {"question_en": "Do you feel like you are (or were) choking or suffocating?", "value_meaning": {}, "data_type": "binary"},
    "E_76": {"question_en": "Do you feel slightly dizzy or lightheaded?", "value_meaning": {}, "data_type": "binary"},
    "E_77": {"question_en": "Do you have a cough that produces colored or more abundant sputum than usual?", "value_meaning": {}, "data_type": "binary"},
    "E_78": {"question_en": "Do you drink alcohol excessively or do you have an addiction to alcohol?", "value_meaning": {}, "data_type": "binary"},
    "E_79": {"question_en": "Do you smoke cigarettes?", "value_meaning": {}, "data_type": "binary"},
    "E_80": {"question_en": "Have you ever been diagnosed with depression?", "value_meaning": {}, "data_type": "binary"},
    "E_81": {"question_en": "Do you suffer from chronic anxiety?", "value_meaning": {}, "data_type": "binary"},
    "E_82": {"question_en": "Do you feel lightheaded and dizzy or do you feel like you are about to faint?", "value_meaning": {}, "data_type": "binary"},
    "E_83": {"question_en": "Have you noticed weakness in your facial muscles and/or eyes?", "value_meaning": {}, "data_type": "binary"},
    "E_84": {"question_en": "Do you feel weakness in both arms and/or both legs?", "value_meaning": {}, "data_type": "binary"},
    "E_86": {"question_en": "Do you have any close family members who suffer from allergies (any type), hay fever or eczema?", "value_meaning": {}, "data_type": "binary"},
    "E_87": {"question_en": "Do you have any family members who have asthma?", "value_meaning": {}, "data_type": "binary"},
    "E_88": {"question_en": "Do you feel so tired that you are unable to do your usual activities or are you stuck in your bed all day long?", "value_meaning": {}, "data_type": "binary"},
    "E_89": {"question_en": "Do you constantly feel fatigued or do you have non-restful sleep?", "value_meaning": {}, "data_type": "binary"},
    "E_90": {"question_en": "Do your symptoms of muscle weakness increase with fatigue and/or stress?", "value_meaning": {}, "data_type": "binary"},
    "E_91": {"question_en": "Do you have a fever (either felt or measured with a thermometer)?", "value_meaning": {}, "data_type": "binary"},
    "E_92": {"question_en": "Did your cheeks suddenly turn red?", "value_meaning": {}, "data_type": "binary"},
    "E_93": {"question_en": "Do you have numbness, loss of sensation or tingling in the feet?", "value_meaning": {}, "data_type": "binary"},
    "E_94": {"question_en": "Have you had chills or shivers?", "value_meaning": {}, "data_type": "binary"},
    "E_95": {"question_en": "Do you have Parkinson's disease?", "value_meaning": {}, "data_type": "binary"},
    "E_96": {"question_en": "Have you gained weight recently?", "value_meaning": {}, "data_type": "binary"},
    "E_97": {"question_en": "Do you have a sore throat?", "value_meaning": {}, "data_type": "binary"},
    "E_98": {"question_en": "Do you have a hiatal hernia?", "value_meaning": {}, "data_type": "binary"},
    "E_99": {"question_en": "Have you ever had a migraine or is a member of your family known to have migraines?", "value_meaning": {}, "data_type": "binary"},
    "E_100": {"question_en": "Do you currently take hormones?", "value_meaning": {}, "data_type": "binary"},
    "E_101": {"question_en": "Have you been hospitalized for an asthma attack in the past year?", "value_meaning": {}, "data_type": "binary"},
    "E_102": {"question_en": "Are you consulting because you have high blood pressure?", "value_meaning": {}, "data_type": "binary"},
    "E_103": {"question_en": "Have you lost your sense of smell?", "value_meaning": {}, "data_type": "binary"},
    "E_104": {"question_en": "Do you have high blood pressure or do you take medications to treat high blood pressure?", "value_meaning": {}, "data_type": "binary"},
    "E_105": {"question_en": "Have you ever had a heart attack or do you have angina (chest pain)?", "value_meaning": {}, "data_type": "binary"},
    "E_106": {"question_en": "Do you have heart failure?", "value_meaning": {}, "data_type": "binary"},
    "E_107": {"question_en": "Have you ever had a stroke?", "value_meaning": {}, "data_type": "binary"},
    "E_108": {"question_en": "Do you have a problem with poor circulation?", "value_meaning": {}, "data_type": "binary"},
    "E_109": {"question_en": "Have you ever had deep vein thrombosis (DVT)?", "value_meaning": {}, "data_type": "binary"},
    "E_110": {"question_en": "Have you been unable to move or get up for more than 3 consecutive days within the last 4 weeks?", "value_meaning": {}, "data_type": "binary"},
    "E_111": {"question_en": "Do you feel like you are dying or were you afraid that you were about do die?", "value_meaning": {}, "data_type": "binary"},
    "E_112": {"question_en": "Do you wheeze while inhaling or is your breathing noisy after coughing spells?", "value_meaning": {}, "data_type": "binary"},
    "E_113": {"question_en": "Do you have chronic kidney failure?", "value_meaning": {}, "data_type": "binary"},
    "E_114": {"question_en": "Are you more irritable or has your mood been very unstable recently?", "value_meaning": {}, "data_type": "binary"},
    "E_115": {"question_en": "Have you had unprotected sex with more than one partner in the last 6 months?", "value_meaning": {}, "data_type": "binary"},
    "E_116": {"question_en": "Have you had a cold in the last 2 weeks?", "value_meaning": {}, "data_type": "binary"},
    "E_118": {"question_en": "Have you ever had pneumonia?", "value_meaning": {}, "data_type": "binary"},
    "E_119": {"question_en": "Have you been diagnosed with chronic sinusitis?", "value_meaning": {}, "data_type": "binary"},
    "E_120": {"question_en": "Do you have polyps in your nose?", "value_meaning": {}, "data_type": "binary"},
    "E_121": {"question_en": "Do you have a deviated nasal septum?", "value_meaning": {}, "data_type": "binary"},
    "E_122": {"question_en": "Do you have a chronic obstructive pulmonary disease (COPD)?", "value_meaning": {}, "data_type": "binary"},
    "E_123": {"question_en": "Do you have a chronic obstructive pulmonary disease (COPD)?", "value_meaning": {}, "data_type": "binary"},
    "E_124": {"question_en": "Do you have asthma or have you ever had to use a bronchodilator in the past?", "value_meaning": {}, "data_type": "binary"},
    "E_125": {"question_en": "Have you ever been diagnosed with gastroesophageal reflux?", "value_meaning": {}, "data_type": "binary"},
    "E_126": {"question_en": "Do you have liver cirrhosis?", "value_meaning": {}, "data_type": "binary"},
    "E_127": {"question_en": "Do you feel that your eyes produce excessive tears?", "value_meaning": {}, "data_type": "binary"},
    "E_128": {"question_en": "Have you ever felt like you were suffocating for a very short time associated with inability to breathe or speak?", "value_meaning": {}, "data_type": "binary"},
    "E_129": {"question_en": "Do you have any lesions, redness or problems on your skin that you believe are related to the condition you are consulting for?", "value_meaning": {}, "data_type": "binary"},
    "E_130": {
        "question_en": "What color is the rash?",
        "value_meaning": {
            "V_11": "NA", "V_86": "dark", "V_107": "yellow",
            "V_138": "pale", "V_156": "pink", "V_157": "red"
        },
        "data_type": "categorical"
    },
    "E_131": {
        "question_en": "Do your lesions peel off?",
        "value_meaning": {"V_10": "No", "V_12": "Yes"},
        "data_type": "categorical"
    },
    "E_132": {"question_en": "Is the rash swollen? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_133": {
        "question_en": "Where is the affected region located?",
        "value_meaning": {},  # Reuse E_55 map at runtime
        "data_type": "multi-choice"
    },
    "E_134": {"question_en": "How intense is the pain caused by the rash? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_135": {
        "question_en": "Is the lesion (or are the lesions) larger than 1cm?",
        "value_meaning": {"V_10": "No", "V_12": "Yes"},
        "data_type": "categorical"
    },
    "E_136": {"question_en": "How severe is the itching? (scale 0-10)", "value_meaning": {}, "data_type": "categorical"},
    "E_137": {"question_en": "Have you ever had surgery to remove lymph nodes?", "value_meaning": {}, "data_type": "binary"},
    "E_138": {"question_en": "Do you suffer from fibromyalgia?", "value_meaning": {}, "data_type": "binary"},
    "E_139": {"question_en": "Do you have a known heart defect?", "value_meaning": {}, "data_type": "binary"},
    "E_140": {"question_en": "Have you recently had stools that were black (like coal)?", "value_meaning": {}, "data_type": "binary"},
    "E_141": {"question_en": "Did you have your first menstrual period before the age of 12?", "value_meaning": {}, "data_type": "binary"},
    "E_142": {"question_en": "Does your mother suffer from asthma?", "value_meaning": {}, "data_type": "binary"},
    "E_143": {"question_en": "Do you exercise regularly, 4 times per week or more?", "value_meaning": {}, "data_type": "binary"},
    "E_144": {"question_en": "Do you have diffuse (widespread) muscle pain?", "value_meaning": {}, "data_type": "binary"},
    "E_145": {"question_en": "Do you have very abundant or very long menstruation periods?", "value_meaning": {}, "data_type": "binary"},
    "E_146": {"question_en": "Are you taking any new oral anticoagulants (NOACs)?", "value_meaning": {}, "data_type": "binary"},
    "E_147": {"question_en": "Have you been treated in hospital recently for nausea, agitation, intoxication or aggressive behavior and received medication via an intravenous or intramuscular route?", "value_meaning": {}, "data_type": "binary"},
    "E_148": {"question_en": "Are you feeling nauseous or do you feel like vomiting?", "value_meaning": {}, "data_type": "binary"},
    "E_149": {"question_en": "Do you take a calcium channel blockers (medication)?", "value_meaning": {}, "data_type": "binary"},
    "E_150": {"question_en": "Have you been able to pass stools or gas since your symptoms increased?", "value_meaning": {}, "data_type": "binary"},
    "E_151": {"question_en": "Do you have swelling in one or more areas of your body?", "value_meaning": {}, "data_type": "binary"},
    "E_152": {
        "question_en": "Where is the swelling located?",
        "value_meaning": {},  # Reuse E_55 map at runtime
        "data_type": "multi-choice"
    },
    "E_153": {"question_en": "Are you being treated for osteoporosis?", "value_meaning": {}, "data_type": "binary"},
    "E_154": {"question_en": "Is your skin much paler than usual?", "value_meaning": {}, "data_type": "binary"},
    "E_155": {"question_en": "Do you feel your heart is beating fast (racing), irregularly (missing a beat) or do you feel palpitations?", "value_meaning": {}, "data_type": "binary"},
    "E_156": {"question_en": "Have you had weakness or paralysis on one side of the face, which may still be present or completely resolved?", "value_meaning": {}, "data_type": "binary"},
    "E_157": {"question_en": "Have you recently had numbness, loss of sensation or tingling, in both arms and legs and around your mouth?", "value_meaning": {}, "data_type": "binary"},
    "E_158": {"question_en": "Were you diagnosed with endocrine disease or a hormone dysfunction?", "value_meaning": {}, "data_type": "binary"},
    "E_159": {"question_en": "Did you lose consciousness?", "value_meaning": {}, "data_type": "binary"},
    "E_160": {"question_en": "Were you born prematurely or did you suffer any complication at birth?", "value_meaning": {}, "data_type": "binary"},
    "E_161": {"question_en": "Have you recently had a loss of appetite or do you get full more quickly then usually?", "value_meaning": {}, "data_type": "binary"},
    "E_162": {"question_en": "Have you had an involuntary weight loss over the last 3 months?", "value_meaning": {}, "data_type": "binary"},
    "E_163": {"question_en": "Have you had any vaginal discharge?", "value_meaning": {}, "data_type": "binary"},
    "E_164": {"question_en": "Do you feel your heart is beating very irregularly or in a disorganized pattern?", "value_meaning": {}, "data_type": "binary"},
    "E_165": {"question_en": "Have any of your family members ever had a pneumothorax?", "value_meaning": {}, "data_type": "binary"},
    "E_166": {"question_en": "Did you vomit after coughing?", "value_meaning": {}, "data_type": "binary"},
    "E_167": {"question_en": "Do you think you are pregnant or are you currently pregnant?", "value_meaning": {}, "data_type": "binary"},
    "E_168": {"question_en": "Do you have trouble keeping your tongue in your mouth?", "value_meaning": {}, "data_type": "binary"},
    "E_169": {"question_en": "Is your nose or the back of your throat itchy?", "value_meaning": {}, "data_type": "binary"},
    "E_170": {"question_en": "Do you have severe itching in one or both eyes?", "value_meaning": {}, "data_type": "binary"},
    "E_171": {"question_en": "Do you feel like you are detached from your own body or your surroundings?", "value_meaning": {}, "data_type": "binary"},
    "E_172": {"question_en": "Do you have a hard time opening/raising one or both eyelids?", "value_meaning": {}, "data_type": "binary"},
    "E_173": {"question_en": "Do you have a burning sensation that starts in your stomach then goes up into your throat, and can be associated with a bitter taste in your mouth?", "value_meaning": {}, "data_type": "binary"},
    "E_174": {"question_en": "Have you been unintentionally losing weight or have you lost your appetite?", "value_meaning": {}, "data_type": "binary"},
    "E_175": {"question_en": "Have you noticed any new fatigue, generalized and vague discomfort, diffuse (widespread) muscle aches or a change in your general well-being related to your consultation today?", "value_meaning": {}, "data_type": "binary"},
    "E_176": {"question_en": "Did you previously, or do you currently, have any weakness/paralysis in one or more of your limbs or in your face?", "value_meaning": {}, "data_type": "binary"},
    "E_177": {"question_en": "Do you currently, or did you ever, have numbness, loss of sensitivity or tingling anywhere on your body?", "value_meaning": {}, "data_type": "binary"},
    "E_178": {"question_en": "Have you noticed any unusual bleeding or bruising related to your consultation today?", "value_meaning": {}, "data_type": "binary"},
    "E_179": {"question_en": "Have you noticed light red blood or blood clots in your stool?", "value_meaning": {}, "data_type": "binary"},
    "E_180": {"question_en": "Are you unable to control the direction of your eyes?", "value_meaning": {}, "data_type": "binary"},
    "E_181": {"question_en": "Do you have nasal congestion or a clear runny nose?", "value_meaning": {}, "data_type": "binary"},
    "E_182": {"question_en": "Do you have greenish or yellowish nasal discharge?", "value_meaning": {}, "data_type": "binary"},
    "E_183": {"question_en": "Do you live in a rural area?", "value_meaning": {}, "data_type": "binary"},
    "E_184": {"question_en": "Do you take medication that dilates your blood vessels?", "value_meaning": {}, "data_type": "binary"},
    "E_185": {"question_en": "Have you ever had a head trauma?", "value_meaning": {}, "data_type": "binary"},
    "E_186": {"question_en": "Have you ever been diagnosed with obstructive sleep apnea (OSA)?", "value_meaning": {}, "data_type": "binary"},
    "E_187": {"question_en": "Did you eat dark-fleshed fish (such as tuna) or Swiss cheese before the reaction occurred?", "value_meaning": {}, "data_type": "binary"},
    "E_188": {"question_en": "Do you have pale stools and dark urine?", "value_meaning": {}, "data_type": "binary"},
    "E_189": {"question_en": "Have you had sexual intercourse with an HIV-positive partner in the past 12 months?", "value_meaning": {}, "data_type": "binary"},
    "E_190": {"question_en": "Have you noticed that you produce more saliva than usual?", "value_meaning": {}, "data_type": "binary"},
    "E_191": {"question_en": "Are you a former smoker?", "value_meaning": {}, "data_type": "binary"},
    "E_192": {"question_en": "Do you feel that muscle spasms or soreness in your neck are keeping you from turning your head to one side?", "value_meaning": {}, "data_type": "binary"},
    "E_193": {"question_en": "Do you have annoying muscle spasms in your face, neck or any other part of your body?", "value_meaning": {}, "data_type": "binary"},
    "E_194": {"question_en": "Have you noticed a high pitched sound when breathing in?", "value_meaning": {}, "data_type": "binary"},
    "E_195": {"question_en": "Do you live in the suburbs?", "value_meaning": {}, "data_type": "binary"},
    "E_196": {"question_en": "Have you had surgery within the last month?", "value_meaning": {}, "data_type": "binary"},
    "E_197": {"question_en": "Do you have a known kidney problem resulting in an inability to retain proteins?", "value_meaning": {}, "data_type": "binary"},
    "E_198": {"question_en": "Do you work in agriculture?", "value_meaning": {}, "data_type": "binary"},
    "E_199": {"question_en": "Do you work in construction?", "value_meaning": {}, "data_type": "binary"},
    "E_200": {"question_en": "Do you work in the mining sector?", "value_meaning": {}, "data_type": "binary"},
    "E_201": {"question_en": "Do you have a cough?", "value_meaning": {}, "data_type": "binary"},
    "E_202": {"question_en": "Does the person have a whooping cough?", "value_meaning": {}, "data_type": "binary"},
    "E_203": {"question_en": "Do you have intense coughing fits?", "value_meaning": {}, "data_type": "binary"},
    "E_204": {
        "question_en": "Have you traveled out of the country in the last 4 weeks?",
        "value_meaning": {
            "V_10": "No", "V_0": "North Africa", "V_1": "West Africa",
            "V_2": "South Africa", "V_3": "Central America", "V_4": "North America",
            "V_5": "South America", "V_6": "Asia", "V_7": "South East Asia",
            "V_8": "Caraibes", "V_9": "Europe", "V_13": "Oceania"
        },
        "data_type": "categorical"
    },
    "E_205": {"question_en": "Do you suddenly have difficulty or an inability to open your mouth or have jaw pain when opening it?", "value_meaning": {}, "data_type": "binary"},
    "E_206": {"question_en": "Do you have painful mouth ulcers or sores?", "value_meaning": {}, "data_type": "binary"},
    "E_207": {"question_en": "Do you live in in a big city?", "value_meaning": {}, "data_type": "binary"},
    "E_208": {"question_en": "Is your BMI less than 18.5, or are you underweight?", "value_meaning": {}, "data_type": "binary"},
    "E_209": {"question_en": "Are your vaccinations up to date?", "value_meaning": {}, "data_type": "binary"},
    "E_210": {"question_en": "Have you recently thrown up blood or something resembling coffee beans?", "value_meaning": {}, "data_type": "binary"},
    "E_211": {"question_en": "Have you vomited several times or have you made several efforts to vomit?", "value_meaning": {}, "data_type": "binary"},
    "E_212": {"question_en": "Have you noticed that the tone of your voice has become deeper, softer or hoarse?", "value_meaning": {}, "data_type": "binary"},
    "E_213": {"question_en": "Have you recently taken decongestants or other substances that may have stimulant effects?", "value_meaning": {}, "data_type": "binary"},
    "E_214": {"question_en": "Have you noticed a wheezing sound when you exhale?", "value_meaning": {}, "data_type": "binary"},
    "E_215": {"question_en": "Do you have symptoms that get worse after eating?", "value_meaning": {}, "data_type": "binary"},
    "E_216": {"question_en": "Do you have pain that is increased with movement?", "value_meaning": {}, "data_type": "binary"},
    "E_217": {"question_en": "Are your symptoms worse when lying down and alleviated while sitting up?", "value_meaning": {}, "data_type": "binary"},
    "E_218": {"question_en": "Do you have symptoms that are increased with physical exertion but alleviated with rest?", "value_meaning": {}, "data_type": "binary"},
    "E_219": {"question_en": "Are your symptoms more prominent at night?", "value_meaning": {}, "data_type": "binary"},
    "E_220": {"question_en": "Do you have pain that is increased when you breathe in deeply?", "value_meaning": {}, "data_type": "binary"},
    "E_221": {"question_en": "Are the symptoms or pain increased with coughing, with an effort like lifting a weight or from forcing a bowel movement?", "value_meaning": {}, "data_type": "binary"},
    "E_222": {"question_en": "Are you exposed to secondhand cigarette smoke on a daily basis?", "value_meaning": {}, "data_type": "binary"},
    "E_223": {"question_en": "Are there members of your family who have been diagnosed with pancreatic cancer?", "value_meaning": {}, "data_type": "binary"},
    "E_224": {"question_en": "Do you have family members who have had lung cancer?", "value_meaning": {}, "data_type": "binary"},
    "E_225": {"question_en": "Do you have close family members who had a cardiovascular disease problem before the age of 50?", "value_meaning": {}, "data_type": "binary"},
    "E_226": {"question_en": "Are you more likely to develop common allergies than the general population?", "value_meaning": {}, "data_type": "binary"},
    "E_227": {"question_en": "Are you immunosuppressed?", "value_meaning": {}, "data_type": "binary"},
}

# E_57 và E_133, E_152 dùng cùng bảng mapping vị trí như E_55
LOCATION_MAP = EVIDENCES["E_55"]["value_meaning"]
EVIDENCES["E_57"]["value_meaning"] = LOCATION_MAP
EVIDENCES["E_133"]["value_meaning"] = LOCATION_MAP
EVIDENCES["E_152"]["value_meaning"] = LOCATION_MAP

# =============================================================================
# 2. NHÚNG NỘI DUNG INLINE CỦA release_conditions.json (tên bệnh)
# =============================================================================

CONDITIONS = {
    "Spontaneous pneumothorax": "Spontaneous pneumothorax",
    "Cluster headache": "Cluster headache",
    "Boerhaave": "Boerhaave syndrome",
    "Spontaneous rib fracture": "Spontaneous rib fracture",
    "GERD": "Gastroesophageal Reflux Disease (GERD)",
    "HIV (initial infection)": "HIV - initial infection",
    "Anemia": "Anemia",
    "Viral pharyngitis": "Viral pharyngitis",
    "Inguinal hernia": "Inguinal hernia",
    "Myasthenia gravis": "Myasthenia gravis",
    "Whooping cough": "Whooping cough (Pertussis)",
    "Anaphylaxis": "Anaphylaxis",
    "Epiglottitis": "Epiglottitis",
    "Guillain-Barré syndrome": "Guillain-Barré syndrome",
    "Acute laryngitis": "Acute laryngitis",
    "Croup": "Croup (Laryngo-tracheo-bronchitis)",
    "PSVT": "Paroxysmal Supraventricular Tachycardia (PSVT)",
    "Atrial fibrillation": "Atrial fibrillation / Flutter",
    "Bronchiectasis": "Bronchiectasis",
    "Allergic sinusitis": "Allergic sinusitis (Allergic rhinitis)",
    "Chagas": "Chagas disease",
    "Scombroid food poisoning": "Scombroid food poisoning",
    "Myocarditis": "Myocarditis",
    "Larygospasm": "Laryngospasm",
    "Acute dystonic reactions": "Acute dystonic reactions",
    "Localized edema": "Localized or generalized edema",
    "SLE": "Systemic Lupus Erythematosus (SLE)",
    "Tuberculosis": "Tuberculosis",
    "Unstable angina": "Unstable angina",
    "Stable angina": "Stable angina",
    "Ebola": "Ebola virus disease",
    "Acute otitis media": "Acute otitis media",
    "Panic attack": "Panic attack",
    "Bronchospasm / acute asthma exacerbation": "Bronchospasm / acute asthma exacerbation",
    "Bronchitis": "Bronchitis",
    "Acute COPD exacerbation / infection": "Acute COPD exacerbation / infection",
    "Pulmonary embolism": "Pulmonary embolism",
    "URTI": "Upper Respiratory Tract Infection (URTI)",
    "Influenza": "Influenza",
    "Pneumonia": "Pneumonia",
    "Acute rhinosinusitis": "Acute rhinosinusitis",
    "Chronic rhinosinusitis": "Chronic rhinosinusitis",
    "Bronchiolitis": "Bronchiolitis",
    "Pulmonary neoplasm": "Pulmonary neoplasm (lung cancer)",
    "Possible NSTEMI / STEMI": "Possible NSTEMI / STEMI (heart attack)",
    "Sarcoidosis": "Sarcoidosis",
    "Pancreatic neoplasm": "Pancreatic neoplasm (pancreatic cancer)",
    "Acute pulmonary edema": "Acute pulmonary edema",
    "Pericarditis": "Pericarditis",
}


# =============================================================================
# 3. HÀM HELPER
# =============================================================================

def get_evidence_description(evidence_token: str) -> str:
    """
    Chuyển đổi mã evidence token (ví dụ: 'E_53', 'E_54_@_V_112', 'E_56_@_6') 
    thành mô tả tiếng Anh đầy đủ.

    Định dạng token:
    - Đơn: 'E_53'           -> câu hỏi của E_53
    - Phức hợp: 'E_54_@_V_112'  -> câu hỏi E_54, giá trị V_112
    - Số:  'E_56_@_6'       -> câu hỏi E_56, giá trị thang điểm = 6
    """
    if "_@_" in evidence_token:
        parts = evidence_token.split("_@_", 1)
        e_code = parts[0]          # e.g. "E_54"
        v_raw  = parts[1]          # e.g. "V_112" hoặc "6"
    else:
        e_code = evidence_token
        v_raw  = None

    info = EVIDENCES.get(e_code)
    if info is None:
        # Không có trong từ điển, trả về nguyên mã
        return evidence_token

    question = info["question_en"]

    if v_raw is None:
        # Triệu chứng nhị phân (Boolean) - chỉ trả về câu hỏi
        return question

    # Có giá trị đính kèm
    value_meaning = info.get("value_meaning", {})

    if v_raw in value_meaning:
        val_desc = value_meaning[v_raw]
        return f"{question} [Answer: {val_desc}]"
    else:
        # Giá trị số (thang điểm C)
        return f"{question} [Value: {v_raw}]"


def get_condition_name(code: str) -> str:
    """Trả về tên đầy đủ của bệnh, dùng từ điển CONDITIONS."""
    return CONDITIONS.get(code, code)


def parse_evidence_list(raw: str) -> list:
    """Parse cột EVIDENCES từ chuỗi string Python-list."""
    try:
        return ast.literal_eval(raw)
    except Exception:
        return []


def parse_differential(raw: str) -> list:
    """Parse cột DIFFERENTIAL_DIAGNOSIS từ chuỗi Python-list of lists."""
    try:
        return ast.literal_eval(raw)
    except Exception:
        return []


# =============================================================================
# 4. HÀM CHÍNH: ĐỌC CSV VÀ TẠO CÁC TRIPLET
# =============================================================================

def convert_to_triplets(input_csv: str, output_csv: str) -> None:
    """
    Đọc file input_csv (transfer.csv) và xuất file output_csv với các triplet
    theo cấu trúc (subject, relation, object).
    """
    fieldnames = ["subject", "relation", "object"]
    rows_written = 0

    with open(input_csv, newline="", encoding="utf-8") as fin, \
         open(output_csv, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for idx, row in enumerate(reader, start=1025603):
            patient_id = f"Patient_{idx:04d}"
            triplets   = []

            # ----------------------------------------------------------------
            # A. Thông tin nhân khẩu học
            # ----------------------------------------------------------------
            age = row.get("AGE", "").strip()
            sex = row.get("SEX", "").strip()

            triplets.append({
                "subject":  patient_id,
                "relation": "HAS_AGE",
                "object":   f"Age: {age}"
            })
            triplets.append({
                "subject":  patient_id,
                "relation": "HAS_SEX",
                "object":   f"Sex: {sex}"
            })

            # ----------------------------------------------------------------
            # B. Triệu chứng khởi phát (INITIAL_EVIDENCE)
            # ----------------------------------------------------------------
            initial_raw = row.get("INITIAL_EVIDENCE", "").strip()
            if initial_raw:
                desc = get_evidence_description(initial_raw)
                triplets.append({
                    "subject":  patient_id,
                    "relation": "HAS_INITIAL_SYMPTOM",
                    "object":   f"Symptom: {desc}"
                })

            # ----------------------------------------------------------------
            # C. Toàn bộ triệu chứng (EVIDENCES)
            # ----------------------------------------------------------------
            evidences = parse_evidence_list(row.get("EVIDENCES", "[]"))
            for ev_token in evidences:
                ev_token = ev_token.strip()
                desc = get_evidence_description(ev_token)

                if "_@_" in ev_token:
                    # Triệu chứng phức hợp - mang giá trị
                    e_code = ev_token.split("_@_")[0]
                    v_code = ev_token.split("_@_")[1]
                    triplets.append({
                        "subject":  patient_id,
                        "relation": f"EXHIBITS",
                        "object":   f"Symptom: {desc}"
                    })
                else:
                    # Triệu chứng đơn (Boolean)
                    triplets.append({
                        "subject":  patient_id,
                        "relation": "EXHIBITS",
                        "object":   f"Symptom: {desc}"
                    })

            # ----------------------------------------------------------------
            # D. Chẩn đoán chính xác (PATHOLOGY)
            # ----------------------------------------------------------------
            pathology = row.get("PATHOLOGY", "").strip()
            if pathology:
                full_name = get_condition_name(pathology)
                triplets.append({
                    "subject":  patient_id,
                    "relation": "DIAGNOSED_WITH",
                    "object":   f"Pathology: {full_name}"
                })

            # ----------------------------------------------------------------
            # E. Chẩn đoán phân biệt (DIFFERENTIAL_DIAGNOSIS)
            # ----------------------------------------------------------------
            diff_list = parse_differential(row.get("DIFFERENTIAL_DIAGNOSIS", "[]"))
            for item in diff_list:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    cond_name, prob = item
                    full_name = get_condition_name(str(cond_name))
                    prob_str  = f"{float(prob):.4f}"
                    triplets.append({
                        "subject":  patient_id,
                        "relation": f"POSSIBLE_DIAGNOSIS {{probability: {prob_str}}}",
                        "object":   f"Pathology: {full_name}"
                    })

            # Ghi tất cả triplet của bệnh nhân này
            writer.writerows(triplets)
            rows_written += len(triplets)

    print(f"[OK] Đã chuyển đổi {idx} bệnh nhân -> {rows_written} triplets")
    print(f"[OK] Kết quả lưu tại: {output_csv}")


# =============================================================================
# 5. ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    input_file   = os.path.join(script_dir, "validate.csv")
    output_file  = os.path.join(script_dir, "graphrag_triplets_validate.csv")

    if not os.path.exists(input_file):
        print(f"[ERROR] Không tìm thấy file input: {input_file}")
    else:
        convert_to_triplets(input_file, output_file)
