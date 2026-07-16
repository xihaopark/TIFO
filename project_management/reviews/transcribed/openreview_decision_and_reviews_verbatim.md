# KDD 2026 Cycle 2 decision and reviews — verbatim transcription

Source: `../original/KDD2027resubmit.pdf`

OpenReview forum: <https://openreview.net/forum?id=2b776YkXBX#discussion>

Source SHA-256: `616d6fae37edd9866f2cc4c5a7fcb36c3495383184d7fee65fdec8cb997c3648`

Transcription note: the source PDF is a two-page image export without a text
layer. The text below was OCR-extracted and manually checked against the page
images on 2026-07-16. Original wording, grammar, capitalization, numbering, and
ratings are preserved; only visual line wrapping is normalized. Mathematical
symbols are represented in plain-text/Markdown form.

Important: the `Resubmission: No` or `N/A` entries inside individual reviews
are fields completed by those reviewers. The authoritative Program Chairs'
decision below is `Decision: Resubmit`.

## Paper Decision

Decision by Program Chairs

16 May 2026, 11:18 (modified: 16 May 2026, 11:28)

```text
Decision: Resubmit

Comment:

Dear Senior Area Chair,

I have read this paper thoroughly, and also all the comments and responses.

The ratings from five reviewers are as following:

• Novelty: 2, 2, 2, 2, 3
• Technical Quality: 2, 2, 3, 3, 3
• Presentation: 2, 3, 1, 3, 3

It seems that the reviewers’ opinions were relatively consistent.

Strengths:

1. The paper insightfully highlights that time-domain mean-variance normalization cannot align structural energy distributions in frequency space under non-stationarity.

2. TIFO is designed as a plug-and-play module that can be integrated seamlessly with diverse forecasting backbones.

3. Experiments report substantial runtime reductions of roughly 60-70% versus baselines.

4. The paper offers a useful theoretical lens linking non-stationarity with spectral distribution shift.

Weaknesses:

1. There is a notable theory-implementation gap: directly predicting scalar weights with an MLP is not equivalent to rigorous kernel eigendecomposition.

2. Frequency reweighting after DFT appears close to existing spectral normalization/filtering ideas, and theoretical justification for novelty remains insufficiently developed.

3. Stronger baselines are missing from 2025-2026.

4. Format issues, e.g., broken cross-references (Table ??).

Based on the above discussion, I would like to give a resubmit recommendation.
```

## Reviewer JwDV

Official Review of Submission991

23 Mar 2026, 11:55 (modified: 16 May 2026, 11:25)

```text
Paper Summary:

This paper proposes TIFO, a frequency-domain modeling approach designed to alleviate distribution shift and non-stationarity in time series forecasting. Unlike existing methods that primarily rely on time-domain normalization to weaken the impact of temporal conditions on data distribution, this paper proposes learning a dataset-level stable frequency structure in the frequency space. Specifically, TIFO consists of two stages: Stage I performs DFT on all time series in the training set and measures the stability of each frequency component using the cross-sample statistic; Stage II uses an MLP to generate weights based on the stationarity score, reweights the Fourier coefficients of each sample, and then maps them back to the time domain via iDFT for the forecasting model. The authors further rely on Bochner's Theorem and Mercer's Theorem to interpret the frequency weights as eigenvalues in the eigen-decomposition of a frequency-domain kernel, attempting to theoretically justify the frequency reweighting. Experiments are conducted on 7 standard time series datasets using DLinear, PatchTST, and iTransformer as backbones. The results show that TIFO achieves significant performance improvements across various settings and reduces computational costs.

Paper Strengths:

(1) Non-stationarity is a critical challenge in time series forecasting. The paper insightfully points out that normalizing the mean and variance in the time domain fails to align the structural distribution of energy in the frequency domain, which is highly inspiring.

(2) TIFO can serve as a plug-and-play module and be seamlessly integrated into various forecasting backbones.

(3) Because the core operations are strictly FFT and lightweight MLPs, experiments show the method reduces running time by 60% to 70% compared to baselines in 16 experimental settings.

Paper Weaknesses:

(1) Significant gap between theoretical analysis and algorithm implementation. The paper utilizes Bochner's and Mercer's theorems to argue that the Fourier transform induces a frequency-domain kernel, and learning this kernel is equivalent to learning the eigenvalues of its eigen-decomposition. However, in the actual Stage II algorithm, the weights are directly mapped using two layers of neural networks. Strictly speaking, using an MLP to directly predict scalar weights is not fully equivalent to a rigorous kernel eigen-decomposition process, making the theoretical claims appear somewhat over-packaged.

(2) Insufficient theoretical derivation for the Stationarity Metric. When facing complex, real-world distribution shifts, the paper lacks first-principle derivations or deeper physical explanations as to why the simple ratio of low-order moments is the optimal representation of frequency stability.

(3) The core idea of using an MLP to modulate frequency components is similar to existing Frequency-domain MLPs (e.g., FilterNet[1]). The authors are encouraged to explain the technical divergence or the potential for TIFO to complement such methods. In addition, can the proposed method enhance this line of methods?

(4) The backbones used (DLinear and PatchTST) no longer represent the recent state-of-the-art.

[1]. FilterNet: Harnessing Frequency Filters for Time Series Forecasting, NeurIPS 2024.

Resubmission:

No

Questions And Suggestions For Rebuttal:

1. Regarding the exceptionally large performance improvements of over 50% on datasets like ETTm2 (e.g., a 55.3% gain for iTransformer), it is recommended to provide a more detailed explanation in the main text or appendix. The authors need to clarify whether equivalent hyperparameter searches were conducted for all baseline models (especially when coupled with other normalization modules) to rule out tuning bias, thereby further enhancing the credibility of the core experimental results.

Relevance: 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

Novelty: 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

Technical Quality: 2: Low - The paper has several technical weaknesses, such as minor methodological flaws, insufficient analysis, or unsupported conclusions. While the work shows some level of competence, it lacks thoroughness and precision. Improvements are necessary for it to be considered robust.

Presentation: 2: Low - The paper has noticeable issues with clarity and coherence. The writing may contain several grammatical and typographical errors. Figures and tables are present but may not be well-integrated or effectively used. The presentation allows for understanding but requires effort from the reader.

Reproducibility: 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

Reviewer Confidence: 4: High - The reviewer is an expert in the subject area and has extensive knowledge of the research methods and context of the paper. They are highly confident in their ability to provide an accurate and thorough assessment. Their evaluation is based on deep expertise and a comprehensive understanding of the work.

Ethics Review Flag: No

Ethics Review Description: N/A
```

## Reviewer 2Q34

Official Review of Submission991

20 Mar 2026, 18:16 (modified: 16 May 2026, 11:25)

```text
Paper Summary:

This paper proposes TIFO, a frequency-domain approach to address distribution shift in non-stationary time series by learning stationarity-aware weights over spectral components. Unlike traditional normalization methods that rely on low-order statistics, TIFO operates in the frequency space to capture global temporal structures across samples. Extensive experiments show that TIFO consistently improves forecasting performance across multiple benchmarks, and reduces distributional discrepancies.

Paper Strengths:

1. The paper analyzes distribution shift from the frequency domain, rather than relying solely on time-domain normalization. This perspective is well-motivated and highlights limitations of existing methods that focus only on low-order statistics.

2. TIFO is model-agnostic and can be easily integrated into different backbones (e.g., DLinear, PatchTST, iTransformer) without architectural changes, making it practical and broadly applicable.

Paper Weaknesses:

1. It would be helpful if Table 2 could also include the original results of the backbone models.

2. Some table references are not properly displayed and appear as “Table ??".

Resubmission:

N/A

Questions And Suggestions For Rebuttal:

1. In Table 2, “TIFO *” represents the results where both TIFO and SAN are used in the backbones. I do not understand why two normalization methods are applied simultaneously, nor whether this practice is appropriate. What does the comparison between “TIFO *” and “TIFO" indicate?

2. The main text seems to lack discussion and explanation of Figure 2. What does Figure 2 illustrate, and how should it be interpreted?

3. “Time-Invariant” is a fundamental concept in signal processing, system theory, and time series modeling, referring to systems whose behavior does not change over time. I do not understand why the authors use “Time-Invariant” to describe their proposed method; on the contrary, I believe the method is actually time-variant. In Section 2.2, the authors argue that existing methods reduce the conditional dependence on t, transforming the time-varying distribution p(x | t) toward a stationary form p(x). Since p(x) does not explicitly depend on time, it can be considered time-invariant, and the authors clearly regard this as a limitation.

Relevance: 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

Novelty: 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

Technical Quality: 2: Low - The paper has several technical weaknesses, such as minor methodological flaws, insufficient analysis, or unsupported conclusions. While the work shows some level of competence, it lacks thoroughness and precision. Improvements are necessary for it to be considered robust.

Presentation: 3: Moderate - The paper is organized and generally clear. The writing is mostly free of grammatical and typographical errors, making it easy to read. Figures and tables are effectively used to support the text. The presentation facilitates understanding and conveys the key points effectively.

Reproducibility: 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

Reviewer Confidence: 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

Ethics Review Flag: No

Ethics Review Description: N/A
```

## Reviewer JIEp

Official Review of Submission991

20 Mar 2026, 15:35 (modified: 16 May 2026, 11:25)

```text
Paper Summary:

This paper introduces TIFO, a plug-and-play preprocessing module designed to address distribution shift in non-stationary time series forecasting. The core mechanism involves mapping time series into the frequency domain via DFT and applying a learnable weighting scheme to emphasize stationary components while suppressing non-stationary ones. In essence, TIFO aims to capture dataset-level stationarity by learning a unified spectral operator that is assumed to be invariant across different temporal distributions.

Paper Strengths:

1. This paper establishes a connection between non-stationarity and spectral analysis through Bochner's and Mercer's theorems, offering a theoretical perspective for understanding distribution shift in time series.

2. The proposed method is unsupervised and model-agnostic, making it a plug-and-play preprocessing module that can be easily integrated into various forecasting architectures, which enhances its practical applicability.

Paper Weaknesses:

1. The core idea of reweighting frequency components after DFT appears to be a straightforward extension of existing frequency-domain normalization or filtering techniques. The contribution mainly relies on a learnable frequency reweighting mechanism, but lacks sufficient theoretical justification to explain why such a design effectively addresses non-stationarity, making the contribution incremental. Why use the deviation of the mean and the standard?

2. The manuscript appears to be in an incomplete state. The presence of numerous broken cross-references (e.g., Table ?? in page 6) hinders a thorough evaluation of the proposed ablation studies and computational claims.

Resubmission:

No

Questions And Suggestions For Rebuttal:

1. The author claims to consider 'all possible time structures' via the time-integral in Eq (2). However, this relies heavily on Assumption 1 (that the training set is representative enough). If the test set exhibits a temporal structure t_new that is outside the support of p(t), the 'Time-Invariant' property might fail. Does the author provide an analysis on how much data is 'sufficient' to represent 'all possible structures'?

2. On the ETTh1 dataset, the improvement brought by S compared to random initialization of weights is limited, and it also increased the standard deviation, which may introduce additional instability into the training process, making the model less robust than simple random initialization. The authors should explain why a principled starting point leads to higher variance and whether this trade-off is acceptable in real-world deployments.

3. There are multiple broken cross-references to critical evidence (e.g., Table ?? in “Frequency modeling ablation studies”, Appendix B.1, and Appendix B.3). These missing elements prevent a thorough evaluation of the proposed ablation studies and efficiency claims.

4. The authors state that the best results are highlighted in bold. However, in Table 16, the MSE for ema_0.9 (0.3932) is better than the bolded value for no_update (0.3938). Such inconsistent and incorrect formatting further diminishes the credibility of the reported experimental analysis.

5. There are several grammatical issues throughout the paper. For example, “... so it can sufficiently representation the distributions”. A careful proofreading would improve the overall clarity of the manuscript.

Relevance: 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

Novelty: 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

Technical Quality: 3: Moderate - The paper demonstrates solid technical quality with a sound methodology and thorough analysis. The results are reliable and well-supported. There may be minor issues, but they do not significantly undermine the overall quality. The work is competently executed and meets acceptable standards.

Presentation: 1: Poor - The paper is poorly organized and difficult to follow. The writing is unclear, with numerous grammatical and typographical errors. Figures and tables, if present, are poorly designed or hard to understand. Overall, the presentation detracts significantly from the readability and comprehension of the work.

Reproducibility: 2: Low - The paper includes some information about the methods, data, and procedures, but key details are missing. There may be supplementary materials, but they are incomplete or unclear. Reproducing the results would require significant effort and additional information.

Reviewer Confidence: 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

Ethics Review Flag: No

Ethics Review Description: No
```

## Reviewer 54Tf

Official Review of Submission991

20 Mar 2026, 15:35 (modified: 16 May 2026, 11:25)

```text
Paper Summary:

This paper proposes the time-invariant frequency operator to address non-stationarity in time series forecasting from a frequency-domain perspective. TIFO leverages global dataset statistics (the signal-to-noise ratio (mean divided by variance) of frequency amplitudes) calculated offline. During training, these stationary scores act as a fixed prior for an MLP-based modulation layer that adaptively weights frequency components to highlight stable patterns and suppress non-stationary ones. TIFO is designed as a plug-and-play module and is evaluated across multiple backbones (DLinear, PatchTST, iTransformer). Experimental results on non-stationary datasets like ETTm2 show significant improvements in MSE and MAE compared to existing normalization baselines.

Paper Strengths:

1. This paper is well-written, with clear logic and a well-organized structure. The author provides a workflow for the algorithm and clearly explains its concepts and principles.

2. It proposes to use dataset-wide statistics (mean/variance of amplitudes) as a stationary score to guide sample-level modulation.

3. It demonstrates seamless integration with diverse architectures, including linear models and Transformers, and it can be easily integrated into multiple backbones.

Paper Weaknesses:

1. According to Figure 1, Step 1 to Step 2 extracts and separates frequency features f_k into stationary (f_s) and non-stationary (f_n) components. However, Section 3.1 describes a different mechanism where the MLP takes pre-calculated scores S as input to produce a single weight λ for modulation. There is no separation operation as depicted in the diagram. This creates a severe disconnect between the visual representation of the method and its actual implementation.

2. The dimension of the amplitude matrix A is not specified.

3. Sections 2.1, 2.2, and 2.3 contain overlapping discussions regarding distribution shifts and the p(x|t) problem

Resubmission:

N/A

Questions And Suggestions For Rebuttal:

The proposed mechanism is somewhat lightweight and simple. What's the potential of the proposed method to work as a general feature enhancement tool beyond long-term forecasting, such as imputation and classification?

Relevance: 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

Novelty: 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

Technical Quality: 3: Moderate - The paper demonstrates solid technical quality with a sound methodology and thorough analysis. The results are reliable and well-supported. There may be minor issues, but they do not significantly undermine the overall quality. The work is competently executed and meets acceptable standards.

Presentation: 3: Moderate - The paper is organized and generally clear. The writing is mostly free of grammatical and typographical errors, making it easy to read. Figures and tables are effectively used to support the text. The presentation facilitates understanding and conveys the key points effectively.

Reproducibility: 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

Reviewer Confidence: 4: High - The reviewer is an expert in the subject area and has extensive knowledge of the research methods and context of the paper. They are highly confident in their ability to provide an accurate and thorough assessment. Their evaluation is based on deep expertise and a comprehensive understanding of the work.

Ethics Review Flag: No

Ethics Review Description: no
```

## Reviewer eBmV

Official Review of Submission991

16 Mar 2026, 11:32 (modified: 16 May 2026, 11:25)

```text
Paper Summary:

The authors proposed a Time-Invariant Frequency Operator (TIFO), which learns stationarity-aware weights over the frequency spectrum across the entire dataset. The weight representation highlights stationary frequency components while suppressing non-stationary ones, thereby mitigating the distribution shift issue in time series.

Paper Strengths:

The stationarity-aware weight representation highlights stationary frequency components while suppressing non-stationary ones, thereby mitigating the distribution shift issue in time series.

TIFO is a plug-and-play approach that can be seamlessly integrated into various forecasting models.

Paper Weaknesses:

1. From normalization methods to TIFO, there are no evidence to support their relationship. What is the relationship between Normalization methods and Time-Invariant Frequency Operator?

2. Why do frequency shifts could replace the distributional shift of training datasets and test datasets? Maybe it only is one part of the distributional shift of datasets.

3. How could TIFO could solve the distributional shift with the theoretical analysis? It lacks theoretical justification.

4. The baseline methods are weak. It lacks SOTA algorithms from 2025 and 2026.

5. How could TIFO obtains stationarity-aware representation in the experiment? Which experimental setting could support the statement?

Resubmission:

N/A

Questions And Suggestions For Rebuttal:

1. How could TIFO could solve the distributional shift with the theoretical analysis? It lacks theoretical justification.

2. The baseline methods are weak. It lacks SOTA algorithms from 2025 and 2026.

3. How could TIFO obtains stationarity-aware representation in the experiment? Which experimental setting could support the statement?

Relevance: 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

Novelty: 3: Moderate - The paper introduces a new and interesting idea or approach that adds value to the field. The contribution is original and represents an advancement of existing knowledge, demonstrating solid innovation and creativity.

Technical Quality: 3: Moderate - The paper demonstrates solid technical quality with a sound methodology and thorough analysis. The results are reliable and well-supported. There may be minor issues, but they do not significantly undermine the overall quality. The work is competently executed and meets acceptable standards.

Presentation: 3: Moderate - The paper is organized and generally clear. The writing is mostly free of grammatical and typographical errors, making it easy to read. Figures and tables are effectively used to support the text. The presentation facilitates understanding and conveys the key points effectively.

Reproducibility: 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

Reviewer Confidence: 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

Ethics Review Flag: No

Ethics Review Description: N/A
```
