# TrialMCP Pack -- Synthetic Datasets

This directory contains synthetic clinical trial datasets used for development, testing, and reproducibility of the TrialMCP Pack MCP servers.

## Provenance

All data in this directory is **fully synthetic** and was generated programmatically for the TrialMCP Pack project. No real patient data, protected health information (PHI), or actual clinical trial records are included.

## Directory Structure

| Path | Description | Schema Version |
|------|-------------|---------------|
| `fhir-bundles/oncology_trial_bundle.json` | FHIR R4 Bundle (collection) with 14 synthetic oncology trial resources | FHIR R4 (4.0.1) |
| `dicom-samples/study_index.json` | DICOM study metadata index with 3 imaging studies and RECIST 1.1 measurements | Custom v1 |
| `scheduling/trial_schedule.json` | Simulated robotic procedure schedule across 2 trial sites | Custom v1 |

## Data Dictionary

### FHIR Bundle (`fhir-bundles/`)

| Resource Type | Count | Key Fields |
|---------------|-------|------------|
| ResearchStudy | 2 | id, title, status, phase, protocol |
| Patient | 3 | id, gender, birthDate (synthetic) |
| ResearchSubject | 3 | id, study reference, individual reference, status |
| Condition | 2 | id, code (NSCLC, colorectal), subject reference |
| Observation | 2 | id, code, value (tumor size, biomarker) |
| MedicationAdministration | 1 | id, medication (Pembrolizumab), dosage |
| AdverseEvent | 1 | id, event (fatigue), seriousness, CTCAE grade |

### DICOM Index (`dicom-samples/`)

| Study | Modality | Series Count | RECIST Targets |
|-------|----------|--------------|----------------|
| CT Chest (patient-001) | CT | 2 | TL-001, TL-002 |
| MR Abdomen (patient-002) | MR | 3 | TL-001 |
| PET/CT Whole Body (patient-003) | PT | 2 | TL-001, TL-002 |

### Scheduling Data (`scheduling/`)

| Event | Robot Platform | USL Score | Trial Site |
|-------|---------------|-----------|------------|
| Robotic biopsy | Franka Emika Panda | 7.4 | Site A |
| Sample collection | Kinova Gen3 | 5.7 | Site B |
| Imaging guidance | da Vinci dVRK | 7.1 | Site A |

## Known Limitations

- Synthetic data does not capture the full variability of real clinical populations (age bands, comorbidities, treatment arm diversity).
- DICOM index contains metadata only; no actual pixel data or DICOM Part 10 files are included.
- Scheduling data uses simplified prerequisite tracking.

## Integrity Verification

File checksums are recorded in `manifest.json` (SHA-256). Verify with:

```bash
python -c "
import json, hashlib, pathlib
manifest = json.loads(pathlib.Path('datasets/manifest.json').read_text())
for entry in manifest['files']:
    h = hashlib.sha256(pathlib.Path(entry['path']).read_bytes()).hexdigest()
    status = 'OK' if h == entry['sha256'] else 'MISMATCH'
    print(f'{status}: {entry[\"path\"]}')"
```

## License

All synthetic datasets are released under the MIT License. See the repository root `LICENSE` file.
