# Conditional GAN — Drug Molecule Generation from Scratch

## Overview

This project implements a Conditional Generative Adversarial Network (cGAN) that generates novel drug-like molecules conditioned on 15 pharmaceutical properties. Both the generator and discriminator are built entirely from scratch — no pretrained models are used.

The model outputs two modalities simultaneously for each generated molecule:
- A **SMILES string** (character-level sequence representing molecular structure)
- An **atom composition vector** (per-element atom counts extracted from molecular formula)

---

## Dataset

**Source:** ChEMBL pharmaceutical compound database (2-part CSV, semicolon-separated)

**Preprocessing pipeline:**
1. Merge two CSV parts into a single DataFrame
2. Select 17 relevant columns (15 molecular properties + formula + SMILES)
3. Drop duplicates and rows missing essential fields
4. Validate SMILES with RDKit — keep only chemically valid structures
5. Impute missing values (median for continuous, 0 for counts, formula-inferred for Molecular Species)
6. Clip outliers using IQR bounds (no data dropped)
7. Encode categorical fields (`Passes Ro3`, `Molecular Species`)
8. Normalize all numerical columns to [0, 1] with MinMaxScaler

**Condition features (15):**

| Feature | Feature | Feature |
|---|---|---|
| Molecular Weight | AlogP | Polar Surface Area |
| HBA | HBD | #RO5 Violations |
| #Rotatable Bonds | QED Weighted | CX LogP |
| CX LogD | Aromatic Rings | Heavy Atoms |
| Np Likeness Score | Passes Ro3 | Molecular Species |

---

## Architecture

### Generator

- **Input:** Noise vector (dim=90) + condition vector (dim=15)
- **Shared trunk:** Dense layers (256 → 128 → 256 → 128) with LeakyReLU/ReLU activations and Dropout
- **Atom branch:** Dense layer → 25-dimensional atom count vector (one per element)
- **SMILES branch:** Custom `ARGRUCell` (Autoregressive GRU) that generates characters one at a time, conditioning each step on the condition vector, the atom output, and an MLP-projected scalar sequence

**ARGRUCell** — a custom Keras layer that:
- Concatenates per-step conditioning with the previous token's soft embedding
- Runs a single GRU step
- Projects output to vocabulary logits
- Feeds softmax probabilities back as a soft token embedding to the next step

### Discriminator

- **SMILES branch:** 4-layer Conv1D (128 → 256 → 128 → 64 filters) + GlobalAveragePooling
- **Atom branch:** Dense(256) + LeakyReLU
- **Condition branch:** Dense(128) + LeakyReLU
- **Merge:** Concatenate all branches → Dense(128) → `MiniBatchDiscrimination` → Dense(64) → sigmoid output

**MiniBatchDiscrimination** — prevents mode collapse by projecting samples into a kernel space, computing pairwise distances, and appending diversity features to the discriminator's representation.

> **Bug fix (v2):** The original discriminator had two Conv1D chains both assigned to `x1`, orphaning the first branch. This version uses a single clean 4-layer Conv1D pipeline.

---

## Training

### Setup

| Parameter | Value |
|---|---|
| Noise dimension | 90 |
| Batch size | 256 |
| Generator LR | 1e-4 (Adam) |
| Discriminator LR | 1e-5 (Adam) |
| Epochs | 100 |
| Mixed precision | float16 (variables in float32) |
| GPU strategy | MirroredStrategy (2× T4, 32GB total) |

### Loss Functions

**Discriminator loss:** Binary cross-entropy with label smoothing (real labels = 0.9)

**Generator loss (combined, single update):**
- Adversarial loss — fool the discriminator
- SMILES reconstruction — sparse categorical cross-entropy against real SMILES tokens
- Consistency loss (weight=0.05) — differentiable MSE between predicted atom composition and atom counts estimated from SMILES logits via single-char and bigram probability matrices

### Adaptive Training Flags

Each epoch, two boolean flags are updated based on evaluation metrics:

- `update_discriminator` — enabled when discriminator accuracy on real or fake samples drops below 60%
- `update_atom_branch` — disabled once atom validity > 95%, atom uniqueness > 95%, and atom MAE < 0.5 (locks in atom quality and focuses training on SMILES)

### Checkpointing

Generator and discriminator weights are saved each epoch to `checkpoints_cgan/` as `.weights.h5` files. Training loss curves are saved as `loss_curves.png`.

---

## Evaluation Metrics

After each epoch, the model is evaluated on 128 test samples:

| Metric | Description |
|---|---|
| SMILES Validity | % of generated SMILES parseable by RDKit |
| SMILES Uniqueness | % of unique generated SMILES strings |
| Atom Validity | % of predicted atom counts within dataset min/max range |
| Atom Uniqueness | % of unique atom composition vectors |
| Atom Exact Match | % of atom vectors exactly matching ground truth |
| Atom MAE | Mean absolute error of atom counts vs. ground truth |
| Discriminator Accuracy | Overall real/fake classification accuracy |
| Real Accuracy | % of real samples correctly identified |
| Fake Accuracy | % of fake samples correctly identified |

---

## SMILES Tokenization

Character-level tokenizer built from the dataset vocabulary.

Special tokens: `<pad>` (0), `<start>` (1), `<end>` (2)

Sequences are right-padded to `max_length = max(SMILES length) + 2`.

---

## Consistency Loss — Element Mapping

The consistency loss uses two pre-built matrices:

- **Single-char matrix** — maps individual SMILES characters (C, N, O, S, P, F, I, H, B, K and their aromatic forms) to element columns
- **Bigram adjustment matrix** — handles two-character elements (Cl, Br, Na, Ca, Cs, Ba, Bi, Ag, Ga, Al, Mg, Li, Rb, Sr, Zn) via positional bigram probabilities, and subtracts the single-char contribution to avoid double-counting (e.g., 'C' in 'Cl' should not be counted as Carbon)

---

## Requirements

```
tensorflow >= 2.x      # mixed precision + MirroredStrategy
rdkit                  # SMILES validation and atom extraction
pandas
numpy
scikit-learn           # MinMaxScaler, train_test_split, MAE
matplotlib
```

Install RDKit in the notebook environment with:
```bash
pip install rdkit
```

---

## Kaggle Setup

- **Accelerator:** GPU T4 × 2 (Settings → Accelerator → GPU T4 x2)
- **Dataset path:** `/kaggle/input/datasets/mohamednasra/compounds/`

---

## Project Structure

```
cgan-latest-version.ipynb
│
├── Cell 1   — GPU setup & mixed precision
├── Cell 2   — Imports
├── Cell 3   — Data loading (ChEMBL, 2-part CSV)
├── Cell 4   — Feature selection & SMILES validation
├── Cell 5   — Missing value imputation
├── Cell 6   — Outlier clipping (IQR)
├── Cell 7   — Categorical encoding
├── Cell 8   — SMILES tokenizer & encoding
├── Cell 9   — Molecular formula parsing → atom feature matrix
├── Cell 10  — Normalization & final preparation
├── Cell 11  — Custom layers: ARGRUCell, MiniBatchDiscrimination
├── Cell 12  — Generator architecture
├── Cell 13  — Discriminator architecture
├── Cell 14  — Dataset preparation & sharding
├── Cell 15  — Evaluation utilities
├── Cell 16  — Training setup (multi-GPU, dummy forward pass)
├── Cell 17  — Train step (tf.function, MirroredStrategy)
└── Cell 18  — Training loop (100 epochs, checkpointing, eval)
```
