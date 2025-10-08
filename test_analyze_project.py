# test_analyze_project.py
from analyzer import ProjectAnalyzer

pa = ProjectAnalyzer()
pa.open_project("/Users/smayra/email-sync/")  # e.g. "/Users/ravi/Desktop/myapp"
print("\n--- AI Analysis ---\n")
result = pa.analyze_technologies()
print(result)
