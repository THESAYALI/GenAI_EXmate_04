# Eval results (15 questions)

| Config | chunk_size (words) | top_k | Answer accuracy | Retrieval hit | 'I don't know' correct | Citation rate | Winner |
|---|---|---|---|---|---|---|---|
| A: small chunks, top-3 | 40 | 3 | 60% | 50% | 100% | 50% |  |
| B: big chunks, top-5 | 120 | 5 | 67% | 58% | 100% | 58% | **YES** |

Winner: **B: big chunks, top-5**

## Per question

| Q | answerable | correct | confident | citations (A) | correct (B) |
|---|---|---|---|---|---|
| Q01 | True | True | True | 1 | True |
| Q02 | True | True | True | 1 | True |
| Q03 | True | False | False | 0 | False |
| Q04 | True | True | True | 1 | True |
| Q05 | True | False | False | 0 | False |
| Q06 | False | True | False | 0 | True |
| Q07 | True | True | True | 1 | True |
| Q08 | True | True | True | 1 | True |
| Q09 | True | False | False | 0 | False |
| Q10 | True | False | False | 0 | True |
| Q11 | True | False | False | 0 | False |
| Q12 | True | False | False | 0 | False |
| Q13 | False | True | False | 0 | True |
| Q14 | False | True | False | 0 | True |
| Q15 | True | True | True | 1 | True |
