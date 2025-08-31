# Challenges Faced

1. **PDF Formatting Issues**
   - Cynthia EHRs were available as PDFs, making text extraction inconsistent.  
   - Some key-value fields did not align properly after extraction.  

2. **Separation of Structured vs. Unstructured Data**
   - Needed custom rules (e.g., keyword matching) to differentiate between patient demographics/diagnoses and free-text clinical notes.  

3. **Inconsistent Column Names**
   - Some structured fields appeared in slightly different formats across PDFs (e.g., "Diagnosis" vs. "Dx").  
   - Standardization was required to maintain consistency in `EHR_cleaned.csv`.  

4. **Noise Handling**
   - Some extracted text included formatting artifacts (extra spaces, line breaks, headers).  
   - Preprocessing steps were added to normalize these values.  

---
