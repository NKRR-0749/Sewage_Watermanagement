# Viva Questions & Answers

**Q1: Why did you use a Multi-Agent System (MAS) instead of a single central script?**
*Answer:* A single script represents a single point of failure and lacks scalability. Using Mesa agents allows us to modularize the logic. If one station goes offline in the real world, the decentralized agents at other stations can continue operating and making decisions.

**Q2: What is the difference between your Rule-Based and ML-Based detection?**
*Answer:* The rule-based system uses hard-coded scientific thresholds (e.g., Turbidity > 30 = Anomaly). The ML system (Isolation Forest) uses unsupervised learning to find outliers based on the data's overall distribution, which helps catch complex anomalies where parameters might individually look okay, but are strange when combined.

**Q3: Does this system actually purify water?**
*Answer:* No, this is a mathematical simulation. The TreatmentAgent simulates the *efficiency* of treatments (e.g., reducing turbidity by 70% mathematically) to demonstrate how the AI's feedback loop works before treatment is sent downstream.

**Q4: Why did you choose Isolation Forest?**
*Answer:* Isolation Forest is ideal for anomaly detection, especially when the dataset is unlabeled (unsupervised). It works by isolating observations by randomly selecting a feature and a split value. Anomalies require fewer splits to isolate, making them easy to identify.

**Q5: How does the Analysis Agent detect the pollution source?**
*Answer:* It uses spatial analysis. It checks the network topologically (S1 to S5). If S2 is normal, but S3, S4, and S5 are highly abnormal, it logically deduces that the likely pollution injection point was S3.
