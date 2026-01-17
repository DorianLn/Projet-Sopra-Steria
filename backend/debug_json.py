from extractors.robust_extractor import extract_cv_robust
import json
print("---- CV_JLA----")
res = extract_cv_robust("data/input/CV_JLA_202504.docx")
print(json.dumps(res, indent=2, ensure_ascii=False))

print("---- CV_LEO_WEBER ----")
res = extract_cv_robust("data/input/CV_LEO_WEBER_1.pdf")
print(json.dumps(res, indent=2, ensure_ascii=False))

print("---- CV_OBI_Fullstack_java_angular ----")
res = extract_cv_robust("data/input/CV_OBI_Fullstack_java_angular (1).pdf")
print(json.dumps(res, indent=2, ensure_ascii=False))        

print("---- CV-Adele PATAROT ----")
res = extract_cv_robust("data/input/CV-Adele PATAROT.pdf")
print(json.dumps(res, indent=2, ensure_ascii=False))

print("---- CV_MAROUEN_BEN_AZZOUZ ----")
res = extract_cv_robust("data/input/CV_MAROUEN_BEN_AZZOUZ_10-2025 6.pdf")
print(json.dumps(res, indent=2, ensure_ascii=False))

print("---- WALLID AZZAOUI ----")
res = extract_cv_robust("data/input/WALLID AZZAOUI_202511.docx")
print(json.dumps(res, indent=2, ensure_ascii=False))

