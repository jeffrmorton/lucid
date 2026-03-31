# EEG Signal Processing, Foundation Models, and BCI Classification
# Exhaustive Academic Research for "Lucid" BCI Platform Design
**Date: 2026-03-26**

---

## Table of Contents
1. [Real-Time Artifact Rejection -- State of the Art (2024-2026)](#1-real-time-artifact-rejection)
2. [EEG Foundation Models -- Latest Research (2025-2026)](#2-eeg-foundation-models)
3. [BCI Classification -- Modern Approaches (2024-2026)](#3-bci-classification)
4. [Neurofeedback -- Clinical Evidence and Protocols (2024-2026)](#4-neurofeedback)
5. [EEG-Schumann Resonance Correlation -- All Known Research](#5-eeg-schumann-resonance-correlation)
6. [Real-Time EEG Processing Pipelines](#6-real-time-eeg-processing-pipelines)

---

## 1. Real-Time Artifact Rejection

### 1.1 The Problem

EEG signals (~1-100 uV) are routinely contaminated by artifacts 10-100x larger than the signals of interest. The primary artifact types are:

| Artifact Type | Amplitude | Frequency Range | Duration | Difficulty |
|---|---|---|---|---|
| Eye blink (EOG) | 50-200 uV | 0-5 Hz (mainly DC-2 Hz) | 200-400 ms | Moderate |
| Eye movement (saccade) | 10-100 uV | DC-5 Hz | 20-100 ms | Moderate |
| Muscle (EMG) | 10-1000 uV | 20-300 Hz (broadband) | Variable | Hard |
| Head/body movement | 50-500 uV | 0-10 Hz | Variable | Hard |
| Electrode pop/shift | 500-5000+ uV | Broadband transient | 10-50 ms | Easy (detection) |
| 50/60 Hz mains | 1-50 uV | 50/60 Hz + harmonics | Continuous | Easy (notch) |
| ECG/pulse | 5-50 uV | 1-2 Hz (QRS complex) | ~100 ms repeating | Moderate |

### 1.2 Adaptive Filtering Methods (LMS, NLMS, RLS)

**Principle**: Use a reference signal (EOG, EMG, IMU) to estimate artifact contamination, then subtract the estimated artifact from the EEG channel.

**LMS (Least Mean Squares)**:
- Simplest adaptive filter. Updates weights at each sample: `w(n+1) = w(n) + mu * e(n) * x(n)`
- Step size `mu` controls convergence speed vs. stability tradeoff
- Computation: O(N) per sample where N = filter order (typically 3-10 for EOG)
- Latency: essentially zero (single sample delay)
- Performance: effective for stationary artifacts (EOG blinks)
- Limitation: slow convergence, sensitive to step size selection
- Reference: Correa et al., "Artifact removal from EEG signals using adaptive filters in cascade"

**NLMS (Normalized LMS)**:
- Normalizes step size by signal power: `mu_n = mu / (||x(n)||^2 + epsilon)`
- Key advantage: eliminates noise amplification problem inherent in LMS
- Comparable execution time to LMS
- Better stability across varying signal conditions
- Among best performers for EMG artifact removal when using EEG as reference signal
- Reference: Frontiers in Computational Neuroscience (2022), single-channel EMG filtering comparison

**RLS (Recursive Least Squares)**:
- Faster convergence than LMS family (typically 10x)
- Uses forgetting factor (lambda, typically 0.95-0.999) to track non-stationary signals
- Computation: O(N^2) per sample -- significantly more expensive
- NVFF-RLS (Numerical Variable Forgetting Factor) variant tracks non-stationary EOG signals more accurately
- Best for: rapidly changing artifacts, non-stationary contamination
- Limitation: computational cost prohibitive for high channel counts in real-time
- Reference: Circuits, Systems, and Signal Processing (2016), EOG excision with NVFF-RLS

**Comparative assessment for real-time BCI**:
- NLMS recommended for most real-time applications (best speed/quality tradeoff)
- RLS preferred when artifact dynamics are fast-changing and channel count is low
- All require dedicated reference channels (EOG, EMG, or IMU)
- Latency contribution: <1 ms at standard EEG sample rates (250-1000 Hz)

### 1.3 Real-Time ICA (Independent Component Analysis)

**Standard ICA** (InfoMax, FastICA):
- Batch algorithm requiring minutes of data for convergence
- Traditional ICA (e.g., RUNICA in EEGLAB): ~28.6 minutes runtime with 512 passes
- NOT suitable for real-time processing in its standard form
- Requires as many or more data points as channels for reliable decomposition

**ORICA (Online Recursive ICA)** -- KEY BREAKTHROUGH:
- Paper: Hsu et al., "Real-Time Adaptive EEG Source Separation Using Online Recursive Independent Component Analysis" (IEEE TNSRE, 2016)
- Online recursive ICA with online RLS whitening for blind source separation
- Offers instantaneous incremental convergence upon presentation of new data
- Single <1 minute run vs. RUNICA's 28.6 minutes
- Implemented in BCILAB and EEGLAB; integrated into Real-time EEG Source-mapping Toolbox (REST)
- Supports: ICA-based online artifact rejection, feature extraction, adaptive classification
- Limitation: still requires initial calibration period; performance degrades with very few channels (<8)

**CNN-Approximated ICA** (2025):
- A 2025 study introduces a CNN that estimates ICA-like component activations and scalp topographies directly from short preprocessed EEG epochs
- Enables real-time and large-scale analysis
- Calibration-free alternative to ICA that preserves component interpretability
- Reference: MDPI AI (2025), "Optimizing EEG ICA Decomposition with Machine Learning"

**Assessment for Lucid**: ORICA is the most mature real-time ICA option. For 8-16 channels, computation is feasible. CNN-approximated ICA is a promising newer alternative that avoids convergence issues entirely.

### 1.4 Deep Learning for Artifact Removal

#### 1.4.1 Autoencoder-Based Approaches

**LSTEEG (2025)**:
- LSTM-based autoencoder for detection and correction of EEG artifacts
- Leverages LSTM layers to capture non-linear dependencies in sequential EEG data
- Outperforms other state-of-the-art convolutional autoencoders for both artifact detection and correction
- Reference: arxiv:2502.08686 (Feb 2025)

**IC-U-Net**:
- U-Net-based denoising autoencoder using mixtures of independent components
- Trained with raw/denoised signal pairs created using ICLabel
- Automatic multi-channel EEG artifact correction
- Architecture: U-Net encoder-decoder with skip connections
- Reference: NeuroImage (2022)

**AnEEG (2024)**:
- Novel attention-based network leveraging deep learning for effective artifact removal
- Published in Scientific Reports (2024)
- Handles multiple artifact types simultaneously

#### 1.4.2 Transformer-Based Approaches

**ART (Artifact Removal Transformer) (2025)**:
- Innovative EEG denoising model employing transformer architecture
- Captures transient millisecond-scale dynamics characteristic of EEG signals
- Evaluations confirm ART surpasses other deep-learning-based artifact removal methods
- Published in NeuroImage (2025)
- Reference: arxiv:2409.07326; ScienceDirect (2025)

**AT-AT (Autoencoder-Targeted Adversarial Transformer) (2025)**:
- Lightweight autoencoder-connected solution for neural interface artifact remediation
- Adversarial training approach for robust artifact removal
- Reference: arxiv:2502.05332 (Feb 2025)

**CLEnet (2025)**:
- Integrates dual-scale CNN and LSTM with improved EMA-1D (Efficient Multi-Scale Attention)
- Extracts morphological and temporal features of EEG to separate signals from artifacts
- Published in Scientific Reports (2025)

#### 1.4.3 Performance/Latency Tradeoffs

Critical finding from comprehensive review (Springer, 2025): "High performing models such as transformer based or multi-branch hybrid architectures typically offer superior artifact suppression at the cost of higher computational resources, making them less suitable for low-latency or resource-constrained environments, while models such as shallow CNNs or simple autoencoders are computationally efficient and more appropriate for real-time applications though they may yield lower denoising accuracy."

### 1.5 Artifact Subspace Reconstruction (ASR)

**Algorithm principle**: ASR is a sliding-window principal component analysis (PCA)-based method that:
1. During calibration: records clean reference data to learn the statistics of artifact-free EEG
2. During operation: computes PCA on sliding windows, identifies principal components exceeding a statistical threshold (typically 10-20 standard deviations from the clean reference distribution)
3. Reconstructs contaminated subspace by interpolating from non-contaminated channels/components

**Key characteristics**:
- Real-time capable: operates as a sliding window algorithm
- Component-based: effectively removes transient/large-amplitude artifacts
- Does NOT require reference channels (unlike adaptive filtering)
- Threshold parameter controls aggressiveness (lower = more aggressive removal)
- Available in EEGLAB (clean_rawdata plugin), MNE-Python, and standalone implementations

**Recent developments (2024-2025)**:

**Embedded ASR (E-ASR) for Single-Channel EEG (2024)**:
- Novel framework applying ASR to single-channel EEG via dynamical embedding
- Creates embedded matrix from single-channel data using delay vectors
- Achieved RRMSE of 43.87% and correlation coefficient of 0.91 on semi-simulated data
- Reference: Sensors (2024), "Dynamical Embedding of Single-Channel EEG for ASR"

**ASR for Extreme Mobile Brain/Body Imaging (2025)**:
- Addresses calibration data quality for high-motion tasks
- New methods: ASRDBSCAN and ASRGEV for defining calibration data quality
- ASRDBSCAN found 42% usable calibration data vs. only 9% by original ASR
- Completely removes artifacts where original ASR failed
- Reference: Journal of Neuroscience Methods (2025), "Juggler's ASR"

**Riemannian ASR (rASR)**:
- Uses Riemannian geometry instead of Euclidean PCA
- Better handles the curved manifold structure of EEG covariance matrices
- Reference: Frontiers in Human Neuroscience (2019)

**Assessment for Lucid**: ASR is the top recommendation for the primary artifact rejection stage. It is real-time, does not need reference channels, handles multiple artifact types simultaneously, and has well-validated implementations. The E-ASR variant enables use even with 4-channel systems.

### 1.6 Wavelet-Based Artifact Removal

**Principle**: Decompose EEG into time-frequency components, identify artifactual components based on their time-frequency signature, remove them, reconstruct.

**Recent methods (2024-2025)**:

**Fixed Frequency Empirical Wavelet Transform (FF-EWT) (2025)**:
- Three-step procedure: FF-EWT decomposes contaminated EEG into 6 IMFs; features threshold identifies EOG-related IMFs; cascaded SG filter reduces blink events
- Published: Scientific Reports (Nov 2025)

**Hybrid VMD-SWT-CCA (2025)**:
- Combines variational mode decomposition, stationary wavelet transform, and canonical correlation analysis
- Specifically targets muscle artifact removal
- CCA component enables real-time performance due to low computational time
- Reference: Cogent Engineering (2025)

**WATV-ICA (2025)**:
- Combined wavelet total variation denoising with ICA
- Targets specific wavelet-ICA components related to artifactual events
- Reference: Analog Integrated Circuits and Signal Processing (2025)

**Two-Stage EWT-CCA-Isolation Forest (2024)**:
- Automatic method handling different artifacts across miscellaneous EEG applications
- Uses isolation forest for outlier detection to identify artifactual components
- Reference: Biomedical Signal Processing and Control (2024)

### 1.7 Combined/Recommended Approaches by Artifact Type

| Artifact | Best Real-Time Method | Alternative | Latency |
|---|---|---|---|
| Eye blink | ASR + reference regression (NLMS from EOG) | Deep learning (LSTEEG) | <5 ms |
| Eye movement | Reference regression (NLMS from HEOG/VEOG) | ASR | <2 ms |
| Muscle (EMG) | ASR (aggressive threshold) + bandpass | Wavelet-CCA hybrid | <10 ms |
| Head movement | ASR + IMU reference regression | ORICA (if >8 channels) | <10 ms |
| Electrode pop | Threshold detection + interpolation | ASR (very high threshold) | <1 ms |
| ECG/pulse | NLMS from ECG reference | ORICA | <5 ms |
| 50/60 Hz mains | Notch filter (IIR, 2nd order) | Adaptive notch | <1 ms |

### 1.8 Latency Requirements for Real-Time BCI

| Application | Maximum Acceptable Latency | Typical Processing Budget |
|---|---|---|
| Motor imagery BCI | 100-250 ms | Full pipeline: 50-200 ms |
| SSVEP BCI | 50-100 ms | Full pipeline: 20-80 ms |
| P300 BCI | 200-500 ms | Full pipeline: 100-300 ms |
| Neurofeedback | 100-500 ms | Full pipeline: 50-250 ms |
| Error potential (ErrP) | 200-400 ms | Full pipeline: 100-300 ms |
| Speech BCI (invasive) | <250 ms | 50-200 ms |

### 1.9 2025-2026 Breakthroughs Summary

1. **ART (Artifact Removal Transformer)**: First transformer achieving SOTA on EEG artifact removal across all artifact types (2025)
2. **LUNA achieving 0.921 AUROC on TUAR artifact detection** with 300x fewer FLOPs than prior models (NeurIPS 2025)
3. **E-ASR**: ASR extended to single-channel via dynamical embedding (2024)
4. **Improved ASR calibration** (ASRDBSCAN): 4.7x more usable calibration data for mobile/active scenarios (2025)
5. **CNN-approximated ICA**: Calibration-free real-time alternative to traditional ICA (2025)

---

## 2. EEG Foundation Models

### 2.1 Overview of the EEG Foundation Model Landscape

The field has exploded since 2023. As of early 2026, there are at least 8 significant EEG foundation models, most with open-source code and pretrained weights. A NeurIPS 2025 workshop ("Foundation Models for the Brain and Body") and multiple benchmarking papers (EEG-FM-Bench, Aug 2025; Brain4FMs, Feb 2026) have attempted to standardize evaluation.

### 2.2 Major EEG Foundation Models

#### 2.2.1 REVE (NeurIPS 2025) -- CURRENT SOTA

**Paper**: "REVE: A Foundation Model for EEG -- Adapting to Any Setup with Large-Scale Pretraining on 25,000 Subjects"

**Architecture**:
- Patch embedding module + 4D positional encoding + Transformer backbone
- Novel 4D positional encoding enables processing signals of arbitrary length and electrode arrangement
- Two sizes: REVE-Base, REVE-Large

**Pretraining**:
- Masked autoencoding objective with spatio-temporal contiguous masking
- 60,000+ hours of EEG from 92 datasets spanning 25,000 subjects (LARGEST to date)
- Top datasets: TUH (26,847 hrs), ICARE (22,707 hrs), HMS (364 hrs)
- Sampling rate: 200 Hz
- Channel diversity: 3 to 129 channels across 10-20, EGI, Biosemi montages

**Downstream Performance (10 tasks)**:
| Task | Dataset | Accuracy |
|---|---|---|
| Motor imagery | BCIC-IV-2a | 0.6396 +/- 0.0095 |
| Seizure detection | TUEV | 0.6759 +/- 0.0229 |
| Sleep staging | ISRUC | 0.7819 +/- 0.0078 |
| Emotion recognition | FACED | 0.5646 +/- 0.0164 |
| Average (all 10) | Various | 0.7150 +/- 0.0057 |

**Availability**: Open-source code (github.com/elouayas/reve_eeg), pretrained weights on HuggingFace (huggingface.co/collections/brain-bzh/reve), Braindecode integration, Colab tutorials

#### 2.2.2 NeuroLM (ICLR 2025)

**Paper**: "NeuroLM: A Universal Multi-task Foundation Model for Bridging the Gap between Language and EEG Signals"

**Architecture**:
- Two-stage approach:
  1. Text-aligned neural tokenizer via vector-quantized temporal-frequency prediction
  2. LLM-based pre-training: multi-channel autoregressive learning
- Variants: NeuroLM-B (base), NeuroLM-XL (1.7 BILLION parameters -- largest EEG model ever)
- Inspired by LaBraM; built upon nanoGPT and LaBraM codebases
- Instruction tuning for multi-task adaptation

**Pretraining**:
- 25,000 hours of EEG data (7x more than LaBraM)
- Trained on 8x NVIDIA A100-80G GPUs

**Key Innovation**: Bridges EEG and language modalities -- can understand both text instructions and EEG signals in a unified framework

**Availability**: Open-source (github.com/935963004/NeuroLM), pretrained weights on HuggingFace (huggingface.co/Weibang/NeuroLM), PyTorch 2.5.0

#### 2.2.3 LUNA (NeurIPS 2025)

**Paper**: "LUNA: Efficient and Topology-Agnostic Foundation Model for EEG Signal Analysis"

**Architecture**:
- Compresses multi-channel EEG into fixed-size, topology-agnostic latent space via learned queries and cross-attention
- Downstream transformer blocks use patch-wise temporal self-attention
- Computation decoupled from electrode count (topology-agnostic)
- Part of the BioFoundation framework (github.com/pulp-bio/biofoundation)

**Pretraining**:
- Masked-patch reconstruction objective
- Trained on TUEG + Siena: 21,000+ hours raw EEG across diverse montages

**Performance**:
- SOTA on TUAR (artifact detection): 0.921 AUROC
- SOTA on TUSL (slowing classification)
- 300x fewer FLOPs than prior models
- 10x less GPU memory

**Key Innovation**: Extreme efficiency -- enables deployment on edge devices and consumer hardware

**Availability**: Open-source (github.com/pulp-bio/biofoundation)

#### 2.2.4 LaBraM (ICLR 2024 Spotlight)

**Paper**: "Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI"

**Architecture**:
- Neural Transformer backbone
- Segments EEG into channel patches
- Vector-quantized neural spectrum prediction for neural tokenizer training
- Masked EEG channel patch prediction

**Pretraining**:
- ~2,500 hours of EEG from ~20 datasets
- Various signal types (BCI, clinical, cognitive)

**Downstream Tasks**: Abnormal detection, event classification, emotion recognition, gait prediction -- outperforms SOTA in all

**Availability**: Open-source (github.com/935963004/LaBraM)
**Significance**: Foundational work that inspired NeuroLM and influenced the entire field

#### 2.2.5 EEGPT (NeurIPS 2024)

**Paper**: "EEGPT: Pretrained Transformer for Universal and Reliable Representation of EEG Signals"

**Architecture**:
- 10-million-parameter pretrained transformer
- Mask-based dual self-supervised learning
- Spatio-temporal representation alignment (key innovation)
- Hierarchical structure: processes spatial and temporal info separately
- Reduces computational complexity vs. joint processing

**Key Innovation**: Constructs self-supervised task on high-SNR EEG representations rather than raw signals -- mitigates poor feature quality from low-SNR inputs

**Performance**: SOTA on range of downstream tasks with linear probing; 4% balance accuracy and 5% AUROC improvement vs. non-pretrained baseline on TUAB

**Availability**: Open-source (github.com/BINE022/EEGPT)

#### 2.2.6 BENDR (Frontiers in Human Neuroscience, 2021)

**Paper**: "BENDR: Using Transformers and a Contrastive Self-Supervised Learning Task to Learn From Massive Amounts of EEG Data"

**Architecture**:
- Convolutional encoder downsamples raw EEG into vector sequence
- Transformer encoder maps to new representations
- Contrastive + masked autoencoder self-supervised learning

**Key Contribution**: Demonstrated a single pre-trained model can handle novel raw EEG from different hardware and different subjects/tasks. Pioneered the EEG foundation model concept.

#### 2.2.7 BrainBERT (ICLR Workshop 2023)

**Architecture**:
- Transformer for intracranial recordings (ECoG/sEEG, not scalp EEG)
- Time-frequency masking strategy on EEG spectrograms
- Self-attention for contextual extraction from unmasked regions
- Enables classification with much less labeled data

**Significance**: Demonstrated BERT-style masked pretraining works for neural signals

#### 2.2.8 EEG-GPT (Neurosity)

**Repository**: github.com/neurosity/EEG-GPT
**Status**: Foundational model specifically for Neurosity Crown (8-channel consumer EEG)
**Availability**: Pretrained weights available for download
**Note**: Primarily designed for Neurosity's proprietary hardware ecosystem

#### 2.2.9 BrainOmni (2025)

First brain foundation model that generalizes across heterogeneous EEG AND MEG recordings. Unifies two modalities in a single pretrained model.

#### 2.2.10 LEAD (GitHub: DL4mHealth/LEAD)

World's first foundational model specifically for EEG-based Alzheimer's Disease detection. Pre-trained model (P-Base) available for download and fine-tuning.

### 2.3 Cross-Subject and Cross-Session Transfer Learning

**Current state of cross-subject transfer (2025)**:
- Subject-dependent MI accuracy (best models): 85-90% (4-class, BCI-IV-2a)
- Subject-independent MI accuracy (best models): ~63% (4-class, BCI-IV-2a) -- TCFormer (2025)
- Foundation model zero-shot MI accuracy: ~64% (REVE on BCI-IV-2a)
- Gap between subject-specific and subject-independent: ~20-25 percentage points

**Cross-session transfer**:
- Foundation models (REVE, NeuroLM) show improved cross-session consistency
- Some calibration still needed for optimal performance
- Calibration-free BCI is NOT reliably solved yet -- "a large gap still exists between zero-calibration and subject-specific calibration performance"

**Transfer learning approaches (2025)**:
| Method | Approach | Cross-Subject Gain |
|---|---|---|
| META-EEG | Gradient-based meta-learning + intermittent freezing | Robust zero-calibration for unseen subjects |
| ConvoReleNet | Convolutional relational networks | Subject-invariant representations |
| CDRC | Cross-device representation consistency | Cross-device + cross-subject |
| One Model for All | Univariate SSL pretraining + Adaptive Resampling Transformer | Universal pre-training across paradigms |

### 2.4 Self-Supervised Learning for EEG

**Dominant SSL paradigms** (from ACM Computing Surveys 2025 systematic survey):
1. **Contrastive learning**: Most widely used. Minimize distance between augmented views of same signal, maximize distance between different signals.
2. **Masked prediction**: Mask portions of EEG, predict missing content (as in BERT/MAE)
3. **Temporal prediction**: Predict future EEG segments from past
4. **Cross-modal alignment**: Align EEG representations with text/audio/image embeddings

**SS-EMERGE (2025)**: Meiosis-based contrastive learning for pretraining + fine-tuning with minimal labeled data for emotion recognition

**CSCL (2025)**: Cross-subject contrastive learning specifically addressing cross-subject generalization in emotion recognition

### 2.5 Data Requirements for Fine-Tuning

Based on current literature (2025):
- **Few-shot fine-tuning** (foundation models): 2-10 trials per class can provide meaningful adaptation
- **Standard calibration**: 40-80 trials per class (15-30 minutes) for traditional CSP-based BCI
- **Transfer learning with META-EEG**: 0 trials (zero-calibration) to 5 trials per class
- **Foundation model linear probing**: typically requires 50-200 labeled examples for significant improvement over zero-shot

### 2.6 Open-Source Pretrained Models Available for Download

| Model | Weights Location | Parameters | Year |
|---|---|---|---|
| REVE | huggingface.co/collections/brain-bzh/reve | Base + Large | 2025 |
| NeuroLM | huggingface.co/Weibang/NeuroLM | 1.7B (XL) | 2025 |
| LUNA | github.com/pulp-bio/biofoundation | Efficient | 2025 |
| EEGPT | github.com/BINE022/EEGPT | 10M | 2024 |
| LaBraM | github.com/935963004/LaBraM | Multiple | 2024 |
| EEG-GPT | github.com/neurosity/EEG-GPT | Unknown | 2024 |
| LEAD | github.com/DL4mHealth/LEAD | P-Base | 2024 |
| BENDR | Per paper / EEGLAB | Moderate | 2021 |

### 2.7 EEGUnity -- Dataset Unification Tool

**Paper**: "EEGUnity: Open-Source Tool in Facilitating Unified EEG Datasets Toward Large-Scale EEG Model" (IEEE, 2025)

**Purpose**: Addresses the critical challenge of heterogeneous EEG datasets for foundation model training

**Modules**:
1. EEG Parser -- intelligent data structure inference
2. Correction -- data cleaning
3. Batch Processing -- unified interface for large-scale processing
4. LLM Boost -- AI-assisted metadata parsing

**Evaluation**: Tested across 25 EEG datasets demonstrating high performance and flexibility
**Significance**: Enables practical construction of large-scale EEG training corpora from disparate sources

---

## 3. BCI Classification

### 3.1 Motor Imagery (MI) Classification

#### 3.1.1 Classical Approaches

**Common Spatial Pattern (CSP)**:
- Gold standard feature extraction for MI since ~2000
- Finds spatial filters maximizing variance ratio between two classes
- Typically combined with LDA or SVM classifier
- Requires 15-30 minutes calibration (40-80 trials per class)
- 2-class accuracy: 70-85% (subject-dependent)
- 4-class accuracy: 60-75% (subject-dependent)
- Limitations: binary only (extensions: FBCSP, one-vs-rest); sensitive to artifacts; requires enough channels over motor cortex

**Filter Bank CSP (FBCSP)**:
- Decomposes EEG into multiple sub-bands, applies CSP to each
- Feature selection identifies most discriminative band-spatial features
- Typically 5-10% improvement over standard CSP

#### 3.1.2 Deep Learning Approaches -- Benchmarks on BCI Competition IV-2a (4-class MI)

| Model | Year | Architecture | Accuracy (SD) | Kappa | Parameters |
|---|---|---|---|---|---|
| EEGNet | 2018 | Depthwise separable CNN | 69.14% (SI) | ~0.59 | ~2.6K |
| ShallowConvNet | 2017 | Shallow CNN | ~66% | -- | ~47K |
| EEG Conformer | 2023 | CNN + Transformer | 78.66% | -- | ~170K |
| TCFormer | 2025 | Temporal Conv + Transformer | 84.8% (SD) / 63% (SI) | -- | -- |
| CIACNet | 2025 | Composite attention CNN | 85.15% | 0.80 | -- |
| DB-BISAN | 2025 | Dual-branch blocked self-attention | ~82% | -- | -- |
| AMEEGNet | 2025 | Attention multiscale EEGNet | ~80% | -- | -- |

Key: SD = Subject-Dependent, SI = Subject-Independent

**EEGNet** (Lawhern et al., 2018):
- Architecture: temporal conv (bandpass) -> depthwise spatial conv (CSP-like) -> separable pointwise conv -> classification
- Only ~2,600 parameters -- extremely compact
- Works across paradigms (MI, SSVEP, P300, ErrP)
- Remains the most-cited and most-used baseline
- Reference: arxiv:1611.08024

**EEG Conformer** (2023):
- Hybrid CNN-Transformer
- CNN extracts local spatial-temporal features; Transformer captures global dependencies
- BCI-IV-2a: 78.66%; BCI-IV-2b: 84.63%; SEED: 95.30%

**CIACNet** (2025) -- CURRENT SOTA for subject-dependent:
- Composite improved attention convolutional network
- BCI-IV-2a: 85.15% (kappa 0.80); BCI-IV-2b: 90.05% (kappa 0.80)
- Reference: Frontiers in Neuroscience (2025)

#### 3.1.3 Few-Electrode MI Classification

- **78.16% accuracy** achieved using only a small number of electrodes with signal prediction method (Sensors, 2025)
- 8 channels over motor cortex (C3, Cz, C4 + neighbors) typically sufficient for 2-class MI
- Accuracy vs channel count: flattens around 8 channels, slow gains from 8 to 22 channels (~6%)
- Single-channel hybrid BCI (MI + SSVEP): 85% accuracy
- Minimum viable: 3 channels (C3, Cz, C4) for 2-class MI with ~65-75% accuracy

### 3.2 SSVEP Classification

#### 3.2.1 Methods and Performance

**CCA (Canonical Correlation Analysis)**:
- Reference-free method using sinusoidal templates
- No training data required
- Accuracy depends on stimulation time (0.5s: ~70%, 1s: ~85%, 2s: ~95%)

**FBCCA (Filter Bank CCA)**:
- Incorporates fundamental + harmonic frequency components
- Highest accuracy: 97.5% on Tsinghua benchmark dataset
- Significant improvement over standard CCA

**TRCA (Task-Related Component Analysis)**:
- Training-based method
- Highest ITRs: 250 bits/min (Benchmark dataset), 186.76 bits/min (BETA dataset)
- Reference: Scientific Reports (2025)

**Deep Learning for SSVEP**:
- sbCNN (sub-band CNN): highest ITRs on two benchmark datasets
- 3DCNN: 89.35% accuracy, 173.02 bits/min ITR with 1s signal (Benchmark dataset)
- H-TRCCA (2025): Hybrid task-related CCA with enhanced recognition

**Embedded SSVEP BCI (2026)**:
- EdgeSSVEP: fully embedded SSVEP BCI for low-power real-time applications
- Average accuracy: 99.17% (8/10 subjects at 100%)
- Reference: arxiv:2601.01772 (Jan 2026)

#### 3.2.2 SSVEP ITR Benchmarks

| Method | Window (s) | Accuracy | ITR (bits/min) | Year |
|---|---|---|---|---|
| FBCCA | 1.0 | 97.5% | ~180 | 2015 |
| TRCA + DNN | 0.5-1.0 | ~95% | 250 | 2025 |
| sbCNN | 1.0 | ~90% | ~175 | 2023 |
| Embedded (EdgeSSVEP) | -- | 99.17% | -- | 2026 |

### 3.3 P300 Classification

**Classical**: LDA on averaged epochs (6-15 flashes per target)
- Online accuracy: 85-95% with sufficient averaging
- Speed limited by number of repetitions needed

**Deep Learning**:
- CNN-based: >98.7% accuracy on BCI Competition II; 99% on BCI Competition III
- Transformer hybrid (P300 + CNN): 93.37% accuracy for clinical PTSD classification
- Multi-scale feature extraction: improved single-trial P300 detection

**Calibration-Free P300 (2025)**:
- "A Plug-and-Play P300-Based BCI with Calibration-Free Application" (bioRxiv, 2025)
- Uses pretrained models to eliminate per-user calibration
- Reference: Kim et al. (2025)

### 3.4 Error-Related Potentials (ErrP)

**Current state (2024-2025)**:
- ErrP detection improves average online task classification accuracy by +7%
- Also improves information transfer rate of BCIs
- Cerebellar information enhances online ErrP classification by 5-10% (2024)
- BCI-integrated ErrP feedback: decoding accuracy consistently above chance (>50%) (2025)

**Novel approaches**:
- ErrP-driven reinforcement learning (2025): uses ErrP signals as reward signals for RL-based BCI adaptation
- Reference: arxiv:2502.18594

### 3.5 Hybrid BCI Systems

| Combination | Accuracy | ITR (bits/min) | Advantage |
|---|---|---|---|
| MI + SSVEP | 89.00% (hybrid task) | -- | Multi-degree-of-freedom control |
| P300 + SSVEP (speller) | 94.29% (online) | 28.64 | Better than either alone |
| P300 + SSVEP (QWERTY) | 96.42% | 131 | Practical typing speed |
| SSVEP-P300 (optimized) | 90.76% | 81.10 | Reduced false alarms |

**Trend**: Hybrid BCIs combining 2+ paradigms consistently outperform single-paradigm systems

### 3.6 ITR Comparison Across Paradigms

| Paradigm | Typical ITR (bits/min) | Best Reported | Channels Needed | Training Required |
|---|---|---|---|---|
| Motor Imagery | 10-25 | ~40 | 3-22 | 20-30 min |
| SSVEP | 40-250 | 250+ | 3-9 (occipital) | 0-5 min |
| P300 | 20-40 | ~80 | 4-16 | 5-15 min |
| Hybrid P300+SSVEP | 30-131 | 131 | 8-16 | 5-15 min |
| ErrP (correction only) | -- | -- | 4-8 (frontocentral) | 10-20 min |

**Key takeaway**: SSVEP achieves the highest ITR by far. For a consumer BCI platform, SSVEP should be the primary high-speed input paradigm. MI is the most intuitive but slowest. P300 offers a good middle ground. Hybrid systems are the future.

### 3.7 Channel Requirements Summary

| Paradigm | Minimum Channels | Recommended | Key Positions |
|---|---|---|---|
| Motor Imagery | 3 | 8-16 | C3, Cz, C4, FC3, FC4, CP3, CP4 |
| SSVEP | 1 | 3-9 | Oz, O1, O2, POz, PO3, PO4 |
| P300 | 4 | 8-16 | Fz, Cz, Pz, Oz, P3, P4 |
| Neurofeedback | 1-2 | 4-8 | Varies by protocol (Cz, Fz, etc.) |
| Full hybrid | 8 | 16 | Full 10-20 subset |

### 3.8 Calibration Time Requirements

| Approach | Trials/Class | Time | Accuracy Impact |
|---|---|---|---|
| Full calibration (CSP) | 40-80 | 20-30 min | Best (baseline) |
| Reduced calibration | 10-20 | 5-10 min | -5-10% |
| Transfer learning | 2-10 | 1-5 min | -10-15% vs full |
| Foundation model (fine-tune) | 5-20 | 2-10 min | -5-15% vs full |
| Zero-calibration (META-EEG) | 0 | 0 min | -15-25% vs full |
| Plug-and-play P300 (2025) | 0 | 0 min | Approaching parity |

---

## 4. Neurofeedback

### 4.1 ADHD -- Latest Meta-Analyses

#### 4.1.1 JAMA Psychiatry Meta-Analysis (2025) -- DEFINITIVE STUDY

**Citation**: JAMA Psychiatry (2025), "Neurofeedback for ADHD: A Systematic Review and Meta-Analysis"
**Scale**: 38 RCTs, 2,472 participants (ages 5-40), 33 EEG-based + 5 fMRI/fNIRS

**Primary outcome (probably-blinded ADHD total symptoms)**:
- Effect size: SMD = 0.04 (95% CI: -0.10 to 0.18), p = 0.56
- **NOT significant** -- neurofeedback shows no meaningful benefit for core ADHD symptoms when assessed by blinded raters

**Standard protocol subset only**:
- Effect size: SMD = 0.21 (95% CI: 0.02 to 0.40), p = 0.03
- Small but nominally significant; authors note "likely falls short of clinical value"

**Secondary outcomes**:
- Inattention: SMD = 0.04 (p = 0.69) -- NOT significant
- Hyperactivity/impulsivity: SMD = 0.03 (p = 0.59) -- NOT significant
- Processing speed: SMD = 0.35 (p = 0.04) -- small significant improvement (high heterogeneity)

**Comparison with medication**: Methylphenidate advantage over neurofeedback: SMD = -0.68 (approximately 4x larger effect than neurofeedback's best result)

**Conclusion**: "Overall, neurofeedback did not appear to meaningfully benefit individuals with ADHD, clinically or neuropsychologically, at the group level"

#### 4.1.2 Executive Function Meta-Analysis (Scientific Reports, 2025)

**Scale**: 17 RCTs, 939 participants
**Findings**: Significant improvements in:
- Global executive function
- Inhibitory control
- Working memory
- **Key moderator**: Neurofeedback exceeding 1,260 minutes (>21 hours) was more effective for inhibitory control and working memory

#### 4.1.3 Network Meta-Analysis (Brain and Behavior, 2024)

Compared different neurofeedback types for pediatric ADHD. Key finding: not all neurofeedback protocols are equal; standard protocols (theta/beta, SMR, SCP) outperform non-standard approaches.

#### 4.1.4 Summary Assessment for ADHD

The evidence is sobering. The most rigorous meta-analysis (JAMA Psychiatry 2025) finds:
- No significant benefit for core ADHD symptoms when using blinded assessment
- Small possible benefit for executive function after prolonged training (>21 hours)
- Standard protocols (theta/beta, SMR, SCP) show better results than non-standard
- Medication (methylphenidate) is substantially more effective

### 4.2 PTSD/Anxiety

**Systematic Review and Meta-Analysis (Frontiers in Neuroscience, 2025)**:
- EEG neurofeedback: 5 studies showed "moderate to large effect" reducing PTSD symptoms vs. passive controls
- fMRI neurofeedback: 2 RCTs with sham controls showed NO improvement
- Confidence: "very low to low" due to bias risk, imprecision, conflicts of interest
- Passive control studies showed greater NF advantage than active control comparisons, suggesting placebo effects
- Conclusion: "improved controls needed to reliably determine whether neurofeedback training, or other factors, are the basis for improvements"

**Frontal Alpha Asymmetry for Anxiety**:
- More established evidence than for depression
- Reduces negative affect and anxiety symptoms
- Clinical trial comparing SMR vs alpha-theta for GAD showed both effective, but limited controls

### 4.3 Depression

**Current evidence (2024-2025)**:
- Frontal alpha asymmetry neurofeedback: reduces negative affect and anxiety, but NO training-specific modulation of depressive symptoms in RCT
- With comorbid depression + anxiety: 87 patients showed decreased symptoms after 10-session neurofeedback, but both active and control groups improved
- 2024 Molecular Psychiatry study: whole-brain fMRI-NF shows promise but clinical efficacy varies greatly between individuals based on activation patterns
- **No consensus "best" protocol for depression** as of 2025
- Neurofeedback for depression appears safe but evidence for specific efficacy remains weak

### 4.4 Sleep

**Meta-analysis of 7 RCTs (Frontiers in Neuroscience, 2024)**:
- Alpha and SMR training protocols across 8-20 sessions
- Session duration: 20-50 minutes
- Electrode placement: sensorimotor cortex (3 studies), frontal area (3 studies), parietal (1 study)

**SMR (12-15 Hz) training for insomnia**:
- Enhanced sleep spindle activity during slow-wave sleep
- Improved sleep quality
- Decreased sleep onset latency
- Improved declarative memory

**2025 pilot study**: SMR amplitude didn't significantly increase, but both SMR groups showed tendency toward improved objective sleep

### 4.5 Meditation and Peak Performance

**Alpha-Theta Cross-Frequency Training (2024-2025)**:
- Upregulates non-harmonic alpha-theta cross-frequency relationships during focused attention meditation
- Durable post-training effects, particularly for those with depressive mood symptoms
- Published: Mindfulness (2025)

**Alpha/Theta (A/T) Training**:
- Originally developed by Kamiya, Green, and Budzynski
- Peniston & Kulkosky: successful application to PTSD and alcoholism
- Facilitates "twilight states of consciousness"
- Used for peak performance, creativity enhancement, deep relaxation

**Flow State Enhancement**:
- Frontal theta (4-8 Hz) activity associated with flow states
- Theta neurofeedback supports motor performance and flow experience (Journal of Cognitive Enhancement, 2021)

### 4.6 Standard Neurofeedback Protocols

| Protocol | Target | Electrode | Frequency | Typical Use |
|---|---|---|---|---|
| Theta/Beta (TBR) | Decrease theta/beta ratio | Cz or Fz | Theta (4-8), Beta (12-20) | ADHD (hypoarousal subtype) |
| SMR | Increase SMR power | Cz or C3/C4 | 12-15 Hz | ADHD, sleep, epilepsy |
| SCP (Slow Cortical Potential) | Regulate cortical excitability | Cz | <1 Hz | ADHD, epilepsy |
| Alpha enhancement | Increase alpha power | Pz or Oz | 8-12 Hz | Anxiety, relaxation, peak performance |
| Alpha asymmetry | Normalize L-R alpha | F3/F4 | 8-12 Hz | Depression (increase left activation) |
| Alpha/theta | Cross-frequency training | Pz or Oz | Alpha (8-12), Theta (4-8) | PTSD, meditation, creativity |
| ILF (Infra-Low Frequency) | Train ultra-slow oscillations | Variable | <0.1 Hz | Anxiety, trauma, regulation |
| Beta downtraining | Reduce high beta | Variable | 20-30 Hz | Anxiety, hyperarousal |

### 4.7 QEEG-Guided Neurofeedback

**Principle**: Use quantitative EEG analysis to select individualized neurofeedback protocols based on each patient's specific EEG phenotype.

**ADHD Subtypes and Protocol Selection (2025)**:
- Cortical hypoarousal -> theta/beta protocol
- Delayed maturation -> SMR training
- Hyperarousal -> SCP training
- TBR abnormalities directly inform theta/beta protocol selection

**Clinical Outcomes**:
- Retrospective study: statistically significant improvement from pre to post with sustained outcomes to follow-up for anxiety
- Multicenter trial: clinical effectiveness replicated; possible to assign patients to protocol based on individual QEEG

**KEY LIMITATION (2025)**: Low predictive value of QEEG subtypes for treatment response. Meta-analyses demonstrate that neither TBR nor subtype membership reliably predicts individual response. Heterogeneity in protocols, placebo effects (~40% short-term improvement), and variability present significant challenges.

### 4.8 Session Count and Dosing

**Typical protocols**:
- Clinical standard: 20-40 sessions
- Session frequency: 2-3x per week
- Session duration: 20-50 minutes of active training
- Executive function benefit threshold: >1,260 minutes total (>21 hours)
- Minimum for measurable effect: ~8-10 sessions
- Home-based feasibility: demonstrated with self-administered protocols

### 4.9 Home-Based Neurofeedback

**Current evidence (2024-2025)**:
- Remote neurofeedback: ADHD and anxiety patients both benefited
- Anxiety: 69% of participants moved from abnormal to healthy score ranges
- StoPain Trial (ongoing): home-based EEG neurofeedback for chronic neuropathic pain after spinal cord injury
- Consistency requirement: minimum 20 sessions, at least 1x/week
- Key limitation: "current evidence insufficient for clinical recommendation due to small samples, short follow-up, and potential publication bias"

### 4.10 Sham-Controlled Trial Summary

**Pattern across all sham-controlled RCTs (2024-2025)**:
- Largest double-blind sham-controlled ADHD trial (fMRI-NF, 88 boys): active NF NOT more effective than sham
- Large 2-site EEG-NF ADHD trial (2024): both active and sham showed large improvements; NF was NOT superior to sham
- Earlier pilot: both active and sham yielded large pre-post improvements
- **Conclusion**: A substantial portion of neurofeedback benefits may be attributable to non-specific factors (attention, expectation, therapeutic relationship, structured activity) rather than specific brain-wave-contingent training

---

## 5. EEG-Schumann Resonance Correlation

### 5.1 Background

Schumann Resonances (SR) are electromagnetic resonances in the Earth-ionosphere waveguide, excited by global lightning activity:
- Mode 1: ~7.83 Hz
- Mode 2: ~14.3 Hz
- Mode 3: ~20.8 Hz
- Mode 4: ~27.3 Hz
- Mode 5: ~33.8 Hz
- Higher modes continue at ~6.5 Hz intervals

The frequency overlap with human EEG bands is notable:
- SR Mode 1 (7.83 Hz) overlaps alpha/theta boundary (8 Hz)
- SR Mode 2 (14.3 Hz) overlaps beta/SMR (12-15 Hz)
- SR Mode 3 (20.8 Hz) overlaps beta (13-30 Hz)

### 5.2 Persinger's Research

**Key paper**: Persinger & Saroka, "Human Quantitative Electroencephalographic and Schumann Resonance Exhibit Real-Time Coherence of Spectral Power Densities: Implications for Interactive Information Processing" (SCIRP, 2015)

**Findings**:
- QEEGs of 41 men and women displayed repeated transient coherence with first three SR modes (7-8 Hz, 13-14 Hz, 19-20 Hz) in real time
- Coherence duration: ~300 ms, occurring approximately twice per minute
- Maximum coherence domain: right caudal hemisphere near parahippocampal gyrus
- Coherence clusters became stable 35-45 ms after onset of synchronizing event
- During first 10-20 ms, isoelectric lines shifted from clockwise to counterclockwise rotation

**Related Persinger findings**:
- SR frequencies clearly found in spectral profiles of human brain activity
- 6-week monitoring study (15 individuals): correlations between EEG variations and SR changes across daily cycle, largest during periods of higher magnetic activity

### 5.3 Cherry (2002)

**Paper**: "Schumann Resonances, a plausible biophysical mechanism for the human health effects of Solar/Geomagnetic Activity"

**Thesis**: SR acts as a global synchronizer for brain and heart rhythms, crucial for biological homeostasis

**Proposed mechanism**: Geomagnetic activity modulates SR parameters, which in turn influence neural oscillations through extremely low frequency (ELF) electromagnetic coupling

### 5.4 HeartMath Institute Research

**Global Coherence Initiative (GCI)**:
- International network of 12 ultrasensitive magnetic field detectors
- Specifically designed to measure Earth's magnetic resonances
- Live data: heartmath.org/gci/gcms/live-data/

**Key claims**:
- SR frequencies "directly overlap with those of the human brain, cardiovascular, and autonomic nervous systems"
- Humans may be "not only receivers of biologically relevant information, but these frequencies also can couple information to the earth's magnetic fields"
- Proposed: physiological coherence (HRV coherence) increases coupling to Earth's magnetic fields
- "Synchronization of Human Autonomic Nervous System Rhythms with Geomagnetic Activity" (PMC, 2017)

**Scientific standing**: HeartMath research is published in peer-reviewed journals but sits at the boundary of mainstream science. The proposed bidirectional information coupling lacks established physical mechanisms.

### 5.5 2024-2025 Research

**Electromagnetic Biology and Medicine (2025)**:
- "Exploring the influence of Schumann resonance and electromagnetic fields on bioelectricity and human health"
- Notes correlation between atmospheric EM frequencies and brain function
- Tentative findings on SR influencing sleep rhythms and heart variability via bioelectricity

**Insomnia Study (Nature Sleep Science)**:
- Explored subjective and objective improvement from non-invasive SR-frequency stimulation for insomnia
- Suggests possible therapeutic application

### 5.6 Skeptical/Critical Assessment

**Major criticisms**:

1. **Signal strength**: SR magnetic field is ~1-2 picotesla. For comparison, Earth's static field is ~25-65 microtesla (10 million times stronger). The SR signal is many orders of magnitude below what is established to affect neural activity.

2. **Frequency overlap is coincidental**: Earth's circumference (~40,000 km) happens to produce standing waves at ~7.83 Hz (wavelength = speed of light / circumference). Brain rhythms at similar frequencies evolved for entirely different biophysical reasons (neural circuit time constants, membrane properties).

3. **Correlation vs. causation**: Studies showing simultaneous EEG-SR coherence have not established directionality or mechanism. Both systems could be independently responding to the same environmental drivers (geomagnetic activity, solar radiation, time of day).

4. **Replication issues**: Persinger's findings are not universally replicated. The effect sizes are small and methodology has been questioned.

5. **No established physical mechanism**: How would a 1 pT oscillating magnetic field couple to neural membrane potentials of ~70 mV across ~7 nm membranes? The energy gap is enormous. No peer-reviewed biophysical model convincingly bridges this gap.

6. **Publication bias**: The EEG-SR research literature is dominated by a small number of research groups with a priori interest in confirming the connection.

### 5.7 Assessment for Lucid/EarthSync

**Scientific status**: The EEG-SR correlation is a legitimate scientific question but currently lacks strong evidence for a causal mechanism. The frequency overlap is real and interesting. Persinger's transient coherence findings are intriguing but require independent replication.

**For EarthSync integration**: The platform already monitors SR. Displaying simultaneous EEG-SR spectral comparisons would be scientifically interesting and unique. However, any claims of coupling should be presented cautiously and accompanied by appropriate caveats about the strength of evidence.

**Recommended approach**: Present as an open scientific question. Allow users to observe their own EEG alongside SR data and draw their own observations, without implying established causal links.

---

## 6. Real-Time EEG Processing Pipelines

### 6.1 Standard BCI Processing Pipeline

```
Raw EEG Data (250-1000 Hz, 8-16 channels)
    |
    v
[1] Hardware Filtering (analog bandpass, 0.1-100 Hz)
    |
    v
[2] Digital Bandpass (IIR/FIR, 1-45 Hz typical)
    |  Latency: <1 ms (IIR) or 5-20 ms (FIR, depends on order)
    v
[3] Notch Filter (50/60 Hz)
    |  Latency: <1 ms
    v
[4] Artifact Rejection (ASR primary + optional reference regression)
    |  Latency: 5-50 ms (depends on window size)
    v
[5] Feature Extraction
    |  - CSP (MI): <5 ms for 8 channels
    |  - FFT/bandpower (NF): <2 ms
    |  - CCA (SSVEP): <5 ms
    |  - Epoch averaging (P300): 0 ms (accumulation)
    v
[6] Classification
    |  - LDA: <1 ms
    |  - EEGNet inference: 1-5 ms (CPU)
    |  - Foundation model inference: 5-50 ms (GPU)
    v
[7] Feedback/Output
    |  - Visual: 16-60 ms (display refresh)
    |  - Audio: 5-20 ms
    |  - Device control: varies
    v
[8] Logging and Storage
```

### 6.2 Latency Budgets

**Total pipeline latency = acquisition + filtering + artifact rejection + feature extraction + classification + feedback rendering**

| Component | Typical Latency | Can Optimize To |
|---|---|---|
| ADC acquisition | 1-4 ms (at 250 Hz) | 0.06 ms (at 16 kHz) |
| Wireless transmission | 5-20 ms (BLE) | 1-2 ms (USB/SPI) |
| Bandpass filter (IIR) | <1 ms | <0.1 ms |
| Notch filter | <1 ms | <0.1 ms |
| ASR (256-sample window) | ~10-30 ms | ~5 ms (optimized) |
| CSP feature extraction | 1-5 ms | <1 ms |
| LDA classification | <1 ms | <0.1 ms |
| EEGNet inference (CPU) | 1-5 ms | <1 ms (ONNX optimized) |
| Display rendering | 16 ms (60 Hz) | 8 ms (120 Hz) |
| **Total (typical)** | **35-75 ms** | **~15-20 ms** |

**Speech BCI benchmark (2025)**: 99% accuracy at <250 ms latency (invasive, Andersen Lab)

### 6.3 JavaScript/Node.js EEG Processing

#### 6.3.1 BCI.js Library

**URL**: bci.js.org (formerly WebBCI)
**Status**: Available but appears lightly maintained (copyright 2017)

**Available methods**:
- Fast Fourier Transform (FFT)
- Common Spatial Pattern (CSP)
- FastICA
- Bandpower analysis (with relative power computation)
- Linear Discriminant Analysis (LDA)
- Feature extraction via windowing and transformation
- Data partitioning utilities

**Performance benchmarks** (16-channel, 128-sample):
| Operation | Latency |
|---|---|
| Bandpower | <1 ms |
| CSP | <4 ms |
| LDA | <1 ms |

**Platform**: Works in both Node.js (NPM) and browser (jsDelivr CDN)

**Assessment**: Sufficient for basic BCI operations. The <4 ms CSP latency confirms JavaScript is fast enough for real-time 8-16 channel processing. However, the library's maintenance status is concerning.

#### 6.3.2 Existing JavaScript EEG Implementations

- **Wits**: Node.js library for Emotiv EPOC EEG headset
- **Brain Monitor**: Terminal app in Node.js for real-time brain signal monitoring
- **Ganglion BLE**: Web Bluetooth client for OpenBCI Ganglion
- **OpenBCI_GUI**: Processing/Java-based (not JS) but has WebSocket output
- Various experimental implementations using Web Bluetooth API + WebSocket streaming

#### 6.3.3 WebSocket EEG Streaming

WebSocket provides full-duplex communication over TCP with:
- Persistent connection (no HTTP overhead per message)
- ~1-2 ms additional latency over raw TCP
- Native browser support
- Node.js: `ws` library (most popular, already used in EarthSync)

**For Lucid**: The existing EarthSync WebSocket infrastructure (ws library, AES-256-CBC encryption) can be extended for EEG streaming. The 5-second interval used for SR data would need to be reduced to per-sample or per-epoch streaming (4-100 ms intervals).

### 6.4 GPU Acceleration for Real-Time EEG

**Question**: Is GPU needed for 8-16 channels?

**Analysis**:

For traditional signal processing (filtering, CSP, bandpower):
- **NO GPU needed**. JavaScript/CPU is sufficient. BCI.js demonstrates <4 ms for CSP on 16 channels.

For deep learning inference (EEGNet, EEG Conformer):
- **Probably NO GPU needed** for compact models. EEGNet has only ~2,600 parameters. Inference on CPU: 1-5 ms.
- **MAY need GPU** for foundation models (REVE, NeuroLM). REVE-Base with 8 channels: likely 10-50 ms on GPU, 100-500 ms on CPU.

For real-time artifact removal with transformers (ART):
- **Beneficial but not required** for 8-16 channels
- GPU would enable running ART + classification simultaneously within latency budget

**Optimization options without GPU**:
- ONNX Runtime: 2-5x speedup over raw PyTorch on CPU
- TensorRT (NVIDIA): significant speedup on NVIDIA GPUs
- Quantization (INT8): 2-4x speedup with minimal accuracy loss
- WebGL/WebGPU: browser-based GPU compute (available in Chrome, Firefox)
- WASM (WebAssembly): near-native speed in browser

**Recommendation for Lucid**: Start with CPU-only processing using ONNX-optimized models. Add GPU acceleration path for users with NVIDIA hardware. For browser-based operation, investigate WebGPU for foundation model inference.

### 6.5 Recommended Architecture for Lucid

```
[Hardware Layer]
  EEG Device (OpenBCI Cyton/Ganglion, ESP-EEG, etc.)
    |
    | USB/BLE/WiFi (device-specific driver)
    v
[Acquisition Layer - Node.js]
  BrainFlow or custom driver
    | Raw samples at native rate (250-1000 Hz)
    v
[Processing Layer - Node.js/WASM]
  1. Ring buffer (2-5 seconds)
  2. IIR bandpass (1-45 Hz)
  3. Notch filter (50/60 Hz)
  4. ASR artifact rejection (WASM implementation)
  5. Feature extraction:
     a. CSP + bandpower (MI)
     b. CCA (SSVEP)
     c. Epoch extraction (P300/ErrP)
     d. Spectral features (neurofeedback)
    | Processed features at epoch rate (4-20 Hz)
    v
[Classification Layer - ONNX/WASM]
  1. EEGNet / compact CNN (ONNX Runtime)
  2. OR: Foundation model fine-tuned (ONNX, larger)
  3. OR: Traditional classifier (LDA, SVM from BCI.js)
    | Predictions at classification rate
    v
[Application Layer - WebSocket -> Browser]
  1. Neurofeedback visualization (React, Plotly.js)
  2. BCI control output
  3. Session logging and metrics
  4. SR overlay (from EarthSync backend)
```

---

## Key Recommendations for Lucid Platform Design

### Signal Processing
1. **Primary artifact rejection**: ASR (mature, real-time, no reference channels needed)
2. **Secondary artifact rejection**: NLMS adaptive filter using EOG/EMG reference channels if available
3. **Future path**: ART (Artifact Removal Transformer) when GPU inference is practical in-browser via WebGPU

### Foundation Models
4. **Starting point**: EEGPT (10M params, smallest, most practical for real-time)
5. **Upgrade path**: REVE (SOTA performance, open weights, but larger computation)
6. **For training/fine-tuning**: Use EEGUnity to assemble large-scale training data from public datasets
7. **Cross-subject**: Use contrastive pretraining; accept ~63% zero-calibration accuracy; offer quick fine-tuning for +15-20%

### Classification
8. **Motor imagery**: EEGNet (baseline) or CIACNet (SOTA, 85% on BCI-IV-2a)
9. **SSVEP**: FBCCA (no training) or TRCA+DNN (best ITR, 250 bits/min)
10. **P300**: CNN-based classifier with plug-and-play pretrained model
11. **Hybrid**: Implement SSVEP+P300 hybrid for speller applications (131 bits/min achievable)

### Neurofeedback
12. **Protocols**: Implement standard set (theta/beta, SMR, alpha, SCP) with QEEG-guided selection
13. **Clinical framing**: Present neurofeedback as experimental/complementary; the JAMA 2025 meta-analysis is definitive that blinded evidence does not support core ADHD symptom improvement
14. **Strongest evidence for**: Executive function improvement (with >21 hours training), sleep (SMR), anxiety reduction (alpha), meditation enhancement (alpha/theta)

### Processing Architecture
15. **JavaScript is viable** for 8-16 channel real-time processing (<4 ms CSP latency demonstrated)
16. **No GPU required** for traditional processing or compact deep learning models
17. **WebSocket streaming** at epoch rate (not sample rate) for browser-based applications
18. **ONNX Runtime** for portable model inference across CPU/GPU/WASM

### Schumann Resonance Integration
19. **Present as scientific curiosity**, not established science
20. **Simultaneous EEG-SR visualization** would be unique and scientifically interesting
21. **Do not claim causal coupling** -- the evidence does not support it
22. **The frequency overlap is real and measurable** -- let users explore it for themselves

---

## Sources

### Artifact Rejection
- [EEG Artifact Detection and Correction with Deep Autoencoders (2025)](https://arxiv.org/html/2502.08686v1)
- [Detection-Guided Artifact Removal for Clinical EEG (2026)](https://www.medrxiv.org/content/10.64898/2026.02.12.26346128v2.full)
- [AnEEG: Deep Learning for Artifact Removal (2024)](https://www.nature.com/articles/s41598-024-75091-z)
- [Novel EEG Artifact Removal with Advanced Attention Mechanism (2025)](https://www.nature.com/articles/s41598-025-98653-1)
- [Deep Learning for EEG Healthcare Applications Review (2025)](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2025.1689073/full)
- [Dynamical Embedding Single-Channel ASR (2024)](https://www.mdpi.com/1424-8220/24/20/6734)
- [Juggler's ASR for Extreme MoBI (2025)](https://pubmed.ncbi.nlm.nih.gov/40324599/)
- [Riemannian ASR (2019)](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2019.00141/full)
- [ART: Artifact Removal Transformer (2025)](https://www.sciencedirect.com/science/article/pii/S1053811925001259)
- [AT-AT: Autoencoder-Targeted Adversarial Transformers (2025)](https://arxiv.org/html/2502.05332v1)
- [Hybrid VMD-SWT-CCA Muscle Artifact Removal (2025)](https://www.tandfonline.com/doi/full/10.1080/23311916.2025.2514941)
- [Wavelet Total Variation + ICA (2025)](https://link.springer.com/article/10.1007/s10470-025-02315-1)
- [FF-EWT Single-Channel EOG Removal (2025)](https://www.nature.com/articles/s41598-025-10276-8)
- [IC-U-Net Denoising Autoencoder (2022)](https://pubmed.ncbi.nlm.nih.gov/36031182/)
- [ORICA: Online Recursive ICA (2016)](https://pubmed.ncbi.nlm.nih.gov/26685257/)
- [CNN-Approximated ICA (2025)](https://www.mdpi.com/2673-2688/6/12/312)
- [Adaptive Filtering Review for EEG (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6427454/)
- [Comprehensive Deep Learning EEG Denoising Review (2025)](https://link.springer.com/article/10.1007/s42452-025-07808-2)

### Foundation Models
- [REVE: NeurIPS 2025 Poster](https://neurips.cc/virtual/2025/poster/117334)
- [REVE Project Page](https://brain-bzh.github.io/reve/)
- [REVE arXiv Paper](https://arxiv.org/abs/2510.21585)
- [REVE GitHub](https://github.com/elouayas/reve_eeg)
- [NeuroLM GitHub (ICLR 2025)](https://github.com/935963004/NeuroLM)
- [NeuroLM OpenReview](https://openreview.net/forum?id=Io9yFt7XH7)
- [LaBraM GitHub (ICLR 2024 Spotlight)](https://github.com/935963004/LaBraM)
- [LaBraM arXiv](https://arxiv.org/abs/2405.18765)
- [LUNA: NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115483)
- [LUNA arXiv](https://arxiv.org/abs/2510.22257)
- [BioFoundation/LUNA GitHub](https://thorirmar.com/project/biofoundation/)
- [EEGPT NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4540d267eeec4e5dbd9dae9448f0b739-Abstract-Conference.html)
- [EEGPT GitHub](https://github.com/BINE022/EEGPT)
- [BENDR (2021)](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.653659/full)
- [BrainBERT OpenReview](https://openreview.net/forum?id=xmcYx_reUn6)
- [EEG-GPT (Neurosity) GitHub](https://github.com/neurosity/EEG-GPT)
- [BrainOmni OpenReview](https://openreview.net/forum?id=cjHQj0tCy6)
- [LEAD GitHub](https://github.com/DL4mHealth/LEAD)
- [EEGUnity IEEE (2025)](https://ieeexplore.ieee.org/document/10979503/)
- [EEGUnity arXiv](https://arxiv.org/abs/2410.07196)
- [EEG Foundation Models Survey (2025)](https://arxiv.org/html/2507.11783v3)
- [EEG-FM-Bench GitHub](https://github.com/xw1216/EEG-FM-Bench)
- [Foundation Models for Neural Signal Decoding (2026)](https://onlinelibrary.wiley.com/doi/10.1111/ejn.70376)
- [EEG Foundation Models Overview](https://www.emergentmind.com/topics/eeg-foundation-models-eeg-fms)
- [Open-Source EEG Foundation Models List](https://github.com/gayalkuruppu/eeg-foundation-models)

### Self-Supervised Learning
- [Self-supervised Learning for EEG: Systematic Survey (ACM 2025)](https://dl.acm.org/doi/10.1145/3736574)
- [Cross-Device Representation Consistency (2025)](https://pubmed.ncbi.nlm.nih.gov/41052170/)
- [Cross-Subject Contrastive Learning for Emotion (2025)](https://www.nature.com/articles/s41598-025-13289-5)
- [SS-EMERGE Self-Supervised EEG (2025)](https://www.nature.com/articles/s41598-025-98623-7)
- [One Model for All: Universal Pre-training (2024)](https://www.researchgate.net/publication/397522231)
- [Zero-Shot Few-Shot EEG Survey (2024)](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.643386/full)
- [META-EEG Subject-Independent Framework (2024)](https://www.sciencedirect.com/science/article/abs/pii/S0893608024000224)

### BCI Classification
- [EEGNet (2018)](https://arxiv.org/abs/1611.08024)
- [CIACNet: Composite Attention CNN (2025)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1543508/full)
- [TCFormer: Temporal Conv Transformer (2025)](https://www.nature.com/articles/s41598-025-16219-7)
- [AMEEGNet: Attention Multiscale EEGNet (2025)](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2025.1540033/full)
- [CTNet: Convolutional Transformer (2024)](https://www.nature.com/articles/s41598-024-71118-7)
- [Transfer Learning ConvoReleNet (2025)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1691929/full)
- [Neural Decoding EEG-BCI Review (2026)](https://www.sciencedirect.com/science/article/pii/S2589238X26000021)
- [Real-World Deep Learning BCI Decoders (2025)](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2025.1718390/full)
- [SSVEP TRCA+DNN (2025)](https://www.nature.com/articles/s41598-024-84534-6)
- [FBCCA (2015)](https://pubmed.ncbi.nlm.nih.gov/26035476/)
- [H-TRCCA Hybrid SSVEP (2025)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1544452/full)
- [EdgeSSVEP Embedded BCI (2026)](https://arxiv.org/html/2601.01772v1)
- [P300 Deep Learning Classification (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10785884/)
- [Plug-and-Play P300 BCI (2025)](https://www.biorxiv.org/content/10.1101/2025.05.21.655021v1.full.pdf)
- [ErrP Reinforcement Learning (2025)](https://arxiv.org/pdf/2502.18594)
- [ErrP Cerebellar Targets (2024)](https://www.mdpi.com/2076-3425/14/3/214)
- [Hybrid P300-SSVEP Speller (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10050351/)
- [EEG Channel Selection Review (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9774545/)
- [Efficient MI-BCI Channel Optimization (2025)](https://www.tandfonline.com/doi/full/10.1080/02533839.2025.2527815)
- [BCI Training Calibration Time Reduction (2022)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263641)
- [BCIs in 2025: Trials, Progress, Challenges](https://andersenlab.com/blueprint/bci-challenges-and-opportunities)

### Neurofeedback
- [JAMA Psychiatry ADHD Meta-Analysis (2025)](https://jamanetwork.com/journals/jamapsychiatry/fullarticle/2827733)
- [NF Executive Function Meta-Analysis (2025)](https://www.nature.com/articles/s41598-025-94242-4)
- [NF ADHD Network Meta-Analysis (2024)](https://onlinelibrary.wiley.com/doi/10.1002/brb3.70194)
- [NF for PTSD Systematic Review (2025)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1658652/full)
- [Frontal Alpha Asymmetry NF (2017)](https://pubmed.ncbi.nlm.nih.gov/28236680/)
- [NF Depression Molecular Psychiatry (2024)](https://www.nature.com/articles/s41380-024-02880-3)
- [NF Psychiatry Decade Review (2025)](https://archivesbiologicalpsychiatry.org/neurofeedback-in-psychiatry-a-decade-of-clinical-and-neuroimaging-insights-a-systematic-review/)
- [NF Sleep Meta-Analysis (2024)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2024.1450163/full)
- [SMR Sleep Pilot Study (2025)](https://pubmed.ncbi.nlm.nih.gov/41060038/)
- [Alpha-Theta Meditation NF (2025)](https://link.springer.com/article/10.1007/s12671-025-02603-x)
- [QEEG ADHD Subtypes and NF (2025)](https://onlinelibrary.wiley.com/doi/10.1002/brb3.70714)
- [QEEG NF Anxiety Outcomes](https://www.neuroregulation.org/article/view/20157)
- [Home-Based NF StoPain Trial (2024)](https://www.nature.com/articles/s41393-024-01031-3)
- [Remote NF Evidence (2022)](https://formative.jmir.org/2022/7/e35636)
- [Double-Blind Sham-Controlled ADHD NF (2014)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3939717/)
- [fMRI-NF Sham RCT ADHD (2022)](https://psychiatryonline.org/doi/full/10.1176/appi.ajp.21100999)
- [NF PTSD Study Protocol (2025)](https://bmcpsychiatry.biomedcentral.com/articles/10.1186/s12888-025-07050-5)
- [SMR/Theta NF Cognitive Performance (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7308493/)
- [NF ADHD QEEG Biomarkers Review (2025)](https://www.mdpi.com/2073-4409/14/17/1339)

### Schumann Resonance
- [Persinger: EEG-SR Real-Time Coherence (2015)](https://www.scirp.org/html/11-3400403_56609.htm)
- [Persinger: SR Frequencies in QEEG (2015)](https://www.scipress.com/ILCPA.30.24)
- [SR-EEG Spectral Power Density Similarity (PLOS ONE, 2016)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0146595)
- [Cherry: SR and Human Health (2002)](https://www.helios3.com/wp-content/uploads/2020/11/Schumann-Resonances-Dr-Neil-Cherry-2002.pdf)
- [HeartMath Global Coherence Research](https://www.heartmath.org/research/science-of-the-heart/global-coherence-research/)
- [HeartMath GCI Live Data](https://www.heartmath.org/gci/gcms/live-data/)
- [Human ANS-Geomagnetic Synchronization (PMC, 2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5551208/)
- [SR and Human Health Review (2025)](https://www.tandfonline.com/doi/full/10.1080/15368378.2025.2508466)
- [Schumann Resonance and Human Consciousness (Talos Labs)](https://taloslabs.substack.com/p/schumann-resonance-and-human-consciousness)
- [SR Conspiracy Theories (Wikipedia)](https://en.wikipedia.org/wiki/Schumann_resonances_conspiracy_theories)
- [SR Skeptical Analysis (Hackaday, 2023)](https://hackaday.com/2023/05/12/what-is-a-schumann-resonance-and-why-am-i-being-offered-a-7-83hz-oscillator/)
- [NASA: Impact of SR on Human Health](https://science.nasa.gov/wp-content/uploads/2023/05/154_48a5766284d47dc2523cb38d856654f6_STOLCVIKTOR.pdf)

### Processing Pipelines
- [BCI.js Library](https://bci.js.org/)
- [Signal Preprocessing and Feature Extraction in EEG-BCIs (2025)](https://www.mdpi.com/2076-3417/15/22/12075)
- [OpenBCI Framework for Neurophysiological Experiments (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10098804/)
- [BCI Latency Measurement (PMC, 2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3161621/)
- [GPU Accelerated EEG Preprocessing (Springer, 2024)](https://link.springer.com/chapter/10.1007/978-3-031-69583-4_19)
- [Enhanced EEG Hybrid Deep Learning Classification (2025)](https://www.nature.com/articles/s41598-025-07427-2)
- [BCI Signal Processing: Foundations and Methods (2025)](https://ijoer.com/brain-computer-interface-signal-processing)
